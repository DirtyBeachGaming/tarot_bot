"""Builds data/playing_cards.json — a standard 52-card deck with traditional
English-language cartomancy meanings (Hearts = love, Diamonds = money,
Clubs = work and friends, Spades = trouble). Read upright.
To use scans, fill in SOURCES (card id -> URL).
"""
import json, os, sys

SUITS = {
    "hearts":   ("Hearts",   "♥", 0xC92A2A, "love, home, family, happiness"),
    "diamonds": ("Diamonds", "♦", 0xE8590C, "money, business, news"),
    "clubs":    ("Clubs",    "♣", 0x2B8A3E, "work, friendship, success"),
    "spades":   ("Spades",   "♠", 0x343A40, "obstacles, trouble, change"),
}
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"]
SHORT = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

M = {
 "hearts": [
  ("home, love, happiness", "The home and the heart. Love, friendship and a happy household."),
  ("partnership, affection, union", "Two people drawn together. A loving partnership or a close friendship."),
  ("indecision in love, caution", "Be careful with your feelings; not every declaration is reliable."),
  ("change, travel, delayed commitment", "A change of scene or a short trip. Commitments may wait."),
  ("jealousy, unease", "Jealousy or ill will from someone close. Don't feed it."),
  ("good luck, kindness, nostalgia", "Unexpected good fortune, or a sweet memory returning."),
  ("an unreliable person, broken promise", "Someone may not keep their word. Keep expectations modest."),
  ("invitation, celebration, visit", "An invitation, a party or a welcome visit."),
  ("the wish card, dreams come true", "The wish card. What you hope for is within reach."),
  ("good fortune, happiness, success", "Happiness and success, especially at home and in love."),
  ("a young friend, a lover", "A warm-hearted young person, a close friend or admirer."),
  ("a kind, fair woman", "A loving, good-natured woman who wishes you well."),
  ("a kind, fair man", "A generous, affectionate man, quick to help."),
 ],
 "diamonds": [
  ("a letter, a ring, money news", "News about money, a message, or a ring."),
  ("a serious romance, a business deal", "An important partnership, in business or love."),
  ("legal matters, disputes", "Paperwork or a dispute. Handle legal matters carefully."),
  ("an inheritance, improvement", "Money improves: an inheritance, a raise or a gift."),
  ("prosperity, success in business", "Business goes well. Prosperity through effort."),
  ("warnings, money trouble at home", "Be careful with money in close relationships."),
  ("gambling, criticism", "A gamble or harsh words. Think before you risk it."),
  ("travel, a late commitment", "A journey, or something that comes later than planned."),
  ("a surprise about money, restlessness", "Money surprises, good or bad. A restless mood."),
  ("money, a big change", "A significant change involving money, often a good one."),
  ("a messenger, an unreliable relative", "News carried by someone young, not always trustworthy."),
  ("a gossip, a flirt", "A lively woman who likes to talk; be careful what you share."),
  ("a powerful, stubborn man", "A man with money and influence who likes his own way."),
 ],
 "clubs": [
  ("wealth, success, good news", "Success and prosperity. Good news about work."),
  ("opposition, disappointment", "Resistance or a small letdown. Don't be discouraged."),
  ("success, a second chance", "Progress through partnership, or another chance at something."),
  ("bad luck, deceit", "A run of bad luck or someone being dishonest."),
  ("a new friend, a good match", "A new friend or a happy partnership."),
  ("help, business success", "Financial help or support brings success."),
  ("prosperity, with caution", "Things go well; just watch for jealousy around you."),
  ("jealousy, greed", "Envy or greed gets in the way."),
  ("stubbornness, argument", "A dispute caused by someone who won't budge."),
  ("unexpected money, travel", "Money you didn't expect, or a journey."),
  ("a reliable friend", "A loyal, dependable young friend."),
  ("a confident, capable woman", "A self-assured woman who can help you."),
  ("an honest, generous man", "A trustworthy, generous man and a good ally."),
 ],
 "spades": [
  ("a major ending, big change", "A major change or ending. Something important closes."),
  ("separation, gossip", "A parting of ways, or talk behind your back."),
  ("heartbreak, betrayal", "Heartache or infidelity. Protect yourself."),
  ("illness, rest needed", "Rest and recovery. Look after your health."),
  ("setbacks, obstacles", "Things are harder than expected. Keep going."),
  ("gradual improvement", "Slow but real improvement. The worst is over."),
  ("sudden sorrow, loss of a friend", "An unexpected sadness or a friendship lost."),
  ("trouble ahead, disappointment", "Caution: plans may disappoint. Adjust early."),
  ("misfortune, worry", "The hardest card in the pack. Brace for a difficult time; it will pass."),
  ("worry, bad news", "Anxiety or unwelcome news. Share the load."),
  ("a well-meaning but lazy youth", "A young person who means well but doesn't follow through."),
  ("a sharp, independent woman", "A clever, independent woman, possibly a widow. She sees clearly."),
  ("an ambitious man, authority", "An ambitious man or an authority figure, like a lawyer."),
 ],
}

SOURCES: dict[str, str] = {}
cards = []
for suit, (en, sym, color, domain) in SUITS.items():
    for i, (kw, meaning) in enumerate(M[suit]):
        cid = f"{suit}_{i+1:02d}"
        cards.append({
            "id": cid, "name": f"{RANKS[i]} of {en}", "arcana": "minor",
            "number": i + 1, "suit": suit, "rank": RANKS[i], "insert": f"{SHORT[i]}{sym}",
            "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
            "image": f"cards/playing_cards/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
        })

deck = {
    "id": "playing_cards",
    "name": "Playing Cards (52)",
    "short_name": "Playing Cards",
    "family": "Playing cards",
    "description": "A standard 52-card deck with traditional English-language cartomancy meanings.",
    "card_aspect": 0.71,
    "color": 0xC92A2A,
    "reversals": False,
    "spreads": ["single", "three", "situation", "box9"],
    "suits": {k: {"name": v[0], "color": v[2], "domain": v[3]} for k, v in SUITS.items()},
    "cards": cards,
}
assert len(cards) == 52
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "playing_cards.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
