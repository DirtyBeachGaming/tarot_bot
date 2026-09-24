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
CARD_W, CARD_H = 300, 516          # render size (source scans are ~830x1430)
BG = (24, 20, 31)
BADGE = (212, 175, 55)


async def ensure_image(card: Card, session: aiohttp.ClientSession) -> Path | None:
    """Return the local image path, downloading and caching it on first use."""
    path = card.image_path
    if path.exists():
        return path
    try:
        async with session.get(card.source_url, headers={"User-Agent": USER_AGENT}) as r:
            r.raise_for_status()
            data = await r.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        log.info("Cached %s", path.name)
        return path
    except Exception as e:  # network trouble shouldn't kill a reading
        log.warning("Could not fetch image for %s: %s", card.id, e)
        return None


def _card_img(draw: Draw, size=(CARD_W, CARD_H)) -> Image.Image:
    path = draw.card.image_path
    if path.exists():
        img = Image.open(path).convert("RGB").resize(size, Image.LANCZOS)
    else:  # placeholder if the image couldn't be fetched
        img = Image.new("RGB", size, (60, 50, 70))
        d = ImageDraw.Draw(img)
        d.multiline_text((size[0] // 2, size[1] // 2), draw.card.name.replace(" of ", "\nof "),
                         fill="white", anchor="mm", align="center", font=_font(24))
    if draw.reversed:
        img = img.rotate(180)
    return img


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def single_card_png(draw: Draw) -> io.BytesIO:
    buf = io.BytesIO()
    _card_img(draw, (600, 1032)).save(buf, "PNG")
    buf.seek(0)
    return buf


def render_spread(spread: Spread, draws: list[Draw]) -> io.BytesIO:
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
        img = _card_img(d)
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
