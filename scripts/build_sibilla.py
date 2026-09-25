"""Builds data/sibilla.json — the 52-card Vera Sibilla Italiana.

Each card is a titled scene with a playing-card index. Titles and basic meanings
follow the common Italian reading tradition (see sibillareadings.wordpress.com).
Read upright, in combinations. To use scans, fill in SOURCES (card id -> URL).
"""
import json, os, sys

SUITS = {
    # key: (Italian, English, symbol, color, domain)
    "cuori":  ("Cuori",  "Hearts",   "♥", 0xC92A2A, "love, home, happiness"),
    "fiori":  ("Fiori",  "Clubs",    "♣", 0x2B8A3E, "luck, social life, progress"),
    "picche": ("Picche", "Spades",   "♠", 0x343A40, "sorrow, obstacles, endings"),
    "quadri": ("Quadri", "Diamonds", "♦", 0xE8590C, "news, thoughts, daily life"),
}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Italian title, English title, keywords, meaning
C = {
 "cuori": [
  ("Conversazione", "Conversation", "words, negotiation, family influence",
   "A conversation that matters: talks, negotiation, or family having their say."),
  ("La Casa", "The House", "home, property, family harmony",
   "Home and family. Property, a household in harmony."),
  ("Belvedere", "The Beautiful View", "news coming, arrival, expectation",
   "Looking out from the balcony: news or an arrival is on its way."),
  ("Amore", "Love", "romance, attraction, warmth",
   "Love and attraction. Feelings grow and open up."),
  ("Allegrezza al Cuore", "Joy of the Heart", "fulfilment, happy outcome, engagement",
   "The heart is glad. A happy outcome, sometimes an engagement."),
  ("Denari", "Money", "wealth, finances, the past",
   "Money matters and material means. Can also point back to the past."),
  ("Letterato", "The Scholar", "a mature man, a professional, family elder",
   "A cultured man over forty: a professional, an advisor, or an older relative."),
  ("Speranza", "Hope", "success, attainment, protection",
   "Hope that is justified. Aims are reached and you are protected."),
  ("La Fedeltà", "Fidelity", "faithfulness, loyalty, success in love",
   "Loyalty and faithfulness. Love that keeps its promises."),
  ("La Costanza", "Constancy", "stability, lasting, goal achieved",
   "Things that last. Steady effort brings the goal within reach."),
  ("L'Amante", "The Lover", "a loved man, a single man, good news",
   "A man who is loved, or a single man in his thirties or forties. Good news in love."),
  ("L'Amante", "The Beloved", "a loved woman, a young woman, romance",
   "A loved or unmarried young woman. Romance on the woman's side."),
  ("Gran Signore", "The Great Gentleman", "a married man, a father, protector",
   "A mature, established man: a husband, father or protector."),
 ],
 "fiori": [
  ("Imeneo", "Marriage", "marriage, partnership, union",
   "Marriage or any formal partnership. A union blessed."),
  ("La Superbia", "Pride", "vitality, magnetism, self-regard",
   "Pride and presence. Strong positive energy and charisma, used with care."),
  ("Viaggio", "Journey", "travel, movement, relocation",
   "A journey or a move. Change of scene."),
  ("L'Amica", "The Friend", "a female friend, help, comfort",
   "A friend, often a woman, who helps and comforts."),
  ("Fortuna", "Fortune", "good luck, favour, opportunity",
   "Good fortune and favourable winds."),
  ("Consolante Sorpresa", "Comforting Surprise", "unexpected success, a raise, relief",
   "A pleasant surprise that lifts the mood: unexpected success or reward."),
  ("Gran Consolazione", "Great Consolation", "well-being, security, stability",
   "Deep comfort and material security. A weight lifts."),
  ("La Riunione", "The Reunion", "reconciliation, return, recovery",
   "People come back together. Reconciliation or a welcome return."),
  ("L'Allegria", "Joy", "celebration, party, fulfilment",
   "Happiness and celebration. A party, good company."),
  ("La Leggerezza", "Frivolity", "carelessness, recklessness, lightness",
   "Lightness that can tip into carelessness. Weakens the cards around it."),
  ("Domestico", "The Servant", "a helpful young man, a son, a colleague",
   "A helpful young man: a son, an assistant or a colleague."),
  ("Giovine Fanciulla", "The Young Maiden", "a young woman, innocence",
   "A young, unmarried woman. Innocence and freshness."),
  ("Dottore", "The Doctor", "health, healing, a professional",
   "A doctor or professional. Health matters and healing."),
 ],
 "picche": [
  ("Dispiacere", "Sorrow", "sad news, failure, upset",
   "Displeasure and sad news. Something fails or hurts."),
  ("La Vecchia Signora", "The Old Lady", "an elderly woman, old matters",
   "An older woman, or a situation that has been around a long time."),
  ("Il Vedovo", "The Widower", "an older man, loneliness, loss",
   "An older man, or loneliness and loss."),
  ("Ammalato", "The Sick Man", "illness, low spirits, isolation",
   "Illness or low spirits. Rest and care are needed."),
  ("Morte", "Death", "ending, break-up, finality",
   "An ending. Something closes for good."),
  ("Sospiri", "Sighs", "anxiety, longing, waiting",
   "Sighs and worry. Anguish caused by waiting."),
  ("Disgrazia", "Misfortune", "accident, damage, anger",
   "A mishap or damage. Anger or an accident; take care."),
  ("Disperato per Gelosia", "Desperate with Jealousy", "envy, jealousy, crisis",
   "Jealousy and envy. Can also mean a financial crisis."),
  ("Prigione", "Prison", "blockage, isolation, dependency",
   "Feeling trapped. A blockage, isolation or dependency."),
  ("Militare", "The Soldier", "a man in uniform, conflict, force",
   "A man in uniform, or conflict and force."),
  ("Il Nemico", "The Enemy", "a rival, a secret opponent",
   "A male rival or hidden opponent. Watch your back."),
  ("La Nemica", "The Female Enemy", "a female rival, envy",
   "A female rival or enemy."),
  ("Sacerdote", "The Priest", "justice, legal matters, authority",
   "A priest or authority figure. Legal and formal matters."),
 ],
 "quadri": [
  ("Stanza", "The Room", "domestic life, privacy, intimacy",
   "A private room. Domestic life and intimacy."),
  ("La Lettera", "The Letter", "writing, documents, messages",
   "A letter or document. Written communication."),
  ("Presente di Pietre Preziose", "Gift of Precious Stones", "a proposal, an offer, luxury",
   "A precious gift or an offer. A proposal, jewels, luxury."),
  ("Falsità", "Falsehood", "lies, deceit, illusion",
   "Lies and deceit. Not everything is as it appears."),
  ("Malinconia", "Melancholy", "passing sadness, regret, setback",
   "A passing sadness or regret. A setback, not a disaster."),
  ("Il Pensiero", "The Thought", "thoughts, intentions, planning",
   "Thoughts and intentions. What someone has in mind."),
  ("Bambino", "The Child", "a child, innocence, new beginning",
   "A child, a pet, or something newly begun."),
  ("La Donna di Servizio", "The Maid", "a working woman, help, progress",
   "A working woman or helper. Progress through effort."),
  ("I Deliranti", "The Madmen", "setbacks, confusion, bad influence",
   "Confusion and contradiction. A bad influence stirs things up."),
  ("Il Ladro", "The Thief", "theft, loss, dishonesty",
   "Something is taken. Loss or dishonesty."),
  ("Messaggiere", "The Messenger", "news, communication, a go-between",
   "A messenger or go-between. News arrives."),
  ("Donna Maritata", "The Married Woman", "a wife, a mother, maturity",
   "A married woman, often a mother."),
  ("Mercante", "The Merchant", "work, career, business",
   "A merchant or businessman. Work, career and finances."),
 ],
}

SOURCES: dict[str, str] = {}

cards = []
for suit, (it, en, sym, color, domain) in SUITS.items():
    for i, (title, title_en, kw, meaning) in enumerate(C[suit]):
        cid = f"{suit}_{i+1:02d}"
        cards.append({
            "id": cid, "name": title, "name_en": title_en,
            "arcana": "oracle", "number": i + 1, "suit": suit, "rank": RANKS[i],
            "insert": f"{RANKS[i]}{sym}",
            "keywords": {"upright": kw.split(", ")}, "meaning": {"upright": meaning},
            "image": f"cards/sibilla/{cid}.jpg", "source_url": SOURCES.get(cid, ""),
        })

deck = {
    "id": "sibilla",
    "name": "Vera Sibilla Italiana",
    "short_name": "Sibilla",
    "family": "Oracle",
    "description": "The 52-card Italian sibyl oracle: titled scenes with playing-card indices. Read upright, in combinations.",
    "card_aspect": 0.58,
    "color": 0x9C36B5,
    "reversals": False,
    "spreads": ["single", "line3", "line5", "box9"],
    "suits": {k: {"name": f"{v[0]} ({v[1]})", "color": v[3], "domain": v[4]} for k, v in SUITS.items()},
    "cards": cards,
}
assert len(cards) == 52
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "sibilla.json")
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
