"""Builds data/lenormand.json — the 36-card Petit Lenormand.

Traditional German/French numbering and playing-card inserts. Lenormand is read
in combinations and without reversals, so each card has one meaning.
To use scans, fill in SOURCES with image URLs (card number -> URL) and re-run.
"""
import json, os, sys

# number, name, insert, keywords, meaning
CARDS = [
 (1, "Rider", "9♥", "news, a visitor, speed, arrival",
  "News or a visitor is on the way. Things move quickly; something comes to you."),
 (2, "Clover", "6♦", "luck, a chance, lightness, brief joy",
  "A small stroke of luck or a short-lived opportunity. Take it while it's there."),
 (3, "Ship", "10♠", "travel, distance, trade, longing",
  "A journey, a move or dealings from afar. Also longing for something distant."),
 (4, "House", "K♥", "home, family, stability, property",
  "Home, family and the private sphere. Security and what you've built."),
 (5, "Tree", "7♥", "health, growth, roots, time",
  "Health and slow, steady growth. Deep roots; things that take time."),
 (6, "Clouds", "K♣", "confusion, doubt, unclear situation",
  "Uncertainty and mixed signals. Wait for the air to clear before deciding."),
 (7, "Snake", "Q♣", "complication, desire, a rival, detour",
  "Complications, a winding path, or a clever and possibly jealous woman."),
 (8, "Coffin", "9♦", "ending, closure, rest, transformation",
  "Something ends or needs to be laid to rest. Clearing space for what's next."),
 (9, "Bouquet", "Q♠", "gift, charm, invitation, appreciation",
  "A gift, a compliment or a pleasant invitation. Beauty and goodwill."),
 (10, "Scythe", "J♦", "sudden cut, decision, danger, harvest",
  "A sudden decision or clean cut. Quick, sharp and final; handle with care."),
 (11, "Whip", "J♣", "conflict, repetition, argument, discipline",
  "Arguments, tension or something repeating. Also discipline and exercise."),
 (12, "Birds", "7♦", "conversation, nerves, chatter, a couple",
  "Talk, phone calls and gossip, or nervous excitement. Often a pair of people."),
 (13, "Child", "J♠", "new beginning, innocence, small, a child",
  "A fresh start, something small or new, or a child. Keep it simple."),
 (14, "Fox", "9♣", "cunning, self-interest, work, caution",
  "Something isn't what it seems. Be smart and look after your own interests."),
 (15, "Bear", "10♣", "strength, power, finances, protection",
  "Strength and authority, often over money. A powerful or protective figure."),
 (16, "Stars", "6♥", "hope, guidance, clarity, dreams",
  "Clear skies and good guidance. Hope, inspiration and wishes on track."),
 (17, "Stork", "Q♥", "change, improvement, moving, renewal",
  "Change for the better: a move, an improvement or a new phase arriving."),
 (18, "Dog", "10♥", "loyalty, friendship, trust, support",
  "A loyal friend or ally. Trust and dependable support."),
 (19, "Tower", "6♠", "institutions, authority, solitude, the long term",
  "Official bodies, big organisations or standing apart. Distance and ambition."),
 (20, "Garden", "8♠", "public life, events, community, networking",
  "Gatherings, social life and being seen. What happens in public."),
 (21, "Mountain", "8♣", "obstacle, delay, challenge, endurance",
  "A block or delay stands in the way. Patience and persistence get you over."),
 (22, "Crossroads", "Q♦", "choice, options, alternatives, a fork",
  "A decision between paths. More than one way forward."),
 (23, "Mice", "7♣", "loss, worry, erosion, stress",
  "Something is being gnawed away: money, health or peace of mind. Plug the leak."),
 (24, "Heart", "J♥", "love, affection, romance, kindness",
  "Love and warmth. Matters of the heart and genuine feeling."),
 (25, "Ring", "A♣", "commitment, contract, union, cycle",
  "A promise, a contract or a committed bond. Something binding or recurring."),
 (26, "Book", "10♦", "secrets, knowledge, study, the unknown",
  "Something hidden or not yet known. Learning, research or a secret."),
 (27, "Letter", "7♠", "message, document, communication",
  "A written message, email or document. News arrives in writing."),
 (28, "Man", "A♥", "the querent (male), a significant man",
  "The person asking, if a man, or the key man in the situation."),
 (29, "Woman", "A♠", "the querent (female), a significant woman",
  "The person asking, if a woman, or the key woman in the situation."),
 (30, "Lily", "K♠", "peace, maturity, virtue, sensuality",
  "Calm, experience and harmony. Also family peace or mature desire."),
 (31, "Sun", "A♦", "success, energy, warmth, victory",
  "Success, confidence and good energy. Everything goes well."),
 (32, "Moon", "8♥", "recognition, emotions, intuition, reputation",
  "Recognition and honour, or the emotional and intuitive side of things."),
 (33, "Key", "8♦", "solution, certainty, answer, importance",
  "The answer is found. Certainty, success and doors opening."),
 (34, "Fish", "K♦", "money, abundance, business, flow",
  "Money, business and plenty. Resources flowing in and out."),
 (35, "Anchor", "9♠", "stability, persistence, security, work",
  "Staying power and a secure foothold. Long-term stability, often at work."),
 (36, "Cross", "6♣", "burden, fate, duty, faith",
  "A burden to carry or a matter of fate. Also faith and meaning in hardship."),
]

SOURCES: dict[int, str] = {}   # card number -> image URL (public domain scans)

cards = [{
    "id": f"len_{n:02d}",
    "name": name,
    "arcana": "lenormand",
    "number": n,
    "suit": None,
    "rank": None,
    "insert": insert,
    "keywords": {"upright": kw.split(", ")},
    "meaning": {"upright": meaning},
    "image": f"cards/lenormand/{n:02d}.jpg",
    "source_url": SOURCES.get(n, ""),
} for n, name, insert, kw, meaning in CARDS]

deck = {
    "id": "lenormand",
    "name": "Petit Lenormand",
    "short_name": "Lenormand",
    "family": "Oracle",
    "description": "The 36-card Petit Lenormand, descended from Hechtel's 'Spiel der Hoffnung' (c. 1799). "
                   "Read in combinations, without reversals.",
    "card_aspect": 0.66,
    "color": 0x8C6D46,
    "reversals": False,
    "spreads": ["single", "line3", "line5", "box9"],
    "suits": {},
    "cards": cards,
}
assert len(cards) == 36
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "lenormand.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
