"""Builds data/marseille.json — the Tarot de Marseille (78 cards).

Uses French card names with the Waite-Smith meanings, matched by card identity
(so Justice is VIII and Strength is XI, as on Marseille decks). Marseille pip cards
aren't illustrated scenes, so many readers lean on number + suit; the meanings
here are a practical starting point. Run build_deck.py first.
To use scans, fill in SOURCES (card id -> URL).
"""
import json, os, sys

HERE = os.path.dirname(__file__)
rws = json.load(open(os.path.join(HERE, "..", "data", "rws1909.json"), encoding="utf-8"))
by_id = {c["id"]: c for c in rws["cards"]}

# (Marseille number or None, French name, Waite-Smith card id)
MAJORS = [
 (None, "Le Mat", "major_00"), (1, "Le Bateleur", "major_01"), (2, "La Papesse", "major_02"),
 (3, "L'Impératrice", "major_03"), (4, "L'Empereur", "major_04"), (5, "Le Pape", "major_05"),
 (6, "L'Amoureux", "major_06"), (7, "Le Chariot", "major_07"), (8, "La Justice", "major_11"),
 (9, "L'Hermite", "major_09"), (10, "La Roue de Fortune", "major_10"), (11, "La Force", "major_08"),
 (12, "Le Pendu", "major_12"), (13, "L'Arcane sans nom", "major_13"), (14, "Tempérance", "major_14"),
 (15, "Le Diable", "major_15"), (16, "La Maison Dieu", "major_16"), (17, "L'Étoile", "major_17"),
 (18, "La Lune", "major_18"), (19, "Le Soleil", "major_19"), (20, "Le Jugement", "major_20"),
 (21, "Le Monde", "major_21"),
]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII",
         "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]
SUITS = {
    # rws key -> (marseille key, French, color)
    "wands":     ("batons", "Bâtons",  0xD9480F),
    "cups":      ("coupes", "Coupes",  0x1971C2),
    "swords":    ("epees",  "Épées",   0x868E96),
    "pentacles": ("deniers", "Deniers", 0xC9A227),
}
RANKS_FR = ["As", "Deux", "Trois", "Quatre", "Cinq", "Six", "Sept", "Huit", "Neuf", "Dix",
            "Valet", "Cavalier", "Reine", "Roi"]

SOURCES: dict[str, str] = {}
cards = []
for num, fr, rid in MAJORS:
    src = by_id[rid]
    cid = f"major_{num:02d}" if num is not None else "major_mat"
    cards.append({
        "id": cid, "name": fr, "name_en": src["name"],
        "arcana": "trump", "number": num if num is not None else 0, "suit": None,
        "rank": ROMAN[num] if num else ("★" if num is None else ""),
        "keywords": src["keywords"], "meaning": src["meaning"],
        "image": f"cards/marseille/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
    })
for c in rws["cards"]:
    if c["arcana"] != "minor":
        continue
    key, fr, _ = SUITS[c["suit"]]
    n = c["number"]
    cid = f"{key}_{n:02d}"
    cards.append({
        "id": cid,
        "name": f"{RANKS_FR[n-1]} d'{fr}" if fr[0] in "AEIOUÉ" else f"{RANKS_FR[n-1]} de {fr}",
        "name_en": c["name"],
        "arcana": "minor", "number": n, "suit": key, "rank": RANKS_FR[n-1],
        "keywords": c["keywords"], "meaning": c["meaning"],
        "image": f"cards/marseille/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
    })

deck = {
    "id": "marseille",
    "name": "Tarot de Marseille",
    "short_name": "Marseille",
    "family": "Tarot",
    "description": "The classic French tarot pattern. French names, Waite-Smith meanings matched by card.",
    "card_aspect": 0.53,
    "color": 0xB08D2E,
    "spreads": ["single", "three", "situation", "celtic"],
    "suits": {v[0]: {"name": v[1], "color": v[2], "element": rws["suits"][k]["element"],
                     "domain": rws["suits"][k]["domain"]} for k, v in SUITS.items()},
    "cards": cards,
}
assert len(cards) == 78
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "marseille.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
