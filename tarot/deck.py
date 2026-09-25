"""Deck loading and card drawing."""
from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# Cryptographically random shuffles, so no one can accuse the bot of rigging the cards.
_rng = secrets.SystemRandom()


@dataclass(frozen=True)
class Card:
    id: str
    name: str
    arcana: str
    number: int
    suit: str | None
    rank: str | None
    keywords: dict
    meaning: dict
    image: str
    source_url: str
    name_en: str | None = None   # English name for decks with non-English card names
    insert: str | None = None    # playing-card insert shown on Lenormand cards, e.g. "9♥"
    reversible: bool = True      # False for cards that look the same upside down (some runes)

    @property
    def image_path(self) -> Path:
        return ROOT / self.image

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.name_en})" if self.name_en else self.name


@dataclass(frozen=True)
class Draw:
    card: Card
    reversed: bool

    @property
    def orientation(self) -> str:
        return "reversed" if self.reversed else "upright"

    @property
    def title(self) -> str:
        return f"{self.card.display_name}{' — reversed' if self.reversed else ''}"

    @property
    def keywords(self) -> list[str]:
        return self.card.keywords.get(self.orientation) or self.card.keywords["upright"]

    @property
    def meaning(self) -> str:
        return self.card.meaning.get(self.orientation) or self.card.meaning["upright"]


class Deck:
    def __init__(self, path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.short_name: str = data.get("short_name", self.name)
        self.family: str = data.get("family", "Other")
        self.description: str = data.get("description", "")
        self.aspect: float = data.get("card_aspect", 0.58)   # width / height
        self.color: int = data.get("color", 0x6A4C93)
        self.suits: dict = data.get("suits", {})
        self.reversals: bool = data.get("reversals", True)
        self.spreads: list[str] = data.get("spreads", ["single", "three", "situation", "celtic"])
        self.cards: list[Card] = [Card(**c) for c in data["cards"]]
        self._by_id = {c.id: c for c in self.cards}

    @classmethod
    def load(cls, deck_id: str) -> "Deck":
        return cls(DATA_DIR / f"{deck_id}.json")

    @classmethod
    def load_all(cls) -> dict[str, "Deck"]:
        return {d.id: d for d in (cls(p) for p in sorted(DATA_DIR.glob("*.json")))}

    def color_for(self, card: Card) -> int:
        return self.suits.get(card.suit, {}).get("color", self.color) if card.suit else self.color

    def get(self, card_id: str) -> Card | None:
        return self._by_id.get(card_id)

    def search(self, text: str, limit: int = 25) -> list[Card]:
        text = text.lower().strip()
        if not text:
            return self.cards[:limit]

        def names(c: Card):
            return [n.lower() for n in (c.name, c.name_en) if n]

        starts = [c for c in self.cards
                  if any(n.removeprefix("the ").startswith(text) for n in names(c))]
        contains = [c for c in self.cards
                    if c not in starts and any(text in n for n in names(c))]
        return (starts + contains)[:limit]

    def draw(self, n: int, reversal_chance: float = 0.3, exclude: set[str] | None = None) -> list[Draw]:
        """Shuffle the deck and deal n cards off the top (no repeats, skipping `exclude` ids)."""
        cards = [c for c in self.cards if not exclude or c.id not in exclude]
        _rng.shuffle(cards)
        chance = reversal_chance if self.reversals else 0.0
        return [Draw(c, c.reversible and _rng.random() < chance) for c in cards[:n]]
