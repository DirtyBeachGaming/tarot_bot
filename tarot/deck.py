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

    @property
    def image_path(self) -> Path:
        return ROOT / self.image


@dataclass(frozen=True)
class Draw:
    card: Card
    reversed: bool

    @property
    def orientation(self) -> str:
        return "reversed" if self.reversed else "upright"

    @property
    def title(self) -> str:
        return f"{self.card.name}{' (reversed)' if self.reversed else ''}"

    @property
    def keywords(self) -> list[str]:
        return self.card.keywords[self.orientation]

    @property
    def meaning(self) -> str:
        return self.card.meaning[self.orientation]


class Deck:
    def __init__(self, path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.description: str = data.get("description", "")
        self.suits: dict = data.get("suits", {})
        self.cards: list[Card] = [Card(**c) for c in data["cards"]]
        self._by_id = {c.id: c for c in self.cards}

    @classmethod
    def load(cls, deck_id: str) -> "Deck":
        return cls(DATA_DIR / f"{deck_id}.json")

    def get(self, card_id: str) -> Card | None:
        return self._by_id.get(card_id)

    def search(self, text: str, limit: int = 25) -> list[Card]:
        text = text.lower().strip()
        if not text:
            return self.cards[:limit]
        starts = [c for c in self.cards if c.name.lower().removeprefix("the ").startswith(text)]
        contains = [c for c in self.cards if text in c.name.lower() and c not in starts]
        return (starts + contains)[:limit]

    def draw(self, n: int, reversal_chance: float = 0.3) -> list[Draw]:
        """Shuffle the full deck and deal n cards off the top (no repeats)."""
        cards = self.cards[:]
        _rng.shuffle(cards)
        return [Draw(c, _rng.random() < reversal_chance) for c in cards[:n]]
