"""I Ching: three-coin casting, King Wen lookup, and hexagram rendering."""
from __future__ import annotations

import io
import secrets
from dataclasses import dataclass

from PIL import Image, ImageDraw

_rng = secrets.SystemRandom()

# Trigrams as (bottom, middle, top) with 1 = yang (solid), 0 = yin (broken)
TRIGRAMS = {
    (1, 1, 1): "Qian", (1, 0, 0): "Zhen", (0, 1, 0): "Kan", (0, 0, 1): "Gen",
    (0, 0, 0): "Kun", (0, 1, 1): "Xun", (1, 0, 1): "Li", (1, 1, 0): "Dui",
}
TRIGRAM_EN = {"Qian": "Heaven", "Zhen": "Thunder", "Kan": "Water", "Gen": "Mountain",
              "Kun": "Earth", "Xun": "Wind", "Li": "Fire", "Dui": "Lake"}
ORDER = ["Qian", "Zhen", "Kan", "Gen", "Kun", "Xun", "Li", "Dui"]
# KING_WEN[lower][upper] -> hexagram number
_TABLE = [
    [1, 34, 5, 26, 11, 9, 14, 43],
    [25, 51, 3, 27, 24, 42, 21, 17],
    [6, 40, 29, 4, 7, 59, 64, 47],
    [33, 62, 39, 52, 15, 53, 56, 31],
    [12, 16, 8, 23, 2, 20, 35, 45],
    [44, 32, 48, 18, 46, 57, 50, 28],
    [13, 55, 63, 22, 36, 37, 30, 49],
    [10, 54, 60, 41, 19, 61, 38, 58],
]
KING_WEN = {lo: {up: _TABLE[i][j] for j, up in enumerate(ORDER)} for i, lo in enumerate(ORDER)}

# number: (name, meaning)
HEXAGRAMS = {
 1: ("The Creative", "Pure creative force. Act with strength and persistence; the time favours initiative."),
 2: ("The Receptive", "Yield and support. Follow rather than lead, and let things grow in their own time."),
 3: ("Difficulty at the Beginning", "Birth pains. Early chaos is normal; get help and don't force the pace."),
 4: ("Youthful Folly", "Inexperience. Be willing to be taught, and ask the question once, sincerely."),
 5: ("Waiting", "Clouds gather before rain. Wait calmly and nourish yourself; the moment will come."),
 6: ("Conflict", "A dispute. Stop halfway and seek a fair mediator rather than fighting to the end."),
 7: ("The Army", "Discipline and organisation. Lead with a clear purpose and good people."),
 8: ("Holding Together", "Unity. Join with others, and join early."),
 9: ("Small Taming", "Small restraints. Gentle influence now; big moves later."),
 10: ("Treading", "Walking on the tiger's tail. Tread carefully and politely and you'll pass safely."),
 11: ("Peace", "Heaven and earth in harmony. A good, flowing time; enjoy it and use it well."),
 12: ("Standstill", "Things are blocked. Keep your integrity and wait out the stagnation."),
 13: ("Fellowship", "Community with others. Openness and shared goals succeed."),
 14: ("Great Possession", "Abundance. Hold it with modesty and generosity."),
 15: ("Modesty", "Modesty carries things through. Level out extremes; don't boast."),
 16: ("Enthusiasm", "Energy that inspires others. Rally people and prepare to move."),
 17: ("Following", "Adapt and follow the times, or attract followers by serving well."),
 18: ("Work on the Decayed", "Something has spoiled. Repair what's been neglected, carefully."),
 19: ("Approach", "Good things approach. Advance while the season is favourable."),
 20: ("Contemplation", "Step back and observe. Understanding comes before action."),
 21: ("Biting Through", "An obstacle must be bitten through. Act decisively and fairly."),
 22: ("Grace", "Beauty and form. Pleasant, but don't confuse the surface with the substance."),
 23: ("Splitting Apart", "Things fall away. Don't act; let the decline run its course."),
 24: ("Return", "The turning point. Light returns; start again slowly."),
 25: ("Innocence", "Act without ulterior motives. Unplanned things happen; stay sincere."),
 26: ("Great Taming", "Hold great power in check. Study, build reserves, then act."),
 27: ("Nourishment", "Watch what you feed yourself and others, in body and in mind."),
 28: ("Great Exceeding", "The ridgepole sags under too much weight. Act, but ease the pressure."),
 29: ("The Abysmal", "Danger repeated. Keep moving like water, steady and sincere, and you'll get through."),
 30: ("The Clinging", "Fire clings to what it burns. Clarity; depend on what's right."),
 31: ("Influence", "Mutual attraction. Stay open and receptive."),
 32: ("Duration", "Endurance. Stay the course; consistency builds what lasts."),
 33: ("Retreat", "Withdraw strategically. Retreating now isn't defeat."),
 34: ("Great Power", "Strength at its height. Use it rightly, not recklessly."),
 35: ("Progress", "Rapid, easy advance. Recognition is coming."),
 36: ("Darkening of the Light", "Hard times. Keep your light hidden and your integrity intact."),
 37: ("The Family", "Roles and household. Order at home brings order everywhere."),
 38: ("Opposition", "Opposing views. Small matters can still succeed; find common ground."),
 39: ("Obstruction", "A block ahead. Turn back, seek help, and look at yourself."),
 40: ("Deliverance", "Release after difficulty. Forgive, tidy up, and move on quickly."),
 41: ("Decrease", "Less is more. Simplify and give up something for something better."),
 42: ("Increase", "Gains flow in. Act boldly and generously while it lasts."),
 43: ("Breakthrough", "Resolution. Declare the truth openly, without violence."),
 44: ("Coming to Meet", "An unexpected encounter. Be careful what, or who, you let in."),
 45: ("Gathering Together", "A gathering around a centre. Prepare for the unexpected in crowds."),
 46: ("Pushing Upward", "Steady growth, like a tree. Effort leads upward."),
 47: ("Oppression", "Exhaustion and confinement. Stay cheerful inside; words won't help now."),
 48: ("The Well", "The unchanging source. Draw on what nourishes everyone; maintain it."),
 49: ("Revolution", "The time for change has come. Act when it's right, and be believed."),
 50: ("The Cauldron", "Transformation and nourishment. Culture and good values feed people."),
 51: ("The Arousing", "Thunder shocks. Fear first, then laughter; stay composed."),
 52: ("Keeping Still", "Stillness. Stop when it's time to stop; quiet the mind."),
 53: ("Development", "Gradual progress, like a tree on a mountain. Go step by step."),
 54: ("The Marrying Maiden", "A subordinate position. Act with tact; know your place for now."),
 55: ("Abundance", "Fullness at its peak, like the noon sun. Enjoy it; don't mourn that it will pass."),
 56: ("The Wanderer", "The traveller. Be modest, careful and correct among strangers."),
 57: ("The Gentle", "Wind: gentle, persistent influence gets in everywhere."),
 58: ("The Joyous", "Joy shared. Friends, conversation and encouragement."),
 59: ("Dispersion", "Dissolving what's rigid or divisive. Bring people back together."),
 60: ("Limitation", "Set limits, but not harsh ones. Boundaries give shape."),
 61: ("Inner Truth", "Sincerity reaches even the stubborn. Be honest with yourself and others."),
 62: ("Small Exceeding", "Attend to small things. Stay low; don't aim too high now."),
 63: ("After Completion", "Everything is in place. Stay alert, because order tends toward disorder."),
 64: ("Before Completion", "Almost there. Take care with the last step."),
}


@dataclass
class Casting:
    lines: list[int]        # bottom to top: 6 old yin, 7 young yang, 8 young yin, 9 old yang

    @property
    def primary(self) -> list[int]:
        return [1 if v in (7, 9) else 0 for v in self.lines]

    @property
    def relating(self) -> list[int]:
        return [1 - b if v in (6, 9) else b for v, b in zip(self.lines, self.primary)]

    @property
    def changing(self) -> list[int]:
        return [i + 1 for i, v in enumerate(self.lines) if v in (6, 9)]


def cast() -> Casting:
    """Three coins per line: heads = 3, tails = 2. Sum 6/7/8/9."""
    return Casting([sum(_rng.choice((2, 3)) for _ in range(3)) for _ in range(6)])


def number(bits: list[int]) -> int:
    lower, upper = TRIGRAMS[tuple(bits[:3])], TRIGRAMS[tuple(bits[3:])]
    return KING_WEN[lower][upper]


def trigrams(bits: list[int]) -> tuple[str, str]:
    lo, up = TRIGRAMS[tuple(bits[:3])], TRIGRAMS[tuple(bits[3:])]
    return f"{TRIGRAM_EN[up]} over {TRIGRAM_EN[lo]}", f"{up}/{lo}"


def render(c: Casting) -> io.BytesIO:
    has_change = bool(c.changing)
    W, H = (760 if has_change else 360), 440
    img = Image.new("RGB", (W, H), (24, 20, 31))
    d = ImageDraw.Draw(img)
    gold, ink, red = (212, 175, 55), (235, 228, 210), (224, 90, 70)

    def hexagram(bits, x0, marks=None):
        for i, b in enumerate(bits):
            y = H - 70 - i * 55
            if b:
                d.rectangle((x0, y, x0 + 240, y + 26), fill=ink)
            else:
                d.rectangle((x0, y, x0 + 100, y + 26), fill=ink)
                d.rectangle((x0 + 140, y, x0 + 240, y + 26), fill=ink)
            if marks and marks[i] in (6, 9):
                cx, cy = x0 + 120, y + 13
                if marks[i] == 9:
                    d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), outline=red, width=5)
                else:
                    d.line((cx - 11, cy - 11, cx + 11, cy + 11), fill=red, width=5)
                    d.line((cx - 11, cy + 11, cx + 11, cy - 11), fill=red, width=5)

    hexagram(c.primary, 60, c.lines)
    if has_change:
        d.polygon([(355, 200), (395, 220), (355, 240)], fill=gold)
        hexagram(c.relating, 460)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf
