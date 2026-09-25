"""Turns a spread into one short 'read together' line in the bot's voice."""
from __future__ import annotations

import secrets

from .deck import Draw

_rng = secrets.SystemRandom()

OPENERS = ["It begins in", "The story opens on", "First comes", "At the root is"]
MIDDLES = ["moves through", "turns on", "passes through", "is shaped by"]
CLOSERS = ["and lands on", "and comes to rest in", "and points toward", "and ends in"]


def _kw(d: Draw) -> str:
    return f"*{d.keywords[0]}*"


def read_together(draws: list[Draw]) -> str | None:
    """One sentence linking the cards' leading keywords, for spreads of 2 to 10 cards."""
    if not 2 <= len(draws) <= 10:
        return None
    first, last, middle = draws[0], draws[-1], draws[1:-1]
    parts = [f"{_rng.choice(OPENERS)} {_kw(first)}"]
    if middle:
        mids = [_kw(d) for d in middle]
        joined = mids[0] if len(mids) == 1 else ", ".join(mids[:-1]) + f" and {mids[-1]}"
        parts.append(f"{_rng.choice(MIDDLES)} {joined}")
    parts.append(f"{_rng.choice(CLOSERS)} {_kw(last)}.")
    reversed_n = sum(d.reversed for d in draws)
    tail = ""
    if reversed_n and reversed_n >= len(draws) / 2:
        tail = " Many cards are reversed: something is blocked or turned inward."
    return "Read together: " + ", ".join(parts[:-1]) + " " + parts[-1] + tail


def yes_no_verdict(draws: list[Draw]) -> str:
    ups = sum(not d.reversed for d in draws)
    return {3: "**Yes.** All three cards are upright.",
            2: "**Leaning yes.** Two of three cards are upright.",
            1: "**Leaning no.** Two of three cards are reversed.",
            0: "**No.** All three cards are reversed."}[ups]
