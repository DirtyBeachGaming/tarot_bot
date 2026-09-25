"""Download all 78 Waite-Smith 1909 card scans from Wikimedia Commons.

Run from the repo root:   python3 scripts/download_cards.py            (every deck)
                          python3 scripts/download_cards.py napoletane (one deck)
Already-downloaded cards are skipped, so it's safe to re-run until everything is in.
Wikimedia rate-limits aggressively, so this goes slowly on purpose (~3s per card)
and waits out any "429 Too Many Requests" before continuing.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tarot.images import shrink_image  # noqa: E402  (re-encodes scans as compact JPEGs)
# Wikimedia's policy asks for a descriptive User-Agent with a contact URL;
# generic ones get throttled much harder.
UA = "TarotDiscordBot/1.0 (https://github.com/DirtyBeachGaming/tarot_bot) python-urllib"
DELAY = 3          # seconds between cards
MAX_TRIES = 6


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main(*deck_ids: str):
    paths = [ROOT / "data" / f"{d}.json" for d in deck_ids] or sorted((ROOT / "data").glob("*.json"))
    failed_total = 0
    for p in paths:
        failed_total += download_deck(json.loads(p.read_text(encoding="utf-8")))
    return 1 if failed_total else 0


def download_deck(deck: dict) -> int:
    print(f"\n== {deck['name']} ==")
    todo = [c for c in deck["cards"] if c.get("source_url")
            and not ((ROOT / c["image"]).exists() and (ROOT / c["image"]).stat().st_size > 10_000)]
    print(f"{len(deck['cards']) - len(todo)} already present, {len(todo)} to download.\n")
    failed = []
    for i, card in enumerate(todo, 1):
        dest = ROOT / card["image"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(1, MAX_TRIES + 1):
            try:
                data = fetch(card["source_url"])
                dest.write_bytes(shrink_image(data))
                print(f"  ✓ [{i}/{len(todo)}] {card['name']}")
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < MAX_TRIES:
                    wait = int(e.headers.get("Retry-After") or 0) or 30 * attempt
                    print(f"  … rate limited on {card['name']} — waiting {wait}s")
                    time.sleep(wait)
                    continue
                err = e
            except Exception as e:
                err = e
                if attempt < MAX_TRIES:
                    time.sleep(5 * attempt)
                    continue
            print(f"  ✗ {card['name']}: {err}")
            failed.append(card["name"])
            break
        time.sleep(DELAY)
    print(f"\nDone: {len(todo) - len(failed)} downloaded, {len(failed)} failed.")
    if failed:
        print("Re-run later to get:", ", ".join(failed))
    return len(failed)


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
