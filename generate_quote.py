"""Render today's quote as assets/quote.png (Africa/Windhoek date picks the quote)."""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
NAVY = (11, 25, 48)
NAVY_LIGHT = (20, 40, 72)
GOLD = (201, 162, 77)
IVORY = (244, 239, 227)
MUTED = (165, 176, 196)

W = 1120          # 2x of the 560px signature width
PAD_X = 64
BAR_W = 8


def font(path, size, weight=None):
    f = ImageFont.truetype(str(ROOT / "fonts" / path), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight] if "Playfair" in path else [14, weight])
        except Exception:
            pass
    return f


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def pick(quotes, today=None):
    day = today or datetime.now(ZoneInfo("Africa/Windhoek")).date()
    return quotes[day.toordinal() % len(quotes)], day


def render(quote, out):
    quote_font = font("PlayfairDisplay-Italic.ttf", 40, 500)
    attr_font = font("Inter.ttf", 22, 600)
    mark_font = font("PlayfairDisplay-Italic.ttf", 150, 700)

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    text_w = W - PAD_X * 2 - BAR_W - 60
    lines = wrap(probe, quote["q"], quote_font, text_w)
    line_h = 56
    height = 52 + len(lines) * line_h + 24 + 34 + 48

    img = Image.new("RGB", (W, height), NAVY)
    # soft vertical gradient
    px = img.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        c = tuple(int(NAVY[i] + (NAVY_LIGHT[i] - NAVY[i]) * t * 0.6) for i in range(3))
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, BAR_W, height), fill=GOLD)
    d.text((PAD_X - 8, 6), "“", font=mark_font, fill=(201, 162, 77))

    x = PAD_X + 92
    y = 52
    for ln in lines:
        d.text((x, y), ln, font=quote_font, fill=IVORY)
        y += line_h
    y += 24
    d.line((x, y + 14, x + 44, y + 14), fill=GOLD, width=3)
    d.text((x + 64, y), quote["a"].upper(), font=attr_font, fill=GOLD, spacing=2)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return img.size


if __name__ == "__main__":
    quotes = json.loads((ROOT / "quotes.json").read_text(encoding="utf-8"))
    chosen, day = pick(quotes)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        chosen = quotes[int(sys.argv[1]) % len(quotes)]
    size = render(chosen, ROOT / "assets" / "quote.png")
    print(day, size, chosen["a"])
