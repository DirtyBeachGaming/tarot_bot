"""Builds data/rws1909.json — the Waite-Smith 1909 deck database."""
import hashlib, json

def commons_url(filename):
    f = filename.replace(" ", "_")
    h = hashlib.md5(f.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{f}"

# name, upright keywords, reversed keywords, upright meaning, reversed meaning
MAJORS = [
 ("The Fool", "beginnings, spontaneity, faith, freedom", "recklessness, naivety, hesitation, risk",
  "A leap into the unknown. Trust the journey and begin without needing every answer.",
  "Carelessness or fear of the leap. Look before you jump, or notice what is holding you back."),
 ("The Magician", "will, skill, manifestation, resourcefulness", "manipulation, untapped talent, trickery",
  "Everything you need is on the table. Focus your will and make it real.",
  "Power misdirected or unused. Beware of deception, including self-deception."),
 ("The High Priestess", "intuition, mystery, the unconscious, inner knowing", "secrets, disconnection, surface thinking",
  "Be still and listen. The answer is known inwardly before it can be spoken.",
  "Ignoring your intuition, or hidden agendas coming to the surface."),
 ("The Empress", "abundance, nurture, fertility, sensuality", "dependence, smothering, creative block",
  "Growth, comfort and creative fullness. Tend what you love and it flourishes.",
  "Neglect of self or over-giving to others. Creative energy feels stuck."),
 ("The Emperor", "structure, authority, stability, leadership", "rigidity, control, domination",
  "Order and firm foundations. Take charge and build something lasting.",
  "Control turned tyrannical, or a lack of discipline where it's needed."),
 ("The Hierophant", "tradition, teaching, institutions, belief", "rebellion, unorthodoxy, personal path",
  "Wisdom through tradition, mentors and shared belief. Learn the rules well.",
  "Breaking from convention. Question the doctrine and find your own way."),
 ("The Lovers", "love, union, choice, alignment of values", "imbalance, disharmony, misaligned choices",
  "A meaningful union or a choice that defines who you are. Choose with the heart and values aligned.",
  "Conflict in a relationship or within yourself. Values and actions are out of step."),
 ("The Chariot", "willpower, victory, direction, control", "scattered force, lack of direction, aggression",
  "Opposing forces held in check. Drive forward with determination and you win.",
  "Losing control of the reins. Momentum without direction."),
 ("Strength", "courage, compassion, patience, inner strength", "self-doubt, weakness, raw emotion",
  "Gentle mastery. Quiet courage tames what force cannot.",
  "Doubt or being overwhelmed by impulses. Reconnect with your inner steadiness."),
 ("The Hermit", "solitude, introspection, guidance, search for truth", "isolation, loneliness, withdrawal",
  "Step back from the noise. The lantern you carry lights the way inward.",
  "Retreat has become isolation. Time to return to others."),
 ("Wheel of Fortune", "cycles, fate, turning points, luck", "bad luck, resistance to change, stagnation",
  "The wheel turns. A shift in fortune arrives; ride the cycle rather than fight it.",
  "A downturn or clinging to what's passing. What goes down comes back up."),
 ("Justice", "fairness, truth, cause and effect, law", "unfairness, dishonesty, avoidance of accountability",
  "Clear judgment and consequences earned. Act with integrity; the scales balance.",
  "Injustice, bias, or dodging responsibility. Something needs to be made right."),
 ("The Hanged Man", "surrender, pause, new perspective, sacrifice", "stalling, resistance, needless sacrifice",
  "Suspend action. Seeing the world upside down reveals what you missed.",
  "Delay without purpose, or refusing to let go."),
 ("Death", "endings, transformation, transition, release", "resistance to change, stagnation, fear of endings",
  "Something ends so something new can begin. Clear the ground.",
  "Holding onto what's already over. Change is delayed but not avoided."),
 ("Temperance", "balance, moderation, patience, synthesis", "excess, imbalance, impatience",
  "Blend opposites slowly. Patience and measure produce something new.",
  "Too much of something. Restore balance before continuing."),
 ("The Devil", "bondage, temptation, materialism, shadow", "release, breaking free, reclaiming power",
  "Chains of habit, desire or fear. Notice they're loose enough to remove.",
  "Breaking free from what bound you. Facing the shadow."),
 ("The Tower", "upheaval, sudden change, revelation, collapse", "averted disaster, fear of change, delayed collapse",
  "What was built on false ground falls. Painful, but it clears the way for truth.",
  "Avoiding a necessary collapse, or an upheaval felt internally."),
 ("The Star", "hope, renewal, inspiration, serenity", "despair, disconnection, lost faith",
  "After the storm, calm and hope. Healing and guidance are here.",
  "Hope feels distant. Reconnect with what inspires you."),
 ("The Moon", "illusion, dreams, intuition, uncertainty", "clarity emerging, released fear, confusion lifting",
  "Things are not what they seem. Move carefully and trust instinct over appearances.",
  "Illusions dissolve and fears lose their grip."),
 ("The Sun", "joy, success, vitality, clarity", "temporary clouds, dimmed joy, overconfidence",
  "Warmth, success and simple happiness. Everything is illuminated.",
  "Joy is present but muted. The sun is behind a cloud, not gone."),
 ("Judgement", "awakening, reckoning, calling, rebirth", "self-doubt, ignoring the call, harsh self-judgment",
  "A call to rise. Reckon with the past and answer who you're meant to be.",
  "Refusing the call or judging yourself too harshly."),
 ("The World", "completion, wholeness, fulfilment, travel", "incompletion, shortcuts, lack of closure",
  "A cycle completes. Celebrate integration and the arrival of a goal.",
  "Almost there. Tie up loose ends before moving on."),
]

SUITS = {
 "wands":     {"name": "Wands",     "element": "fire",  "color": 0xD9480F, "domain": "will, passion, creativity, action"},
 "cups":      {"name": "Cups",      "element": "water", "color": 0x1971C2, "domain": "emotion, love, relationships, intuition"},
 "swords":    {"name": "Swords",    "element": "air",   "color": 0xADB5BD, "domain": "thought, conflict, truth, communication"},
 "pentacles": {"name": "Pentacles", "element": "earth", "color": 0x2B8A3E, "domain": "money, work, body, material world"},
}
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
         "Page", "Knight", "Queen", "King"]

MINORS = {
 "wands": [
  ("inspiration, spark, new venture", "delays, lack of motivation", "A creative spark or new passion is offered. Grab it.", "The spark is there but won't catch. Energy blocked or misdirected."),
  ("planning, future vision, decisions", "fear of the unknown, poor planning", "The world in your hand. Plan your next move beyond familiar ground.", "Playing it safe or hesitating to leave comfort."),
  ("expansion, foresight, ships coming in", "obstacles, delays, frustration", "Your efforts are underway and horizons widen. Look ahead.", "Plans stall. Expect delays and reassess."),
  ("celebration, home, harmony, milestone", "transition, instability at home", "A joyful milestone. Celebrate with community and home.", "Harmony disrupted or a celebration postponed."),
  ("competition, conflict, rivalry", "avoiding conflict, resolution", "Clashing egos and scrappy competition. Test your mettle.", "Conflict winds down, or tension is suppressed."),
  ("victory, recognition, success", "ego, fall from grace, lack of recognition", "Public victory and recognition. Ride proudly.", "Success feels hollow, or recognition is withheld."),
  ("defence, perseverance, standing ground", "overwhelm, giving up", "Hold your position against challengers. You have the high ground.", "Worn down by opposition. Choose your battles."),
  ("speed, movement, swift news", "delays, frustration, slowing down", "Things move fast. Messages, travel and momentum.", "Momentum stalls or rushes out of control."),
  ("resilience, persistence, last stand", "exhaustion, paranoia", "Battered but standing. One more push.", "Defensiveness has become exhaustion. Rest."),
  ("burden, responsibility, overwork", "release, delegation", "Carrying too much. The goal is near but the load is heavy.", "Putting down what isn't yours to carry."),
  ("curiosity, discovery, enthusiastic news", "hasty ideas, immaturity", "A fresh, adventurous message or idea. Explore it.", "Enthusiasm without follow-through."),
  ("energy, adventure, impulsiveness", "haste, frustration, scattered energy", "Charging ahead with passion. Bold action.", "Recklessness or restlessness burning out."),
  ("confidence, warmth, determination", "jealousy, insecurity, demanding", "Magnetic, vibrant and self-assured. Lead with warmth.", "Confidence turned to insecurity or possessiveness."),
  ("vision, leadership, entrepreneurship", "impulsiveness, overbearing, high expectations", "Bold vision and natural leadership. Make it happen.", "Leadership becomes domineering or rash."),
 ],
 "cups": [
  ("new love, compassion, emotional opening", "blocked emotions, emptiness", "The heart overflows. New love, feeling or creativity begins.", "Emotions held back or a love left unexpressed."),
  ("partnership, mutual attraction, union", "imbalance, broken communication", "A meeting of equals. Connection and mutual respect.", "Disharmony or a partnership out of balance."),
  ("friendship, celebration, community", "overindulgence, gossip, isolation", "Raise a glass with friends. Joy shared.", "Too much of a good thing, or feeling left out."),
  ("apathy, contemplation, reevaluation", "new awareness, acceptance of offers", "Bored with what's offered, missing the cup being handed to you.", "Waking from apathy. Seizing an opportunity."),
  ("loss, grief, regret", "acceptance, moving on, forgiveness", "Mourning what spilled. Two cups still stand behind you.", "Turning toward what remains. Healing begins."),
  ("nostalgia, innocence, childhood memories", "stuck in the past, idealising", "A sweet memory or a gift from the past. Innocence.", "Living in the past instead of the present."),
  ("choices, fantasy, illusion", "clarity, focus, reality check", "Many dazzling options, not all real. Discern.", "Fantasies fade and a real choice emerges."),
  ("walking away, disillusionment, seeking more", "fear of change, aimless drifting", "Leaving behind what no longer fulfils, to seek something deeper.", "Afraid to leave, or leaving without purpose."),
  ("contentment, wishes fulfilled, satisfaction", "smugness, dissatisfaction", "The wish card. Satisfaction and pleasure.", "Material satisfaction that doesn't reach the heart."),
  ("harmony, family, emotional fulfilment", "broken home, misaligned values", "Lasting happiness and harmony at home.", "Discord in the family or unmet ideals."),
  ("creative message, intuition, emotional curiosity", "emotional immaturity, blocked creativity", "A surprising message of feeling or a creative idea.", "Moodiness or ignoring your creative voice."),
  ("romance, charm, following the heart", "moodiness, unrealistic ideals", "An offer of love or beauty arrives. The romantic.", "Charm without substance. Promises unkept."),
  ("compassion, emotional security, intuition", "codependence, emotional overwhelm", "Deep empathy and emotional wisdom. Care for others and self.", "Drowning in others' feelings. Set boundaries."),
  ("emotional balance, diplomacy, calm", "volatility, manipulation, coldness", "Calm mastery of feeling. Steady in rough seas.", "Suppressed emotion or emotional manipulation."),
 ],
 "swords": [
  ("clarity, breakthrough, truth", "confusion, misused power", "A sharp new idea cuts through the fog. Speak truth.", "Clouded thinking or harsh words."),
  ("stalemate, difficult choice, avoidance", "information revealed, indecision ends", "Blindfolded between two options. Avoiding the choice.", "The blindfold comes off. Time to decide."),
  ("heartbreak, sorrow, grief", "recovery, releasing pain", "Painful truth pierces the heart.", "The wound begins to heal. Letting go of sorrow."),
  ("rest, recovery, contemplation", "restlessness, burnout", "Lay down your sword. Rest and restore.", "Refusing rest until burnout forces it."),
  ("conflict, hollow victory, defeat", "reconciliation, making amends", "Winning at a cost. Was the fight worth it?", "Ending the conflict. Moving past resentment."),
  ("transition, moving on, passage", "unfinished business, resistance", "Leaving troubled waters for calmer shores.", "Carrying baggage along, or unable to leave."),
  ("deception, strategy, stealth", "confession, conscience, getting caught", "Someone is getting away with something. Be strategic, or be wary.", "Secrets come out. Coming clean."),
  ("restriction, feeling trapped, victim mindset", "release, new perspective", "Bound by your own thoughts. The ties are looser than they seem.", "Stepping free of self-imposed limits."),
  ("anxiety, worry, nightmares", "hope, reaching out, releasing worry", "Sleepless fear. The mind magnifies the danger.", "The worst of the worry passes. Share it."),
  ("rock bottom, painful ending, betrayal", "recovery, regeneration", "It can't get worse. Dawn is on the horizon.", "Rising from the lowest point."),
  ("curiosity, vigilance, new ideas", "gossip, all talk, hastiness", "Alert and eager for truth. Ask questions.", "Talk without action, or spreading rumours."),
  ("ambition, drive, fast thinking", "rashness, aggression, burnout", "Charging headlong into battle for an idea.", "Impulsive or combative in ways that backfire."),
  ("clear boundaries, independence, honesty", "coldness, bitterness", "Sharp perception and honest words, earned through experience.", "Cruelty in place of clarity."),
  ("intellect, authority, truth", "manipulation, abuse of power", "Clear-headed judgment and principled authority.", "Cold, manipulative logic."),
 ],
 "pentacles": [
  ("opportunity, prosperity, new venture", "missed opportunity, poor planning", "A tangible opportunity for wealth or health is offered.", "An opportunity slips through your fingers."),
  ("balance, adaptability, juggling", "overwhelm, disorganisation", "Keeping many things in motion. Flexibility.", "Dropping the ball. Too much at once."),
  ("teamwork, craftsmanship, collaboration", "lack of teamwork, mediocrity", "Skilled work recognised. Collaboration builds something real.", "Disharmony on the team or careless work."),
  ("security, saving, control", "greed, over-attachment, spending", "Holding on tightly to what you have.", "Loosening your grip, or clinging too hard."),
  ("hardship, poverty, isolation", "recovery, help arrives", "Out in the cold. Help is closer than you think.", "Recovering from hard times."),
  ("generosity, charity, sharing", "debt, strings attached", "Giving and receiving in balance.", "Generosity with an agenda, or imbalance of power."),
  ("patience, investment, long-term view", "impatience, poor returns", "Pause to assess the harvest. Growth takes time.", "Frustration with slow results."),
  ("diligence, mastery, skill-building", "perfectionism, lack of focus", "Head down, honing your craft.", "Work without meaning, or cutting corners."),
  ("independence, luxury, self-sufficiency", "overwork, hollow success", "Enjoying the fruits of your labour in comfort.", "Wealth without fulfilment."),
  ("legacy, inheritance, family wealth", "financial loss, family disputes", "Lasting security and a legacy for generations.", "Disputes over money or legacy."),
  ("ambition, study, manifestation", "procrastination, lack of progress", "A student with a new plan or opportunity. Study it.", "Daydreaming without doing."),
  ("hard work, routine, reliability", "stagnation, boredom, laziness", "Slow, steady and dependable. Keep ploughing.", "Stuck in a rut."),
  ("nurturing, practicality, security", "self-neglect, work-home imbalance", "Grounded care for home, body and finances.", "Neglecting yourself while caring for everything else."),
  ("abundance, security, leadership", "greed, stubbornness, materialism", "Mastery of the material world. Prosperity and stability.", "Obsessed with wealth and status."),
 ],
}

cards = []
for i, (name, ku, kr, up, rev) in enumerate(MAJORS):
    src = f"RWS1909 - {i:02d} {name.replace('The ', '')}.jpeg"
    cards.append({
        "id": f"major_{i:02d}", "name": name, "arcana": "major", "number": i,
        "suit": None, "rank": None,
        "keywords": {"upright": ku.split(", "), "reversed": kr.split(", ")},
        "meaning": {"upright": up, "reversed": rev},
        "image": f"cards/rws1909/major_{i:02d}.jpg",
        "source_url": commons_url(src),
    })
for suit, rows in MINORS.items():
    assert len(rows) == 14, suit
    for n, (ku, kr, up, rev) in enumerate(rows, start=1):
        src = f"RWS1909 - {suit.title()} {n:02d}.jpeg"
        cards.append({
            "id": f"{suit}_{n:02d}", "name": f"{RANKS[n-1]} of {suit.title()}", "arcana": "minor",
            "number": n, "suit": suit, "rank": RANKS[n-1],
            "keywords": {"upright": ku.split(", "), "reversed": kr.split(", ")},
            "meaning": {"upright": up, "reversed": rev},
            "image": f"cards/rws1909/{suit}_{n:02d}.jpg",
            "source_url": commons_url(src),
        })

deck = {
    "id": "rws1909",
    "name": "Waite-Smith Tarot (1909)",
    "short_name": "Waite-Smith",
    "family": "Tarot",
    "card_aspect": 830 / 1430,
    "color": 0x6A4C93,
    "description": "Arthur Edward Waite and Pamela Colman Smith, first edition ('Roses & Lilies'). Public domain.",
    "source": "https://commons.wikimedia.org/wiki/Category:Rider-Waite_tarot_deck_(Roses_%26_Lilies)",
    "back_image": None,
    "suits": SUITS,
    "cards": cards,
}
assert len(cards) == 78
import os, sys
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "rws1909.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(deck, open(out, "w"), indent=2, ensure_ascii=False)
print("wrote", out, len(cards), "cards")
