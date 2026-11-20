#!/usr/bin/env python3
"""Draw the news-image-20261120 v2 front page: 24 verified stories from
Friday 20 November 2026, in one 1024x1024 PNG. All artwork is drawn with
PIL primitives; no photos, no external images, no network. Deterministic:
same input always yields the same bytes."""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 16
CW = W - 2 * MARGIN  # content width: 992

PAPER = (247, 243, 234)
INK = (26, 26, 26)
GREY = (92, 92, 88)
RULE = (60, 60, 60)
RED = (178, 34, 28)
DARKRED = (140, 22, 18)
NAVY = (22, 42, 74)
SKY = (214, 232, 244)
GOLD = (197, 145, 44)

REGION_COLORS = {
    "Europe": (31, 78, 121),
    "Asia-Pacific": (178, 34, 28),
    "Middle East": (192, 122, 26),
    "Africa": (46, 125, 50),
    "Americas": (106, 27, 154),
    "Oceania": (0, 131, 143),
    "Global": (85, 85, 85),
}

FONT_DIRS = [
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/noto",
]


def find_font(names):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    raise FileNotFoundError("no font found among %s" % (names,))


SERIF_B = find_font(["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"])
SERIF = find_font(["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"])
SERIF_I = find_font(["LiberationSerif-Italic.ttf", "DejaVuSerif-Italic.ttf"])
SANS_B = find_font(["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"])
SANS = find_font(["LiberationSans-Regular.ttf", "DejaVuSans.ttf"])

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def fit_font(draw, text, path, start_size, max_width, min_size=8):
    """Largest size at or below start_size that fits max_width."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 1
    return font(path, min_size)


def wrap(draw, text, f, max_width):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, f, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def chip(draw, x, y, text, f, fg, bg, pad_x=6, pad_y=2):
    """Solid label chip; returns its width."""
    w = int(draw.textlength(text, font=f)) + 2 * pad_x
    h = f.size + 2 * pad_y + 2
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    draw.text((x + pad_x, y + pad_y), text, font=f, fill=fg)
    return w


def number_disc(draw, cx, cy, n, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    f = font(SANS_B, 11)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((cx - tw / 2, cy - 7), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------------------
# Illustrations: every panel is drawn from PIL primitives.
# ---------------------------------------------------------------------------

def illo_kyiv(d, x, y, w, h):
    """Night skyline, river bridge, missile trails, fire."""
    d.rectangle([x, y, x + w, y + h], fill=(13, 27, 54))
    for sx, sy in [(18, 14), (60, 26), (120, 10), (180, 22), (240, 12), (290, 28)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 240, 180))
    # skyline blocks
    blocks = [(0, 62, 34, 78), (38, 48, 70, 78), (74, 66, 104, 78),
              (150, 52, 182, 78), (186, 64, 214, 78), (250, 44, 282, 78),
              (286, 60, 322, 78)]
    for bx0, by0, bx1, by1 in blocks:
        d.rectangle([x + bx0, y + by0 * h // 118, x + bx1, y + by1 * h // 118],
                    fill=(30, 52, 92))
    # lit windows
    for wx, wy in [(46, 58), (56, 66), (160, 60), (196, 70), (260, 54), (268, 62)]:
        d.rectangle([x + wx, y + wy * h // 118, x + wx + 5, y + wy * h // 118 + 5],
                    fill=(255, 210, 110))
    # river
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(28, 68, 110))
    # bridge deck + piers
    by = y + h - 34
    d.rectangle([x, by, x + w, by + 6], fill=(210, 205, 190))
    for px in (30, 120, 210, 290):
        d.rectangle([x + px, by + 6, x + px + 8, y + h - 26], fill=(210, 205, 190))
    # missile trails (dashed arcs)
    for x0, y0, x1, y1 in [(250, 6, 120, 66), (300, 2, 210, 62), (200, 4, 60, 68)]:
        steps = 14
        for i in range(0, steps, 2):
            t0, t1 = i / steps, (i + 1) / steps
            ax = x + x0 + (x1 - x0) * t0
            ay = y + y0 + (y1 - y0) * t0 - 18 * (1 - abs(2 * t0 - 1))
            bx = x + x0 + (x1 - x0) * t1
            byy = y + y0 + (y1 - y0) * t1 - 18 * (1 - abs(2 * t1 - 1))
            d.line([ax, ay, bx, byy], fill=(255, 220, 120), width=2)
    # fire bursts on the bridge
    for fx, fy in [(60, 74), (150, 70), (238, 74)]:
        fy = fy * h // 118
        d.ellipse([x + fx - 9, y + fy - 9, x + fx + 9, y + fy + 9], fill=(255, 140, 30))
        d.ellipse([x + fx - 5, y + fy - 5, x + fx + 5, y + fy + 5], fill=(255, 220, 80))
    chip(d, x + 8, y + 8, "KYIV", font(SANS_B, 15), (255, 255, 255), RED)
    chip(d, x + 8, y + h - 22, "3 BRIDGES HIT", font(SANS_B, 11),
         (255, 255, 255), (0, 0, 0))


def illo_akvan(d, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal coast."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 130, 170))
    # land (India coast, left side)
    d.polygon([(x, y), (x + 118, y), (x + 96, y + 34), (x + 128, y + 62),
               (x + 104, y + h), (x, y + h)], fill=(214, 196, 150))
    d.text((x + 14, y + 40), "INDIA", font=font(SANS_B, 11), fill=(120, 96, 50))
    # Gopalpur marker
    gx, gy = x + 118, y + 62
    d.ellipse([gx - 6, gy - 6, gx + 6, gy + 6], fill=RED)
    d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=(255, 255, 255))
    d.text((gx - 46, gy + 8), "GOPALPUR", font=font(SANS_B, 10), fill=(255, 255, 255))
    # spiral bands
    cx, cy = x + 218, y + 52
    for r, col in [(44, (255, 255, 255)), (34, (200, 228, 242)),
                   (24, (255, 255, 255)), (14, (200, 228, 242))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=140,
              fill=col, width=7)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))
    # rain streaks
    for rx in range(150, 320, 22):
        d.line([x + rx, y + 84, x + rx - 6, y + 100], fill=(210, 230, 242), width=2)
    chip(d, x + 8, y + 8, "CYCLONE AKVAN", font(SANS_B, 15), (255, 255, 255), RED)
    chip(d, x + w - 118, y + 8, "LANDFALL 8 AM", font(SANS_B, 11), INK, (255, 255, 255))


def illo_markets(d, x, y, w, h):
    """Falling red chart plus index closes."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 24, 34))
    # grid bars
    for i, bh in enumerate([62, 56, 50, 44, 38, 30, 24]):
        bx = x + 14 + i * 20
        d.rectangle([bx, y + h - 20 - bh, bx + 12, y + h - 20], fill=(64, 40, 40))
    pts = [(x + 14, y + 30), (x + 52, y + 44), (x + 90, y + 40),
           (x + 128, y + 62), (x + 166, y + 58), (x + 204, y + 84),
           (x + 242, y + 96)]
    d.line(pts, fill=(255, 70, 60), width=4)
    d.polygon([(242 + x, 96 + y), (232 + x, 88 + y), (240 + x, 104 + y)],
              fill=(255, 70, 60))
    rows = [("TAIPEI", "-6.6%"), ("SEOUL", "-5.2%"), ("TOKYO", "-4.8%"),
            ("H. KONG", "-1.7%")]
    fy = y + 34
    for name, val in rows:
        d.text((x + 216, fy), name, font=font(SANS_B, 11), fill=(220, 220, 220))
        vw = d.textlength(val, font=font(SANS_B, 12))
        d.text((x + w - 10 - vw, fy - 1), val, font=font(SANS_B, 12),
               fill=(255, 90, 80))
        fy += 20
    chip(d, x + 8, y + 8, "AI SELL-OFF", font(SANS_B, 15), (255, 255, 255), RED)
    chip(d, x + 8, y + h - 22, "FRIDAY'S CLOSE", font(SANS_B, 11),
         (255, 255, 255), (0, 0, 0))


def illo_ukeu(d, x, y, w, h):
    """Union Jack and EU flag side by side."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 48, 96))
    # Union Jack (schematic)
    ux, uy, uw, uh = x + 8, y + 26, 74, 40
    d.rectangle([ux, uy, ux + uw, uy + uh], fill=(1, 33, 105))
    d.polygon([(ux, uy), (ux + 14, uy), (ux + uw, uy + uh - 12), (ux + uw, uy + uh),
               (ux + uw - 14, uy + uh), (ux, uy + 12)], fill=(255, 255, 255))
    d.polygon([(ux + uw, uy), (ux + uw - 14, uy), (ux, uy + uh - 12), (ux, uy + uh),
               (ux + 14, uy + uh), (ux + uw, uy + 12)], fill=(255, 255, 255))
    d.rectangle([ux + uw // 2 - 7, uy, ux + uw // 2 + 7, uy + uh], fill=(255, 255, 255))
    d.rectangle([ux, uy + uh // 2 - 7, ux + uw, uy + uh // 2 + 7], fill=(255, 255, 255))
    d.rectangle([ux + uw // 2 - 4, uy, ux + uw // 2 + 4, uy + uh], fill=(200, 16, 46))
    d.rectangle([ux, uy + uh // 2 - 4, ux + uw, uy + uh // 2 + 4], fill=(200, 16, 46))
    # EU flag
    ex, ey, ew, eh = x + 104, y + 26, 74, 40
    d.rectangle([ex, ey, ex + ew, ey + eh], fill=(0, 51, 153))
    import math
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx = ex + ew // 2 + int(13 * math.cos(a))
        sy = ey + eh // 2 + int(13 * math.sin(a))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    chip(d, x + 8, y + 6, "UK-EU DEAL", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 108, y + h - 20, "AGREED", font(SANS_B, 10), INK, (255, 255, 255))


def illo_cop31(d, x, y, w, h):
    """Globe, thermometer, clock: talks run out of time."""
    d.rectangle([x, y, x + w, y + h], fill=(22, 90, 96))
    cx, cy, r = x + 44, y + 40, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 190, 220))
    d.ellipse([cx - 14, cy - 12, cx + 2, cy + 2], fill=(90, 170, 90))
    d.ellipse([cx + 2, cy + 4, cx + 16, cy + 18], fill=(90, 170, 90))
    # thermometer
    tx = x + 96
    d.rectangle([tx, y + 14, tx + 10, y + 58], fill=(255, 255, 255))
    d.ellipse([tx - 4, y + 52, tx + 14, y + 68], fill=(255, 255, 255))
    d.rectangle([tx + 2, y + 30, tx + 8, y + 58], fill=RED)
    d.ellipse([tx - 1, y + 55, tx + 11, y + 65], fill=RED)
    # clock
    kx, ky, kr = x + 150, y + 40, 22
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(255, 255, 255))
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], outline=INK, width=2)
    d.line([kx, ky, kx, ky - 14], fill=INK, width=3)
    d.line([kx, ky, kx + 11, ky + 4], fill=INK, width=3)
    chip(d, x + 8, y + 6, "COP31: NO DEAL", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 96, y + h - 20, "LAST DAY", font(SANS_B, 10), INK, (255, 255, 255))


def illo_poland(d, x, y, w, h):
    """Missile over fields; NATO compass star."""
    d.rectangle([x, y, x + w, y + h], fill=(140, 180, 120))
    d.rectangle([x, y + 46, x + w, y + h], fill=(110, 150, 90))
    d.rectangle([x, y, x + w, y + 46], fill=(170, 205, 225))
    # field stripes
    for i in range(4):
        d.rectangle([x + i * 48, y + 46, x + i * 48 + 24, y + h], fill=(126, 164, 100))
    # missile
    mx, my = x + 96, y + 24
    d.ellipse([mx - 26, my - 5, mx + 26, my + 5], fill=(230, 230, 230))
    d.polygon([(mx + 26, my - 5), (mx + 40, my), (mx + 26, my + 5)], fill=(200, 40, 30))
    d.polygon([(mx - 26, my - 5), (mx - 34, my - 12), (mx - 30, my)], fill=(120, 120, 120))
    d.polygon([(mx - 26, my + 5), (mx - 34, my + 12), (mx - 30, my)], fill=(120, 120, 120))
    # dashed trail
    for i in range(6):
        tx0 = x + 6 + i * 12
        d.line([tx0, my + 2, tx0 + 6, my + 2], fill=(255, 255, 255), width=2)
    # impact smoke
    d.ellipse([x + 150, y + 50, x + 172, y + 68], fill=(200, 200, 200))
    d.ellipse([x + 158, y + 44, x + 176, y + 60], fill=(220, 220, 220))
    chip(d, x + 8, y + 6, "POLAND: MISSILE", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 112, y + h - 20, "NATO JETS UP", font(SANS_B, 10), INK,
         (255, 255, 255))


def illo_italy(d, x, y, w, h):
    """Marching crowd under a strike banner."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    # banner (below the top chip row)
    d.rectangle([x + 14, y + 30, x + w - 14, y + 48], fill=RED)
    d.text((x + 22, y + 33), "SCIOPERO GENERALE", font=font(SANS_B, 12),
           fill=(255, 255, 255))
    # crowd silhouettes
    for i, cx in enumerate(range(18, w - 10, 26)):
        cy = y + 52 + (3 if i % 2 else 0)
        d.ellipse([x + cx, cy, x + cx + 12, cy + 12], fill=(40, 40, 40))
        d.polygon([(x + cx - 2, cy + 20), (x + cx + 6, cy + 12),
                   (x + cx + 14, cy + 20)], fill=(40, 40, 40))
    chip(d, x + 8, y + 6, "ITALY: STRIKE", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 118, y + h - 20, "100+ CITIES", font(SANS_B, 10), INK,
         (255, 255, 255))


def illo_japan(d, x, y, w, h):
    """Rising sun disc and climbing bars."""
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.ellipse([x + 18, y + 26, x + 62, y + 70], fill=(188, 0, 45))
    bars = [16, 22, 28, 36, 44]
    for i, bh in enumerate(bars):
        bx = x + 82 + i * 20
        d.rectangle([bx, y + 70 - bh, bx + 13, y + 70], fill=(60, 60, 60))
    d.text((x + 82, y + 30), "+2.3%", font=font(SANS_B, 15), fill=RED)
    chip(d, x + 8, y + 6, "JAPAN: +2.3%", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 108, y + h - 20, "OCT CPI", font(SANS_B, 10), INK,
         (230, 230, 230))


def illo_korea(d, x, y, w, h):
    """Courthouse columns and gavel."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 84, 120))
    # pediment
    d.polygon([(x + 20, y + 34), (x + 96, y + 12), (x + 172, y + 34)],
              fill=(230, 225, 210))
    for i in range(5):
        cx = x + 30 + i * 32
        d.rectangle([cx, y + 38, cx + 12, y + 62], fill=(230, 225, 210))
    d.rectangle([x + 20, y + 62, x + 172, y + 68], fill=(230, 225, 210))
    chip(d, x + 8, y + 6, "SEOUL: IMPEACH", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 118, y + h - 20, "TOP JUDGE", font(SANS_B, 10), INK,
         (255, 255, 255))


def illo_cricket(d, x, y, w, h):
    """Cricket bat, ball and big 118."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 125, 50))
    d.rectangle([x, y + 52, x + w, y + h], fill=(56, 142, 60))
    # bat
    d.polygon([(x + 30, y + 14), (x + 52, y + 14), (x + 62, y + 58),
               (x + 40, y + 58)], fill=(222, 184, 135))
    d.rectangle([x + 38, y + 6, x + 46, y + 16], fill=(120, 72, 30))
    # ball
    d.ellipse([x + 150, y + 18, x + 172, y + 40], fill=(178, 34, 28))
    d.arc([x + 152, y + 20, x + 170, y + 38], start=60, end=300,
          fill=(255, 255, 255), width=2)
    d.text((x + 84, y + 14), "118", font=font(SANS_B, 34), fill=(255, 255, 255))
    chip(d, x + 8, y + 6, "PHILLIPS: 118", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 118, y + h - 20, "v INDIA", font(SANS_B, 10), INK,
         (255, 255, 255))


def illo_kenya(d, x, y, w, h):
    """Oil derrick at sunset."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 200, 110))
    d.ellipse([x + 138, y + 8, x + 178, y + 48], fill=(255, 150, 40))
    d.rectangle([x, y + 56, x + w, y + h], fill=(150, 100, 50))
    # derrick
    dx = x + 40
    d.polygon([(dx, y + 56), (dx + 18, y + 10), (dx + 36, y + 10),
               (dx + 54, y + 56)], outline=(60, 40, 20), width=3)
    d.line([dx + 10, y + 44, dx + 44, y + 44], fill=(60, 40, 20), width=2)
    d.line([dx + 14, y + 32, dx + 40, y + 32], fill=(60, 40, 20), width=2)
    d.line([dx + 18, y + 20, dx + 36, y + 20], fill=(60, 40, 20), width=2)
    # pumpjack
    d.line([x + 120, y + 56, x + 120, y + 36], fill=(60, 40, 20), width=3)
    d.line([x + 104, y + 36, x + 140, y + 30], fill=(60, 40, 20), width=3)
    chip(d, x + 8, y + 6, "KENYA: OIL", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 118, y + h - 20, "FIRST WELL", font(SANS_B, 10), INK,
         (255, 255, 255))


def illo_iraq(d, x, y, w, h):
    """Desert convoy and palms."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 210, 160))
    d.rectangle([x, y, x + w, y + 34], fill=(190, 220, 235))
    d.ellipse([x + 160, y + 6, x + 182, y + 28], fill=(255, 230, 140))
    # palms
    for px in (24, 168):
        d.line([x + px, y + 52, x + px, y + 30], fill=(110, 80, 40), width=4)
        for dx2, dy2 in [(-12, -8), (-6, -12), (0, -14), (6, -12), (12, -8)]:
            d.line([x + px, y + 30, x + px + dx2, y + 30 + dy2],
                   fill=(60, 120, 60), width=3)
    # armoured vehicle
    vx, vy = x + 62, y + 40
    d.rectangle([vx, vy, vx + 72, vy + 16], fill=(90, 100, 70))
    d.rectangle([vx + 14, vy - 8, vx + 48, vy], fill=(90, 100, 70))
    d.line([vx + 48, vy - 4, vx + 66, vy - 4], fill=(70, 80, 55), width=3)
    for wx in (vx + 8, vx + 30, vx + 52):
        d.ellipse([wx, vy + 12, wx + 12, vy + 24], fill=(40, 40, 40))
    chip(d, x + 8, y + 6, "IRAQ: ARMY IN", font(SANS_B, 13), (255, 255, 255), RED)
    chip(d, x + w - 118, y + h - 20, "JURF AL-SAKHAR", font(SANS_B, 10), INK,
         (255, 255, 255))


# ---------------------------------------------------------------------------
# Schematic world map (equirectangular, lon -170..190, lat 75..-60).
# ---------------------------------------------------------------------------

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 72), (-85, 70),
     (-80, 73), (-65, 62), (-60, 52), (-65, 44), (-70, 42), (-75, 35),
     (-80, 32), (-81, 25), (-85, 30), (-90, 29), (-97, 26), (-105, 23),
     (-110, 24), (-114, 29), (-120, 34), (-124, 40), (-124, 48), (-130, 55),
     (-140, 60), (-155, 58), (-165, 60)],
    # South America
    [(-78, 8), (-72, 11), (-62, 10), (-52, 5), (-44, -3), (-35, -8),
     (-38, -15), (-40, -22), (-48, -28), (-52, -33), (-58, -38), (-62, -41),
     (-65, -45), (-68, -50), (-70, -54), (-73, -50), (-73, -40), (-72, -30),
     (-70, -20), (-75, -15), (-80, -8), (-80, 0)],
    # Africa
    [(-17, 15), (-10, 12), (-8, 4), (4, 6), (9, 4), (13, -1), (12, -6),
     (13, -12), (15, -17), (12, -18), (17, -29), (19, -34), (26, -34),
     (32, -29), (35, -24), (36, -18), (40, -15), (40, -10), (42, -2),
     (48, 2), (51, 11), (44, 11), (40, 15), (38, 18), (35, 20), (33, 27),
     (32, 31), (20, 32), (10, 34), (0, 36), (-6, 36), (-10, 31), (-15, 25),
     (-17, 20)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (5, 60), (5, 62), (10, 64), (14, 67), (18, 69), (25, 71), (32, 70),
     (40, 68), (50, 69), (60, 70), (70, 72), (80, 73), (90, 75), (100, 77),
     (110, 74), (120, 73), (130, 71), (140, 72), (150, 70), (160, 69),
     (170, 67), (178, 65), (178, 62), (170, 60), (162, 58), (158, 52),
     (150, 50), (142, 50), (140, 45), (135, 43), (130, 42), (127, 40),
     (122, 38), (120, 35), (122, 30), (120, 25), (110, 20), (108, 15),
     (105, 10), (103, 8), (100, 7), (98, 12), (95, 16), (92, 21), (88, 22),
     (85, 20), (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25),
     (62, 25), (57, 27), (52, 28), (50, 29), (48, 30), (44, 29), (40, 31),
     (36, 36), (30, 36), (27, 37), (23, 36), (20, 40), (16, 40), (12, 44),
     (8, 44), (3, 43), (0, 40), (-5, 37), (-9, 37)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (151, -24), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
]

ISLANDS = [
    [(-5, 58), (-2, 57), (1, 52), (0, 50), (-5, 50), (-6, 54)],  # Britain
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (144, 44),
     (142, 44), (140, 39), (136, 34), (132, 33)],  # Japan
    [(95, 5), (104, -2), (110, -6), (114, -8), (120, -10), (124, -9),
     (119, -5), (112, -3), (106, 1), (100, 4)],  # Indonesia
    [(44, -12), (47, -16), (49, -20), (47, -25), (44, -25), (43, -20),
     (43, -15)],  # Madagascar
    [(167, -46), (171, -43), (174, -39), (177, -38), (178, -37), (175, -40),
     (172, -43), (168, -47)],  # New Zealand
]

# (number, lon, lat) for the 12 drawn stories; Europe pins nudged apart
PINS = [
    (1, 30.5, 50.4), (2, 84.5, 20.0), (3, 121.5, 25.0), (4, 1.0, 53.5),
    (5, 34.0, 35.0), (6, 24.0, 53.0), (7, 11.0, 39.5), (8, 139.7, 35.7),
    (9, 127.0, 37.5), (10, 174.8, -41.3), (11, 36.0, 3.5), (12, 48.0, 30.0),
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 50, 74))

    def proj(lon, lat):
        px = x + (lon + 170) / 360.0 * w
        py = y + (75 - lat) / 135.0 * h
        return (px, py)

    for poly in CONTINENTS + ISLANDS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(217, 201, 163))
    for n, lon, lat in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = font(SANS_B, 9)
        t = str(n)
        tw = d.textlength(t, font=f)
        d.text((px - tw / 2, py - 6), t, font=f, fill=(255, 255, 255))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


# ---------------------------------------------------------------------------
# Story data: 24 stories, all verified as Friday 20 November 2026 news.
# ---------------------------------------------------------------------------

HEROES = [
    dict(num=1, illo=illo_kyiv, place="KYIV, UKRAINE", beat="WAR",
         head="Russian missiles hit three Kyiv bridges",
         body=("An overnight barrage of 110+ missiles and 400 drones killed at "
               "least eight across Ukraine and cut power and water in the "
               "capital. (Reuters, Kyiv Independent)")),
    dict(num=2, illo=illo_akvan, place="ODISHA, INDIA", beat="CYCLONE",
         head="Cyclone Akvan comes ashore in eastern India",
         body=("The storm crossed the coast near Gopalpur from about 8 am; "
               "370,000+ people were moved to shelters. No deaths were "
               "reported. (IMD, Reuters)")),
    dict(num=3, illo=illo_markets, place="TAIPEI · SEOUL · TOKYO",
         beat="MARKETS",
         head="AI sell-off sinks Asia's stock markets",
         body=("Taiwan's index fell 6.6% to its worst week since 1991; Seoul "
               "lost 5.2% and Tokyo 4.8% as chipmakers led the slide. "
               "(Reuters, Aju Press)")),
]

CARDS = [
    dict(num=4, illo=illo_ukeu, place="BRUSSELS", beat="DIPLOMACY",
         head="UK and EU seal a \u201creset\u201d deal",
         body=("Food trade, youth visas and a carbon link; PM Burnham calls "
               "it \u201cwin-win\u201d. (Reuters, gov.uk)")),
    dict(num=5, illo=illo_cop31, place="ANTALYA", beat="CLIMATE",
         head="COP31 reaches its last day with no deal",
         body=("The draft text leaves out fossil fuels and the $120bn "
               "adaptation figure. (UN News, Carbon Brief)")),
    dict(num=6, illo=illo_poland, place="EASTERN POLAND", beat="SECURITY",
         head="Russian missile lands in Poland",
         body=("A Kh-101 came down in a field; NATO jets scrambled, no one "
               "hurt. (Reuters, Polish MoD)")),
    dict(num=7, illo=illo_italy, place="ITALY", beat="LABOUR",
         head="General strike over Italy's budget",
         body=("CGIL stoppage brings marches to 100+ cities; 1m+ out, the "
               "union says. (Reuters, AP)")),
    dict(num=8, illo=illo_japan, place="TOKYO", beat="ECONOMY",
         head="Japan's inflation picks up to 2.3%",
         body=("October CPI, highest in a year; a December rate rise stays "
               "in view. (Statistics Bureau)")),
    dict(num=9, illo=illo_korea, place="SEOUL", beat="POLITICS",
         head="Korea's ruling party to impeach top judge",
         body=("DP adopts the move after the court partly cleared ex-PM Han. "
               "(Yonhap)")),
    dict(num=10, illo=illo_cricket, place="WELLINGTON", beat="CRICKET",
         head="Phillips hits 118 against India",
         body=("First man with centuries in all three formats vs India in a "
               "year. (Reuters, ICC)")),
    dict(num=11, illo=illo_kenya, place="TURKANA, KENYA", beat="ENERGY",
         head="Kenya starts drilling its first oil well",
         body=("Rig switched on at Amosing; first crude due on 1 December. "
               "(Capital FM)")),
    dict(num=12, illo=illo_iraq, place="CENTRAL IRAQ", beat="SECURITY",
         head="Iraqi army enters a militia stronghold",
         body=("Troops deploy to Jurf al-Sakhar under a deal with Kataib "
               "Hezbollah. (Reuters)")),
]

BRIEFS = [
    (13, "Shenzhen", "Xi hails \u201cfull turnaround\u201d in ties with "
     "Australia; 2027 named tourism year (Reuters)"),
    (14, "Lviv", "Strike on a railway station kills two, ten in hospital "
     "(Mayor Sadovyi)"),
    (15, "Blantyre", "Malawi fuel queues stretch overnight; minister pledges "
     "forex fix (Al Jazeera)"),
    (16, "Mercury", "BepiColombo reaches Mercury after 8 years; orbit burn "
     "set for Saturday (ESA)"),
    (17, "Hormuz", "Strait shut, day 265: 3 ships crossed Thursday, ~50 hold "
     "offshore (trackers)"),
    (18, "Beijing", "China holds loan rates for an 18th month: 1-yr 3.0%, "
     "5-yr 3.5% (PBOC)"),
    (19, "Las Vegas", "Russell fastest in wet F1 practice, 1:47.272, ahead of "
     "Gasly (Formula1.com)"),
    (20, "Turin", "Alcaraz beats Cobolli 6-4, 6-1, tops ATP Finals group "
     "unbeaten (ATP)"),
    (21, "Antalya", "Panama leads bloc demanding a fossil-fuel phaseout at "
     "COP31 (UN News)"),
    (22, "Kharkiv", "Drone hits a hospital; at least four hurt in overnight "
     "strikes (Reuters)"),
    (23, "Florida", "St Johns River crests at a record 18.7 ft; emergency "
     "widened (NWS)"),
    (24, "Global", "UN marks World Children's Day across member states "
     "(UN News)"),
]

STATS = [
    ("3", "bridges over the Dnipro damaged in Kyiv"),
    ("370,000+", "people moved to shelters before Akvan"),
    ("\u22126.6%", "Taiwan's share index, Friday's close"),
    ("100,000", "youth visas a year in the UK-EU deal"),
    ("2.3%", "Japan consumer inflation in October"),
    ("118", "runs by Glenn Phillips against India"),
]

REGIONS = [("Europe", 7), ("Asia-Pacific", 6), ("Middle East", 2),
           ("Africa", 2), ("Americas", 2), ("Oceania", 1), ("Global", 4)]

DATE_CHECK = (
    "DATE CHECK \u2014 Left out as Thursday 19 November's news: the Shenzhen summit "
    "\u00b7 the ICJ Myanmar ruling \u00b7 Trump's Iran delay \u00b7 Voyager 1's light-day "
    "\u00b7 Bukele's filing \u00b7 Indonesia's asset-seizure law \u00b7 the Pentagon's "
    "$48.3bn figure \u00b7 Denmark's Greenland vote \u00b7 the Senegal boat toll \u00b7 "
    "Anthropic's IPO \u00b7 Wall Street's 2% fall. Not yet happened: BepiColombo's "
    "orbit burn (Saturday) and any final COP31 text.")


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def draw_hero(d, x, y, w, s):
    illo_h = 106
    s["illo"](d, x, y, w, illo_h)
    d.rectangle([x, y, x + w, y + illo_h], outline=INK, width=1)
    ky = y + illo_h + 6
    number_disc(d, x + 9, ky + 7, s["num"])
    d.text((x + 22, ky), "%s \u00b7 %s" % (s["place"], s["beat"]),
           font=font(SANS_B, 11), fill=RED)
    hy = ky + 18
    head_f = font(SERIF_B, 19)
    for ln in wrap(d, s["head"], head_f, w):
        d.text((x, hy), ln, font=head_f, fill=INK)
        hy += 22
    by = hy + 3
    body_f = font(SANS, 12)
    for ln in wrap(d, s["body"], body_f, w):
        d.text((x, by), ln, font=body_f, fill=(40, 40, 40))
        by += 14
    return by


def draw_card(d, x, y, w, s):
    illo_h = 74
    s["illo"](d, x, y, w, illo_h)
    d.rectangle([x, y, x + w, y + illo_h], outline=INK, width=1)
    ky = y + illo_h + 6
    number_disc(d, x + 8, ky + 6, s["num"], r=8)
    d.text((x + 20, ky), "%s \u00b7 %s" % (s["place"], s["beat"]),
           font=font(SANS_B, 10), fill=RED)
    hy = ky + 16
    head_f = font(SERIF_B, 13)
    for ln in wrap(d, s["head"], head_f, w):
        d.text((x, hy), ln, font=head_f, fill=INK)
        hy += 15
    by = hy + 2
    body_f = font(SANS, 11)
    for ln in wrap(d, s["body"], body_f, w):
        d.text((x, by), ln, font=body_f, fill=(40, 40, 40))
        by += 12
    return by


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Eyebrow
    d.text((MARGIN, 8), "THE WORLD IN ONE DAY", font=font(SANS_B, 11), fill=RED)
    right = "24 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    rf = font(SANS_B, 11)
    d.text((W - MARGIN - d.textlength(right, font=rf), 8), right, font=rf, fill=INK)
    d.line([MARGIN, 28, W - MARGIN, 28], fill=INK, width=2)

    # Masthead
    mast = "Friday 20 November 2026"
    mf = fit_font(d, mast, SERIF_B, 60, CW)
    mw = d.textlength(mast, font=mf)
    d.text(((W - mw) / 2, 32), mast, font=mf, fill=INK)

    # Subtitle
    sub = ("Russian missiles hit Kyiv's bridges \u00b7 Cyclone Akvan strikes India "
           "\u00b7 AI sell-off sinks Asia's markets \u00b7 UK and EU seal a deal")
    sf = fit_font(d, sub, SERIF_I, 17, CW)
    sw = d.textlength(sub, font=sf)
    d.text(((W - sw) / 2, 98), sub, font=sf, fill=(50, 50, 50))
    d.line([MARGIN, 122, W - MARGIN, 122], fill=INK, width=2)

    # Stat strip
    sy = 128
    cell_w = CW / 6
    for i, (num, label) in enumerate(STATS):
        cx = MARGIN + i * cell_w
        if i:
            d.line([cx - 4, sy + 2, cx - 4, sy + 44], fill=(200, 195, 180), width=1)
        d.text((cx, sy), num, font=font(SERIF_B, 24), fill=INK)
        lf = font(SANS, 10)
        ly = sy + 28
        for ln in wrap(d, label, lf, cell_w - 12):
            d.text((cx, ly), ln, font=lf, fill=GREY)
            ly += 12

    # Region bar
    ry, rh = 180, 18
    seg_w = CW / len(REGIONS)
    for i, (name, count) in enumerate(REGIONS):
        sx = MARGIN + i * seg_w
        d.rectangle([sx, ry, sx + seg_w - 1, ry + rh],
                    fill=REGION_COLORS[name])
        label = "%s %d" % (name, count)
        lf = font(SANS_B, 10)
        tw = d.textlength(label, font=lf)
        d.text((sx + (seg_w - tw) / 2, ry + 3), label, font=lf,
               fill=(255, 255, 255))

    # Heroes
    hy = 206
    gap = 12
    hw = int((CW - 2 * gap) / 3)
    hero_bottom = hy
    for i, s in enumerate(HEROES):
        hx = MARGIN + i * (hw + gap)
        hero_bottom = max(hero_bottom, draw_hero(d, hx, hy, hw, s))

    # Cards row 1 (5) and row 2 (4)
    cy = hero_bottom + 8
    gap5 = 8
    cw5 = int((CW - 4 * gap5) / 5)
    row1_bottom = cy
    for i, s in enumerate(CARDS[:5]):
        cx = MARGIN + i * (cw5 + gap5)
        row1_bottom = max(row1_bottom, draw_card(d, cx, cy, cw5, s))
    cy2 = row1_bottom + 8
    cw4 = int((CW - 3 * gap5) / 4)
    row2_bottom = cy2
    for i, s in enumerate(CARDS[5:]):
        cx = MARGIN + i * (cw4 + gap5)
        row2_bottom = max(row2_bottom, draw_card(d, cx, cy2, cw4, s))

    # Bottom section: map + briefs
    by = row2_bottom + 8
    d.text((MARGIN, by), "WHERE IT HAPPENED",
           font=font(SANS_B, 12), fill=INK)
    bx = MARGIN + 316
    d.text((bx, by), "ALSO ON FRIDAY 20 NOVEMBER \u2014 12 MORE STORIES",
           font=font(SANS_B, 12), fill=INK)
    d.line([MARGIN, by + 17, W - MARGIN, by + 17], fill=RULE, width=1)
    my = by + 22
    map_h = 152
    draw_map(d, MARGIN, my, 300, map_h)
    d.text((MARGIN, my + map_h + 5),
           "Each number is that story on this page.",
           font=font(SANS, 10), fill=GREY)

    # Briefs in two columns
    brief_w = int((W - MARGIN - bx - 16) / 2)
    bf = font(SANS, 11)
    bhead_f = font(SANS_B, 11)
    for col in range(2):
        col_x = bx + col * (brief_w + 16)
        yy = my
        for num, place, text in BRIEFS[col * 6:(col + 1) * 6]:
            num_t = "%d " % num
            d.text((col_x, yy), num_t, font=bhead_f, fill=RED)
            nx = col_x + d.textlength(num_t, font=bhead_f)
            d.text((nx, yy), place + " ", font=bhead_f, fill=INK)
            px = nx + d.textlength(place + " ", font=bhead_f)
            # first line starts after "N Place ", continuation lines full width
            first_w = brief_w - (px - col_x)
            lines = wrap(d, text, bf, brief_w)
            # reflow: first line must fit first_w
            first_lines = wrap(d, text, bf, first_w)
            if first_lines:
                d.text((px, yy), first_lines[0], font=bf, fill=(40, 40, 40))
                rest = text[len(first_lines[0]):].strip()
            else:
                rest = text
            yy += 14
            for ln in wrap(d, rest, bf, brief_w):
                d.text((col_x, yy), ln, font=bf, fill=(40, 40, 40))
                yy += 14
            yy += 3

    # Date check box
    dy = my + map_h + 22
    box_h = 48
    d.rectangle([MARGIN, dy, W - MARGIN, dy + box_h], outline=RED, width=2)
    dcf = font(SANS, 11)
    dcb = font(SANS_B, 11)
    lines = wrap(d, DATE_CHECK, dcf, CW - 20)
    ly = dy + 5
    for i, ln in enumerate(lines):
        f = dcb if i == 0 and ln.startswith("DATE CHECK") else dcf
        # bold just the "DATE CHECK" lead on the first line
        if i == 0:
            d.text((MARGIN + 10, ly), "DATE CHECK ", font=dcb, fill=RED)
            lead_w = d.textlength("DATE CHECK ", font=dcb)
            rest = ln[len("DATE CHECK "):]
            d.text((MARGIN + 10 + lead_w, ly), rest, font=dcf, fill=INK)
        else:
            d.text((MARGIN + 10, ly), ln, font=dcf, fill=INK)
        ly += 13

    # Footer
    fy = dy + box_h + 6
    foot_l = ("Every story here happened, or was first reported, on Friday "
              "20 November 2026. Officials' counts are attributed.")
    foot_r = "Sources named beside each story \u00b7 original drawings"
    ff = font(SANS, 10)
    d.text((MARGIN, fy), foot_l, font=ff, fill=GREY)
    d.text((W - MARGIN - d.textlength(foot_r, font=ff), fy), foot_r, font=ff,
           fill=GREY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    img.save(out, format="PNG")  # deterministic: no timestamps in PNG
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))


if __name__ == "__main__":
    main()
