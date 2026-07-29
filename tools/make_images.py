#!/usr/bin/env python3
"""Authoring tool: renders OG images (1200x630 per locale), favicon.ico and
apple-touch-icon.png with Pillow. Outputs are committed; re-run only when the
claim texts or branding change."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OG_DIR = os.path.join(ROOT, "assets", "og")
os.makedirs(OG_DIR, exist_ok=True)

PINE = (30, 90, 60)
PINE_DEEP = (20, 61, 40)
CREAM = (250, 246, 236)
SUN = (242, 179, 44)

CLAIMS = {
    "cs": ["Napiš, odkud vyrážíš a s kým.", "AI naplánuje celý den."],
    "en": ["Tell us where you start and who's coming.", "AI plans your whole day."],
    "de": ["Sag, wo du startest und wer mitkommt.", "Die KI plant deinen Tag."],
    "it": ["Dicci da dove parti e con chi.", "L'AI organizza la giornata."],
}

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_compass(d, cx, cy, r, ring=CREAM, needle=SUN, width=10):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ring, width=width)
    # NE-pointing needle (two kites)
    import math
    ang = math.radians(45)
    def rot(x, y):
        return (cx + (x * math.cos(ang) - y * math.sin(ang)),
                cy + (x * math.sin(ang) + y * math.cos(ang)))
    n = r * 0.88
    w = r * 0.30
    d.polygon([rot(0, -n), rot(w, 0), rot(0, r * 0.2), rot(-w, 0)], fill=needle)
    d.polygon([rot(0, n), rot(w, 0), rot(0, r * 0.2), rot(-w, 0)], fill=CREAM)
    d.ellipse([cx - r * 0.12, cy - r * 0.12, cx + r * 0.12, cy + r * 0.12], fill=needle)


def og_image(locale, lines):
    img = Image.new("RGB", (1200, 630), PINE)
    d = ImageDraw.Draw(img)
    # subtle deep band bottom
    d.rectangle([0, 560, 1200, 630], fill=PINE_DEEP)
    # compass, right side
    draw_compass(d, 1010, 220, 120, width=14)
    # wordmark
    f_brand = font(FONT_BOLD, 110)
    d.text((80, 120), "Scoperta", font=f_brand, fill=CREAM)
    # yellow accent bar under wordmark
    w = d.textlength("Scoperta", font=f_brand)
    d.rectangle([84, 250, 84 + w * 0.55, 268], fill=SUN)
    # claim
    f_claim = font(FONT_REG, 46)
    y = 340
    for line in lines:
        d.text((84, y), line, font=f_claim, fill=CREAM)
        y += 66
    # domain
    f_dom = font(FONT_BOLD, 30)
    d.text((84, 575), "scoperta.app", font=f_dom, fill=SUN)
    out = os.path.join(OG_DIR, "%s.png" % locale)
    img.save(out, optimize=True)
    print("wrote", out, img.size)


def icon(size):
    img = Image.new("RGB", (size, size), PINE)
    d = ImageDraw.Draw(img)
    r = int(size * 0.30)
    draw_compass(d, size // 2, size // 2, r, width=max(2, size // 18))
    return img


def main():
    for lc, lines in CLAIMS.items():
        og_image(lc, lines)
    # apple-touch-icon 180x180 (opaque)
    icon(180).save(os.path.join(ROOT, "assets", "apple-touch-icon.png"), optimize=True)
    print("wrote assets/apple-touch-icon.png")
    # favicon.ico 32+16
    big = icon(64)
    big.save(os.path.join(ROOT, "assets", "favicon.ico"), sizes=[(16, 16), (32, 32)])
    print("wrote assets/favicon.ico")


if __name__ == "__main__":
    main()
