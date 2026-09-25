"""Builds data/geomancy.json — the 16 figures of geomancy.

Each figure is four rows of one or two dots (head, neck, body, feet), shown here
as the digits 1 and 2. Figures are read upright. The bot draws the dots itself.
"""
import json, os, sys

# name, English, rows (top to bottom), keywords, meaning
FIGURES = [
 ("Via", "The Way", "1111", "journey, change, movement",
  "The road. Things are in motion; good for travel and change, less so for staying put."),
 ("Populus", "The People", "2222", "crowds, the community, receptivity",
  "The crowd. Outcomes depend on others; it takes on the colour of what's around it."),
 ("Conjunctio", "Conjunction", "2112", "meeting, combination, agreement",
  "Two paths meet. Partnerships, deals and things coming together."),
 ("Carcer", "The Prison", "1221", "restriction, delay, stability",
  "Walls on every side. Delay and restriction, or solid security, depending on the question."),
 ("Fortuna Major", "Greater Fortune", "2211", "great success, lasting luck",
  "Great good fortune that you've earned. Lasting success."),
 ("Fortuna Minor", "Lesser Fortune", "1122", "quick luck, fleeting help",
  "Help from outside that comes and goes fast. Use it quickly."),
 ("Acquisitio", "Gain", "2121", "gain, profit, acquiring",
  "You gain what you seek. Very favourable for money and goals."),
 ("Amissio", "Loss", "1212", "loss, letting go, release",
  "Something slips away. Bad for keeping things, good for getting rid of them."),
 ("Laetitia", "Joy", "1222", "happiness, health, uplift",
  "Joy and good health. Spirits rise."),
 ("Tristitia", "Sorrow", "2221", "sadness, stability, depth",
  "Sorrow, or things sinking. Good only for foundations and what should stay down."),
 ("Puella", "The Girl", "1211", "harmony, beauty, pleasantness",
  "Grace and harmony. Pleasant, though sometimes fickle."),
 ("Puer", "The Boy", "1121", "energy, aggression, boldness",
  "Rash energy and a fighting spirit. Good for contests, poor for peace."),
 ("Rubeus", "Red", "2122", "passion, anger, danger",
  "Red passion. Strong emotions and danger; be careful."),
 ("Albus", "White", "2212", "peace, wisdom, clarity",
  "White: calm, clear thinking and good counsel."),
 ("Caput Draconis", "Dragon's Head", "2111", "beginnings, entrance, doorway",
  "The dragon's head: a beginning. Favourable for starting things."),
 ("Cauda Draconis", "Dragon's Tail", "1112", "endings, exit, release",
  "The dragon's tail: an ending. Good for finishing, poor for beginning."),
]

cards = [{
    "id": f"geo_{i+1:02d}", "name": name, "name_en": en,
    "arcana": "geomancy", "number": i + 1, "suit": None, "rank": rows,
    "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
    "image": f"cards/geomancy/{i+1:02d}.png", "source_url": "",
} for i, (name, en, rows, kw, meaning) in enumerate(FIGURES)]

deck = {
    "id": "geomancy", "name": "Geomancy", "short_name": "Geomancy", "family": "Staves & signs",
    "description": "The 16 figures of European geomancy. Read upright.",
    "card_aspect": 0.62, "color": 0x8C6D46, "reversals": False,
    "spreads": ["single", "three", "line5"], "suits": {}, "cards": cards,
}
assert len(cards) == 16
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "geomancy.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
