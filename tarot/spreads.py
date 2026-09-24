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
}
