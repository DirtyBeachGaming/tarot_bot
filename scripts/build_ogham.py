"""Builds data/ogham.json — the 20 letters (feda) of the Ogham alphabet and their trees.

Meanings follow common modern Ogham divination. Staves are read upright.
No scans needed: the bot draws each letter on its stem line (tarot/images.py).
"""
import json, os, sys

# name, tree, aicme group (B, H, M, A), strokes 1-5, keywords, meaning
FEDA = [
 ("Beith", "Birch", "B", 1, "beginnings, renewal, clearing the way",
  "The birch is first to grow on cleared ground. A fresh start; sweep out the old."),
 ("Luis", "Rowan", "B", 2, "protection, insight, quickening",
  "Rowan guards against harm. Trust your perception and stay protected."),
 ("Fearn", "Alder", "B", 3, "support, courage, bridging",
  "Alder stands in water and doesn't rot. Be the support; hold firm under pressure."),
 ("Sail", "Willow", "B", 4, "intuition, flexibility, feeling",
  "The willow bends by the water. Follow feelings and cycles; flexibility wins."),
 ("Nion", "Ash", "B", 5, "connection, the wider world, action",
  "Ash links worlds. See how your situation connects to everything around it."),
 ("Uath", "Hawthorn", "H", 1, "obstacles, patience, a threshold",
  "Hawthorn blocks the gap in the hedge. A pause at a threshold; don't force it."),
 ("Dair", "Oak", "H", 2, "strength, endurance, a doorway",
  "The oak is the door. Strength and stability open the way forward."),
 ("Tinne", "Holly", "H", 3, "challenge, balance, defence",
  "Holly is the warrior's tree. Meet the challenge with fairness and resolve."),
 ("Coll", "Hazel", "H", 4, "wisdom, creativity, inspiration",
  "The hazel of wisdom. An idea or insight worth acting on."),
 ("Quert", "Apple", "H", 5, "choice, beauty, wholeness",
  "The apple: a choice between good things, and a taste of contentment."),
 ("Muin", "Vine", "M", 1, "harvest, truth, celebration",
  "The vine brings its harvest. Speak truthfully and enjoy what's ripened."),
 ("Gort", "Ivy", "M", 2, "persistence, growth, ties",
  "Ivy spirals and holds on. Slow, determined growth; watch what binds you."),
 ("nGéadal", "Reed", "M", 3, "direction, purpose, communication",
  "The reed points straight. Act with purpose and say what you mean."),
 ("Straif", "Blackthorn", "M", 4, "hard necessity, strife, fate",
  "Blackthorn: something unavoidable. Hard, but it clears the path."),
 ("Ruis", "Elder", "M", 5, "endings, transition, renewal",
  "The elder closes a cycle. Let something end so it can regrow."),
 ("Ailm", "Pine", "A", 1, "clarity, perspective, vision",
  "From the pine's height, see far. Get the long view before deciding."),
 ("Onn", "Gorse", "A", 2, "hope, persistence, gathering",
  "Gorse flowers all year. Keep hope; gather what you need."),
 ("Úr", "Heather", "A", 3, "healing, passion, the heart",
  "Heather by the doorstep. Healing, warmth and matters of the heart."),
 ("Eadhadh", "Aspen", "A", 4, "courage, facing fear, endurance",
  "The trembling aspen. Fear is present; courage goes on anyway."),
 ("Iodhadh", "Yew", "A", 5, "death and rebirth, long memory",
  "The ancient yew. Endings that are also beginnings; what lasts across time."),
]

cards = [{
    "id": f"ogham_{i+1:02d}", "name": name, "name_en": tree,
    "arcana": "ogham", "number": i + 1, "suit": group, "rank": str(n),
    "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
    "image": f"cards/ogham/{i+1:02d}.png", "source_url": "",
} for i, (name, tree, group, n, kw, meaning) in enumerate(FEDA)]

deck = {
    "id": "ogham", "name": "Ogham", "short_name": "Ogham", "family": "Staves & signs",
    "description": "The 20 Ogham letters and their trees. Read upright.",
    "card_aspect": 0.5, "color": 0x2F9E44, "reversals": False,
    "spreads": ["single", "three", "line5"], "suits": {}, "cards": cards,
}
assert len(cards) == 20
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "ogham.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
