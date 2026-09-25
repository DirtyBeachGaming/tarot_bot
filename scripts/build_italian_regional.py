"""Builds the Italian regional 40-card decks (data/<id>.json).

All regional patterns share the same cartomancy conventions, so the meanings come
from the Napoletane deck; only the name, art and a few details differ.

Latin-suited (Denari, Coppe, Spade, Bastoni; Fante, Cavallo, Re)
French-suited (Quadri, Cuori, Picche, Fiori; Fante, Donna, Re), mapped to the
Latin suits the usual way: Quadri = Denari, Cuori = Coppe, Picche = Spade, Fiori = Bastoni.

Double-headed patterns are read without reversals (you can't tell which way up they are).
Run build_napoletane.py first. To use scans, fill in SOURCES[deck_id] (card id -> URL).
"""
import json, os, sys

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")
nap = json.load(open(os.path.join(DATA, "napoletane.json"), encoding="utf-8"))

# id: (name, region / description, double-headed?, suit system, aspect)
LATIN = {
    "piacentine": ("Carte Piacentine", "From Piacenza; the most widely used pattern in northern and central Italy.", False, 0.56),
    "siciliane":  ("Carte Siciliane", "The Sicilian pattern.", False, 0.58),
    "trevisane":  ("Carte Trevisane", "From Treviso and the Veneto.", True, 0.55),
    "bergamasche": ("Carte Bergamasche", "From Bergamo, in Lombardy.", True, 0.55),
    "bresciane":  ("Carte Bresciane", "From Brescia, in Lombardy.", True, 0.55),
    "romagnole":  ("Carte Romagnole", "From Romagna.", False, 0.56),
    "sarde":      ("Carte Sarde", "The Sardinian pattern, related to the Spanish deck.", False, 0.62),
    "triestine":  ("Carte Triestine", "From Trieste and Friuli.", True, 0.56),
    "trentine":   ("Carte Trentine", "From Trentino.", True, 0.55),
}
FRENCH = {
    "piemontesi": ("Carte Piemontesi", "The Piedmontese pattern, French-suited.", True, 0.58),
    "genovesi":   ("Carte Genovesi", "The Genoese pattern from Liguria, French-suited.", True, 0.6),
    "toscane":    ("Carte Toscane", "The Tuscan (Florentine) pattern, French-suited.", True, 0.6),
    "milanesi":   ("Carte Milanesi", "The Milanese pattern from Lombardy, French-suited.", True, 0.6),
}

FR_SUITS = {  # napoletane suit -> (key, Italian name, English, symbol, color)
    "denari":  ("quadri", "Quadri", "Diamonds", "♦", 0xE8590C),
    "coppe":   ("cuori",  "Cuori",  "Hearts",   "♥", 0xC92A2A),
    "spade":   ("picche", "Picche", "Spades",   "♠", 0x343A40),
    "bastoni": ("fiori",  "Fiori",  "Clubs",    "♣", 0x2B8A3E),
}
FR_RANKS = ["Asso", "Due", "Tre", "Quattro", "Cinque", "Sei", "Sette", "Fante", "Donna", "Re"]
FR_RANKS_EN = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Jack", "Queen", "King"]
FR_SHORT = ["A", "2", "3", "4", "5", "6", "7", "J", "Q", "K"]

# French-suited decks have a Donna (Queen) where Latin decks have a Cavallo.
DONNA = {
    "denari": ("a businesswoman, good sense, thrift", "a spendthrift, calculation",
               "A shrewd woman who manages money well.", "A woman who counts every coin, or spends too freely."),
    "coppe":  ("a loving woman, warmth, devotion", "jealousy, moodiness",
               "A loving, generous woman. Affection and care.", "Love that turns possessive or moody."),
    "spade":  ("a sharp woman, independence, sorrow", "coldness, spite",
               "A clear-sighted woman who has known hardship.", "Cold words or quiet spite."),
    "bastoni": ("a capable woman, energy, home and work", "overwork, impatience",
                "A capable, energetic woman who keeps everything running.", "Stretched thin; impatience at home."),
}

SOURCES: dict[str, dict[str, str]] = {}


def common(deck_id, name, desc, double, aspect):
    return {
        "id": deck_id, "name": name, "short_name": name.replace("Carte ", ""),
        "family": "Italian regional",
        "description": f"{desc} 40 cards. Meanings follow Italian cartomancy (shared with the Napoletane)."
                       + (" Double-headed, so read without reversals." if double else ""),
        "card_aspect": aspect, "reversals": not double,
        "spreads": ["single", "three", "situation", "celtic"],
    }


written = []
for deck_id, (name, desc, double, aspect) in LATIN.items():
    src = SOURCES.get(deck_id, {})
    deck = common(deck_id, name, desc, double, aspect)
    deck.update({"color": nap["color"], "suits": nap["suits"], "cards": [
        {**c, "image": f"cards/{deck_id}/{c['id']}.jpg", "source_url": src.get(c["id"], "")}
        for c in nap["cards"]]})
    written.append(deck)

for deck_id, (name, desc, double, aspect) in FRENCH.items():
    src = SOURCES.get(deck_id, {})
    cards = []
    for c in nap["cards"]:
        key, it, en, sym, color = FR_SUITS[c["suit"]]
        r = c["number"] - 1
        cid = f"{key}_{r+1:02d}"
        kw, meaning = c["keywords"], c["meaning"]
        if r == 8:  # Donna replaces Cavallo
            ku, kr, up, rev = DONNA[c["suit"]]
            kw = {"upright": ku.split(", "), "reversed": kr.split(", ")}
            meaning = {"upright": up, "reversed": rev}
        cards.append({
            "id": cid, "name": f"{FR_RANKS[r]} di {it}", "name_en": f"{FR_RANKS_EN[r]} of {en}",
            "arcana": c["arcana"], "number": r + 1, "suit": key, "rank": FR_RANKS[r],
            "insert": f"{FR_SHORT[r]}{sym}",
            "keywords": kw, "meaning": meaning,
            "image": f"cards/{deck_id}/{cid}.jpg", "source_url": src.get(cid, ""),
        })
    deck = common(deck_id, name, desc, double, aspect)
    deck.update({
        "color": 0xC92A2A,
        "suits": {v[0]: {"name": f"{v[1]} ({v[2]})", "color": v[4], "domain": nap["suits"][k]["domain"]}
                  for k, v in FR_SUITS.items()},
        "cards": cards,
    })
    written.append(deck)

for deck in written:
    assert len(deck["cards"]) == 40
    path = os.path.join(DATA, f"{deck['id']}.json")
    json.dump(deck, open(path, "w"), indent=2, ensure_ascii=False)
print("wrote", len(written), "regional decks:", ", ".join(d["id"] for d in written))
