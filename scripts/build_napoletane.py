"""Builds data/napoletane.json — the 40-card Neapolitan (Napoletane) deck.

Meanings follow the general suit and rank conventions of Italian cartomancy
(Denari = money, Coppe = love and home, Spade = trouble and conflict,
Bastoni = work, effort and travel). Local readings vary; edit freely.
"""
import hashlib, json, os, sys


def commons_url(filename):
    f = filename.replace(" ", "_")
    h = hashlib.md5(f.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{f}"


SUITS = {
    # key: (Italian, English, color, domain, file-name spelling)
    "denari":  ("Denari",  "Coins",  0xC9A227, "money, business, gain, practical matters"),
    "coppe":   ("Coppe",   "Cups",   0xC2255C, "love, home, family, feelings, joy"),
    "spade":   ("Spade",   "Swords", 0x1864AB, "obstacles, conflict, worry, hard truths"),
    "bastoni": ("Bastoni", "Clubs",  0x2B8A3E, "work, effort, strength, travel"),
}
RANKS_IT = ["Asso", "Due", "Tre", "Quattro", "Cinque", "Sei", "Sette", "Fante", "Cavallo", "Re"]
RANKS_EN = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Knave", "Knight", "King"]
# Commons file names use the pip number words even for the court cards (8 = Fante, 9 = Cavallo, 10 = Re)
FILE_WORDS = ["Asso", "Due", "Tre", "Quattro", "Cinque", "Sei", "Sette", "Otto", "Nove", "Dieci"]

# upright keywords, reversed keywords, upright meaning, reversed meaning
M = {
 "denari": [
  ("gain, good news, a payment", "delayed payment, missed chance",
   "A gift, a payment or good news about money. Something of value arrives.",
   "Money is slow to arrive, or an opportunity is undervalued."),
  ("exchange, deal, balance", "bad bargain, imbalance",
   "A deal or exchange between two parties, on fair terms.",
   "One side gets the better of the bargain."),
  ("growth, first profit, cooperation", "small returns, poor teamwork",
   "Effort begins to pay. Money grows through shared work.",
   "Returns are smaller than hoped."),
  ("security, savings, property", "stinginess, money tied up",
   "Solid ground: savings, a home, something that lasts.",
   "Holding money so tightly it can't work for you."),
  ("expense, uncertainty, money worries", "recovery, budget restored",
   "An unexpected cost or a shaky month. Tighten up.",
   "The worst of the expense has passed."),
  ("generosity, fair pay, gifts", "debts, strings attached",
   "Giving and receiving freely. A fair wage, or kindness returned.",
   "A favour that comes with a price."),
  ("fortune, the prize, luck", "luck slipping away, greed",
   "Il Settebello, the most prized card in the pack. Great luck and a winning hand.",
   "Luck is there but slips through greedy fingers."),
  ("a young person, practical news, study", "carelessness, broken promise",
   "A young or junior person, or news about work and money. Learn the trade.",
   "Unreliable messages or careless spending."),
  ("money in motion, business travel, funds arriving", "delays, a stalled deal",
   "Money on the move: a payment arrives, a business trip, a deal advancing.",
   "The deal stalls on the road."),
  ("man of means, patron, financial authority", "miser, corrupt power",
   "A man of means or influence: a boss, banker or benefactor. Material mastery.",
   "Wealth used to control, or a stingy authority."),
 ],
 "coppe": [
  ("home, love, family, joy", "cold house, distance",
   "The house and the heart. Love, family and a happy home.",
   "Coldness at home, or feelings held back."),
  ("union, love, engagement", "separation, misunderstanding",
   "Two hearts meet. Romance, partnership or reconciliation.",
   "A rift between two people."),
  ("celebration, friendship, feasting", "overindulgence, gossip",
   "A party, a wedding, a table full of friends.",
   "Too much wine and loose talk."),
  ("contentment, stability, comfort", "boredom, apathy",
   "Feelings settle into steady comfort.",
   "Comfort has turned into boredom."),
  ("disappointment, sorrow, longing", "consolation, healing",
   "A letdown in love, or a sadness that lingers.",
   "Consolation comes and the heart starts to mend."),
  ("memories, the past, sweetness", "nostalgia, stuck in the past",
   "Old affections return: a memory, a childhood place, an old friend.",
   "Living in yesterday."),
  ("desire, dreams, attraction", "illusion, jealousy",
   "Longing and attraction. A wish you can almost taste.",
   "Desire clouds judgment. Beware jealousy."),
  ("young lover, sweet message, invitation", "flirt, fickle feelings",
   "A young person with a warm heart, or a loving message or invitation.",
   "Charm that doesn't last."),
  ("love arriving, proposal, a visit", "someone leaving, empty promises",
   "Love on horseback: an arrival, a proposal, someone coming to you.",
   "Someone rides away, or a promise isn't kept."),
  ("kind man, protector, emotional maturity", "moody, possessive",
   "A warm, generous man: a father, partner or protector.",
   "Affection turned possessive or moody."),
 ],
 "spade": [
  ("force, decision, a serious matter", "a blow, bad news, harsh words",
   "A serious matter demands a clear decision. Strength and will.",
   "A blow or hard news. Words that wound."),
  ("tension, standoff, rivalry", "truce, release",
   "Two forces locked against each other.",
   "The standoff eases into a truce."),
  ("heartache, jealousy, a rival", "recovery, forgiveness",
   "Heartache, jealousy, or a third person in the way.",
   "The sting fades and forgiveness becomes possible."),
  ("rest, recovery, retreat", "restlessness, lingering strain",
   "Step back and recover. A pause after the struggle.",
   "Unable to rest; the strain lingers."),
  ("quarrel, loss, wounded pride", "reconciliation, lessons learned",
   "An argument, or a defeat that stings.",
   "Making peace after the quarrel."),
  ("departure, leaving trouble behind", "stuck, unable to leave",
   "Leaving trouble behind: a journey or a change of scene.",
   "Trying to leave but held back."),
  ("deceit, gossip, betrayal", "the truth comes out",
   "Watch for lies, gossip, or someone acting behind your back.",
   "The deception is exposed."),
  ("worrying news, a troublemaker, spying", "slander, malice",
   "Worrying news, or a young person who stirs up trouble. Stay alert.",
   "Malicious talk. Don't take the bait."),
  ("sudden change, confrontation, haste", "recklessness, an accident",
   "Trouble rides in fast: a sudden change or a confrontation.",
   "Haste causes harm. Slow down."),
  ("judge, lawyer, stern authority", "tyranny, cruelty",
   "A stern man of law or authority. Judgment, justice, official matters.",
   "Authority that is harsh or unjust."),
 ],
 "bastoni": [
  ("strength, will, new work", "false start, frustration",
   "Raw energy and a new undertaking. The will to begin.",
   "Plans that won't take root."),
  ("plans, choices, working partnership", "indecision, fear",
   "A decision about work or direction, or a partnership in work.",
   "Hesitation wastes the moment."),
  ("progress, trade, news from afar", "delays, setbacks",
   "Efforts expand: trade, travel or news from far away.",
   "Delays in plans or deliveries."),
  ("stability, reward for work, peace at home", "unsettled, instability",
   "A stable foundation earned by work. Peace at home.",
   "Things feel unsettled."),
  ("struggle, competition, rivalry", "agreement, conflict avoided",
   "A struggle or competition. Stand your ground.",
   "The dispute resolves or is avoided."),
  ("victory, recognition, good news", "delayed success, pride",
   "Recognition for hard work. Success is on the way.",
   "Success delayed, or spoiled by pride."),
  ("effort, persistence, defence", "exhaustion, giving up",
   "Hard work and defending what's yours.",
   "Worn out. Know when to yield."),
  ("worker, messenger, errand", "delays, laziness",
   "A hardworking young person, or a message about work.",
   "Messages delayed, tasks left undone."),
  ("journey, a move, rapid progress", "travel problems, postponement",
   "A journey or relocation. Things move quickly.",
   "A trip postponed, or a move that goes wrong."),
  ("hardworking man, leader, steady hand", "stubborn, harsh",
   "A strong, honest, hardworking man. Leadership through effort.",
   "Stubbornness, or a heavy hand."),
 ],
}

cards = []
n = 0
for suit, (it, en, color, domain) in SUITS.items():
    for r in range(10):
        n += 1
        ku, kr, up, rev = M[suit][r]
        word_suit = "Bastoni" if (suit == "bastoni" and r == 9) else suit  # "40 Dieci di Bastoni.jpg"
        src = f"{n:02d} {FILE_WORDS[r]} di {word_suit}.jpg"
        cards.append({
            "id": f"{suit}_{r+1:02d}",
            "name": f"{RANKS_IT[r]} di {it}",
            "name_en": f"{RANKS_EN[r]} of {en}",
            "arcana": "court" if r >= 7 else "pip",
            "number": r + 1,
            "suit": suit,
            "rank": RANKS_IT[r],
            "keywords": {"upright": ku.split(", "), "reversed": kr.split(", ")},
            "meaning": {"upright": up, "reversed": rev},
            "image": f"cards/napoletane/{suit}_{r+1:02d}.jpg",
            "source_url": commons_url(src),
        })

deck = {
    "id": "napoletane",
    "name": "Carte Napoletane",
    "short_name": "Napoletane",
    "family": "Italian regional",
    "description": "The 40-card Neapolitan pattern with Latin suits: Denari, Coppe, Spade, Bastoni. "
                   "Meanings follow the general conventions of Italian cartomancy.",
    "source": "https://commons.wikimedia.org/wiki/Category:Naples_deck",
    "card_aspect": 1324 / 2188,
    "color": 0xC9A227,
    "suits": {k: {"name": f"{v[0]} ({v[1]})", "color": v[2], "domain": v[3]} for k, v in SUITS.items()},
    "cards": cards,
}
assert len(cards) == 40
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "napoletane.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
