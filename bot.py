"""Card-reading Discord bot: slash commands, locked to one channel."""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from tarot import extras, iching
from tarot.deck import Deck, Draw
from tarot.images import ensure_image, render_spread, single_card_png
from tarot.limits import ReadingLimiter
from tarot.spreads import SPREADS, spreads_for
from tarot.store import UserStore
from tarot.story import read_together, yes_no_verdict

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("tarot")

# ---------- settings (.env or Railway variables) ----------
TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["TAROT_CHANNEL_ID"])
GUILD_ID = int(os.environ["GUILD_ID"]) if os.getenv("GUILD_ID") else None
REVERSAL_CHANCE = float(os.getenv("REVERSAL_CHANCE", "0.3"))
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "1"))          # readings per user per 24h; 0 = unlimited
EXEMPT_ADMINS = os.getenv("LIMIT_EXEMPT_ADMINS", "true").lower() == "true"
STATE_DIR = Path(os.getenv("STATE_DIR", "state"))        # on Railway, point this at a volume
TIMEZONE = ZoneInfo(os.getenv("TIMEZONE", "America/Los_Angeles"))
DAILY_CARD_TIME = os.getenv("DAILY_CARD_TIME", "09:00")  # 24h clock in TIMEZONE; "off" to disable
DAILY_CARD_DECK = os.getenv("DAILY_CARD_DECK", "")        # empty = the default deck

DECKS = Deck.load_all()                                  # every data/*.json
DEFAULT_DECK = os.getenv("DEFAULT_DECK", "rws1909")
if DEFAULT_DECK not in DECKS:
    DEFAULT_DECK = next(iter(DECKS))
FAMILY_ORDER = ["Tarot", "Italian tarot", "Central European tarot", "Italian regional", "Spanish",
                "Oracle", "Playing cards", "Runes", "Staves & signs", "Other"]

limiter = ReadingLimiter(STATE_DIR / "readings.db", DAILY_LIMIT)
store = UserStore(STATE_DIR / "readings.db")


# ---------- deck helpers ----------

def find_deck(value: str | None) -> Deck | None:
    """A deck id (from autocomplete) or a typed deck name, or None if nothing matches."""
    if not value:
        return None
    if value in DECKS:
        return DECKS[value]
    v = value.lower().strip()
    for dk in DECKS.values():
        if v in (dk.name.lower(), dk.short_name.lower()):
            return dk
    for dk in DECKS.values():
        if v in dk.name.lower():
            return dk
    return None


def pick_deck(value: str | None, user_id: int | None = None) -> Deck:
    """Explicit choice, else the member's own deck (/mydeck), else the server default."""
    dk = find_deck(value)
    if dk:
        return dk
    if user_id is not None and (mine := store.get_deck(user_id)) in DECKS:
        return DECKS[mine]
    return DECKS[DEFAULT_DECK]


def _deck_sort_key(dk: Deck):
    fam = FAMILY_ORDER.index(dk.family) if dk.family in FAMILY_ORDER else len(FAMILY_ORDER)
    return (dk.id != DEFAULT_DECK, fam, dk.name)


async def deck_autocomplete(interaction: discord.Interaction, current: str):
    cur = current.lower().strip()
    hits = [dk for dk in sorted(DECKS.values(), key=_deck_sort_key)
            if not cur or cur in dk.name.lower() or cur in dk.family.lower()]
    return [app_commands.Choice(name=f"{dk.name} · {dk.family}"[:100], value=dk.id) for dk in hits[:25]]


def deck_from_namespace(interaction: discord.Interaction) -> Deck:
    value = getattr(interaction.namespace, "deck", None)
    return pick_deck(value if isinstance(value, str) else None, interaction.user.id)


# ---------- channel lock ----------

def in_tarot_channel(channel) -> bool:
    if channel is None:
        return False
    if channel.id == CHANNEL_ID:
        return True
    return isinstance(channel, discord.Thread) and channel.parent_id == CHANNEL_ID


class TarotTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if in_tarot_channel(interaction.channel):
            return True
        if interaction.type == discord.InteractionType.autocomplete:
            return False
        await interaction.response.send_message(
            f"🔮 Readings are only given in <#{CHANNEL_ID}>.", ephemeral=True)
        return False


class TarotBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = TarotTree(self)
        self.http_session: aiohttp.ClientSession | None = None

    async def setup_hook(self):
        self.http_session = aiohttp.ClientSession()
        if GUILD_ID:  # instant command registration for one server
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info("Synced commands to guild %s", GUILD_ID)
        else:
            await self.tree.sync()
            log.info("Synced commands globally")
        if DAILY_CARD_TIME.lower() != "off":
            daily_card.start()

    async def close(self):
        if self.http_session:
            await self.http_session.close()
        await super().close()

    async def on_ready(self):
        log.info("Logged in as %s — channel %s — %d decks", self.user, CHANNEL_ID, len(DECKS))


bot = TarotBot()


# ---------- reading helpers ----------

def card_line(d: Draw) -> str:
    return f"*{', '.join(d.keywords)}*\n{d.meaning}"


async def fetch_images(draws: list[Draw]):
    await asyncio.gather(*(ensure_image(d.card, bot.http_session) for d in draws))


async def check_limit(interaction: discord.Interaction) -> str | None:
    """Uses one of the member's daily readings. Returns a footer note, or None if blocked
    (the member has then already been told privately)."""
    member = interaction.user
    if EXEMPT_ADMINS and getattr(member, "guild_permissions", None) and member.guild_permissions.manage_guild:
        return ""
    allowed, left, next_at = limiter.try_use(member.id)
    if not allowed:
        await interaction.response.send_message(
            f"🌙 The cards need rest. You've had your reading for today — "
            f"your next one is available <t:{int(next_at)}:R> (<t:{int(next_at)}:t>).",
            ephemeral=True)
        return None
    if left < 0:
        return ""
    return f" · {left} reading{'s' if left != 1 else ''} left today" if left else " · last reading for today"


def reading_embed(dk: Deck, sp, draws: list[Draw], question: str | None, footer: str) -> discord.Embed:
    embed = discord.Embed(title=f"{sp.name} · {dk.short_name}", color=dk.color)
    lines = []
    if question:
        lines.append(f"**“{question}”**")
    if sp.key == "yesno":
        lines.append(yes_no_verdict(draws))
    if not dk.reversals and 1 < sp.size <= 10:
        lines.append(" → ".join(d.card.name for d in draws))
    if together := read_together(draws):
        lines.append(together)

    if sp.size <= 12:
        for i, (pos, d) in enumerate(zip(sp.positions, draws), start=1):
            embed.add_field(name=f"{i}. {pos.label} — {d.title}"[:256],
                            value=f"↳ {pos.prompt}\n{card_line(d)}"[:1024], inline=False)
    else:  # big layouts: one compact line per card
        lines.append("")
        lines += [f"`{i:>2}` {pos.label}: **{d.title}** — *{d.keywords[0]}*"
                  for i, (pos, d) in enumerate(zip(sp.positions, draws), start=1)]
    embed.description = "\n".join(lines)[:4096] or None
    embed.set_footer(text=footer)
    return embed


class ClarifyView(discord.ui.View):
    """One 'Clarify' button under a reading: draws one more card from what's left."""

    def __init__(self, owner_id: int, dk: Deck, drawn: list[Draw], question: str | None):
        super().__init__(timeout=900)
        self.owner_id, self.dk, self.drawn, self.question = owner_id, dk, drawn, question
        self.message: discord.Message | None = None

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(label="Clarify", emoji="✨", style=discord.ButtonStyle.secondary)
    async def clarify(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Only the person who asked can draw a clarifier.",
                                                    ephemeral=True)
            return
        button.disabled = True
        await interaction.response.edit_message(view=self)
        d = self.dk.draw(1, REVERSAL_CHANCE, exclude={x.card.id for x in self.drawn})[0]
        await fetch_images([d])
        embed = discord.Embed(title=f"Clarifier — {d.title}", description=card_line(d),
                              color=self.dk.color_for(d.card))
        embed.set_footer(text=f"{self.dk.name} · drawn for {interaction.user.display_name}")
        file = discord.File(await asyncio.to_thread(single_card_png, d, self.dk.aspect), filename="card.png")
        embed.set_thumbnail(url="attachment://card.png")
        await interaction.followup.send(embed=embed, file=file)
        store.add(self.owner_id, self.dk.id, "clarifier", self.question, [d.title])
        self.stop()


# ---------- commands: readings ----------

@bot.tree.command(name="draw", description="Draw a single card")
@app_commands.describe(question="Optional: what you're asking about", deck="Which deck (default: yours)")
@app_commands.autocomplete(deck=deck_autocomplete)
async def draw_cmd(interaction: discord.Interaction, question: str | None = None, deck: str | None = None):
    note = await check_limit(interaction)
    if note is None:
        return
    await interaction.response.defer(thinking=True)
    dk = pick_deck(deck, interaction.user.id)
    d = dk.draw(1, REVERSAL_CHANCE)[0]
    await fetch_images([d])

    embed = discord.Embed(title=d.title, description=card_line(d), color=dk.color_for(d.card))
    if question:
        embed.set_author(name=f"“{question}”")
    embed.set_footer(text=f"{dk.name} · drawn for {interaction.user.display_name}{note}")
    file = discord.File(await asyncio.to_thread(single_card_png, d, dk.aspect), filename="card.png")
    embed.set_image(url="attachment://card.png")
    view = ClarifyView(interaction.user.id, dk, [d], question)
    view.message = await interaction.followup.send(embed=embed, file=file, view=view)
    store.add(interaction.user.id, dk.id, "single", question, [d.title])


@bot.tree.command(name="reading", description="Lay out a spread")
@app_commands.describe(deck="Which deck (pick first: spreads depend on the deck)",
                       spread="Which spread to lay", question="Optional: what you're asking about")
@app_commands.autocomplete(deck=deck_autocomplete)
async def reading_cmd(interaction: discord.Interaction, spread: str,
                      question: str | None = None, deck: str | None = None):
    dk = pick_deck(deck, interaction.user.id)
    allowed = spreads_for(dk)
    by_name = {SPREADS[k].name.lower(): k for k in allowed}
    spread = spread if spread in SPREADS else by_name.get(spread.lower().strip(), spread)
    if spread not in allowed:  # checked before the daily limit is used
        names = ", ".join(SPREADS[k].name for k in allowed)
        await interaction.response.send_message(f"{dk.short_name} spreads: {names}.", ephemeral=True)
        return
    note = await check_limit(interaction)
    if note is None:
        return
    await interaction.response.defer(thinking=True)
    sp = SPREADS[spread]
    draws = dk.draw(sp.size, REVERSAL_CHANCE)
    await fetch_images(draws)

    embed = reading_embed(dk, sp, draws, question,
                          f"{dk.name} · read for {interaction.user.display_name}{note}")
    png = await asyncio.to_thread(render_spread, sp, draws, dk.aspect)
    file = discord.File(png, filename="spread.png")
    embed.set_image(url="attachment://spread.png")
    if sp.size < len(dk.cards):
        view = ClarifyView(interaction.user.id, dk, draws, question)
        view.message = await interaction.followup.send(embed=embed, file=file, view=view)
    else:
        await interaction.followup.send(embed=embed, file=file)
    store.add(interaction.user.id, dk.id, sp.name, question, [d.title for d in draws])


@reading_cmd.autocomplete("spread")
async def spread_autocomplete(interaction: discord.Interaction, current: str):
    dk = deck_from_namespace(interaction)
    return [app_commands.Choice(name=f"{SPREADS[k].name} ({SPREADS[k].size})", value=k)
            for k in spreads_for(dk) if current.lower() in SPREADS[k].name.lower()][:25]


@bot.tree.command(name="iching", description="Cast an I Ching hexagram with three coins")
@app_commands.describe(question="Optional: what you're asking about")
async def iching_cmd(interaction: discord.Interaction, question: str | None = None):
    note = await check_limit(interaction)
    if note is None:
        return
    await interaction.response.defer(thinking=True)
    c = iching.cast()
    n1 = iching.number(c.primary)
    name1, text1 = iching.HEXAGRAMS[n1]
    shape1, _ = iching.trigrams(c.primary)
    embed = discord.Embed(title=f"Hexagram {n1} · {name1}", color=0xB08D2E)
    embed.description = ((f"**“{question}”**\n" if question else "") + f"*{shape1}*\n{text1}")
    if c.changing:
        n2 = iching.number(c.relating)
        name2, text2 = iching.HEXAGRAMS[n2]
        shape2, _ = iching.trigrams(c.relating)
        embed.add_field(name="Changing lines", inline=False,
                        value=f"Line{'s' if len(c.changing) > 1 else ''} {', '.join(map(str, c.changing))} "
                              "(counted from the bottom) are in motion.")
        embed.add_field(name=f"Becoming Hexagram {n2} · {name2}", value=f"*{shape2}*\n{text2}", inline=False)
    else:
        embed.add_field(name="No changing lines", value="The situation is stable as it stands.", inline=False)
    embed.set_footer(text=f"I Ching · cast for {interaction.user.display_name}{note}")
    file = discord.File(await asyncio.to_thread(iching.render, c), filename="hexagram.png")
    embed.set_image(url="attachment://hexagram.png")
    await interaction.followup.send(embed=embed, file=file)
    cards = [f"{n1} {name1}"] + ([f"→ {iching.number(c.relating)} {iching.HEXAGRAMS[iching.number(c.relating)][0]}"]
                                 if c.changing else [])
    store.add(interaction.user.id, "iching", "Hexagram", question, cards)


@bot.tree.command(name="pendulum", description="Ask the pendulum a yes-or-no question")
@app_commands.describe(question="Your yes-or-no question")
async def pendulum_cmd(interaction: discord.Interaction, question: str):
    answer, text = extras.pendulum()
    embed = discord.Embed(title=f"🔮 {answer}", description=f"**“{question}”**\n{text}", color=0x7048E8)
    embed.set_footer(text=f"Pendulum · for {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="astrodice", description="Roll the three astrology dice: planet, sign and house")
@app_commands.describe(question="Optional: what you're asking about")
async def astrodice_cmd(interaction: discord.Interaction, question: str | None = None):
    note = await check_limit(interaction)
    if note is None:
        return
    p, s, h, summary = extras.astro_dice()
    embed = discord.Embed(title="🎲 Astrology dice", color=0x1864AB,
                          description=(f"**“{question}”**\n" if question else "") + summary)
    embed.add_field(name=p[0], value=p[1])
    embed.add_field(name=s[0], value=s[1])
    embed.add_field(name=h[0], value=h[1])
    embed.set_footer(text=f"Astrology dice · rolled for {interaction.user.display_name}{note}")
    await interaction.response.send_message(embed=embed)
    store.add(interaction.user.id, "astrodice", "Dice", question, [p[0], s[0], h[0]])


# ---------- commands: lookup & personal ----------

def _resolve_card(value: str, interaction: discord.Interaction, deck_value: str | None):
    """Autocomplete sends 'deck:card_id'; typed text falls back to a name search."""
    if ":" in value:
        deck_id, card_id = value.split(":", 1)
        if deck_id in DECKS and (c := DECKS[deck_id].get(card_id)):
            return DECKS[deck_id], c
    dk = pick_deck(deck_value, interaction.user.id)
    found = dk.search(value, 1)
    return (dk, found[0]) if found else (dk, None)


@bot.tree.command(name="card", description="Look up a card's meaning")
@app_commands.describe(deck="Which deck (pick this first to search its cards)", name="Card name",
                       reversed="Show the card reversed")
@app_commands.autocomplete(deck=deck_autocomplete)
async def card_cmd(interaction: discord.Interaction, name: str, reversed: bool = False, deck: str | None = None):
    dk, card = _resolve_card(name, interaction, deck)
    if not card:
        await interaction.response.send_message(f"No card called “{name}” in {dk.short_name}.", ephemeral=True)
        return
    await interaction.response.defer()
    d = Draw(card, reversed and dk.reversals and card.reversible)
    await fetch_images([d])

    embed = discord.Embed(title=d.title, color=dk.color_for(card))
    if "reversed" in card.meaning:
        embed.add_field(name="Upright", value=f"*{', '.join(card.keywords['upright'])}*\n{card.meaning['upright']}", inline=False)
        embed.add_field(name="Reversed", value=f"*{', '.join(card.keywords['reversed'])}*\n{card.meaning['reversed']}", inline=False)
    else:
        embed.description = f"*{', '.join(card.keywords['upright'])}*\n{card.meaning['upright']}"
    if card.suit and card.suit in dk.suits:
        s = dk.suits[card.suit]
        bits = [s.get("name", card.suit.title()), s.get("element"), s.get("domain")]
        embed.set_footer(text=f"{dk.short_name} · " + " · ".join(b for b in bits if b))
    elif card.insert:
        embed.set_footer(text=f"{dk.short_name} · card {card.number} · {card.insert}")
    else:
        embed.set_footer(text=f"{dk.short_name} · {card.number}")
    file = discord.File(await asyncio.to_thread(single_card_png, d, dk.aspect), filename="card.png")
    embed.set_image(url="attachment://card.png")
    await interaction.followup.send(embed=embed, file=file)


@card_cmd.autocomplete("name")
async def card_autocomplete(interaction: discord.Interaction, current: str):
    dk = deck_from_namespace(interaction)
    return [app_commands.Choice(name=c.display_name[:100], value=f"{dk.id}:{c.id}") for c in dk.search(current)]


@bot.tree.command(name="mydeck", description="Set the deck you read with by default")
@app_commands.describe(deck="Your deck (leave empty to see your current one)", reset="Go back to the server default")
@app_commands.autocomplete(deck=deck_autocomplete)
async def mydeck_cmd(interaction: discord.Interaction, deck: str | None = None, reset: bool = False):
    if reset:
        store.set_deck(interaction.user.id, None)
        msg = f"Back to the server default: **{DECKS[DEFAULT_DECK].name}**."
    elif deck:
        dk = find_deck(deck)
        if not dk:
            msg = f"No deck called “{deck}”. Try `/decks` to see them all."
        else:
            store.set_deck(interaction.user.id, dk.id)
            msg = f"Your deck is now **{dk.name}**. `/draw` and `/reading` will use it unless you pick another."
    else:
        mine = store.get_deck(interaction.user.id)
        msg = (f"Your deck: **{DECKS[mine].name}**." if mine in DECKS
               else f"You're using the server default: **{DECKS[DEFAULT_DECK].name}**.")
    await interaction.response.send_message(msg, ephemeral=True)


@bot.tree.command(name="history", description="Your last few readings (only you can see this)")
async def history_cmd(interaction: discord.Interaction):
    rows = store.recent(interaction.user.id, 5)
    if not rows:
        await interaction.response.send_message("No readings yet.", ephemeral=True)
        return
    embed = discord.Embed(title="Your recent readings", color=DECKS[DEFAULT_DECK].color)
    for r in rows:
        deck_name = DECKS[r["deck"]].short_name if r["deck"] in DECKS else r["deck"].title()
        cards = ", ".join(r["cards"])
        q = f"“{r['question']}”\n" if r["question"] else ""
        embed.add_field(name=f"{deck_name} · {r['spread']}"[:256],
                        value=f"<t:{int(r['ts'])}:R>\n{q}{cards}"[:1024], inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="decks", description="List every deck and divination method")
async def decks_cmd(interaction: discord.Interaction):
    lines, family = [], None
    for dk in sorted(DECKS.values(), key=lambda d: _deck_sort_key(d)[1:]):
        if dk.family != family:
            family = dk.family
            lines.append(f"\n**{family}**")
        star = " ★ default" if dk.id == DEFAULT_DECK else ""
        lines.append(f"• {dk.name} · {len(dk.cards)}{star}")
    lines.append("\n**Other methods**\n• `/iching` · `/astrodice` · `/pendulum`")
    embed = discord.Embed(title=f"The decks ({len(DECKS)})", description="\n".join(lines).strip()[:4096],
                          color=DECKS[DEFAULT_DECK].color)
    embed.set_footer(text="Type in the deck option to search. /mydeck sets your own default.")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="credits", description="Where the card art comes from")
async def credits_cmd(interaction: discord.Interaction):
    lines = [f"**{dk.name}**: {dk.credit}" for dk in sorted(DECKS.values(), key=lambda d: d.name) if dk.credit]
    lines.append("\nOther decks use cards drawn by the bot. Meanings: see /decks.")
    embed = discord.Embed(title="Card art credits", description="\n".join(lines)[:4096], color=DECKS[DEFAULT_DECK].color)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="resetlimit", description="(Admins) Give a member their daily reading back")
@app_commands.default_permissions(manage_guild=True)
@app_commands.describe(member="Whose limit to reset")
async def resetlimit_cmd(interaction: discord.Interaction, member: discord.Member):
    limiter.reset(member.id)
    await interaction.response.send_message(f"Reset {member.mention}'s daily reading.", ephemeral=True)


# ---------- card of the day ----------

def _daily_time() -> dt.time:
    try:
        h, m = (int(x) for x in DAILY_CARD_TIME.split(":"))
    except ValueError:
        h, m = 9, 0
    return dt.time(hour=h, minute=m, tzinfo=TIMEZONE)


@tasks.loop(time=_daily_time())
async def daily_card():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        log.warning("Card of the day: channel %s not found", CHANNEL_ID)
        return
    dk = pick_deck(DAILY_CARD_DECK or None)
    d = dk.draw(1, REVERSAL_CHANCE)[0]
    await fetch_images([d])
    today = dt.datetime.now(TIMEZONE).strftime("%A, %B %-d")
    embed = discord.Embed(title=f"Card of the Day · {d.title}", description=card_line(d),
                          color=dk.color_for(d.card))
    embed.set_author(name=today)
    embed.set_footer(text=f"{dk.name} · the card for everyone today")
    file = discord.File(await asyncio.to_thread(single_card_png, d, dk.aspect), filename="card.png")
    embed.set_image(url="attachment://card.png")
    await channel.send(embed=embed, file=file)


@daily_card.before_loop
async def _wait_ready():
    await bot.wait_until_ready()


# ---------- errors ----------

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        return  # already answered in interaction_check
    log.exception("Command failed", exc_info=error)
    msg = "The cards are clouded — something went wrong. Try again."
    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


if __name__ == "__main__":
    bot.run(TOKEN, log_handler=None)
