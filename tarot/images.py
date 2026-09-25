"""Card image fetching/caching and spread rendering."""
from __future__ import annotations

import io
import logging
from pathlib import Path

import aiohttp
from PIL import Image, ImageDraw, ImageFont

from .deck import Card, Draw
from .spreads import Spread

log = logging.getLogger(__name__)

USER_AGENT = "TarotDiscordBot/1.0 (https://github.com/DirtyBeachGaming/tarot_bot) aiohttp"
CARD_W = 300                       # render width; height follows each deck's card shape
BG = (24, 20, 31)
BADGE = (212, 175, 55)


def shrink_image(data: bytes, max_h: int = 1000) -> bytes:
    """Re-encode a downloaded scan as a JPEG no taller than max_h (keeps the repo small)."""
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    img = img.convert("RGB")
    if img.height > max_h:
        img = img.resize((round(img.width * max_h / img.height), max_h), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, "JPEG", quality=85, optimize=True)
    return out.getvalue()


async def ensure_image(card: Card, session: aiohttp.ClientSession) -> Path | None:
    """Return the local image path, downloading and caching it on first use."""
    path = card.image_path
    if path.exists():
        return path
    if not card.source_url:  # no scan yet: a drawn placeholder card is used
        return None
    try:
        async with session.get(card.source_url, headers={"User-Agent": USER_AGENT}) as r:
            r.raise_for_status()
            data = await r.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shrink_image(data))
        log.info("Cached %s", path.name)
        return path
    except Exception as e:  # network trouble shouldn't kill a reading
        log.warning("Could not fetch image for %s: %s", card.id, e)
        return None


def _card_img(draw: Draw, size: tuple[int, int]) -> Image.Image:
    path = draw.card.image_path
    if path.exists():
        img = _fit_image(Image.open(path).convert("RGB"), size)
    else:  # no scan: draw a simple cream card with number, name and insert
        img = _text_card(draw.card, size)
    if draw.reversed:
        img = img.rotate(180)
    return img


def _fit_image(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Scale a scan to fit the card slot without stretching (small margins if shapes differ)."""
    w, h = size
    if abs(img.width / img.height - w / h) < 0.02:
        return img.resize(size, Image.LANCZOS)
    scale = min(w / img.width, h / img.height)
    inner = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGB", size, BG)
    canvas.paste(inner, ((w - inner.width) // 2, (h - inner.height) // 2))
    return canvas


def _text_card(card: Card, size: tuple[int, int]) -> Image.Image:
    w, h = size
    s = w / 300
    img = Image.new("RGB", size, (243, 234, 214))
    d = ImageDraw.Draw(img)
    ink, accent = (58, 42, 30), (140, 109, 70)
    d.rectangle((6 * s, 6 * s, w - 6 * s, h - 6 * s), outline=accent, width=max(2, int(3 * s)))
    d.rectangle((14 * s, 14 * s, w - 14 * s, h - 14 * s), outline=accent, width=max(1, int(1 * s)))
    if card.arcana == "rune":
        return _rune_card(card, size)
    if card.arcana == "ogham":
        return _ogham_card(card, size)
    if card.arcana == "geomancy":
        return _geomancy_card(card, size)
    subtitle = None
    if card.arcana == "trump":            # Tarock/Marseille: roman numeral on top, title in the middle
        top = "★" if card.rank in ("Sküs", "★") else card.rank
        name = card.name.split(" · ", 1)[-1]
        if card.name_en and card.name_en != name:
            subtitle = card.name_en
    else:
        top = str(card.number) if card.arcana == "lenormand" or (card.arcana == "oracle" and not card.insert) else ""
        name = card.name
        if card.arcana == "oracle" and card.name_en:
            subtitle = card.name_en
    if top == "★":
        _star(d, w / 2, 50 * s, 16 * s, accent)
    elif top:
        d.text((w / 2, 50 * s), top, fill=accent, anchor="mm", font=_font(int(34 * s)))
    box_w = w - 44 * s
    title_lines, title_font = _fit(d, name, box_w, int(40 * s), max_lines=3)
    blocks = [(title_lines, title_font, ink)]
    if subtitle:
        sub_lines, sub_font = _fit(d, subtitle, box_w, int(24 * s), max_lines=3)
        blocks.append((sub_lines, sub_font, accent))
    heights = [len(ls) * f.size * 1.25 for ls, f, _ in blocks]
    gap = 18 * s
    y = h / 2 - (sum(heights) + gap * (len(blocks) - 1)) / 2
    for (ls, f, colour), bh in zip(blocks, heights):
        for i, line in enumerate(ls):
            d.text((w / 2, y + (i + 0.5) * f.size * 1.25), line, fill=colour, anchor="mm", font=f)
        y += bh + gap
    if card.insert:
        rank, suit = card.insert[:-1], card.insert[-1]
        colour = (170, 40, 40) if suit in "♥♦" else ink
        y = h - 62 * s
        d.text((w / 2 - 6 * s, y), rank, fill=colour, anchor="rm", font=_font(int(34 * s)))
        _suit_shape(d, suit, w / 2 + 18 * s, y, 13 * s, colour)
    return img


# Elder Futhark runes as strokes on a 2 x 4 grid (x right, y down)
RUNE_STROKES = {
    "Fehu": [[(0, 0), (0, 4)], [(0, 1.2), (1.6, 0.1)], [(0, 2.2), (1.6, 1.1)]],
    "Uruz": [[(0, 4), (0, 0), (1.6, 1.3), (1.6, 4)]],
    "Thurisaz": [[(0, 0), (0, 4)], [(0, 1), (1.3, 2), (0, 3)]],
    "Ansuz": [[(0, 0), (0, 4)], [(0, 0), (1.4, 1)], [(0, 1), (1.4, 2)]],
    "Raidho": [[(0, 4), (0, 0), (1.3, 1), (0, 2), (1.4, 4)]],
    "Kenaz": [[(1.3, 0.8), (0, 2), (1.3, 3.2)]],
    "Gebo": [[(0, 0.5), (2, 3.5)], [(2, 0.5), (0, 3.5)]],
    "Wunjo": [[(0, 0), (0, 4)], [(0, 0), (1.3, 1), (0, 2)]],
    "Hagalaz": [[(0, 0), (0, 4)], [(1.6, 0), (1.6, 4)], [(0, 1.5), (1.6, 2.5)]],
    "Nauthiz": [[(0.8, 0), (0.8, 4)], [(0, 1.5), (1.6, 2.5)]],
    "Isa": [[(0, 0), (0, 4)]],
    "Jera": [[(0.9, 0.6), (0, 1.6), (0.9, 2.6)], [(1.1, 1.4), (2, 2.4), (1.1, 3.4)]],
    "Eihwaz": [[(1.7, 0.8), (1, 0), (1, 4), (0.3, 3.2)]],
    "Perthro": [[(1.6, 0.3), (1.2, 1), (0, 0), (0, 4), (1.2, 3), (1.6, 3.7)]],
    "Algiz": [[(1, 0), (1, 4)], [(0, 0.6), (1, 1.8), (2, 0.6)]],
    "Sowilo": [[(1.4, 0), (0.4, 1.6), (1.6, 2.4), (0.6, 4)]],
    "Tiwaz": [[(1, 0), (1, 4)], [(0, 1.1), (1, 0), (2, 1.1)]],
    "Berkano": [[(0, 0), (0, 4)], [(0, 0), (1.3, 1), (0, 2), (1.3, 3), (0, 4)]],
    "Ehwaz": [[(0, 4), (0, 0), (1, 1.2), (2, 0), (2, 4)]],
    "Mannaz": [[(0, 4), (0, 0), (2, 2)], [(2, 4), (2, 0), (0, 2)]],
    "Laguz": [[(0, 4), (0, 0), (1.3, 1)]],
    "Ingwaz": [[(1, 0.8), (2, 2), (1, 3.2), (0, 2), (1, 0.8)]],
    "Dagaz": [[(0, 0.5), (0, 3.5), (2, 0.5), (2, 3.5), (0, 0.5)]],
    "Othala": [[(0.3, 3.7), (1.8, 1.4), (1, 0.2), (0.2, 1.4), (1.7, 3.7)]],
}


def _rune_card(card: Card, size: tuple[int, int]) -> Image.Image:
    """A dark stone with the rune cut into it and its name underneath."""
    w, h = size
    s = w / 300
    img = Image.new("RGB", size, (24, 20, 31))
    d = ImageDraw.Draw(img)
    stone, groove, ink = (92, 88, 84), (214, 178, 94), (225, 220, 210)
    d.rounded_rectangle((12 * s, 12 * s, w - 12 * s, h - 12 * s), radius=int(60 * s), fill=stone,
                        outline=(120, 115, 110), width=max(2, int(3 * s)))
    strokes = RUNE_STROKES.get(card.rank, [])
    if strokes:
        xs = [x for st in strokes for x, _ in st]
        unit = 38 * s
        glyph_w = (max(xs) - min(xs)) * unit
        ox = w / 2 - glyph_w / 2 - min(xs) * unit
        oy = h * 0.42 - 2 * unit
        for st in strokes:
            d.line([(ox + x * unit, oy + y * unit) for x, y in st], fill=groove,
                   width=max(3, int(11 * s)), joint="curve")
    d.text((w / 2, h - 58 * s), card.rank, fill=ink, anchor="mm", font=_font(int(30 * s)))
    return img


def _fit(d: ImageDraw.ImageDraw, text: str, max_w: float, size: int, max_lines: int = 3):
    """Word-wrap text to max_w, shrinking the font until it fits in max_lines."""
    while True:
        font = _font(size)
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if d.textlength(trial, font=font) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
        too_wide = any(d.textlength(l, font=font) > max_w for l in lines)
        if (len(lines) <= max_lines and not too_wide) or size <= 12:
            return lines, font
        size -= 2


def _ogham_card(card: Card, size: tuple[int, int]) -> Image.Image:
    """A wooden stave with the letter cut across its stem line (read bottom to top)."""
    w, h = size
    s = w / 300
    img = Image.new("RGB", size, (24, 20, 31))
    d = ImageDraw.Draw(img)
    wood, cut, ink = (120, 86, 52), (238, 214, 160), (245, 236, 215)
    d.rounded_rectangle((70 * s, 14 * s, w - 70 * s, h - 14 * s), radius=int(30 * s), fill=wood)
    cx, top, bottom = w / 2, h * 0.14, h * 0.70
    d.line((cx, top, cx, bottom), fill=cut, width=max(3, int(6 * s)))
    n, group = int(card.rank), card.suit
    step, reach = 30 * s, 48 * s
    y0 = (top + bottom) / 2 + (n - 1) * step / 2
    for i in range(n):
        y = y0 - i * step
        if group == "B":
            d.line((cx, y, cx + reach, y), fill=cut, width=max(3, int(7 * s)))
        elif group == "H":
            d.line((cx - reach, y, cx, y), fill=cut, width=max(3, int(7 * s)))
        elif group == "M":
            d.line((cx - reach, y + 14 * s, cx + reach, y - 14 * s), fill=cut, width=max(3, int(7 * s)))
        else:  # vowels: short notches across the stem
            d.line((cx - 16 * s, y, cx + 16 * s, y), fill=cut, width=max(4, int(10 * s)))
    d.text((w / 2, h * 0.80), card.name, fill=ink, anchor="mm", font=_font(int(28 * s)))
    d.text((w / 2, h * 0.87), card.name_en or "", fill=cut, anchor="mm", font=_font(int(20 * s)))
    return img


def _geomancy_card(card: Card, size: tuple[int, int]) -> Image.Image:
    """Four rows of one or two dots, as drawn in sand."""
    w, h = size
    s = w / 300
    img = Image.new("RGB", size, (214, 190, 150))
    d = ImageDraw.Draw(img)
    ink, accent = (58, 42, 30), (120, 90, 60)
    d.rectangle((8 * s, 8 * s, w - 8 * s, h - 8 * s), outline=accent, width=max(2, int(3 * s)))
    r = 17 * s
    for i, ch in enumerate(card.rank):
        y = h * 0.14 + i * 62 * s
        xs = [w / 2] if ch == "1" else [w / 2 - 40 * s, w / 2 + 40 * s]
        for x in xs:
            d.ellipse((x - r, y - r, x + r, y + r), fill=ink)
    lines, f = _fit(d, card.name, w - 40 * s, int(30 * s), max_lines=2)
    y = h * 0.74
    for line in lines:
        d.text((w / 2, y), line, fill=ink, anchor="mm", font=f)
        y += f.size * 1.2
    d.text((w / 2, y + 6 * s), card.name_en or "", fill=accent, anchor="mm", font=_font(int(20 * s)))
    return img


def _star(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill):
    import math
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.sin(i * math.pi / 5),
            cy - (r if i % 2 == 0 else r * 0.45) * math.cos(i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=fill)


def _suit_shape(d: ImageDraw.ImageDraw, suit: str, cx: float, cy: float, r: float, fill):
    """Draw a card suit as vector shapes (the default font has no suit glyphs)."""
    if suit == "♦":
        d.polygon([(cx, cy - r * 1.3), (cx + r, cy), (cx, cy + r * 1.3), (cx - r, cy)], fill=fill)
    elif suit in "♥♠":
        k = 1 if suit == "♥" else -1          # spade = upside-down heart + stem
        lobe = r * 0.55
        for dx in (-lobe, lobe):
            ly = cy - k * r * 0.35
            d.ellipse((cx + dx - lobe, ly - lobe, cx + dx + lobe, ly + lobe), fill=fill)
        d.polygon([(cx - r * 1.08, cy - k * r * 0.2), (cx + r * 1.08, cy - k * r * 0.2),
                   (cx, cy + k * r * 1.1)], fill=fill)
        if suit == "♠":
            d.polygon([(cx, cy + r * 0.3), (cx - r * 0.45, cy + r * 1.2), (cx + r * 0.45, cy + r * 1.2)], fill=fill)
    elif suit == "♣":
        lobe = r * 0.5
        for dx, dy in ((0, -r * 0.55), (-r * 0.55, r * 0.15), (r * 0.55, r * 0.15)):
            d.ellipse((cx + dx - lobe, cy + dy - lobe, cx + dx + lobe, cy + dy + lobe), fill=fill)
        d.polygon([(cx, cy), (cx - r * 0.45, cy + r * 1.2), (cx + r * 0.45, cy + r * 1.2)], fill=fill)


FONT_PATH = Path(__file__).resolve().parent.parent / "fonts" / "DejaVuSerif.ttf"


def _font(size: int):
    try:  # bundled font: covers accents like ü and é
        return ImageFont.truetype(str(FONT_PATH), size)
    except OSError:
        pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def single_card_png(draw: Draw, aspect: float) -> io.BytesIO:
    buf = io.BytesIO()
    _card_img(draw, (600, round(600 / aspect))).save(buf, "PNG")
    buf.seek(0)
    return buf


def render_spread(spread: Spread, draws: list[Draw], aspect: float) -> io.BytesIO:
    CARD_W = 300 if spread.size <= 12 else 170   # smaller cards for big layouts
    CARD_H = round(CARD_W / aspect)
    has_cross = any(p.cross for p in spread.positions)
    gap_x = int(CARD_W * (0.45 if has_cross else 0.08))
    gap_y = int(CARD_H * 0.06)
    pad = 40
    unit_x, unit_y = CARD_W + gap_x, CARD_H + gap_y

    max_x = max(p.x for p in spread.positions)
    max_y = max(p.y for p in spread.positions)
    width = int(pad * 2 + max_x * unit_x + CARD_W)
    height = int(pad * 2 + max_y * unit_y + CARD_H)
    canvas = Image.new("RGB", (width, height), BG)
    dc = ImageDraw.Draw(canvas)
    font = _font(26)

    for i, (pos, d) in enumerate(zip(spread.positions, draws), start=1):
        img = _card_img(d, (CARD_W, CARD_H))
        cx = pad + pos.x * unit_x + CARD_W / 2
        cy = pad + pos.y * unit_y + CARD_H / 2
        if pos.cross:
            img = img.rotate(90, expand=True)
        w, h = img.size
        left, top = int(cx - w / 2), int(cy - h / 2)
        canvas.paste(img, (left, top))
        if spread.size > 1:  # numbered badge so the image matches the text
            bx, by = left + 26, top + 26
            dc.ellipse((bx - 20, by - 20, bx + 20, by + 20), fill=BADGE, outline=BG, width=3)
            dc.text((bx, by), str(i), fill=BG, anchor="mm", font=font)

    buf = io.BytesIO()
    canvas.save(buf, "PNG", optimize=True)
    buf.seek(0)
    return buf
