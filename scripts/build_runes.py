"""Builds data/runes.json — the 24 runes of the Elder Futhark.

Meanings follow common modern rune-casting practice. Runes that look the same
upside down (Gebo, Hagalaz, Nauthiz, Isa, Jera, Eihwaz, Sowilo, Ingwaz, Dagaz)
can't be reversed; the rest can come up "merkstave" (reversed).
No scans needed: the bot draws each rune from its strokes (tarot/images.py).
"""
import json, os, sys

# name, glyph, aett, keywords up, keywords reversed (or None), meaning up, meaning reversed
RUNES = [
 ("Fehu", "ᚠ", "cattle, wealth, earned prosperity", "loss, greed, slipping money",
  "Wealth that moves: earnings, resources, what you've worked for.",
  "Money or energy draining away. Guard what you have."),
 ("Uruz", "ᚢ", "strength, health, raw vitality", "weakness, missed chance",
  "Wild strength and good health. Take on the challenge.",
  "Energy is low or misdirected. Don't force it."),
 ("Thurisaz", "ᚦ", "force, defence, a thorn", "danger, impulsiveness, spite",
  "A thorn that protects. A forceful moment; act deliberately.",
  "Reckless force or spite. Wait before striking."),
 ("Ansuz", "ᚨ", "words, wisdom, signals", "misunderstanding, bad advice",
  "A message or insight. Listen closely; words carry power.",
  "Crossed wires or bad advice. Check your sources."),
 ("Raidho", "ᚱ", "journey, rhythm, right action", "delay, a wrong turn",
  "A journey, or things falling into the right rhythm.",
  "Plans stall or go off course. Re-route."),
 ("Kenaz", "ᚲ", "torch, insight, creativity", "blocked vision, a creative slump",
  "A torch in the dark. Clarity, craft and inspiration.",
  "The light dims. Something is hidden from you, or you're stuck."),
 ("Gebo", "ᚷ", "gift, exchange, partnership", None,
  "A gift given and returned. Balance in a relationship or deal.", None),
 ("Wunjo", "ᚹ", "joy, harmony, belonging", "sorrow, alienation",
  "Joy and fellowship. Things are right with your people.",
  "Discontent or feeling left out."),
 ("Hagalaz", "ᚺ", "hail, disruption, forces beyond control", None,
  "Hail falls: sudden disruption you didn't cause. It clears the ground.", None),
 ("Nauthiz", "ᚾ", "need, constraint, endurance", None,
  "Need and hardship. Endure it; necessity teaches.", None),
 ("Isa", "ᛁ", "ice, stillness, pause", None,
  "Everything freezes. Wait; now isn't the time to push.", None),
 ("Jera", "ᛃ", "harvest, a year's reward, cycles", None,
  "The harvest comes in its season. Patience is rewarded.", None),
 ("Eihwaz", "ᛇ", "yew, endurance, transformation", None,
  "The yew endures. Steadfastness through change.", None),
 ("Perthro", "ᛈ", "mystery, chance, fate", "secrets kept, stagnation",
  "The dice cup: chance, fate and hidden things.",
  "What's hidden stays hidden, or luck turns sour."),
 ("Algiz", "ᛉ", "protection, sanctuary, instinct", "vulnerability, a warning",
  "A raised hand of protection. Trust your instincts; you're shielded.",
  "Your guard is down. Heed the warning."),
 ("Sowilo", "ᛊ", "sun, success, vitality", None,
  "The sun: success, clarity and life force.", None),
 ("Tiwaz", "ᛏ", "honour, justice, courage", "injustice, cowardice, defeat",
  "The warrior's rune. Act with honour and win fairly.",
  "Courage fails, or a fight isn't fair."),
 ("Berkano", "ᛒ", "birch, birth, growth, care", "stagnation, family trouble",
  "New growth and nurturing. A beginning that needs care.",
  "Growth is blocked or home life is strained."),
 ("Ehwaz", "ᛖ", "horse, teamwork, progress", "restlessness, mistrust",
  "Horse and rider working together. Steady progress with a partner.",
  "Partners pulling apart. Restlessness."),
 ("Mannaz", "ᛗ", "humanity, the self, community", "isolation, self-deception",
  "You among others. Know yourself and your place in the group.",
  "Cut off from others, or not seeing yourself clearly."),
 ("Laguz", "ᛚ", "water, flow, intuition", "confusion, fear, poor judgment",
  "Water flows. Follow intuition and go with the current.",
  "Muddy waters. Emotions cloud judgment."),
 ("Ingwaz", "ᛜ", "seed, gestation, completion", None,
  "A seed completes its growth. Rest, then a new phase begins.", None),
 ("Dagaz", "ᛞ", "dawn, breakthrough, awakening", None,
  "Daybreak. A breakthrough and a clear new day.", None),
 ("Othala", "ᛟ", "heritage, home, inheritance", "loss of roots, prejudice",
  "Ancestral ground: home, heritage and what's passed down.",
  "Cut off from roots, or clinging to the past."),
]

cards = []
for i, (name, glyph, ku, kr, up, rev) in enumerate(RUNES):
    card = {
        "id": f"rune_{i+1:02d}", "name": f"{name} {glyph}", "name_en": None,
        "arcana": "rune", "number": i + 1, "suit": None, "rank": name,
        "keywords": {"upright": ku.split(", ")}, "meaning": {"upright": up},
        "image": f"cards/runes/{i+1:02d}.png", "source_url": "",
    }
    if kr:
        card["keywords"]["reversed"] = kr.split(", ")
        card["meaning"]["reversed"] = rev
    else:
        card["reversible"] = False
    cards.append(card)

deck = {
    "id": "runes",
    "name": "Elder Futhark Runes",
    "short_name": "Runes",
    "family": "Runes",
    "description": "The 24 runes of the Elder Futhark. Symmetrical runes can't be reversed; the rest can come up merkstave.",
    "card_aspect": 0.72,
    "color": 0x5C940D,
    "spreads": ["single", "norns", "line5"],
    "suits": {},
    "cards": cards,
}
assert len(cards) == 24
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "runes.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
