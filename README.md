# Tarot Bot

A Discord bot for card readings. It has 29 decks plus the I Ching, astrology dice and a pendulum. Use `/decks` in Discord to see them all. The `deck` option is searchable, so type part of a name ("piac", "minchiate") or a family ("italian"). Every command has an optional `deck` option, and Waite-Smith is the default. The bot only answers in one channel.

## Commands

| Command | What it does |
|---|---|
| `/draw [question]` | Draws a single card |
| `/reading spread:<…> [question] [deck]` | Lays out a spread. Pick the deck first, because the spread list depends on it. Tarot and Napoletane: Single, Past·Present·Future, Situation·Action·Outcome, Celtic Cross. Lenormand: Single, Line of Three, Line of Five, Nine-Card Box. Tarock: Single, Industrie und Glück, The Trull, plus the tarot spreads. |
| `/card name:<…> [reversed]` | Looks up a card's upright and reversed meaning. Card names autocomplete. Always free. |
| `/decks` | Lists every deck and method (only you see the reply) |
| `/mydeck [deck] [reset]` | Sets the deck you read with by default |
| `/history` | Your last five readings (only you see it) |
| `/iching [question]` | Casts a hexagram with three coins, including changing lines and the hexagram it's becoming |
| `/astrodice [question]` | Rolls a planet, a sign and a house |
| `/pendulum question` | A yes-or-no answer (doesn't use your daily reading) |
| `/credits` | Where each deck's card art comes from |
| `/resetlimit member:<…>` | Admins only: gives a member their daily reading back |

Each card has a 30% chance of coming up reversed. You can change this with `REVERSAL_CHANCE` in `.env`.

**Clarify button:** every reading has a ✨ Clarify button. Only the person who asked can press it, once, to draw one more card.

**More spreads:** decks with 5 or more cards get Relationship, decks with 12 or more get Year Ahead, decks that use reversals get Yes or No (three cards: upright leans yes), and Lenormand gets the full 36-card Grand Tableau.

**Card of the day:** the bot posts a card in the channel every day at `DAILY_CARD_TIME` (default `09:00`) in `TIMEZONE` (default `America/Los_Angeles`). Set `DAILY_CARD_TIME=off` to turn it off, and `DAILY_CARD_DECK` to use a particular deck.

**Daily limit:** each member gets `DAILY_LIMIT` readings (`/draw` or `/reading`) per rolling 24 hours. The default is 1, and 0 means unlimited. If they try again too early, the bot privately tells them when their next reading is available. People with Manage Server permission are exempt (`LIMIT_EXEMPT_ADMINS`).

## Setup

### 1. Create the bot on Discord
1. Go to https://discord.com/developers/applications and click **New Application**.
2. On the **Bot** tab, click **Reset Token** and copy the token. You'll put it in `.env`. The bot doesn't need any privileged intents.
3. On the **OAuth2 → URL Generator** tab:
   - Scopes: `bot`, `applications.commands`
   - Bot permissions: View Channels, Send Messages, Send Messages in Threads, Embed Links, Attach Files
4. Open the generated URL and invite the bot to your server.

### 2. Configure
```bash
cp .env.example .env
```
Fill in `DISCORD_TOKEN`, `GUILD_ID` and `TAROT_CHANNEL_ID`. To copy these IDs, first turn on Discord → Settings → Advanced → **Developer Mode**. Then right-click the server icon for the server ID, and right-click the channel for the channel ID.

### 3. Install and run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/download_cards.py   # fetches all 78 card scans (~25 MB), one time only
python3 bot.py
```

## Deploying on Railway
1. Railway → New Project → Deploy from GitHub repo → pick this repo.
2. Service → Variables: add DISCORD_TOKEN, GUILD_ID, TAROT_CHANNEL_ID, REVERSAL_CHANCE.
3. For the daily limit to survive redeploys: right-click the service → **Attach Volume**, set the mount path to `/data`, and add the variable `STATE_DIR=/data`.
4. Railway reads `railway.json` (start command `python bot.py`) and `.python-version`. No public domain/port needed — it's a worker.

Commit the downloaded card images (`cards/rws1909/*.jpg`) so Railway has them; its disk resets on each deploy.

## Keeping it to one channel

The bot has two layers of protection:

1. **The code:** every command checks `TAROT_CHANNEL_ID`. If someone uses a command anywhere else, the bot replies privately and points them to the tarot channel. Threads inside that channel also work.
2. **Discord (optional, recommended):** go to Server Settings → Integrations → *your bot* → Channels. Turn off **All Channels** and add only the tarot channel. The commands then won't show up anywhere else.

## Project layout
```
bot.py                  # Discord commands and the channel lock
tarot/deck.py           # loads the deck, shuffles and draws (crypto-random)
tarot/spreads.py        # spread positions and layouts
tarot/images.py         # card image cache and spread rendering
data/rws1909.json       # 78 cards: names, keywords, upright/reversed meanings, image sources
cards/rws1909/          # card scans (downloaded by the script)
scripts/download_cards.py
```

## Decks

| Deck | Cards | Reversals | Card images |
|---|---|---|---|
| Waite-Smith Tarot (1909) | 78 | yes | public-domain scans |
| Tarot de Marseille | 78 | yes | placeholders (French names, Waite-Smith meanings) |
| Carte Napoletane | 40 | yes | public-domain scans |
| Baraja Española | 40 | yes | placeholders (meanings shared with Napoletane) |
| Petit Lenormand | 36 | no | placeholders |
| Kipper Cards | 36 | no | placeholders |
| Vera Sibilla Italiana | 52 | no | placeholders |
| Austrian Tarock | 54 | no | placeholders (original meaning system) |
| Playing Cards | 52 | no | placeholders |
| Elder Futhark Runes | 24 | yes (except the 9 symmetrical runes) | drawn rune stones |
| Tarocco Piemontese | 78 | no (double-headed) | placeholders (Waite-Smith meanings) |
| Tarocco Bolognese | 62 | no (double-headed) | placeholders (four Mori, no 2–5) |
| Minchiate | 97 | yes | placeholders (virtue, element and zodiac trumps have their own meanings) |
| Italian regional, Latin suits: Piacentine, Siciliane, Trevisane, Bergamasche, Bresciane, Romagnole, Sarde, Triestine, Trentine | 40 each | single-headed patterns only | placeholders (Napoletane meanings) |
| Italian regional, French suits: Piemontesi, Genovesi, Toscane, Milanesi | 40 each | no (double-headed) | placeholders (Napoletane meanings; the Donna gets its own) |

## Adding decks

Every deck is a JSON file in `data/`, and they all use the same card format. The bot loads every deck file automatically. A deck file can list its own `spreads` and set `"reversals": false`, as Lenormand does. `scripts/build_napoletane.py` is a template for writing a new one. Ideas for later: Hanafuda, Grand Jeu Lenormand, Oracle Belline, Etteilla, Minchiate, I Ching.

**Austrian Tarock** is a game deck with no fortune-telling tradition, so its meanings are an original system written for this bot. The tarocks run as a journey through 19th-century town life, from I · Pagat (the underdog) to XXI · Mond and the Sküs.

**Card scans.** Sixteen decks use real scans, mostly 19th-century decks from the Bibliothèque nationale de France (via Wikimedia Commons): Waite-Smith, Marseille, Napoletane, Piacentine, Trevisane, Piemontese, Bolognese, Minchiate, Bergamasche, Bresciane, Romagnole (38 of 40), Baraja (Fournier 1878), Lenormand (W. Reuter), Playing Cards and Hanafuda. The others show cards drawn by the bot. `scripts/apply_scans.py` holds the scan list. Run it after any `build_*.py` script, then run `scripts/download_cards.py` to fetch the images. Scans are saved as compact JPEGs (about 1000px tall). Credits are in `/credits`, and some sets are CC BY-SA, which requires that credit.

## Credits

Placeholder card faces use the DejaVu Serif font (free license, in `fonts/`).


Card images come from the Waite-Smith Tarot (A. E. Waite & Pamela Colman Smith, 1909, the "Roses & Lilies" first edition). The scans are from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Rider-Waite_tarot_deck_(Roses_%26_Lilies)). The deck is in the public domain.

Carte Napoletane scans are from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Naples_deck) (public domain). Their meanings follow general Italian cartomancy conventions.
