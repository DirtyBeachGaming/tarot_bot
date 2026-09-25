"""Builds data/tarock.json — Austrian Tarock (the 54-card "Industrie und Glück" pack).

Tarock is a game deck with no fortune-telling tradition of its own, so this is an
original meaning system written for the bot. The 22 tarocks form a journey through
19th-century town life, from Pagat (the humble underdog) up to Mond (XXI) and the
untouchable Sküs. The cards are double-ended, so they are read without reversals.
To use scans, fill in SOURCES (card id -> image URL) and re-run.
"""
import json, os, sys

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII",
         "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"]

# number, nickname (or None), theme, keywords, meaning
TAROCKS = [
 (1, "Pagat", "The Underdog", "small start, the last trick, cunning, humility",
  "The lowest tarock, and the one that can still win the final trick. Start small; timing beats rank."),
 (2, "Uhu", "The Owl", "watchfulness, night thoughts, quiet wisdom",
  "Keep your eyes open while others sleep. What you notice now pays off later."),
 (3, "Kakadu", "The Cockatoo", "show, chatter, being noticed",
  "A loud entrance. Being seen helps, but don't mistake noise for substance."),
 (4, "Marabu", "The Marabou", "patience, waiting, taking what's left",
  "Wait at the edge of things. Opportunity comes to whoever is still standing there."),
 (5, None, "The Workshop", "honest labour, craft, routine",
  "Steady work with your own hands. Industry, the first half of the motto."),
 (6, None, "The Market", "trade, bargaining, exchange",
  "Everything has a price today. Haggle well and know what you'll walk away from."),
 (7, None, "The Harvest", "reward, results, gathering in",
  "What you planted comes in. Gather it before the weather turns."),
 (8, None, "The Hearth", "home, comfort, domestic peace",
  "A warm room and a closed door. Rest where you're safe."),
 (9, None, "The Dance", "courtship, celebration, attraction",
  "Music and a partner. Say yes to the invitation."),
 (10, None, "The Turn", "halfway, change of fortune, reversal",
  "The midpoint of the tarocks. What was rising may fall, and the reverse."),
 (11, None, "The Road", "travel, departure, distance",
  "Pack a bag. A journey, literal or not, changes your view."),
 (12, None, "The Letter", "news, a message, correspondence",
  "Something written arrives. Read it twice before you answer."),
 (13, None, "The Storm", "upheaval, sudden trouble, clearing air",
  "Weather you can't control. Take shelter; it passes, and the air is cleaner after."),
 (14, None, "The Café", "society, conversation, gossip, ideas",
  "The coffee-house table: news, opinions and alliances made over a newspaper."),
 (15, None, "The Ledger", "accounts, debts, what's owed",
  "Check the numbers. Settle what you owe and collect what's yours."),
 (16, None, "The Garden", "leisure, growth, cultivation",
  "Tend something slowly. Pleasure that rewards patience."),
 (17, None, "The Theatre", "masks, performance, appearances",
  "Everyone is playing a part. Enjoy the show, but know who's acting."),
 (18, None, "The Carriage", "status, advancement, ambition",
  "Moving up in the world. Mind who is holding the reins."),
 (19, None, "The Festival", "public joy, success, community",
  "Lanterns in the square. A shared success, celebrated openly."),
 (20, None, "The Lottery", "pure chance, luck, the draw",
  "Glück, the other half of the motto. Nothing you did earned it; take it gracefully."),
 (21, "Mond", "The Moon", "mastery, supreme power, completion",
  "The highest numbered tarock. Command of the situation, and power over the night."),
]
SKUS = ("Sküs", "The Excuse", "freedom, the wild card, untouchable, escape",
        "The Sküs can't be captured and outranks everything. You're free of the rules this time; play it well.")

SUITS = {
    # key: (German, English, symbol, color, domain, ranks)
    "herz":  ("Herz",  "Hearts",   "♥", 0xC92A2A, "love, home, friendship",
              [("König", "King", "K"), ("Dame", "Queen", "Q"), ("Reiter", "Cavalier", "C"), ("Bube", "Jack", "J"),
               ("1", "One", "1"), ("2", "Two", "2"), ("3", "Three", "3"), ("4", "Four", "4")]),
    "karo":  ("Karo",  "Diamonds", "♦", 0xE8590C, "money, trade, possessions",
              [("König", "King", "K"), ("Dame", "Queen", "Q"), ("Reiter", "Cavalier", "C"), ("Bube", "Jack", "J"),
               ("1", "One", "1"), ("2", "Two", "2"), ("3", "Three", "3"), ("4", "Four", "4")]),
    "kreuz": ("Kreuz", "Clubs",    "♣", 0x2B8A3E, "work, effort, ambition",
              [("König", "King", "K"), ("Dame", "Queen", "Q"), ("Reiter", "Cavalier", "C"), ("Bube", "Jack", "J"),
               ("10", "Ten", "10"), ("9", "Nine", "9"), ("8", "Eight", "8"), ("7", "Seven", "7")]),
    "pik":   ("Pik",   "Spades",   "♠", 0x343A40, "trouble, fate, hard lessons",
              [("König", "King", "K"), ("Dame", "Queen", "Q"), ("Reiter", "Cavalier", "C"), ("Bube", "Jack", "J"),
               ("10", "Ten", "10"), ("9", "Nine", "9"), ("8", "Eight", "8"), ("7", "Seven", "7")]),
}

# keywords, meaning — in the order of the ranks above
SUIT_MEANINGS = {
 "herz": [
  ("warm authority, a father, generosity", "A generous man who looks after his own. Love expressed as protection."),
  ("devotion, care, emotional wisdom", "A loving woman who holds a household together. Feelings handled wisely."),
  ("romance arriving, a suitor, a visit", "Someone rides toward you with an open heart. An invitation or a declaration."),
  ("a sweetheart, young affection, a friend", "A young admirer or a loyal friend. Simple, uncomplicated fondness."),
  ("the whole heart, deep love, home", "In the red suits the 1 is the highest pip. Small in number, largest in feeling."),
  ("a pair, partnership, reconciliation", "Two people find each other, or find their way back."),
  ("friendship, a gathering, warmth shared", "Company around a table. Affection that includes others."),
  ("contentment, a settled heart", "The lowest red pip, and the calmest. Love that no longer needs proving."),
 ],
 "karo": [
  ("a wealthy man, a banker, a patron", "A man with money and the power it brings. Useful, if he's on your side."),
  ("shrewd management, a businesswoman", "A woman who knows the value of everything. Good sense with resources."),
  ("money on the move, a deal in progress", "Funds, goods or an offer on the way. Move while it's moving."),
  ("a clerk, an errand, small gains", "A junior in business, or a small transaction handled well."),
  ("the best bargain, a windfall", "The top red pip: the one deal that matters most. A real gain."),
  ("an exchange, a contract, fair terms", "Two parties trade. Read the terms before you shake."),
  ("steady income, growth", "Money builds modestly and reliably."),
  ("small change, thrift", "Pennies saved. Not much, but it's yours."),
 ],
 "kreuz": [
  ("a boss, a master craftsman, leadership", "A man who has earned his position through work. Respect him and learn."),
  ("an organiser, a capable woman", "A woman who gets things done and keeps everyone on task."),
  ("a new job, an opportunity, momentum", "Work arrives at a gallop: a project, an offer, a push forward."),
  ("an apprentice, a messenger, eagerness", "Someone young and willing, still learning the trade."),
  ("accomplishment, a task completed", "The work is finished and it's good. Take the credit."),
  ("hard effort, long hours", "The grind. It's tiring, but it's leading somewhere."),
  ("competition, a rival at work", "Someone else wants the same position. Stay sharp."),
  ("a small step, the first task", "The lowest club: begin with the simplest thing."),
 ],
 "pik": [
  ("stern authority, a judge, an official", "A severe man with power over you. Deal with him formally and honestly."),
  ("a cold woman, a widow, sharp judgment", "A woman who has known loss. She sees clearly and says so."),
  ("trouble approaching, bad news riding in", "Something unwelcome is coming fast. Better to meet it than wait."),
  ("a troublemaker, spite, petty malice", "A small person causing big irritation. Don't feed it."),
  ("a heavy blow, a hard ending", "The strongest black pip. Something falls hard; you will get up again."),
  ("worry, sleepless nights", "The mind runs in circles. Name the fear and it shrinks."),
  ("obstacles, delays, frustration", "The road is blocked for now. Take another route or wait it out."),
  ("a minor setback, a warning", "A small thing goes wrong. Notice it now so it stays small."),
 ],
}

SOURCES: dict[str, str] = {}   # card id -> image URL (public domain scans)

cards = []
for n, nick, theme, kw, meaning in TAROCKS:
    cid = f"tarock_{n:02d}"
    name = f"{ROMAN[n]} · {nick}" if nick else f"{ROMAN[n]} · {theme}"
    cards.append({
        "id": cid, "name": name, "name_en": theme if nick else None,
        "arcana": "trump", "number": n, "suit": None, "rank": ROMAN[n],
        "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
        "image": f"cards/tarock/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
    })
nick, theme, kw, meaning = SKUS
cards.append({
    "id": "tarock_skus", "name": nick, "name_en": theme,
    "arcana": "trump", "number": 22, "suit": None, "rank": "Sküs",
    "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
    "image": "cards/tarock/tarock_skus.jpg", "source_url": SOURCES.get("tarock_skus", ""),
})

for suit, (de, en, sym, color, domain, ranks) in SUITS.items():
    for i, ((r_de, r_en, r_short), (kw, meaning)) in enumerate(zip(ranks, SUIT_MEANINGS[suit]), start=1):
        cid = f"{suit}_{i:02d}"
        court = i <= 4
        cards.append({
            "id": cid,
            "name": f"{de}-{r_de}" if court else f"{de} {r_de}",
            "name_en": f"{r_en} of {en}",
            "arcana": "court" if court else "pip",
            "number": i, "suit": suit, "rank": r_de,
            "insert": f"{r_short}{sym}",
            "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
            "image": f"cards/tarock/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
        })

deck = {
    "id": "tarock",
    "name": "Austrian Tarock (Industrie und Glück)",
    "short_name": "Tarock",
    "family": "Central European tarot",
    "description": "The 54-card Austrian Tarock pack: 22 tarocks plus 32 French-suited cards. "
                   "Tarock is a game deck; these meanings are an original system written for this bot.",
    "card_aspect": 0.53,
    "color": 0x5C7A99,
    "reversals": False,
    "spreads": ["single", "industrie", "trull", "three", "situation", "celtic"],
    "suits": {k: {"name": f"{v[0]} ({v[1]})", "color": v[3], "domain": v[4]} for k, v in SUITS.items()},
    "cards": cards,
}
assert len(cards) == 54, len(cards)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "tarock.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
