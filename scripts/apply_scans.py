"""Fills in card-image sources (Wikimedia Commons scans) for the decks that have them.

Run after any build_*.py script (a rebuild clears the sources), then run
download_cards.py to fetch the images:

    python3 scripts/apply_scans.py
    python3 scripts/download_cards.py

Every set below is public domain, CC0, or CC BY-SA (credited in CREDITS.md).
"""
import hashlib
import json
import os
import urllib.parse

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def commons_url(filename: str, width: int | None = None) -> str:
    """Direct upload.wikimedia.org URL for a Commons file (SVGs are rendered to PNG)."""
    f = filename.replace(" ", "_")
    h = hashlib.md5(f.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(f, safe="()_,.-'!")
    if f.lower().endswith(".svg"):
        return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width or 960}px-{q}.png"
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"


def marseille():
    """Lequart (Paris) Tarot de Marseille, via Gallica. Public domain."""
    out = {"major_mat": "TT Tarot.png"}
    out.update({f"major_{n:02d}": f"T{n} Tarot.png" for n in range(1, 22)})
    suits = {"B": "batons", "C": "coupes", "S": "epees", "P": "deniers"}
    ranks = {**{str(n): n for n in range(1, 11)}, "J": 11, "H": 12, "Q": 13, "K": 14}
    for s, key in suits.items():
        for r, n in ranks.items():
            out[f"{key}_{n:02d}"] = f"{r}{s} Tarot.png"
    return out


def piemontese():
    """Solesio, Piedmontese tarot, 1865. Public domain."""
    trumps = ["The Fool", "The Magician", "The Popess", "The Empress", "The Emperor", "The Pope", "The Lovers",
              "The Chariot", "Justice", "The Hermit", "Wheel of Fortune", "Strength", "The Hanged Man", "Death",
              "Temperance", "The Devil", "The Tower", "The Stars", "The Moon", "The Sun", "Judgement", "The World"]
    p = "Piedmontese tarot deck - Solesio - 1865 - "
    out = {f"major_{n:02d}": f"{p}Trump - {n:02d} - {t}.jpg" for n, t in enumerate(trumps)}
    suits = {"bastoni": "Batons", "coppe": "Cups", "spade": "Swords", "denari": "Coins"}
    names = {1: "Ace", 11: "Jack", 12: "Knight", 13: "Queen", 14: "King"}
    for key, en in suits.items():
        for n in range(1, 15):
            out[f"{key}_{n:02d}"] = f"{p}{names.get(n, n)} of {en}.jpg"
    return out


def minchiate():
    """Florentine Minchiate, 1860-1890. Public domain."""
    p = "Minchiate card deck - Florence - 1860-1890 - "
    trumps = ["Papa uno", "Papa due", "Papa tre", "Papa quattro", "Papa cinque", "La Temperanza", "La Forza",
              "La Giustizia", "La Ruota della Fortuna", "Il Carro", "Il Gobbo", "L'Impiccato", "La Morte",
              "Il Diavolo", "La Casa del Diavolo", "La Speranza", "La Prudenza", "La Fede", "La Carità", "Il Fuoco",
              "L'Acqua", "La Terra", "L'Aria", "La Bilancia", "La Vergine", "Il Scorpione", "L'Ariete",
              "Il Capricorno", "Il Sagittario", "Il Cancro", "I Pesci", "L'Acquario", "Il Leone", "Il Toro",
              "I Gemelli", "La Stella", "La Luna", "Il Sole", "Il Mondo", "Le Trombe"]
    out = {"t_00": f"{p}Trumps - Il Matto -.jpg"}
    out.update({f"t_{n:02d}": f"{p}Trumps - {n:02d} - {t}.jpg" for n, t in enumerate(trumps, start=1)})
    suits = {"bastoni": "Batons", "coppe": "Cups", "spade": "Swords", "denari": "Coins"}
    courts = {11: "11 - Jack", 12: "12 - Knight", 13: "13 - Queen", 14: "14 - King"}
    for key, en in suits.items():
        for n in range(1, 15):
            out[f"{key}_{n:02d}"] = f"{p}{en} - {courts.get(n, f'{n:02d}')}.jpg"
    return out


def bergamasche():
    """Bergamo deck by Poulpy. CC BY-SA 3.0."""
    suits = {"denari": "Coins", "coppe": "Cups", "spade": "Swords", "bastoni": "Wands"}
    ranks = {1: "Ace", 8: "Jack", 9: "Knight", 10: "King"}
    return {f"{k}_{n:02d}": f"Bergamo Deck - {en} - {ranks.get(n, f'{n:02d}')}.jpg"
            for k, en in suits.items() for n in range(1, 11)}


def bresciane():
    """Brescia deck (SVG) by ZZandro. CC BY-SA 4.0."""
    suits = {"denari": "Denari", "coppe": "Coppe", "spade": "Spade", "bastoni": "Bastoni"}
    ranks = {1: "Asso", 8: "Fante", 9: "Cavallo", 10: "Re"}
    return {f"{k}_{n:02d}": f"{ranks.get(n, f'{n:02d}')}-{it}.svg" for k, it in suits.items() for n in range(1, 11)}


def romagnole():
    """Roman/Romagna pattern (PNG). CC0. The Kings of Batons and Coins are missing on Commons."""
    suits = {"bastoni": ("maczug", "maczugi"), "spade": ("mieczy", "miecze"),
             "denari": ("monet", "monety"), "coppe": ("puszek", "puszki")}
    nums = {2: ("Dwie", "Dwa"), 3: "Trzy", 4: "Cztery", 5: "Pięć", 6: "Sześć", 7: "Siedem"}
    out = {}
    for k, (gen, pl) in suits.items():
        out[f"{k}_01"] = f"As {gen} z wzoru rzymskiego.png"
        for n in range(2, 8):
            word = nums[n]
            if n == 2:
                word = "Dwa" if k == "spade" else "Dwie"
            form = pl if n in (2, 3, 4) else gen
            out[f"{k}_{n:02d}"] = f"{word} {form} z wzoru rzymskiego.png"
        out[f"{k}_08"] = f"Paź {gen} z wzoru rzymskiego.png"
        out[f"{k}_09"] = f"Jeździec {gen} z wzoru rzymskiego.png"
        if k in ("spade", "coppe"):
            out[f"{k}_10"] = f"Król {gen} z wzoru rzymskiego.png"
    return out


def baraja():
    """Heraclio Fournier, 1878 (Basque file names). Public domain."""
    suits = {"oros": "urrea", "copas": "kopa", "espadas": "ezpata", "bastos": "bastoia"}
    ranks = {1: "bateko", 2: "biko", 3: "hiruko", 4: "lauko", 5: "bosteko", 6: "seiko", 7: "zazpiko",
             10: "txota", 11: "zaldi", 12: "errege"}
    return {f"{k}_{n:02d}": f"Fournier 1878 - {r} {eu} (ref. 44470).png"
            for k, eu in suits.items() for n, r in ranks.items()}


def playing_cards():
    """English pattern (SVG) by Dmitry Fomin. CC0."""
    ranks = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"]
    return {f"{s}_{i+1:02d}": f"English pattern {r} of {s}.svg"
            for s in ("hearts", "diamonds", "clubs", "spades") for i, r in enumerate(ranks)}


def hanafuda():
    """Hanafuda (SVG, traditional colours) by Louie Mantia and すけじょ. CC BY-SA 4.0."""
    months = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]
    deck = json.load(open(os.path.join(DATA, "hanafuda.json"), encoding="utf-8"))
    kind = {"bright": "Hikari", "animal": "Tane", "ribbon": "Tanzaku"}
    out, kasu_count = {}, {}
    for c in deck["cards"]:
        m = c["number"]
        if c["rank"] == "plain":
            kasu_count[m] = kasu_count.get(m, 0) + 1
            plains = sum(1 for x in deck["cards"] if x["number"] == m and x["rank"] == "plain")
            label = "Kasu" if plains == 1 else f"Kasu {kasu_count[m]}"
        else:
            label = kind[c["rank"]]
        out[c["id"]] = f"Hanafuda {months[m-1]} {label} Alt.svg"
    return out


def lenormand():
    """Petit Lenormand by W. Reuter, Darmstadt, 19th c. (BnF/Gallica). Public domain.
    All 36 cards; card n is image 2n-1 (each front is followed by its back)."""
    p = "Jeu de cartomancie - jeu de cartes, estampe - btv1b10543188k ({:02d} of 72).jpg"
    return {f"len_{n:02d}": p.format(2 * n - 1) for n in range(1, 37)}


# width / height of each scan set, so cards aren't letterboxed
ASPECT = {"marseille": 0.525, "piemontese": 0.568, "minchiate": 0.597, "bergamasche": 0.545,
          "bresciane": 0.498, "romagnole": 0.534, "playing_cards": 0.667, "hanafuda": 0.61,
          "lenormand": 0.614, "piacentine": 0.645, "bolognese": 0.466, "trevisane": 0.494}

CREDIT = {
    "rws1909": "Waite-Smith Tarot, A. E. Waite & Pamela Colman Smith, 1909. Public domain.",
    "napoletane": "Carte Napoletane scans by Trocche100 (it.wikipedia). Public domain.",
    "lenormand": "Petit Lenormand by W. Reuter, Darmstadt, Bibliothèque nationale de France (Gallica). Public domain.",
    "piacentine": "Piacentine-type deck by Fabbrica Nazionale, Bologna, Bibliothèque nationale de France (Gallica). Public domain.",
    "bolognese": "Tarocchino di Bologna, Bibliothèque nationale de France (Gallica). Public domain.",
    "trevisane": "Venetian (Trevisane) pattern, Bibliothèque nationale de France (Gallica). Public domain.",
    "marseille": "Tarot de Marseille by Lequart (Paris), Bibliothèque nationale de France (Gallica). Public domain.",
    "piemontese": "Piedmontese tarot, Solesio, 1865. Public domain.",
    "minchiate": "Minchiate, Florence, 1860–1890. Public domain.",
    "bergamasche": "Bergamo deck by Poulpy, CC BY-SA 3.0 (Wikimedia Commons).",
    "bresciane": "Brescia deck by ZZandro, CC BY-SA 4.0 (Wikimedia Commons).",
    "romagnole": "Roman/Romagna pattern cards, CC0 (Wikimedia Commons).",
    "baraja": "Heraclio Fournier, 1878. Public domain.",
    "playing_cards": "English pattern playing cards by Dmitry Fomin, CC0 (Wikimedia Commons).",
    "hanafuda": "Hanafuda by Louie Mantia and すけじょ, CC BY-SA 4.0 (Wikimedia Commons).",
}

def piacentine():
    """Piacentine-type pattern by Fabbrica Nazionale, Bologna, 19th c. (BnF/Gallica). Public domain.
    Fronts are the odd-numbered images."""
    p = "Jeu de cartes à enseignes italiennes - estampe - btv1b10535064z ({:02d} of 80).jpg"
    # suit: (Re, Fante, Cavallo, Ace, first pip image) — pips 2..7 follow every other image
    layout = {"denari": (1, 3, 5, 7, 9), "bastoni": (21, 25, 23, 27, 29),
              "spade": (41, 43, 45, 47, 49), "coppe": (61, 63, 65, 67, 69)}
    out = {}
    for suit, (re, fante, cavallo, ace, first) in layout.items():
        out[f"{suit}_10"], out[f"{suit}_08"], out[f"{suit}_09"] = p.format(re), p.format(fante), p.format(cavallo)
        out[f"{suit}_01"] = p.format(ace)
        for n in range(2, 8):
            out[f"{suit}_{n:02d}"] = p.format(first + 2 * (n - 2))
    return out


def bolognese():
    """Tarocchino de Bologne (BnF/Gallica). Public domain. Fronts are odd-numbered;
    the Ace of Coins is the tax-stamp card, as on real Bolognese packs."""
    p = "Tarocchino de Bologne - jeu de cartes, estampe - btv1b105138709 ({:03d} of 126).jpg"
    trumps = {"moro_1": 1, "moro_2": 3, "moro_3": 5, "moro_4": 7, "amore": 9, "carro": 11,
              "temperanza": 13, "giustizia": 15, "forza": 17, "ruota": 19, "tempo": 21, "traditore": 23,
              "morte": 25, "diavolo": 27, "saetta": 29, "stella": 31, "angelo": 33, "sole": 35,
              "luna": 37, "mondo": 39, "bagatto": 41, "matto": 43}
    out = {f"t_{k}": p.format(v) for k, v in trumps.items()}
    # suit: (Ace, Re, Regina, Cavallo, Fante, image of the 6) — 6..10 follow every other image
    layout = {"denari": (45, 47, 49, 51, 53, 55), "coppe": (65, 67, 69, 71, 73, 75),
              "bastoni": (85, 87, 89, 91, 93, 95), "spade": (105, 107, 109, 111, 113, 115)}
    for suit, (ace, re, regina, cavallo, fante, six) in layout.items():
        out[f"{suit}_01"], out[f"{suit}_14"], out[f"{suit}_13"] = p.format(ace), p.format(re), p.format(regina)
        out[f"{suit}_12"], out[f"{suit}_11"] = p.format(cavallo), p.format(fante)
        for n in range(6, 11):
            out[f"{suit}_{n:02d}"] = p.format(six + 2 * (n - 6))
    return out


def trevisane():
    """Venetian (Trevisane) pattern, double-headed, 19th c. (BnF/Gallica). Public domain.
    Each suit is a block of 26 images: Re, Cavallo, Fante, Asso, 2..10, each followed by its back."""
    p = "Jeu de cartes au portrait vénitien à deux têtes - jeu de cartes, estampe - btv1b10520246r ({:03d} of 104).jpg"
    out = {}
    for suit, b in {"coppe": 1, "bastoni": 27, "denari": 53, "spade": 79}.items():
        out[f"{suit}_10"], out[f"{suit}_09"], out[f"{suit}_08"] = p.format(b), p.format(b + 2), p.format(b + 4)
        for n in range(1, 8):
            out[f"{suit}_{n:02d}"] = p.format(b + 6 + 2 * (n - 1))
    return out


RENAMED = {"lenormand": "reuter"}

SETS = {
    "trevisane": trevisane,
    "piacentine": piacentine,
    "bolognese": bolognese,
    "lenormand": lenormand,
    "marseille": marseille, "piemontese": piemontese, "minchiate": minchiate,
    "bergamasche": bergamasche, "bresciane": bresciane, "romagnole": romagnole,
    "baraja": baraja, "playing_cards": playing_cards, "hanafuda": hanafuda,
}

if __name__ == "__main__":
    for deck_id, fn in SETS.items():
        path = os.path.join(DATA, f"{deck_id}.json")
        deck = json.load(open(path, encoding="utf-8"))
        files = fn()
        hit = 0
        for c in deck["cards"]:
            if c["id"] in files:
                c["source_url"] = commons_url(files[c["id"]])
                if deck_id in RENAMED:  # scan set was swapped: new file names force a fresh download
                    c["image"] = f"cards/{deck_id}/{RENAMED[deck_id]}_{c['id']}.jpg"
                hit += 1
        deck["credit"] = CREDIT.get(deck_id, "")
        if deck_id in ASPECT:
            deck["card_aspect"] = ASPECT[deck_id]
        json.dump(deck, open(path, "w"), indent=2, ensure_ascii=False)
        print(f"{deck_id:14} {hit}/{len(deck['cards'])} cards have scans")
    for deck_id in ("rws1909", "napoletane"):  # decks whose sources live in their build scripts
        path = os.path.join(DATA, f"{deck_id}.json")
        deck = json.load(open(path, encoding="utf-8"))
        deck["credit"] = CREDIT[deck_id]
        json.dump(deck, open(path, "w"), indent=2, ensure_ascii=False)
