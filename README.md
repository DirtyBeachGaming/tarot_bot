# Tarot Bot

A Discord bot for tarot readings. It uses the 1909 Waite-Smith deck, which is in the public domain. The bot only answers in one channel.

## Commands

| Command | What it does |
|---|---|
| `/draw [question]` | Draws a single card |
| `/reading spread:<…> [question]` | Lays out a spread: Single, Past·Present·Future, Situation·Action·Outcome or Celtic Cross |
| `/card name:<…> [reversed]` | Looks up a card's upright and reversed meaning. Card names autocomplete. Always free. |
| `/resetlimit member:<…>` | Admins only: gives a member their daily reading back |

Each card has a 30% chance of coming up reversed. You can change this with `REVERSAL_CHANCE` in `.env`.

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

## Adding decks

Every deck is a JSON file in `data/`, and they all use the same card format. Planned decks: Vera Sibilla, Lenormand, Austrian Tarock, Napoletane.

## Credits

Card images come from the Waite-Smith Tarot (A. E. Waite & Pamela Colman Smith, 1909, the "Roses & Lilies" first edition). The scans are from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Rider-Waite_tarot_deck_(Roses_%26_Lilies)). The deck is in the public domain.
