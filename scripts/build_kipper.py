"""Builds data/kipper.json — the 36-card German Kipper fortune-telling deck (1890s).

Numbered scene cards read upright and in combinations, like Lenormand.
To use scans, fill in SOURCES (card number -> URL).
"""
import json, os, sys

# number, German name, English name, keywords, meaning
CARDS = [
 (1, "Hauptperson (männlich)", "Main Person (Male)", "the querent, a man, will",
  "The person asking, if a man, or the key man in the matter."),
 (2, "Hauptperson (weiblich)", "Main Person (Female)", "the querent, a woman, intuition",
  "The person asking, if a woman, or the key woman in the matter."),
 (3, "Ehe", "Marriage", "partnership, commitment, contract",
  "A committed partnership, in love or in business."),
 (4, "Begegnung", "Meeting", "gathering, encounter, cooperation",
  "People come together: a meeting, a gathering, working side by side."),
 (5, "Guter Herr", "Good Gentleman", "a kind man, a helper, protection",
  "A well-meaning man who helps and protects."),
 (6, "Gute Dame", "Good Lady", "a kind woman, support, patience",
  "A warm, generous woman who offers support."),
 (7, "Angenehmer Brief", "Pleasant Letter", "good news, an invitation",
  "Welcome news or an invitation arrives."),
 (8, "Falsche Person", "False Person", "deceit, a two-faced person",
  "Someone isn't honest. Watch for betrayal."),
 (9, "Veränderung", "A Change", "change, transition, fresh start",
  "Things shift. A transition into something new."),
 (10, "Reise", "A Journey", "travel, departure, movement",
  "A trip or a departure. Movement and new experiences."),
 (11, "Viel Geld gewinnen", "Win Lots of Money", "wealth, gain, abundance",
  "Financial success and plenty."),
 (12, "Reiches Mädchen", "Rich Girl", "a young woman, ease, prosperity",
  "A young woman with means, or an easy, prosperous time."),
 (13, "Reicher guter Herr", "Rich Good Gentleman", "a wealthy man, stability",
  "A wealthy, generous man with influence."),
 (14, "Traurige Nachricht", "Sad News", "bad news, disappointment",
  "Unwelcome or saddening news."),
 (15, "Liebesglück", "Happiness in Love", "romance goes well, harmony",
  "Love turns out well. Harmony between two people."),
 (16, "Seine Gedanken", "His Thoughts", "thoughts, intentions, plans",
  "What someone is thinking and planning."),
 (17, "Geschenk", "A Gift", "a present, a pleasant surprise",
  "A gift or kindness, a pleasant surprise."),
 (18, "Kleines Kind", "Small Child", "a child, a new beginning",
  "A child, or something small and new starting."),
 (19, "Todesfall", "Death", "ending, loss, transformation",
  "A final ending. Something is over and must be let go."),
 (20, "Haus", "House", "home, family, property",
  "Home and family, or property. A solid foundation."),
 (21, "Wohnzimmer", "Living Room", "privacy, intimacy, domestic life",
  "Private life behind closed doors."),
 (22, "Militärperson", "Military Person", "discipline, duty, authority",
  "Order and duty, or someone in uniform."),
 (23, "Gericht", "Court", "judgment, justice, decisions",
  "A court or judgment. A matter is decided."),
 (24, "Diebstahl", "Theft", "loss, fraud, danger",
  "Something is taken or lost. Guard what's yours."),
 (25, "Hohe Ehren", "High Honours", "success, recognition, promotion",
  "Recognition and advancement."),
 (26, "Großes Glück", "Great Fortune", "joy, luck, achievement",
  "Great good fortune and happiness."),
 (27, "Unverhofftes Geld", "Unexpected Money", "a windfall, surprise gain",
  "Money arrives from an unexpected direction."),
 (28, "Erwartung", "Expectation", "hope, anticipation, waiting",
  "Waiting with hope. Patience is needed."),
 (29, "Gefängnis", "Prison", "restriction, isolation, stuck",
  "Feeling confined. Something holds you in place."),
 (30, "Gerichtsperson", "Legal Person", "an official, a lawyer, authority",
  "A lawyer, official or judge. Formal authority."),
 (31, "Kurze Krankheit", "Short Illness", "a pause, a brief setback, recovery",
  "A short illness or temporary setback. It passes."),
 (32, "Kummer und Widerwärtigkeiten", "Grief and Adversity", "hardship, worry, trouble",
  "A hard patch. Worries and difficulties pile up."),
 (33, "Trübe Gedanken", "Gloomy Thoughts", "doubt, fear, sadness",
  "Dark thoughts and self-doubt."),
 (34, "Arbeit", "Work", "job, duties, effort",
  "Work and responsibilities. Effort that's needed."),
 (35, "Weiter Weg", "Long Road", "distance, patience, long-term",
  "A long way to go. Persistence pays off over time."),
 (36, "Hoffnung, großes Wasser", "Hope, Great Water", "hope, faith, distance over water",
  "Hope and confidence, and sometimes a journey across water."),
]

SOURCES: dict[int, str] = {}

cards = [{
    "id": f"kipper_{n:02d}", "name": de, "name_en": en,
    "arcana": "oracle", "number": n, "suit": None, "rank": None,
    "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
    "image": f"cards/kipper/{n:02d}.jpg", "source_url": SOURCES.get(n, ""),
} for n, de, en, kw, meaning in CARDS]

deck = {
    "id": "kipper",
    "name": "Kipper Cards",
    "short_name": "Kipper",
    "family": "Oracle",
    "description": "The 36-card German Kipper fortune-telling deck (1890s). Read upright, in combinations.",
    "card_aspect": 0.62,
    "color": 0x1C7ED6,
    "reversals": False,
    "spreads": ["single", "line3", "line5", "box9"],
    "suits": {},
    "cards": cards,
}
assert len(cards) == 36
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "kipper.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
