"""Tarot reading Discord bot — slash commands, locked to one channel."""
from __future__ import annotations

import asyncio
import logging
import os

import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv

from tarot.deck import Deck, Draw
from pathlib import Path

from tarot.limits import ReadingLimiter
from tarot.images import ensure_image, render_spread, single_card_png
from tarot.spreads import SPREADS

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("tarot")

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["TAROT_CHANNEL_ID"])
GUILD_ID = int(os.environ["GUILD_ID"]) if os.getenv("GUILD_ID") else None
REVERSAL_CHANCE = float(os.getenv("REVERSAL_CHANCE", "0.3"))
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "1"))          # readings per user per 24h; 0 = unlimited
EXEMPT_ADMINS = os.getenv("LIMIT_EXEMPT_ADMINS", "true").lower() == "true"
STATE_DIR = Path(os.getenv("STATE_DIR", "state"))        # on Railway, point this at a volume

SUIT_COLORS = {
    None: 0x6A4C93,         # major arcana: violet
    "wands": 0xD9480F,      # fire
    "cups": 0x1971C2,       # water
    "swords": 0xADB5BD,     # air
    "pentacles": 0x2B8A3E,  # earth
}

deck = Deck.load("rws1909")
limiter = ReadingLimiter(STATE_DIR / "readings.db", DAILY_LIMIT)


def in_tarot_channel(channel: discord.abc.GuildChannel | discord.Thread | None) -> bool:
    if channel is None:
        return False
    if channel.id == CHANNEL_ID:
        return True
    # Allow threads opened inside the tarot channel too.
    return isinstance(channel, discord.Thread) and channel.parent_id == CHANNEL_ID


class TarotTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if in_tarot_channel(interaction.channel):
            return True
        if interaction.type == discord.InteractionType.autocomplete:
            return False
        await interaction.response.send_message(
            f"🔮 Readings are only given in <#{CHANNEL_ID}>.", ephemeral=True
        )
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
        else:  # global sync can take up to an hour to appear
            await self.tree.sync()
            log.info("Synced commands globally")

    async def close(self):
        if self.http_session:
            await self.http_session.close()
        await super().close()

    async def on_ready(self):
        log.info("Logged in as %s — tarot channel %s", self.user, CHANNEL_ID)


bot = TarotBot()


# ---------- helpers ----------

def card_line(d: Draw) -> str:
    return f"*{', '.join(d.keywords)}*\n{d.meaning}"


async def fetch_images(draws: list[Draw]):
    await asyncio.gather(*(ensure_image(d.card, bot.http_session) for d in draws))


async def check_limit(interaction: discord.Interaction) -> str | None:
    """Uses one of the member's daily readings. Returns a footer note, or None if blocked
    (in which case the member has already been told privately)."""
    member = interaction.user
    if EXEMPT_ADMINS and getattr(member, "guild_permissions", None) and member.guild_permissions.manage_guild:
        return ""
    allowed, left, next_at = limiter.try_use(member.id)
    if not allowed:
        await interaction.response.send_message(
            f"🌙 The cards need rest. You've had your reading for today — "
            f"your next one is available <t:{int(next_at)}:R> (<t:{int(next_at)}:t>).",
            ephemeral=True,
        )
        return None
    if left < 0:
        return ""
    return f" · {left} reading{'s' if left != 1 else ''} left today" if left else " · last reading for today"


# ---------- commands ----------

@bot.tree.command(name="draw", description="Draw a single card")
@app_commands.describe(question="Optional: what you're asking about")
async def draw_cmd(interaction: discord.Interaction, question: str | None = None):
    note = await check_limit(interaction)
    if note is None:
        return
    await interaction.response.defer(thinking=True)
    d = deck.draw(1, REVERSAL_CHANCE)[0]
    await fetch_images([d])

    embed = discord.Embed(title=d.title, description=card_line(d), color=SUIT_COLORS[d.card.suit])
    if question:
        embed.set_author(name=f"“{question}”")
    embed.set_footer(text=f"{deck.name} · drawn for {interaction.user.display_name}{note}")
    file = discord.File(await asyncio.to_thread(single_card_png, d), filename="card.png")
    embed.set_image(url="attachment://card.png")
    await interaction.followup.send(embed=embed, file=file)


@bot.tree.command(name="reading", description="Lay out a tarot spread")
@app_commands.describe(spread="Which spread to lay", question="Optional: what you're asking about")
@app_commands.choices(spread=[app_commands.Choice(name=s.name, value=k) for k, s in SPREADS.items()])
async def reading_cmd(interaction: discord.Interaction, spread: app_commands.Choice[str],
                      question: str | None = None):
    note = await check_limit(interaction)
    if note is None:
        return
    await interaction.response.defer(thinking=True)
    sp = SPREADS[spread.value]
    draws = deck.draw(sp.size, REVERSAL_CHANCE)
    await fetch_images(draws)

    embed = discord.Embed(title=sp.name, color=SUIT_COLORS[None])
    if question:
        embed.description = f"**“{question}”**"
    for i, (pos, d) in enumerate(zip(sp.positions, draws), start=1):
        embed.add_field(
            name=f"{i}. {pos.label} — {d.title}",
            value=f"↳ {pos.prompt}\n{card_line(d)}"[:1024],
            inline=False,
        )
    embed.set_footer(text=f"{deck.name} · read for {interaction.user.display_name}{note}")
    png = await asyncio.to_thread(render_spread, sp, draws)
    file = discord.File(png, filename="spread.png")
    embed.set_image(url="attachment://spread.png")
    await interaction.followup.send(embed=embed, file=file)


@bot.tree.command(name="card", description="Look up a card's meaning")
@app_commands.describe(name="Card name", reversed="Show the reversed meaning")
async def card_cmd(interaction: discord.Interaction, name: str, reversed: bool = False):
    card = deck.get(name) or next(iter(deck.search(name, 1)), None)
    if not card:
        await interaction.response.send_message(f"No card called “{name}”.", ephemeral=True)
        return
    await interaction.response.defer()
    d = Draw(card, reversed)
    await fetch_images([d])

    embed = discord.Embed(title=d.title, color=SUIT_COLORS[card.suit])
    embed.add_field(name="Upright", value=f"*{', '.join(card.keywords['upright'])}*\n{card.meaning['upright']}", inline=False)
    embed.add_field(name="Reversed", value=f"*{', '.join(card.keywords['reversed'])}*\n{card.meaning['reversed']}", inline=False)
    if card.suit:
        s = deck.suits.get(card.suit, {})
        embed.set_footer(text=f"{card.suit.title()} · {s.get('element', '')} · {s.get('domain', '')}")
    else:
        embed.set_footer(text=f"Major Arcana · {card.number}")
    file = discord.File(await asyncio.to_thread(single_card_png, d), filename="card.png")
    embed.set_image(url="attachment://card.png")
    await interaction.followup.send(embed=embed, file=file)


@card_cmd.autocomplete("name")
async def card_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=c.name, value=c.id) for c in deck.search(current)]


@bot.tree.command(name="resetlimit", description="(Admins) Give a member their daily reading back")
@app_commands.default_permissions(manage_guild=True)
@app_commands.describe(member="Whose limit to reset")
async def resetlimit_cmd(interaction: discord.Interaction, member: discord.Member):
    limiter.reset(member.id)
    await interaction.response.send_message(f"Reset {member.mention}'s daily reading.", ephemeral=True)


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
