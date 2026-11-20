#!/usr/bin/env python3
"""draw_v4.py — "Friday 20 November 2026 — One Image", v4.

A one-page newspaper front page drawn 100% with PIL: 24 stories, all of
them verified as Friday 20 November 2026 news, in the v2 layout (3 heroes,
9 illustrated cards, 12 briefs, a world map, a stat strip, a region bar
and a DATE CHECK box) with the faithfulness corrections found by
re-verifying every story against the day's reporting:

  * Cyclone Akvan evacuations: 300,000+ (not 370,000+)
  * TAIEX Friday close: -6.2% (official TWSE close 36,033.29, -6.23%)
  * Nikkei Friday close: -5.1% (official close -5.06%)
  * Hang Seng Friday close: -1.9% (official close -1.89%)
  * Poland: two missiles and a jet-powered drone (not one Kh-101)
  * Story 17: Gulf of Aden skiff attack on a bulk carrier (UKMTO 213-26),
    replacing the wrong Hormuz "strait shut" item
  * DATE CHECK gains four verified Thursday exclusions

Deterministic: no randomness, no clock, no external assets. Two runs
produce byte-identical PNGs. Output is 1024x1024, well under 1 MiB.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 14
CW = W - 2 * MARGIN  # content width: 996

# ---------------------------------------------------------------- palette
PAPER = (253, 252, 247)
INK = (26, 26, 46)
NAVY = (15, 42, 74)
NAVY_SOFT = (36, 68, 110)
GREY = (92, 96, 104)
LIGHT_LINE = (205, 203, 192)
RED = (178, 34, 34)
BLUE = (36, 113, 163)
GREEN = (39, 174, 96)
AMBER = (196, 120, 20)
PURPLE = (126, 58, 168)
TEAL = (22, 160, 133)
SLATE = (93, 109, 126)

REGION_COLORS = [
    ("EUROPE", 7, (46, 134, 193)),
    ("ASIA-PACIFIC", 6, (192, 57, 43)),
    ("MID EAST", 2, (202, 124, 22)),
    ("AFRICA", 2, (39, 174, 96)),
    ("AMERICAS", 2, (142, 68, 173)),
    ("OCEANIA", 1, (22, 160, 133)),
    ("GLOBAL", 4, (93, 109, 126)),
]

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"


def _font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


def serif_b(size):
    return _font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return _font("DejaVuSerif.ttf", size)


def sans(size):
    return _font("DejaVuSans.ttf", size)


def sans_b(size):
    return _font("DejaVuSans-Bold.ttf", size)


# ---------------------------------------------------------------- helpers
def wrap(text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(dr, lines, x, y, font, fill, lh):
    for i, line in enumerate(lines):
        dr.text((x, y + i * lh), line, font=font, fill=fill)
    return y + len(lines) * lh


def text_center(dr, cx, y, text, font, fill):
    dr.text((cx - font.getlength(text) / 2, y), text, font=font, fill=fill)


def chip(dr, x, y, w, h, fill, outline=None):
    dr.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill,
                         outline=outline, width=1 if outline else 0)


# ---------------------------------------------------------------- data
SUBTITLE = ("Russian missiles hit Kyiv's bridges \u00b7 Cyclone Akvan strikes "
            "India \u00b7 AI sell-off sinks Asia's markets \u00b7 UK and EU seal a deal")

STATS = [
    ("3", "bridges over the Dnipro damaged in Kyiv"),
    ("300,000+", "people moved to shelters before Akvan"),
    ("\u22126.2%", "Taiwan's share index, Friday's close"),
    ("100,000", "youth visas a year in the UK-EU deal"),
    ("2.3%", "Japan consumer inflation in October"),
    ("118", "runs by Glenn Phillips against India"),
]

HEROES = [
    dict(
        kicker="KYIV, UKRAINE \u00b7 WAR",
        color=RED,
        headline="Russian missiles hit three Kyiv bridges",
        body=("An overnight barrage of 110+ missiles and 400 drones killed at "
              "least eight across Ukraine and cut power and water in the "
              "capital. (Reuters, Kyiv Independent)"),
        art="kyiv",
    ),
    dict(
        kicker="ODISHA, INDIA \u00b7 CYCLONE",
        color=BLUE,
        headline="Cyclone Akvan comes ashore in eastern India",
        body=("The storm crossed the coast near Gopalpur from about 8 am; "
              "300,000+ people were moved to shelters. No deaths were "
              "reported. (IMD, Reuters)"),
        art="akvan",
    ),
    dict(
        kicker="TAIPEI \u00b7 SEOUL \u00b7 TOKYO \u00b7 MARKETS",
        color=RED,
        headline="AI sell-off sinks Asia's stock markets",
        body=("Taiwan's index fell 6.2% to its worst week since 1991; Seoul "
              "lost 5.2% and Tokyo 5.1% as chipmakers led the slide. "
              "(Reuters, Aju Press)"),
        art="markets",
    ),
]

CARDS = [
    dict(
        kicker="BRUSSELS \u00b7 DIPLOMACY",
        color=BLUE,
        headline="UK and EU seal a 'reset' deal",
        body=("Food trade, youth visas and a carbon link; PM Burnham calls "
              "it 'win-win'. (Reuters, gov.uk)"),
        art="flags",
    ),
    dict(
        kicker="ANTALYA \u00b7 CLIMATE",
        color=GREEN,
        headline="COP31 reaches its last day with no deal",
        body=("The draft text leaves out fossil fuels and the $120bn "
              "adaptation figure. (UN News, Carbon Brief)"),
        art="cop",
    ),
    dict(
        kicker="EASTERN POLAND \u00b7 SECURITY",
        color=RED,
        headline="Russian missiles land in Poland",
        body=("Two missiles and a jet-powered drone came down in the "
              "south-east; NATO jets scrambled, no one hurt. "
              "(Reuters, Polish MoD)"),
        art="poland",
    ),
    dict(
        kicker="ITALY \u00b7 LABOUR",
        color=AMBER,
        headline="General strike over Italy's budget",
        body=("CGIL stoppage brings marches to 100+ cities; 1m+ out, the "
              "union says. (Reuters, AP)"),
        art="strike",
    ),
    dict(
        kicker="TOKYO \u00b7 ECONOMY",
        color=BLUE,
        headline="Japan's inflation picks up to 2.3%",
        body=("October CPI, highest in a year; a December rate rise stays "
              "in view. (Statistics Bureau)"),
        art="cpi",
    ),
    dict(
        kicker="SEOUL \u00b7 POLITICS",
        color=NAVY_SOFT,
        headline="Korea's ruling party to impeach top judge",
        body=("DP adopts the move after the court partly cleared ex-PM Han. "
              "(Yonhap)"),
        art="court",
    ),
    dict(
        kicker="WELLINGTON \u00b7 CRICKET",
        color=GREEN,
        headline="Phillips hits 118 against India",
        body=("First man with centuries in all three formats vs India in a "
              "year. (Reuters, ICC)"),
        art="cricket",
    ),
    dict(
        kicker="TURKANA, KENYA \u00b7 ENERGY",
        color=AMBER,
        headline="Kenya starts drilling its first oil well",
        body=("Rig switched on at Amosing; first crude due on 1 December. "
              "(Capital FM)"),
        art="oil",
    ),
    dict(
        kicker="CENTRAL IRAQ \u00b7 SECURITY",
        color=RED,
        headline="Iraqi army enters a militia stronghold",
        body=("Troops deploy to Jurf al-Sakhar under a deal with Kataib "
              "Hezbollah. (Reuters)"),
        art="iraq",
    ),
]

BRIEFS = [
    ("13", "Shenzhen",
     "Xi hails \u201cfull turnaround\u201d in ties with Australia; 2027 named "
     "tourism year (Reuters)."),
    ("14", "Lviv",
     "Strike on a railway station kills two, ten in hospital "
     "(Mayor Sadovyi)."),
    ("15", "Blantyre",
     "Malawi fuel queues stretch overnight; minister pledges forex fix "
     "(Al Jazeera)."),
    ("16", "Mercury",
     "BepiColombo reaches Mercury after 8 years; orbit burn set for "
     "Saturday (ESA)."),
    ("17", "Gulf of Aden",
     "Armed skiff fires on a bulk carrier 95nm off Yemen; guards\u2019 "
     "warning shots drive it off, no one hurt (UKMTO)."),
    ("18", "Beijing",
     "China holds loan rates for an 18th month: 1-yr 3.0%, 5-yr 3.5% "
     "(PBOC)."),
    ("19", "Las Vegas",
     "Russell fastest in wet F1 practice, 1:47.272, ahead of Gasly "
     "(Formula1.com)."),
    ("20", "Turin",
     "Alcaraz beats Cobolli 6-4, 6-1, tops ATP Finals group unbeaten "
     "(ATP)."),
    ("21", "Antalya",
     "Panama leads bloc demanding a fossil-fuel phaseout at COP31 "
     "(UN News)."),
    ("22", "Kharkiv",
     "Drone hits a hospital; at least four hurt in overnight strikes "
     "(Reuters)."),
    ("23", "Florida",
     "St John\u2019s River crests at a record 18.7 ft, emergency widened "
     "(NWS)."),
    ("24", "Global",
     "UN marks World Children\u2019s Day across member states (UN News)."),
]

DATE_CHECK = (
    "Left out as Thursday 19 November\u2019s news: the Shenzhen summit \u00b7 "
    "the ICJ Myanmar ruling \u00b7 Trump\u2019s Iran delay \u00b7 Voyager 1\u2019s "
    "light-day \u00b7 Bukele\u2019s filing \u00b7 Indonesia\u2019s asset-seizure law "
    "\u00b7 the Pentagon\u2019s $48.3bn figure \u00b7 Denmark\u2019s Greenland vote "
    "\u00b7 the Senegal boat toll \u00b7 Anthropic\u2019s IPO \u00b7 Wall Street\u2019s "
    "2% fall \u00b7 the US Senate energy vote (62\u201333) \u00b7 Argentina\u2019s "
    "disability approval (71-0) \u00b7 hippo Fiona\u2019s death \u00b7 Canada\u2019s "
    "Budget vote (162\u2013151). Not yet happened: BepiColombo\u2019s orbit burn "
    "(Saturday) and any final COP31 text."
)


# ---------------------------------------------------------------- artwork
# Every illustration is drawn with PIL primitives only: no photos, no
# external images. Each function paints inside the box (x0, y0, x1, y1).


def art_kyiv(dr, x0, y0, x1, y1):
    """Night skyline over the Dnipro, three bridges, bursts above them."""
    dr.rectangle([x0, y0, x1, y1], fill=(13, 27, 54))
    for sx, sy in [(18, 12), (52, 22), (96, 8), (140, 18), (188, 10),
                   (232, 24), (276, 12), (308, 20), (70, 30), (210, 32)]:
        dr.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                   fill=(255, 244, 200))
    # river band
    dr.rectangle([x0, y1 - 26, x1, y1], fill=(28, 66, 110))
    # skyline blocks with lit windows
    blocks = [(8, 44, 34, 20), (42, 30, 30, 34), (76, 48, 38, 16),
              (120, 26, 26, 38), (150, 42, 36, 22), (192, 34, 30, 30),
              (226, 48, 34, 16), (264, 28, 28, 36), (296, 44, 22, 20)]
    for bx, bh, bw, _ in blocks:
        dr.rectangle([x0 + bx, y1 - 26 - bh, x0 + bx + bw, y1 - 26],
                     fill=(8, 16, 32))
        for wy in range(y1 - 26 - bh + 4, y1 - 30, 9):
            for wx in range(x0 + bx + 4, x0 + bx + bw - 4, 8):
                if (wx * 7 + wy * 3) % 5 < 2:
                    dr.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 110))
    # three bridge arcs over the river
    for cx in (60, 165, 268):
        dr.arc([x0 + cx - 34, y1 - 44, x0 + cx + 34, y1 - 4], 180, 360,
               fill=(190, 200, 215), width=3)
        dr.line([x0 + cx - 34, y1 - 24, x0 + cx + 34, y1 - 24],
                fill=(190, 200, 215), width=2)
    # explosion bursts above the bridges
    for cx, cy in [(60, y1 - 62), (165, y1 - 70), (268, y1 - 58)]:
        for r, col in [(14, (255, 140, 40)), (9, (255, 200, 60)),
                       (5, (255, 240, 180))]:
            dr.ellipse([x0 + cx - r, cy - r, x0 + cx + r, cy + r], fill=col)
    chip(dr, x0 + 8, y0 + 8, 118, 20, (178, 34, 34))
    dr.text((x0 + 14, y0 + 11), "3 BRIDGES HIT", font=sans_b(11),
            fill=(255, 255, 255))


def art_akvan(dr, x0, y0, x1, y1):
    """Cyclone spiral over a simplified east coast of India."""
    dr.rectangle([x0, y0, x1, y1], fill=(214, 234, 248))
    # land mass (east coast)
    coast = [(x0, y1), (x0, y0 + 34), (x0 + 52, y0 + 26), (x0 + 92, y0 + 44),
             (x0 + 118, y0 + 66), (x0 + 128, y0 + 92), (x0 + 104, y1)]
    dr.polygon(coast, fill=(168, 208, 160))
    dr.line(coast[:5], fill=(90, 140, 85), width=2)
    # cyclone spiral: concentric arcs, tightening inward
    cx, cy = x0 + 208, y0 + 52
    for i, r in enumerate([46, 38, 30, 22, 14]):
        start = 200 + i * 55
        dr.arc([cx - r, cy - r, cx + r, cy + r], start, start + 250,
               fill=(255, 255, 255) if i % 2 == 0 else (120, 170, 220),
               width=6)
    dr.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255),
               outline=(120, 170, 220))
    # rain streaks
    for rx in range(x0 + 140, x1 - 8, 18):
        dr.line([rx, y0 + 8, rx - 6, y0 + 22], fill=(140, 180, 220), width=2)
    # landfall marker
    dr.ellipse([x0 + 116, y0 + 58, x0 + 128, y0 + 70], fill=(178, 34, 34))
    dr.text((x0 + 132, y0 + 58), "GOPALPUR", font=sans_b(10), fill=INK)
    chip(dr, x0 + 8, y0 + 8, 118, 20, (36, 113, 163))
    dr.text((x0 + 14, y0 + 11), "LANDFALL 8 AM", font=sans_b(11),
            fill=(255, 255, 255))


def art_markets(dr, x0, y0, x1, y1):
    """Friday's closes: four falling indices with a plunging line."""
    dr.rectangle([x0, y0, x1, y1], fill=(250, 244, 244))
    dr.rectangle([x0, y0, x1, y0 + 18], fill=(178, 34, 34))
    dr.text((x0 + 10, y0 + 2), "FRIDAY'S CLOSE", font=sans_b(11),
            fill=(255, 255, 255))
    rows = [("TAIPEI", "\u22126.2%", 62), ("SEOUL", "\u22125.2%", 52),
            ("TOKYO", "\u22125.1%", 51), ("H. KONG", "\u22121.9%", 19)]
    y = y0 + 24
    for name, val, pct in rows:
        dr.text((x0 + 10, y), name, font=sans_b(10), fill=INK)
        bar_w = int((x1 - x0 - 150) * pct / 62)
        dr.rectangle([x0 + 78, y + 2, x0 + 78 + bar_w, y + 11],
                     fill=(205, 80, 80))
        dr.text((x1 - 52, y - 1), val, font=sans_b(12), fill=RED)
        y += 17


def art_flags(dr, x0, y0, x1, y1):
    """EU stars beside a Union Jack, joined by a link."""
    dr.rectangle([x0, y0, x1, y1], fill=(232, 240, 248))
    # EU flag
    dr.rectangle([x0 + 12, y0 + 12, x0 + 82, y0 + 52], fill=(0, 51, 153))
    import math
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        sx = x0 + 47 + int(13 * math.cos(a))
        sy = y0 + 32 + int(13 * math.sin(a))
        dr.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    # Union Jack (simplified)
    dr.rectangle([x0 + 100, y0 + 12, x0 + 170, y0 + 52], fill=(1, 33, 105))
    dr.line([x0 + 100, y0 + 12, x0 + 170, y0 + 52], fill=(255, 255, 255),
            width=6)
    dr.line([x0 + 170, y0 + 12, x0 + 100, y0 + 52], fill=(255, 255, 255),
            width=6)
    dr.line([x0 + 100, y0 + 12, x0 + 170, y0 + 52], fill=(200, 16, 46),
            width=2)
    dr.line([x0 + 170, y0 + 12, x0 + 100, y0 + 52], fill=(200, 16, 46),
            width=2)
    dr.rectangle([x0 + 130, y0 + 12, x0 + 140, y0 + 52], fill=(255, 255, 255))
    dr.rectangle([x0 + 100, y0 + 27, x0 + 170, y0 + 37], fill=(255, 255, 255))
    dr.rectangle([x0 + 133, y0 + 12, x0 + 137, y0 + 52], fill=(200, 16, 46))
    dr.rectangle([x0 + 100, y0 + 30, x0 + 170, y0 + 34], fill=(200, 16, 46))
    # link between the flags
    dr.line([x0 + 82, y0 + 32, x0 + 100, y0 + 32], fill=(39, 174, 96),
            width=4)
    dr.text((x0 + 12, y1 - 18), "RESET DEAL", font=sans_b(10),
            fill=(36, 113, 163))


def art_cop(dr, x0, y0, x1, y1):
    """A globe under a hot sun, with an empty chair of talks."""
    dr.rectangle([x0, y0, x1, y1], fill=(232, 245, 233))
    cx, cy, r = x0 + 48, y0 + 36, 26
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 180, 220),
               outline=(36, 113, 163), width=2)
    dr.ellipse([cx - 14, cy - 12, cx + 2, cy + 2], fill=(120, 200, 130))
    dr.ellipse([cx + 2, cy + 4, cx + 16, cy + 18], fill=(120, 200, 130))
    # sun
    sx, sy = x1 - 34, y0 + 22
    dr.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=(245, 176, 65))
    for dx, dy in [(0, -16), (12, -12), (16, 0), (12, 12), (0, 16),
                   (-12, 12), (-16, 0), (-12, -12)]:
        dr.line([sx, sy, sx + dx, sy + dy], fill=(245, 176, 65), width=2)
    # draft page with the fossil line struck out
    dr.rectangle([x0 + 92, y0 + 12, x1 - 12, y1 - 16], fill=(255, 255, 255),
                 outline=(180, 180, 170))
    for i in range(3):
        ly = y0 + 20 + i * 8
        dr.line([x0 + 98, ly, x1 - 20, ly], fill=(190, 190, 180), width=2)
    dr.text((x0 + 98, y0 + 42), "FOSSIL", font=sans_b(9), fill=(160, 160, 150))
    dr.line([x0 + 96, y0 + 48, x1 - 22, y0 + 48], fill=(178, 34, 34),
            width=2)


def art_poland(dr, x0, y0, x1, y1):
    """A field under a sky with jets scrambled."""
    dr.rectangle([x0, y0, x1, y1], fill=(214, 234, 248))
    dr.rectangle([x0, y1 - 26, x1, y1], fill=(120, 180, 110))
    # field furrows
    for fx in range(x0 + 8, x1 - 8, 16):
        dr.line([fx, y1 - 26, fx + 6, y1 - 4], fill=(95, 150, 88), width=2)
    # two missile trails + one drone
    for mx, my in [(x0 + 52, y0 + 26), (x0 + 118, y0 + 18)]:
        dr.line([mx, my, mx - 26, my - 12], fill=(200, 200, 200), width=2)
        dr.polygon([(mx, my - 4), (mx + 12, my), (mx, my + 4)],
                   fill=(120, 120, 130))
    dr.ellipse([x0 + 158, y0 + 34, x0 + 172, y0 + 40], fill=(80, 80, 90))
    dr.line([x0 + 150, y0 + 37, x0 + 180, y0 + 37], fill=(80, 80, 90),
            width=2)
    # jet silhouette
    jx, jy = x0 + 60, y0 + 44
    dr.polygon([(jx, jy), (jx + 26, jy + 6), (jx + 26, jy + 10),
                (jx + 6, jy + 10), (jx, jy + 14)], fill=(36, 68, 110))
    chip(dr, x0 + 8, y0 + 6, 104, 18, (36, 68, 110))
    dr.text((x0 + 13, y0 + 8), "NATO JETS UP", font=sans_b(10),
            fill=(255, 255, 255))


def art_strike(dr, x0, y0, x1, y1):
    """A marching crowd with placards under an Italian tricolour."""
    dr.rectangle([x0, y0, x1, y1], fill=(252, 248, 235))
    dr.rectangle([x0, y0, x0 + 14, y1], fill=(0, 146, 70))
    dr.rectangle([x0 + 14, y0, x0 + 28, y1], fill=(255, 255, 255))
    dr.rectangle([x0 + 28, y0, x0 + 42, y1], fill=(206, 43, 55))
    # marchers: heads + bodies + placards
    for i, mx in enumerate(range(x0 + 56, x1 - 20, 26)):
        dr.ellipse([mx - 5, y0 + 26, mx + 5, y0 + 36], fill=(230, 190, 150))
        dr.rectangle([mx - 6, y0 + 37, mx + 6, y1 - 12],
                     fill=[(178, 34, 34), (36, 113, 163), (39, 174, 96),
                           (196, 120, 20)][i % 4])
        if i % 2 == 0:
            dr.rectangle([mx + 8, y0 + 10, mx + 26, y0 + 24],
                         fill=(255, 255, 255), outline=INK)
            dr.line([mx + 17, y0 + 24, mx + 17, y0 + 38], fill=INK, width=2)


def art_cpi(dr, x0, y0, x1, y1):
    """A rising price line with the 2.3% figure."""
    dr.rectangle([x0, y0, x1, y1], fill=(235, 245, 251))
    dr.text((x0 + 10, y0 + 6), "2.3%", font=sans_b(24), fill=(36, 113, 163))
    dr.text((x0 + 86, y0 + 16), "OCT CPI", font=sans_b(10), fill=GREY)
    pts = [(x0 + 12, y1 - 16), (x0 + 55, y1 - 26), (x0 + 95, y1 - 22),
           (x0 + 135, y1 - 38), (x0 + 175, y1 - 46)]
    dr.line(pts, fill=(178, 34, 34), width=3)
    for px, py in pts:
        dr.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(178, 34, 34))
    # arrow head
    dr.polygon([(x0 + 175, y1 - 46), (x0 + 163, y1 - 46), (x0 + 172, y1 - 56)],
               fill=(178, 34, 34))


def art_court(dr, x0, y0, x1, y1):
    """A courthouse facade with a gavel."""
    dr.rectangle([x0, y0, x1, y1], fill=(238, 238, 240))
    # pediment
    dr.polygon([(x0 + 30, y0 + 30), (x0 + 95, y0 + 8), (x0 + 160, y0 + 30)],
               fill=(93, 109, 126))
    dr.rectangle([x0 + 26, y0 + 30, x0 + 164, y0 + 36], fill=(70, 85, 100))
    for cx in (44, 74, 104, 134):
        dr.rectangle([x0 + cx, y0 + 38, x0 + cx + 10, y1 - 14],
                     fill=(150, 160, 170))
    dr.rectangle([x0 + 26, y1 - 14, x0 + 164, y1 - 8], fill=(70, 85, 100))
    # gavel
    dr.rectangle([x0 + 178, y0 + 40, x0 + 206, y0 + 50], fill=(120, 72, 30))
    dr.line([x0 + 192, y0 + 50, x0 + 192, y1 - 12], fill=(120, 72, 30),
            width=4)
    dr.rectangle([x0 + 178, y1 - 14, x0 + 206, y1 - 8], fill=(120, 72, 30))


def art_cricket(dr, x0, y0, x1, y1):
    """A bat, a ball and the 118 on a green outfield."""
    dr.rectangle([x0, y0, x1, y1], fill=(220, 240, 215))
    dr.ellipse([x0 + 20, y0 + 44, x1 - 20, y1 - 8], fill=(180, 215, 165))
    # stumps
    for sx in (x0 + 40, x0 + 48, x0 + 56):
        dr.rectangle([sx, y0 + 26, sx + 4, y0 + 48], fill=(220, 180, 120))
    # bat
    dr.polygon([(x0 + 84, y0 + 14), (x0 + 96, y0 + 14), (x0 + 100, y0 + 44),
                (x0 + 88, y0 + 44)], fill=(210, 170, 110))
    dr.rectangle([x0 + 88, y0 + 6, x0 + 93, y0 + 16], fill=(120, 80, 40))
    # ball
    dr.ellipse([x0 + 120, y0 + 18, x0 + 134, y0 + 32], fill=(178, 34, 34))
    dr.text((x0 + 148, y0 + 22), "118", font=sans_b(26), fill=INK)
    dr.text((x0 + 148, y0 + 50), "RUNS", font=sans_b(10), fill=GREY)


def art_oil(dr, x0, y0, x1, y1):
    """A drilling derrick against a dry Turkana sky."""
    dr.rectangle([x0, y0, x1, y1], fill=(250, 240, 220))
    dr.ellipse([x1 - 40, y0 + 10, x1 - 16, y0 + 34], fill=(245, 176, 65))
    dr.rectangle([x0, y1 - 14, x1, y1], fill=(190, 160, 110))
    # derrick: two legs + cross braces
    bx, by = x0 + 60, y1 - 14
    dr.line([bx - 34, by, bx + 6, y0 + 12], fill=(90, 70, 50), width=4)
    dr.line([bx + 34, by, bx + 6, y0 + 12], fill=(90, 70, 50), width=4)
    for t in (0.25, 0.5, 0.75):
        yl = by - (by - (y0 + 12)) * t
        half = 34 * (1 - t) + 2
        dr.line([bx - half + 6, yl, bx + half + 6, yl], fill=(90, 70, 50),
                width=2)
    dr.rectangle([bx, y0 + 8, bx + 12, y0 + 14], fill=(90, 70, 50))
    # drill pipe + oil drop
    dr.line([bx + 6, y0 + 14, bx + 6, by], fill=(60, 45, 30), width=3)
    dr.ellipse([x0 + 150, y0 + 40, x0 + 172, y0 + 62], fill=(40, 40, 50))
    dr.polygon([(x0 + 161, y0 + 28), (x0 + 150, y0 + 48),
                (x0 + 172, y0 + 48)], fill=(40, 40, 50))
    dr.text((x0 + 148, y1 - 30), "1 DEC", font=sans_b(10), fill=(90, 70, 50))


def art_iraq(dr, x0, y0, x1, y1):
    """A convoy on a desert road toward a town."""
    dr.rectangle([x0, y0, x1, y1], fill=(245, 235, 210))
    dr.rectangle([x0, y1 - 22, x1, y1], fill=(200, 175, 130))
    dr.line([x0, y1 - 12, x1, y1 - 12], fill=(255, 255, 255), width=2)
    # town silhouette
    dr.rectangle([x1 - 66, y0 + 22, x1 - 20, y1 - 22], fill=(170, 150, 110))
    dr.rectangle([x1 - 52, y0 + 10, x1 - 44, y0 + 24], fill=(170, 150, 110))
    # convoy trucks
    for tx in (x0 + 14, x0 + 62, x0 + 110):
        dr.rectangle([tx, y0 + 36, tx + 34, y0 + 52], fill=(90, 110, 80))
        dr.rectangle([tx + 34, y0 + 42, tx + 44, y0 + 52], fill=(70, 90, 65))
        for wx in (tx + 6, tx + 22, tx + 38):
            dr.ellipse([wx, y0 + 50, wx + 8, y0 + 58], fill=(40, 40, 40))
        dr.line([tx + 17, y0 + 24, tx + 17, y0 + 36], fill=(60, 60, 60),
                width=2)
        dr.rectangle([tx + 17, y0 + 24, tx + 27, y0 + 30], fill=(178, 34, 34))

ART = {
    "kyiv": art_kyiv, "akvan": art_akvan, "markets": art_markets,
    "flags": art_flags, "cop": art_cop, "poland": art_poland,
    "strike": art_strike, "cpi": art_cpi, "court": art_court,
    "cricket": art_cricket, "oil": art_oil, "iraq": art_iraq,
}


# ---------------------------------------------------------------- world map
# Schematic continents, drawn from rough shapes (not traced from any
# source). Pins 1-12 mark the hero and card stories.
CONTINENTS = [
    # North America
    [(6, 28), (52, 14), (104, 20), (128, 44), (112, 66), (84, 62),
     (70, 84), (46, 92), (22, 78), (6, 56)],
    # South America
    [(88, 100), (122, 98), (138, 122), (124, 160), (106, 178),
     (96, 148), (84, 122)],
    # Europe
    [(140, 26), (176, 18), (198, 30), (192, 52), (168, 58), (146, 48)],
    # Africa
    [(148, 66), (192, 60), (212, 84), (204, 118), (182, 148),
     (162, 128), (148, 98)],
    # Asia
    [(202, 18), (262, 12), (296, 26), (292, 58), (262, 78), (228, 86),
     (208, 66), (200, 42)],
    # Australia
    [(248, 128), (288, 124), (296, 150), (272, 166), (246, 152)],
]

# pin positions (map-local), story number -> (x, y)
PINS = {
    1: (186, 40),    # Kyiv
    2: (246, 74),    # Odisha
    3: (278, 62),    # Taipei / Seoul / Tokyo
    4: (154, 38),    # Brussels
    5: (182, 56),    # Antalya
    6: (170, 30),    # Poland
    7: (158, 54),    # Italy
    8: (292, 44),    # Tokyo (shares the East Asia cluster)
    9: (268, 44),    # Seoul
    10: (294, 164),  # Wellington
    11: (184, 104),  # Turkana
    12: (206, 62),   # Iraq
}


def draw_map(dr, x0, y0, x1, y1):
    dr.rectangle([x0, y0, x1, y1], fill=(214, 234, 248),
                 outline=LIGHT_LINE)
    for poly in CONTINENTS:
        pts = [(x0 + px, y0 + py) for px, py in poly]
        dr.polygon(pts, fill=(196, 220, 180), outline=(140, 180, 130))
    for num, (px, py) in PINS.items():
        cx, cy = x0 + px, y0 + py
        dr.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=NAVY,
                   outline=(255, 255, 255), width=1)
        label = str(num)
        f = sans_b(8)
        dr.text((cx - f.getlength(label) / 2, cy - 6), label, font=f,
                fill=(255, 255, 255))


# ---------------------------------------------------------------- compose
def compose():
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # ---- top bar
    dr.rectangle([0, 0, W, 20], fill=NAVY)
    dr.text((MARGIN, 3), "THE WORLD IN ONE DAY", font=sans_b(11),
            fill=(255, 255, 255))
    right = "24 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    f_top = sans_b(11)
    dr.text((W - MARGIN - f_top.getlength(right), 3), right, font=f_top,
            fill=(200, 215, 235))

    # ---- masthead + subtitle
    text_center(dr, W // 2, 23, "Friday 20 November 2026", serif_b(40), INK)
    text_center(dr, W // 2, 66, SUBTITLE, sans(13), (70, 70, 80))
    dr.line([MARGIN, 86, W - MARGIN, 86], fill=LIGHT_LINE, width=1)

    # ---- stat strip
    cell_w = CW / 6
    for i, (num, label) in enumerate(STATS):
        cx = MARGIN + cell_w * i + cell_w / 2
        text_center(dr, cx, 92, num, sans_b(22), NAVY)
        for j, line in enumerate(wrap(label, sans(10), cell_w - 12)):
            text_center(dr, cx, 118 + j * 12, line, sans(10), GREY)
        if i:
            x = MARGIN + cell_w * i
            dr.line([x, 94, x, 138], fill=LIGHT_LINE, width=1)

    # ---- region bar
    reg_w = CW / 7
    for i, (name, count, color) in enumerate(REGION_COLORS):
        x0 = MARGIN + reg_w * i
        label = "%s \u00b7 %d" % (name, count)
        f_reg = sans_b(11)
        dr.text((x0 + (reg_w - f_reg.getlength(label)) / 2, 144), label,
                font=f_reg, fill=color)
        dr.rectangle([x0 + 4, 160, x0 + reg_w - 4, 163], fill=color)

    # ---- heroes (3 columns)
    hero_w, hero_gap = 324, 12
    for i, hero in enumerate(HEROES):
        x0 = MARGIN + i * (hero_w + hero_gap)
        x1 = x0 + hero_w
        ART[hero["art"]](dr, x0, 168, x1, 256)
        dr.rectangle([x0, 168, x1, 256], outline=LIGHT_LINE)
        dr.text((x0, 261), hero["kicker"], font=sans_b(10),
                fill=hero["color"])
        draw_lines(dr, wrap(hero["headline"], sans_b(16), hero_w), x0, 275,
                   sans_b(16), INK, 19)
        draw_lines(dr, wrap(hero["body"], sans(11), hero_w), x0, 315,
                   sans(11), (50, 50, 60), 13)

    # ---- cards row 1 (5) and row 2 (4)
    def card_row(cards, y_img, ncols, gap):
        cw = (CW - gap * (ncols - 1)) / ncols
        for i, card in enumerate(cards):
            x0 = MARGIN + i * (cw + gap)
            x1 = x0 + cw
            ART[card["art"]](dr, int(x0), y_img, int(x1), y_img + 70)
            dr.rectangle([int(x0), y_img, int(x1), y_img + 70],
                         outline=LIGHT_LINE)
            dr.text((x0, y_img + 75), card["kicker"], font=sans_b(9),
                    fill=card["color"])
            draw_lines(dr, wrap(card["headline"], sans_b(12), cw), x0,
                       y_img + 88, sans_b(12), INK, 15)
            draw_lines(dr, wrap(card["body"], sans(10), cw), x0, y_img + 120,
                       sans(10), (50, 50, 60), 12)

    card_row(CARDS[:5], 362, 5, 10)
    card_row(CARDS[5:], 527, 4, 11)

    # ---- lower section headers
    dr.text((MARGIN, 692), "WHERE IT HAPPENED", font=sans_b(12), fill=NAVY)
    dr.text((330, 692), "ALSO ON FRIDAY 20 NOVEMBER \u2014 12 MORE STORIES",
            font=sans_b(12), fill=NAVY)
    dr.line([MARGIN, 710, W - MARGIN, 710], fill=LIGHT_LINE, width=1)

    # ---- map (left) + briefs (right, 2 columns x 6 rows)
    draw_map(dr, MARGIN, 714, 320, 898)
    dr.text((MARGIN, 900), "Each number is that story on this page.",
            font=sans(9), fill=GREY)
    brief_w = 335
    for idx, (num, place, text) in enumerate(BRIEFS):
        col, row = idx % 2, idx // 2
        x0 = 330 + col * (brief_w + 10)
        y0 = 714 + row * 30
        chip(dr, x0, y0 + 1, 20, 15, NAVY)
        f_num = sans_b(9)
        dr.text((x0 + (20 - f_num.getlength(num)) / 2, y0 + 2), num,
                font=f_num, fill=(255, 255, 255))
        head = place + " \u2014 "
        dr.text((x0 + 24, y0), head, font=sans_b(10), fill=INK)
        hw = sans_b(10).getlength(head)
        first = wrap(text, sans(10), brief_w - 24 - hw)
        rest = []
        if first:
            dr.text((x0 + 24 + hw, y0), first[0], font=sans(10),
                    fill=(50, 50, 60))
            rest = first[1:]
        if rest:
            draw_lines(dr, wrap(" ".join(rest), sans(10), brief_w - 24),
                       x0 + 24, y0 + 13, sans(10), (50, 50, 60), 12)

    # ---- DATE CHECK box
    box_y0, box_y1 = 916, 968
    dr.rectangle([MARGIN, box_y0, W - MARGIN, box_y1], fill=(255, 248, 225),
                 outline=(200, 170, 90))
    dr.text((MARGIN + 10, box_y0 + 6), "DATE CHECK", font=sans_b(11),
            fill=(140, 90, 10))
    title_w = sans_b(11).getlength("DATE CHECK  ")
    f_dc = sans(10)
    first = wrap(DATE_CHECK, f_dc, CW - 20 - title_w)
    dr.text((MARGIN + 10 + title_w, box_y0 + 6), first[0], font=f_dc,
            fill=(60, 50, 30))
    if len(first) > 1:
        draw_lines(dr, first[1:], MARGIN + 10, box_y0 + 20, f_dc,
                   (60, 50, 30), 12)

    # ---- footer
    text_center(dr, W // 2, 984,
                "Every story here happened, or was first reported, on "
                "Friday 20 November 2026. Officials\u2019 counts are attributed.",
                sans(10), GREY)
    text_center(dr, W // 2, 998,
                "Sources named beside each story \u00b7 original drawings",
                sans(9), GREY)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = compose()
    img.save(out, format="PNG")
    size = os.path.getsize(out)
    print("wrote %s (%d bytes, %dx%d)" % (out, size, img.width, img.height))
    if size > 1024 * 1024:
        print("WARNING: over the 1 MiB gate")
        sys.exit(1)


if __name__ == "__main__":
    main()
