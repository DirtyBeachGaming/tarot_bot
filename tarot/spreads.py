"""Spread definitions.

Each position has a label, a short prompt, and a layout slot (x, y) in card-sized
grid units used by the image renderer. `cross=True` lays the card sideways.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Position:
    label: str
    prompt: str
    x: float
    y: float
    cross: bool = False


@dataclass(frozen=True)
class Spread:
    key: str
    name: str
    positions: list[Position] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.positions)


SPREADS: dict[str, Spread] = {
    "single": Spread("single", "Single Card", [
        Position("The Card", "What you need to know right now", 0, 0),
    ]),
    "three": Spread("three", "Past · Present · Future", [
        Position("Past", "What led here", 0, 0),
        Position("Present", "Where you stand", 1, 0),
        Position("Future", "Where this is heading", 2, 0),
    ]),
    "situation": Spread("situation", "Situation · Action · Outcome", [
        Position("Situation", "The heart of the matter", 0, 0),
        Position("Action", "What to do", 1, 0),
        Position("Outcome", "Likely result", 2, 0),
    ]),
    "celtic": Spread("celtic", "Celtic Cross", [
        Position("Present", "The heart of the matter", 1, 1.5),
        Position("Challenge", "What crosses you", 1, 1.5, cross=True),
        Position("Foundation", "The root beneath it", 1, 2.5),
        Position("Recent Past", "What is passing", 0, 1.5),
        Position("Potential", "What could be", 1, 0.5),
        Position("Near Future", "What approaches", 2, 1.5),
        Position("Self", "Your stance", 3, 3),
        Position("Environment", "Others and surroundings", 3, 2),
        Position("Hopes & Fears", "What you hope or dread", 3, 1),
        Position("Outcome", "Where it all leads", 3, 0),
    ]),
    # ----- Lenormand -----
    "line3": Spread("line3", "Line of Three", [
        Position("Subject", "What this is about", 0, 0),
        Position("Detail", "How it's coloured", 1, 0),
        Position("Outcome", "Where it lands", 2, 0),
    ]),
    "line5": Spread("line5", "Line of Five", [
        Position("Background", "What lies behind", 0, 0),
        Position("Lead-up", "What brought it here", 1, 0),
        Position("Focus", "The heart of the matter", 2, 0),
        Position("Development", "What unfolds", 3, 0),
        Position("Outcome", "Where it leads", 4, 0),
    ]),
    "box9": Spread("box9", "Nine-Card Box", [
        Position("Past · Mind", "Old thoughts and plans", 0, 0),
        Position("Now · Mind", "What's on your mind", 1, 0),
        Position("Next · Mind", "Where your thinking goes", 2, 0),
        Position("Past · Situation", "What's just passed", 0, 1),
        Position("Heart of the Matter", "The centre of it all", 1, 1),
        Position("Next · Situation", "What's coming", 2, 1),
        Position("Past · Roots", "Old foundations", 0, 2),
        Position("Now · Roots", "What's underneath", 1, 2),
        Position("Next · Roots", "What will be built on", 2, 2),
    ]),
    # ----- Austrian Tarock -----
    "industrie": Spread("industrie", "Industrie und Glück", [
        Position("Industrie", "What your own effort brings", 0, 0),
        Position("Glück", "What luck brings", 1, 0),
    ]),
    "trull": Spread("trull", "The Trull", [
        Position("Pagat", "Where you start small", 0, 0),
        Position("Mond", "What holds the power", 1, 0),
        Position("Sküs", "The wild card", 2, 0),
    ]),
    # ----- Runes -----
    "norns": Spread("norns", "The Three Norns", [
        Position("Urðr", "What has been", 0, 0),
        Position("Verðandi", "What is becoming", 1, 0),
        Position("Skuld", "What shall be", 2, 0),
    ]),
    # ----- General -----
    "relationship": Spread("relationship", "Relationship", [
        Position("You", "Where you stand", 0, 0.5),
        Position("The Connection", "What's between you", 1, 0),
        Position("Them", "Where they stand", 2, 0.5),
        Position("The Challenge", "What tests it", 1, 1),
        Position("Where It's Going", "The likely direction", 3, 0.5),
    ]),
    "yesno": Spread("yesno", "Yes or No", [
        Position("First", "Upright leans yes, reversed leans no", 0, 0),
        Position("Second", "Upright leans yes, reversed leans no", 1, 0),
        Position("Third", "Upright leans yes, reversed leans no", 2, 0),
    ]),
    "year": Spread("year", "Year Ahead", [
        Position(f"Month {i + 1}", "The theme of this month", i % 6, i // 6) for i in range(12)
    ]),
    "grand_tableau": Spread("grand_tableau", "Grand Tableau", [
        Position(f"House of the {name}", "", (i % 8) if i < 32 else (i - 32) + 2, i // 8 if i < 32 else 4)
        for i, name in enumerate(['Rider', 'Clover', 'Ship', 'House', 'Tree', 'Clouds', 'Snake', 'Coffin', 'Bouquet', 'Scythe', 'Whip', 'Birds', 'Child', 'Fox', 'Bear', 'Stars', 'Stork', 'Dog', 'Tower', 'Garden', 'Mountain', 'Crossroads', 'Mice', 'Heart', 'Ring', 'Book', 'Letter', 'Man', 'Woman', 'Lily', 'Sun', 'Moon', 'Key', 'Fish', 'Anchor', 'Cross'])
    ]),
}

EXTRA_SPREADS = ("relationship", "yesno", "year", "grand_tableau")


def spreads_for(deck) -> list[str]:
    """A deck's own spreads plus the general ones that fit it."""
    keys = list(deck.spreads)
    n = len(deck.cards)
    if n >= 5:
        keys.append("relationship")
    if deck.reversals:
        keys.append("yesno")
    if n >= 12:
        keys.append("year")
    if deck.id == "lenormand":
        keys.append("grand_tableau")
    return [k for i, k in enumerate(keys) if k not in keys[:i]]
