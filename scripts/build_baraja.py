"""Builds data/baraja.json — the 40-card Spanish deck (baraja española).

Spanish and Italian cartomancy share the same Latin suits and broad conventions
(Oros = money, Copas = love and home, Espadas = conflict, Bastos = work and effort),
so this reuses the Napoletane meanings with Spanish names. Edit freely.
Run build_napoletane.py first. To use scans, fill in SOURCES (card id -> URL).
"""
import json, os, sys

HERE = os.path.dirname(__file__)
nap = json.load(open(os.path.join(HERE, "..", "data", "napoletane.json"), encoding="utf-8"))

SUITS = {
    # napoletane key -> (baraja key, Spanish, English, color)
    "denari":  ("oros",    "Oros",    "Coins",  0xC9A227),
    "coppe":   ("copas",   "Copas",   "Cups",   0xC2255C),
    "spade":   ("espadas", "Espadas", "Swords", 0x1864AB),
    "bastoni": ("bastos",  "Bastos",  "Clubs",  0x2B8A3E),
}
RANKS_ES = ["As", "Dos", "Tres", "Cuatro", "Cinco", "Seis", "Siete", "Sota", "Caballo", "Rey"]
RANKS_EN = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Knave", "Knight", "King"]
PIP_NUM = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]   # printed numbers (Sota 10, Caballo 11, Rey 12)

SOURCES: dict[str, str] = {}

cards = []
for c in nap["cards"]:
    key, es, en, color = SUITS[c["suit"]]
    r = c["number"] - 1
    cid = f"{key}_{PIP_NUM[r]:02d}"
    meaning = dict(c["meaning"])
    if cid == "oros_07":  # the Settebello line is Italian-specific
        meaning["upright"] = "Great luck and a winning hand. Money and good fortune come together."
    cards.append({
        "id": cid,
        "name": f"{RANKS_ES[r]} de {es}",
        "name_en": f"{RANKS_EN[r]} of {en}",
        "arcana": c["arcana"], "number": PIP_NUM[r], "suit": key, "rank": RANKS_ES[r],
        "keywords": c["keywords"], "meaning": meaning,
        "image": f"cards/baraja/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
    })

deck = {
    "id": "baraja",
    "name": "Baraja Española",
    "short_name": "Baraja",
    "family": "Spanish",
    "description": "The 40-card Spanish deck: Oros, Copas, Espadas, Bastos. "
                   "Meanings follow the broad conventions of Spanish and Italian cartomancy.",
    "card_aspect": 0.64,
    "color": 0xC92A2A,
    "spreads": ["single", "three", "situation", "celtic"],
    "suits": {v[0]: {"name": f"{v[1]} ({v[2]})", "color": v[3],
                     "domain": nap["suits"][k]["domain"]} for k, v in SUITS.items()},
    "cards": cards,
}
assert len(cards) == 40
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "baraja.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
