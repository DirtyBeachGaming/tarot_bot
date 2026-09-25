"""Builds the Italian tarot decks: Tarocco Piemontese (78), Tarocco Bolognese (62)
and Minchiate (97).

Trumps with a tarot equivalent use the Waite-Smith meanings for that card; the
Minchiate's extra trumps (virtues, elements, zodiac) get meanings written for this bot.
Number cards reuse the Waite-Smith minor meanings by suit and rank.
Run build_deck.py first. To use scans, fill in SOURCES[deck_id] (card id -> URL).
"""
import json, os

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")
rws = json.load(open(os.path.join(DATA, "rws1909.json"), encoding="utf-8"))
R = {c["id"]: c for c in rws["cards"]}
ROMAN = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV",
         "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI",
         "XXVII", "XXVIII", "XXIX", "XXX", "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV"]

IT_SUITS = {  # rws suit -> (key, Italian, English, color)
    "wands":     ("bastoni", "Bastoni", "Batons", 0xD9480F),
    "cups":      ("coppe",   "Coppe",   "Cups",   0x1971C2),
    "swords":    ("spade",   "Spade",   "Swords", 0x868E96),
    "pentacles": ("denari",  "Denari",  "Coins",  0xC9A227),
}
IT_RANKS = ["Asso", "Due", "Tre", "Quattro", "Cinque", "Sei", "Sette", "Otto", "Nove", "Dieci",
            "Fante", "Cavallo", "Regina", "Re"]
SOURCES: dict[str, dict[str, str]] = {}


def trump(deck_id, cid, name, number, rank, rws_id=None, kw=None, up=None, rev=None, name_en=None):
    base = R[rws_id] if rws_id else None
    return {
        "id": cid, "name": name, "name_en": name_en or (base["name"] if base else None),
        "arcana": "trump", "number": number, "suit": None, "rank": rank,
        "keywords": base["keywords"] if base else {"upright": kw[0].split(", "), "reversed": kw[1].split(", ")},
        "meaning": base["meaning"] if base else {"upright": up, "reversed": rev},
        "image": f"cards/{deck_id}/{cid}.jpg", "source_url": SOURCES.get(deck_id, {}).get(cid, ""),
    }


def minors(deck_id, ranks_kept, rank_names=IT_RANKS):
    out = []
    for c in rws["cards"]:
        if c["arcana"] != "minor" or c["number"] not in ranks_kept:
            continue
        key, it, en, _ = IT_SUITS[c["suit"]]
        n = c["number"]
        rank = rank_names(key, n) if callable(rank_names) else rank_names[n - 1]
        cid = f"{key}_{n:02d}"
        out.append({
            "id": cid, "name": f"{rank} di {it}", "name_en": c["name"],
            "arcana": "minor", "number": n, "suit": key, "rank": rank,
            "keywords": c["keywords"], "meaning": c["meaning"],
            "image": f"cards/{deck_id}/{cid}.jpg", "source_url": SOURCES.get(deck_id, {}).get(cid, ""),
        })
    return out


def suits_meta():
    return {v[0]: {"name": f"{v[1]} ({v[2]})", "color": v[3], "element": rws["suits"][k]["element"],
                   "domain": rws["suits"][k]["domain"]} for k, v in IT_SUITS.items()}


decks = []

# ---------- Tarocco Piemontese: Marseille-style order (Justice VIII, Strength XI) ----------
PIEM = [
 (0, "Il Matto", "major_00"), (1, "Il Bagatto", "major_01"), (2, "La Papessa", "major_02"),
 (3, "L'Imperatrice", "major_03"), (4, "L'Imperatore", "major_04"), (5, "Il Papa", "major_05"),
 (6, "Gli Amanti", "major_06"), (7, "Il Carro", "major_07"), (8, "La Giustizia", "major_11"),
 (9, "L'Eremita", "major_09"), (10, "La Ruota della Fortuna", "major_10"), (11, "La Forza", "major_08"),
 (12, "L'Appeso", "major_12"), (13, "La Morte", "major_13"), (14, "La Temperanza", "major_14"),
 (15, "Il Diavolo", "major_15"), (16, "La Torre", "major_16"), (17, "Le Stelle", "major_17"),
 (18, "La Luna", "major_18"), (19, "Il Sole", "major_19"), (20, "Il Giudizio", "major_20"),
 (21, "Il Mondo", "major_21"),
]
cards = [trump("piemontese", f"major_{n:02d}", name, n, "★" if n == 0 else ROMAN[n], rid) for n, name, rid in PIEM]
cards += minors("piemontese", range(1, 15))
decks.append({
    "id": "piemontese", "name": "Tarocco Piemontese", "short_name": "Piemontese", "family": "Italian tarot",
    "description": "The Piedmontese tarot, 78 cards, still played in northwest Italy. Double-headed, so read "
                   "without reversals. Waite-Smith meanings matched by card.",
    "card_aspect": 0.53, "color": 0x7048E8, "reversals": False,
    "spreads": ["single", "three", "situation", "celtic"], "suits": suits_meta(), "cards": cards,
})

# ---------- Tarocco Bolognese: 62 cards, four equal "Mori", no 2-5 in the suits ----------
BOLO = [
 ("matto", "Il Matto", "★", "major_00"), ("bagatto", "Il Bagatto", "I", "major_01"),
 ("moro_1", "Il Moro (I)", "", "major_02"), ("moro_2", "Il Moro (II)", "", "major_03"),
 ("moro_3", "Il Moro (III)", "", "major_04"), ("moro_4", "Il Moro (IV)", "", "major_05"),
 ("amore", "L'Amore", "", "major_06"), ("carro", "Il Carro", "", "major_07"),
 ("temperanza", "La Temperanza", "", "major_14"), ("giustizia", "La Giustizia", "", "major_11"),
 ("forza", "La Forza", "", "major_08"), ("ruota", "La Ruota", "", "major_10"),
 ("tempo", "Il Tempo", "", "major_09"), ("traditore", "Il Traditore", "", "major_12"),
 ("morte", "La Morte", "", "major_13"), ("diavolo", "Il Diavolo", "", "major_15"),
 ("saetta", "La Saetta", "", "major_16"), ("stella", "La Stella", "", "major_17"),
 ("luna", "La Luna", "", "major_18"), ("sole", "Il Sole", "", "major_19"),
 ("mondo", "Il Mondo", "", "major_21"), ("angelo", "L'Angelo", "", "major_20"),
]
MORI_EN = {"moro_1": "Moor (High Priestess role)", "moro_2": "Moor (Empress role)",
           "moro_3": "Moor (Emperor role)", "moro_4": "Moor (Hierophant role)"}
cards = [trump("bolognese", f"t_{k}", name, i, rank, rid, name_en=MORI_EN.get(k))
         for i, (k, name, rank, rid) in enumerate(BOLO)]
cards += minors("bolognese", [1, 6, 7, 8, 9, 10, 11, 12, 13, 14])
decks.append({
    "id": "bolognese", "name": "Tarocco Bolognese", "short_name": "Bolognese", "family": "Italian tarot",
    "description": "The Bolognese tarot, 62 cards: no 2 to 5 in the suits, and four equal 'Mori' (Moors) in "
                   "place of the Pope, Popess, Emperor and Empress. Double-headed, read without reversals.",
    "card_aspect": 0.5, "color": 0xA61E4D, "reversals": False,
    "spreads": ["single", "three", "situation", "celtic"], "suits": suits_meta(), "cards": cards,
})

# ---------- Minchiate: 97 cards, 41 trumps ----------
# (number, name, English, rws id or None, (kw up, kw rev), up, rev)
MIN = [
 (0, "Il Matto", "The Fool", "major_00", None, None, None),
 (1, "Il Papa Uno", "The Magician", "major_01", None, None, None),
 (2, "Il Granduca", "The Grand Duke", "major_02", None, None, None),
 (3, "L'Imperatore d'Occidente", "Emperor of the West", "major_03", None, None, None),
 (4, "L'Imperatore d'Oriente", "Emperor of the East", "major_04", None, None, None),
 (5, "L'Amore", "Love", "major_06", None, None, None),
 (6, "La Temperanza", "Temperance", "major_14", None, None, None),
 (7, "La Fortezza", "Strength", "major_08", None, None, None),
 (8, "La Giustizia", "Justice", "major_11", None, None, None),
 (9, "La Ruota", "The Wheel", "major_10", None, None, None),
 (10, "Il Carro", "The Chariot", "major_07", None, None, None),
 (11, "Il Gobbo", "The Hunchback (Time)", "major_09", None, None, None),
 (12, "L'Impiccato", "The Hanged Man", "major_12", None, None, None),
 (13, "La Morte", "Death", "major_13", None, None, None),
 (14, "Il Diavolo", "The Devil", "major_15", None, None, None),
 (15, "La Casa del Diavolo", "The Devil's House", "major_16", None, None, None),
 (16, "La Speranza", "Hope", None, ("hope, trust, looking ahead", "despair, false hope"),
  "Hope that keeps you moving. Trust that things can improve.", "Hope has thinned out, or rests on the wrong thing."),
 (17, "La Prudenza", "Prudence", None, ("caution, foresight, wisdom", "recklessness, hesitation"),
  "Look ahead before you step. Careful judgment pays.", "Either too careless or too cautious to act."),
 (18, "La Fede", "Faith", None, ("faith, loyalty, conviction", "doubt, broken trust"),
  "Keep faith in someone or something. Loyalty is rewarded.", "Doubt creeps in, or trust is broken."),
 (19, "La Carità", "Charity", None, ("generosity, compassion, giving", "selfishness, strings attached"),
  "Give freely. Compassion comes back around.", "Giving with conditions, or not giving at all."),
 (20, "Il Fuoco", "Fire", None, ("passion, energy, will", "burnout, anger"),
  "The element of fire: drive, passion and the will to act.", "Fire out of control: anger or burnout."),
 (21, "L'Acqua", "Water", None, ("emotion, flow, intuition", "overwhelm, stagnation"),
  "The element of water: feeling, intuition and flow.", "Emotions flood in or go stagnant."),
 (22, "La Terra", "Earth", None, ("stability, body, material things", "stubbornness, inertia"),
  "The element of earth: the practical, the physical, the solid.", "Stuck in the mud; too rigid to move."),
 (23, "L'Aria", "Air", None, ("thought, communication, clarity", "confusion, scattered mind"),
  "The element of air: ideas, words and clear thinking.", "Thoughts scatter; too much talk, too little said."),
 (24, "La Bilancia", "Libra", None, ("balance, fairness, partnership", "imbalance, indecision"),
  "The scales: weigh both sides and find a fair balance.", "Things tip out of balance, or you can't decide."),
 (25, "La Vergine", "Virgo", None, ("order, care, detail", "fussiness, criticism"),
  "Care and precision. Put things in order.", "Too critical; lost in details."),
 (26, "Lo Scorpione", "Scorpio", None, ("intensity, secrets, transformation", "jealousy, revenge"),
  "Deep and intense. What's hidden comes to the surface.", "Stings of jealousy or a wish for revenge."),
 (27, "L'Ariete", "Aries", None, ("initiative, courage, beginning", "impatience, aggression"),
  "Charge ahead. A bold beginning.", "Rushing in headfirst."),
 (28, "Il Capricorno", "Capricorn", None, ("ambition, discipline, the long climb", "coldness, rigidity"),
  "Climb steadily toward a serious goal.", "Ambition turned cold or rigid."),
 (29, "Il Sagittario", "Sagittarius", None, ("adventure, optimism, aim", "restlessness, overpromising"),
  "Aim high and go far. Travel, study, optimism.", "Scattered arrows; promises too big."),
 (30, "Il Cancro", "Cancer", None, ("home, protection, feeling", "moodiness, clinging"),
  "The shell of home. Protect what you love.", "Retreating into the shell; clinging."),
 (31, "I Pesci", "Pisces", None, ("imagination, empathy, dreams", "escapism, confusion"),
  "Dreams and compassion. Swim with your intuition.", "Drifting away from what's real."),
 (32, "L'Acquario", "Aquarius", None, ("ideas, friendship, the future", "detachment, rebellion for its own sake"),
  "New ideas and good friends. Think ahead.", "Too detached, or contrary just to be different."),
 (33, "Il Leone", "Leo", None, ("pride, generosity, leadership", "arrogance, vanity"),
  "Lead with a big heart. Step into the spotlight.", "Pride tips into vanity."),
 (34, "Il Toro", "Taurus", None, ("steadiness, pleasure, patience", "stubbornness, greed"),
  "Slow and steady. Enjoy what you've built.", "Won't budge; wants more than enough."),
 (35, "I Gemelli", "Gemini", None, ("duality, conversation, curiosity", "inconsistency, two-facedness"),
  "Two sides, many ideas. Talk it through.", "Mixed messages; can't pick a side."),
 (36, "La Stella", "The Star", "major_17", None, None, None),
 (37, "La Luna", "The Moon", "major_18", None, None, None),
 (38, "Il Sole", "The Sun", "major_19", None, None, None),
 (39, "Il Mondo", "The World", "major_21", None, None, None),
 (40, "Le Trombe", "The Trumpets (Fame)", "major_20", None, None, None),
]
cards = []
for n, name, en, rid, kw, up, rev in MIN:
    rank = "★" if n == 0 else (ROMAN[n] if n <= 35 else "")
    cards.append(trump("minchiate", f"t_{n:02d}", name, n, rank, rid, kw, up, rev, name_en=en))


def minchiate_rank(suit_key, n):
    if n == 11:  # the Fante of Cups and Coins is a maid (Fantesca)
        return "Fantesca" if suit_key in ("coppe", "denari") else "Fante"
    return ["Asso", "Due", "Tre", "Quattro", "Cinque", "Sei", "Sette", "Otto", "Nove", "Dieci",
            "", "Cavallo", "Donna", "Re"][n - 1]


cards += minors("minchiate", range(1, 15), minchiate_rank)
decks.append({
    "id": "minchiate", "name": "Minchiate", "short_name": "Minchiate", "family": "Italian tarot",
    "description": "The Florentine Minchiate, 97 cards with 41 trumps: the virtues, the four elements and the "
                   "twelve signs of the zodiac join the familiar tarot figures.",
    "card_aspect": 0.54, "color": 0xE67700,
    "spreads": ["single", "three", "situation", "celtic"], "suits": suits_meta(), "cards": cards,
})

for d in decks:
    json.dump(d, open(os.path.join(DATA, f"{d['id']}.json"), "w"), indent=2, ensure_ascii=False)
    print("wrote", d["id"], len(d["cards"]), "cards")
assert [len(d["cards"]) for d in decks] == [78, 62, 97]
