"""Builds data/hanafuda.json — the 48 Japanese flower cards (12 months x 4).

Hanafuda has a fortune-telling tradition (hana-uranai), but its meanings vary a lot,
so these are written for this bot from each month's flower and season, shaded by
the card's rank: brights (hikari) strongest, then animals (tane), ribbons (tan)
and plain cards (kasu). Read upright. To use scans, fill in SOURCES (card id -> URL).
"""
import json, os, sys

# month: (flower, theme keywords, theme sentence, [(card name, type), ... x4])
MONTHS = [
 ("Pine", "longevity, good fortune, new year", "Steady, evergreen luck and a strong start.",
  [("Crane", "bright"), ("Poetry Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Plum Blossom", "resilience, early hope, first signs", "Blossoms before the snow has gone: hope arriving early.",
  [("Bush Warbler", "animal"), ("Poetry Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Cherry Blossom", "beauty, celebration, transience", "Full bloom: enjoy it now, because it won't last.",
  [("Curtain", "bright"), ("Poetry Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Wisteria", "romance, longing, welcome", "Trailing blossoms and longing. Affection reaching out.",
  [("Cuckoo", "animal"), ("Red Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Iris", "protection, clarity, crossing over", "Irises by the water: protection, and a way across.",
  [("Eight-Plank Bridge", "animal"), ("Red Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Peony", "prosperity, pride, abundance", "The king of flowers: wealth, honour and a full life.",
  [("Butterflies", "animal"), ("Blue Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Bush Clover", "strength, courage, rustic life", "Wild clover on the hillside: raw energy and nerve.",
  [("Boar", "animal"), ("Red Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Susuki Grass", "reflection, harvest moon, fullness", "The harvest moon over tall grass: reflection and fulfilment.",
  [("Full Moon", "bright"), ("Geese", "animal"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Chrysanthemum", "long life, dignity, enjoyment", "The chrysanthemum festival: dignity, health and a cup raised.",
  [("Sake Cup", "animal"), ("Blue Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Maple", "change, maturity, letting go", "Red leaves falling: change, maturity and graceful endings.",
  [("Deer", "animal"), ("Blue Ribbon", "ribbon"), ("Plain", "plain"), ("Plain", "plain")]),
 ("Willow", "perseverance, flexibility, the unexpected", "Rain on the willow: keep trying, bend, and expect surprises.",
  [("Rain Man", "bright"), ("Swallow", "animal"), ("Red Ribbon", "ribbon"), ("Lightning", "plain")]),
 ("Paulownia", "nobility, completion, a phoenix rising", "The phoenix in the paulownia: a cycle completes, something noble rises.",
  [("Phoenix", "bright"), ("Plain", "plain"), ("Plain", "plain"), ("Plain", "plain")]),
]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August",
               "September", "October", "November", "December"]
TYPE_TEXT = {
    "bright":  ("strong, decisive", "A bright card: this is the month's full power, and it's strongly in your favour."),
    "animal":  ("active, lively", "An animal card: the month's energy in motion; something acts on your behalf."),
    "ribbon":  ("messages, ties, promises", "A ribbon card: a message, a promise or a tie between people."),
    "plain":   ("small, everyday", "A plain card: the month's mood in small, everyday ways."),
}
SPECIAL = {  # a few cards with their own twist
    (11, "Lightning"): "Lightning in the rain: a sudden jolt that clears the air.",
    (11, "Rain Man"): "The rain man with his umbrella: an odd, unexpected turn that works out.",
    (8, "Full Moon"): "The full moon: things are fully visible now. Clarity and completion.",
    (9, "Sake Cup"): "The sake cup: celebrate, and share your luck with others.",
    (5, "Eight-Plank Bridge"): "The zigzag bridge through the irises: an indirect path that still gets you across.",
}
SOURCES: dict[str, str] = {}

cards = []
for m, (flower, theme_kw, theme, month_cards) in enumerate(MONTHS, start=1):
    plain_n = 0
    for card_name, ctype in month_cards:
        if card_name == "Plain":
            plain_n += 1
            card_name = f"Plain {plain_n}" if sum(1 for c, _ in month_cards if c == "Plain") > 1 else "Plain"
        cid = f"hana_{m:02d}_{len([c for c in cards if c['number'] == m]) + 1}"
        kw = theme_kw.split(", ")[:2] + TYPE_TEXT[ctype][0].split(", ")[:1]
        extra = SPECIAL.get((m, card_name), TYPE_TEXT[ctype][1])
        cards.append({
            "id": cid, "name": f"{flower} · {card_name}", "name_en": f"{MONTH_NAMES[m-1]} · {ctype}",
            "arcana": "oracle", "number": m, "suit": None, "rank": ctype,
            "keywords": {"upright": kw}, "meaning": {"upright": f"{theme} {extra}"},
            "image": f"cards/hanafuda/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
        })

deck = {
    "id": "hanafuda", "name": "Hanafuda", "short_name": "Hanafuda", "family": "Oracle",
    "description": "The 48 Japanese flower cards, one suit per month. Meanings written for this bot from each "
                   "month's flower, shaded by the card's rank. Read upright.",
    "card_aspect": 0.62, "color": 0xE03131, "reversals": False,
    "spreads": ["single", "three", "line5"], "suits": {}, "cards": cards,
}
assert len(cards) == 48
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "hanafuda.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
