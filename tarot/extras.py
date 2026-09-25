"""Pendulum and astrology dice."""
from __future__ import annotations

import secrets

_rng = secrets.SystemRandom()

PENDULUM = [
    (40, "Yes", "The pendulum swings clockwise, wide and sure."),
    (40, "No", "The pendulum swings counter-clockwise, steady and firm."),
    (12, "Not yet", "The pendulum drifts back and forth. The answer isn't settled; ask again later."),
    (8, "Ask differently", "The pendulum barely moves. The question needs to be put another way."),
]


def pendulum() -> tuple[str, str]:
    total = sum(w for w, _, _ in PENDULUM)
    r = _rng.uniform(0, total)
    for w, answer, text in PENDULUM:
        r -= w
        if r <= 0:
            return answer, text
    return PENDULUM[-1][1], PENDULUM[-1][2]


PLANETS = [
    ("☉ Sun", "identity, vitality, purpose"), ("☽ Moon", "emotions, needs, home"),
    ("☿ Mercury", "communication, thinking, short trips"), ("♀ Venus", "love, beauty, money, pleasure"),
    ("♂ Mars", "action, drive, conflict"), ("♃ Jupiter", "growth, luck, generosity"),
    ("♄ Saturn", "discipline, limits, time, lessons"), ("♅ Uranus", "sudden change, freedom, surprise"),
    ("♆ Neptune", "dreams, intuition, confusion"), ("♇ Pluto", "transformation, power, endings"),
    ("☊ North Node", "where you're headed, growth"), ("☋ South Node", "what you're leaving behind, habits"),
]
SIGNS = [
    ("♈ Aries", "boldly, quickly, head-first"), ("♉ Taurus", "slowly, steadily, sensually"),
    ("♊ Gemini", "curiously, through talk and ideas"), ("♋ Cancer", "protectively, emotionally"),
    ("♌ Leo", "proudly, generously, in the spotlight"), ("♍ Virgo", "carefully, practically, in detail"),
    ("♎ Libra", "diplomatically, through partnership"), ("♏ Scorpio", "intensely, secretly, all-in"),
    ("♐ Sagittarius", "optimistically, adventurously"), ("♑ Capricorn", "ambitiously, patiently, by the rules"),
    ("♒ Aquarius", "unconventionally, with friends and ideas"), ("♓ Pisces", "intuitively, compassionately, dreamily"),
]
HOUSES = [
    ("1st House", "you, your body, first impressions"), ("2nd House", "money, possessions, self-worth"),
    ("3rd House", "communication, siblings, the neighbourhood"), ("4th House", "home, family, roots"),
    ("5th House", "romance, creativity, fun, children"), ("6th House", "work, routines, health"),
    ("7th House", "partners, contracts, open rivals"), ("8th House", "shared money, intimacy, transformation"),
    ("9th House", "travel, study, beliefs"), ("10th House", "career, reputation, public life"),
    ("11th House", "friends, groups, hopes"), ("12th House", "the hidden, rest, the subconscious"),
]


def astro_dice():
    p, s, h = _rng.choice(PLANETS), _rng.choice(SIGNS), _rng.choice(HOUSES)
    summary = (f"**{p[0].split(' ', 1)[1]}** ({p[1]}) acts **{s[1]}**, "
               f"in the area of **{h[1]}**.")
    return p, s, h, summary
