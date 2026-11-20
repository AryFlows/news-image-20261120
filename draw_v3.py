#!/usr/bin/env python3
"""draw_v3.py — news-image-20261120 v3: "Friday 20 November 2026 — One Image v3".

One 1024x1024 front page summing up Friday 20 November 2026: 34 stories,
every one verified as having happened (or first been reported) on that day,
across 7 regions. Drawn 100% in code with PIL — no photos, no outside art.

Deterministic: no randomness, no timestamps, no network. Run twice and the
PNG bytes are identical.

Usage: python3 draw_v3.py   # writes entry.png next to this file
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14                      # page margin
CW = W - 2 * M              # content width = 996

PAPER = (247, 243, 232)
INK = (17, 17, 17)
MUTED = (90, 86, 76)
RED = (185, 28, 28)
RULE = (40, 40, 40)
CARD_BG = (255, 253, 247)

REGION_COLORS = {
    "Europe": (36, 80, 122),
    "Asia-Pacific": (166, 58, 46),
    "Middle East": (192, 138, 30),
    "Africa": (46, 125, 79),
    "Americas": (106, 74, 158),
    "Oceania": (31, 138, 140),
    "Global": (107, 107, 107),
}
REGIONS = [("Europe", 10), ("Asia-Pacific", 6), ("Middle East", 4),
           ("Africa", 4), ("Americas", 4), ("Oceania", 2), ("Global", 5)]

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- data
# Every story below was checked against reporting dated Friday 20 Nov 2026.
# Figures that v2 got slightly wrong are fixed here: Akvan evacuations
# 300,000+ (not 370,000+), Hang Seng -2.2% (not -1.7%), Xi's phrase was
# "comprehensive turnaround" (not "full turnaround").

STATS = [
    ("3", "bridges over the Dnipro\ndamaged in Kyiv"),
    ("300,000+", "people moved to shelters\nbefore Akvan"),
    ("\u22126.6%", "Taiwan's share index,\nFriday's close"),
    ("100,000", "youth visas a year in\nthe UK\u2013EU deal"),
    ("2.3%", "Japan consumer inflation\nin October"),
    ("118", "runs by Glenn Phillips\nagainst India"),
]

HEROES = [
    dict(num=1, kicker="KYIV, UKRAINE \u00b7 WAR", art="kyiv",
         head="Russian missiles hit three Kyiv bridges",
         body="An overnight barrage of 110+ missiles and 400 drones killed at "
              "least eight across Ukraine and cut power and water in the "
              "capital. (Reuters, Kyiv Independent)"),
    dict(num=2, kicker="ODISHA, INDIA \u00b7 CYCLONE", art="akvan",
         head="Cyclone Akvan comes ashore in eastern India",
         body="The storm crossed the coast near Gopalpur from about 8 am; "
              "300,000+ people were moved to shelters. No deaths were "
              "reported. (IMD, Reuters)"),
    dict(num=3, kicker="TAIPEI \u00b7 SEOUL \u00b7 TOKYO \u00b7 MARKETS", art="selloff",
         head="AI sell-off sinks Asia's stock markets",
         body="Taiwan's index fell 6.6% to its worst week since 1991; Seoul "
              "lost 5.2% and Tokyo 4.8% as chipmakers led the slide. "
              "(Reuters, Aju Press)"),
]

CARDS = [
    dict(num=4, kicker="BRUSSELS \u00b7 DIPLOMACY", art="ukeu",
         head="UK and EU seal a \u201creset\u201d deal",
         body="Food trade, youth visas and a carbon link; PM Burnham calls "
              "it \u201cwin-win\u201d. (Reuters, gov.uk)"),
    dict(num=5, kicker="ANTALYA \u00b7 CLIMATE", art="cop31",
         head="COP31 reaches its last day with no deal",
         body="Draft text leaves out fossil fuels and the $120bn figure. "
              "(UN News, Carbon Brief)"),
    dict(num=6, kicker="EASTERN POLAND \u00b7 SECURITY", art="poland",
         head="Russian objects cross into Poland",
         body="Two missiles and a drone came down; NATO jets scrambled, no "
              "one hurt. (Reuters, Polish MoD)"),
    dict(num=7, kicker="ITALY \u00b7 LABOUR", art="italy",
         head="General strike over Italy's budget",
         body="CGIL stoppage brings marches to 100+ cities; 1m+ out, the "
              "union says. (Reuters, AP)"),
    dict(num=8, kicker="TOKYO \u00b7 ECONOMY", art="japan",
         head="Japan inflation picks up to 2.3%",
         body="October CPI, highest in a year; a December rate rise stays "
              "in view. (Statistics Bureau)"),
    dict(num=9, kicker="SEOUL \u00b7 POLITICS", art="seoul",
         head="Korea's ruling party to impeach top judge",
         body="DP adopts the move after the court partly cleared ex-PM Han. "
              "(Yonhap)"),
    dict(num=10, kicker="WELLINGTON \u00b7 CRICKET", art="cricket",
         head="Phillips hits 118 against India",
         body="First man with centuries in all three formats vs India in a "
              "year. (Reuters, ICC)"),
    dict(num=11, kicker="TURKANA, KENYA \u00b7 ENERGY", art="kenya",
         head="Kenya starts drilling its first oil well",
         body="Rig switched on at Amosing; first crude due on 1 December. "
              "(Capital FM)"),
    dict(num=12, kicker="CENTRAL IRAQ \u00b7 SECURITY", art="iraq",
         head="Iraqi army enters a militia stronghold",
         body="Troops deploy to Jurf al-Sakhar under a deal with Kataib "
              "Hezbollah. (Reuters)"),
]

# (number, place, rest of item) — each item wraps to at most 2 lines.
# Fix 21 Nov: #31/#32 replaced — the US Senate permitting vote and the
# Argentina disability law both happened Thu 19 Nov, not Fri 20 Nov.
# Replacements verified as Friday 20 Nov events: the UK-EU Youth Experience
# Scheme (summit agreement, Reuters) and Doerkson's swearing-in as BC premier
# (Canadian Press). Both removed stories are now DATE CHECK exclusions.
LIST_ITEMS = [
    (13, "Shenzhen", "Xi hails \u201ccomprehensive turnaround\u201d in ties with "
     "Australia; 2027 tourism year (Reuters)"),
    (14, "Lviv", "Strike on Skniliv railway station kills two, ten in "
     "hospital (Mayor Sadovyi)"),
    (15, "Blantyre", "Malawi fuel queues stretch overnight; petrol $3.24 a "
     "litre, rationed (Al Jazeera)"),
    (16, "Mercury", "BepiColombo reaches Mercury after 8 years; orbit burn "
     "set for Saturday (ESA)"),
    (17, "Hormuz", "Tanker struck off Khasab catches fire; no casualties, "
     "no spill (UKMTO, Reuters)"),
    (18, "Beijing", "China holds loan rates for an 18th month: 1-yr 3.0%, "
     "5-yr 3.5% (PBOC)"),
    (19, "Las Vegas", "Russell fastest in wet F1 practice, 1:47.272, ahead "
     "of Gasly (Formula1.com)"),
    (20, "Turin", "Alcaraz beats Cobolli 6-4, 6-1, tops ATP Finals group "
     "unbeaten (ATP)"),
    (21, "Antalya", "France and Panama lead bloc demanding fossil-fuel "
     "language at COP31 (UN News)"),
    (22, "Kharkiv", "Drone hits a hospital; at least four hurt in overnight "
     "strikes (Reuters)"),
    (23, "Florida", "St Johns River hits record 18.7 ft near Cocoa; 100+ "
     "rescues (NWS)"),
    (24, "Global", "UN marks World Children's Day across member states "
     "(UN News)"),
    (25, "Brussels", "EU Council adopts \u20ac1bn in military aid for Ukraine "
     "(Council of the EU)"),
    (26, "Europe", "Students march in 25+ countries over living costs, "
     "militarisation (AP)"),
    (27, "Riyadh", "Saudi intercepts Houthi missile and five drones; "
     "capital targeted (AP)"),
    (28, "Gulf of Aden", "Gunfire reported near bulk carrier off Yemen; no "
     "damage (UKMTO)"),
    (29, "Mogadishu", "Thousands rally backing expulsion of UAE ambassador "
     "(Dawan)"),
    (30, "South Africa", "Nearly 600 women killed in three months, police "
     "figures show (OkayAfrica)"),
    (31, "London", "UK\u2013EU youth scheme agreed: 100,000 places a year each "
     "way, ages 18\u201331 (Reuters)"),
    (32, "Victoria", "Doerkson sworn in as BC's 38th premier; first Tory "
     "government in ~100 years (CP)"),
    (33, "Cook Islands", "Cyclone Xavier weakens near northern islands; gales "
     "hold (MetService)"),
    (34, "Gold", "Gold falls ~4% as dollar and yields stay high; 10-yr "
     "above 5% (CNBC)"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Left out as 18\u201319 November news: the Shenzhen summit \u00b7 the ICJ "
    "Myanmar ruling \u00b7 Trump's Iran delay \u00b7 Voyager 1's light-day \u00b7 Bukele's filing \u00b7 "
    "Anthropic's IPO \u00b7 Wall Street's 2% fall \u00b7 the Senate's Iran vote \u00b7 the Haiti "
    "raid \u00b7 the Riyadh tower strike \u00b7 the Berlin summit \u00b7 the Gaza Yellow Line "
    "raid \u00b7 Jepchirchir's ban \u00b7 Somalia's expulsion \u00b7 Zimbabwe's landmines \u00b7 "
    "Japan Tobacco's charge \u00b7 the US Senate permitting vote (Thu 19 Nov) \u00b7 "
    "Argentina's disability law (Thu 19 Nov). Not yet happened: BepiColombo's orbit burn (Saturday) "
    "and any final COP31 text."
)

# Map pins: story number -> (lon, lat, dx, dy) nudge in px.
PINS = {
    1: (30.5, 50.4, 0, 0), 2: (84.9, 19.3, 0, 0), 3: (121.6, 25.0, 0, 0),
    4: (4.4, 50.8, -4, -2), 5: (30.7, 36.9, 2, 2), 6: (23.0, 51.5, 0, -6),
    7: (12.5, 41.9, -3, 3), 8: (139.7, 35.7, 0, 0), 9: (127.0, 37.5, 0, 0),
    10: (174.8, -41.3, 0, 0), 11: (36.0, 3.5, 0, 0), 12: (44.2, 32.9, 0, 0),
    13: (114.1, 22.5, 0, 4), 14: (24.0, 49.8, -2, 6), 15: (35.0, -15.8, 0, 0),
    17: (56.5, 26.5, 0, 0), 18: (116.4, 39.9, 0, -4), 19: (-115.1, 36.2, 0, 0),
    20: (7.7, 45.1, 2, -4), 21: (30.7, 36.9, -8, -6), 22: (36.2, 50.0, 6, 0),
    23: (-80.9, 28.4, 0, 0), 25: (4.4, 50.8, 5, 6), 26: (13.4, 52.5, 0, -4),
    27: (46.7, 24.7, 0, 0), 28: (49.5, 13.0, 0, 0), 29: (45.3, 2.0, 0, 0),
    30: (28.0, -26.2, 0, 0), 31: (-0.1, 51.5, -14, 10), 32: (-123.4, 48.4, -6, -4),
    33: (-160.0, -10.0, 0, 0),
}


# ---------------------------------------------------------------- helpers
def wrap(d, text, font, width):
    """Greedy word wrap; returns list of lines that fit `width`."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def chip(d, x, y, text, font, fg=(255, 255, 255), bg=RED, pad_x=6, pad_y=2):
    w = d.textlength(text, font=font) + 2 * pad_x
    h = font.size + 2 * pad_y + 2
    d.rectangle([x, y, x + w, y + h], fill=bg)
    d.text((x + pad_x, y + pad_y), text, font=font, fill=fg)
    return w, h


def num_badge(d, cx, cy, num, r=9):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    f = F(SANS_B, 11 if num < 10 else 10)
    t = str(num)
    d.text((cx - d.textlength(t, font=f) / 2, cy - f.size / 2 - 1),
           t, font=f, fill=(255, 255, 255))


def skyline(d, x0, y_base, w, heights, color, win_color=(255, 214, 130)):
    """Row of buildings with lit windows; heights is a fixed list."""
    n = len(heights)
    bw = w / n
    for i, h in enumerate(heights):
        x = x0 + i * bw
        d.rectangle([x + 1, y_base - h, x + bw - 1, y_base], fill=color)
        for wy in range(int(y_base - h + 4), int(y_base - 3), 7):
            for wx in (x + 3, x + bw / 2):
                if (i * 7 + int(wy)) % 3 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=win_color)


# ---------------------------------------------------------------- hero art
def art_kyiv(d, x, y, w, h):
    # Night sky: layered bands + stars.
    for i in range(5):
        d.rectangle([x, y + i * h // 5, x + w, y + (i + 1) * h // 5 + 1],
                    fill=(16 + i * 4, 32 + i * 5, 66 + i * 6))
    for sx, sy in [(18, 8), (52, 16), (96, 6), (150, 14), (210, 8),
                   (262, 18), (300, 6), (120, 22), (180, 4), (240, 24)]:
        d.ellipse([x + sx, y + sy, x + sx + 1.6, y + sy + 1.6],
                  fill=(255, 255, 220))
    # Moon.
    d.ellipse([x + w - 34, y + 8, x + w - 16, y + 26], fill=(240, 238, 210))
    d.ellipse([x + w - 30, y + 10, x + w - 18, y + 22], fill=(30, 48, 88))
    # Skyline on both banks.
    skyline(d, x, y + h - 30, w, [26, 34, 22, 40, 28, 20, 36, 24, 30, 18, 32, 26],
            (13, 24, 48))
    # River.
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(28, 62, 104))
    for rx in range(6, w, 26):
        d.line([x + rx, y + h - 12, x + rx + 12, y + h - 12],
               fill=(120, 170, 220), width=1)
    # Three bridges across the river.
    for bx, span in [(18, 78), (122, 78), (226, 78)]:
        d.rectangle([x + bx, y + h - 40, x + bx + span, y + h - 36],
                    fill=(210, 205, 190))
        d.arc([x + bx + 8, y + h - 52, x + bx + span - 8, y + h - 34],
              180, 360, fill=(210, 205, 190), width=2)
        for px in range(bx + 12, bx + span - 6, 14):
            d.line([x + px, y + h - 44, x + px, y + h - 38],
                   fill=(210, 205, 190), width=1)
    # Missile trails (dashed arcs) + explosion bursts on each bridge.
    for tx, ty in [(30, 6), (150, 2), (258, 8)]:
        for i in range(6):
            px = x + tx + i * 7
            py = y + ty + i * 5
            d.line([px, py, px + 4, py + 3], fill=(255, 220, 130), width=2)
    for bx in [56, 161, 265]:
        cx, cy = x + bx, y + h - 46
        for r, c in [(16, (255, 120, 30)), (11, (255, 180, 60)),
                     (6, (255, 240, 170))]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        d.polygon([(cx, cy - 20), (cx + 3, cy - 6), (cx + 18, cy - 10),
                   (cx + 6, cy), (cx + 16, cy + 8), (cx, cy + 5),
                   (cx - 16, cy + 8), (cx - 6, cy), (cx - 18, cy - 10),
                   (cx - 3, cy - 6)], fill=(255, 200, 80))
    # Smoke plumes.
    for bx in [56, 161, 265]:
        for i, (ox, oy, r) in enumerate([(0, -26, 7), (5, -34, 9), (-4, -42, 6)]):
            d.ellipse([x + bx + ox - r, y + h - 46 + oy - r,
                       x + bx + ox + r, y + h - 46 + oy + r],
                      fill=(120, 120, 125))
    chip(d, x + 6, y + 6, "KYIV", F(SANS_B, 13))
    d.rectangle([x + 6, y + h - 26, x + 108, y + h - 8], fill=(10, 10, 10))
    d.text((x + 11, y + h - 24), "3 BRIDGES HIT", font=F(SANS_B, 11),
           fill=(255, 255, 255))


def art_akvan(d, x, y, w, h):
    # Sea + sky.
    d.rectangle([x, y, x + w, y + h], fill=(64, 128, 168))
    for i in range(4):
        d.rectangle([x, y + i * h // 4, x + w, y + (i + 1) * h // 4 + 1],
                    fill=(70 + i * 8, 132 + i * 6, 170 - i * 8))
    # Landmass (Odisha coast) bottom-left.
    d.polygon([(x, y + h), (x, y + 52), (x + 70, y + 44), (x + 118, y + 58),
               (x + 150, y + 78), (x + 132, y + h)], fill=(214, 190, 138))
    d.polygon([(x + 4, y + 60), (x + 66, y + 52), (x + 110, y + 64),
               (x + 128, y + 80), (x + 118, y + h), (x + 4, y + h)],
              fill=(168, 148, 96))
    # Cyclone spiral: concentric arcs + rain bands.
    cx, cy = x + w - 78, y + 44
    for r, wd in [(46, 5), (36, 5), (26, 4), (16, 4)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300,
              fill=(255, 255, 255), width=wd)
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340,
              fill=(200, 225, 240), width=wd)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(240, 248, 255))
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(64, 128, 168))
    # Rain streaks.
    for rx, ry in [(150, 12), (180, 30), (205, 8), (232, 26), (258, 12),
                   (282, 34), (300, 18), (140, 44), (168, 58), (196, 52)]:
        d.line([x + rx, y + ry, x + rx - 5, y + ry + 12],
               fill=(220, 235, 245), width=2)
    # Landfall pin at Gopalpur.
    px, py = x + 112, y + 52
    d.ellipse([px - 9, py - 9, px + 9, py + 9], outline=(255, 255, 255), width=2)
    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED)
    d.rectangle([x + 74, y + 64, x + 148, y + 78], fill=(10, 10, 10))
    d.text((x + 79, y + 66), "GOPALPUR", font=F(SANS_B, 9),
           fill=(255, 255, 255))
    # Shelter houses on the coast.
    for hx in (6, 28, 50):
        d.polygon([(x + hx, y + h - 22), (x + hx + 8, y + h - 30),
                   (x + hx + 16, y + h - 22)], fill=(150, 60, 50))
        d.rectangle([x + hx + 2, y + h - 22, x + hx + 14, y + h - 12],
                    fill=(245, 240, 225))
    chip(d, x + 6, y + 6, "CYCLONE AKVAN", F(SANS_B, 13))
    d.rectangle([x + w - 108, y + 6, x + w - 6, y + 24], fill=(10, 10, 10))
    d.text((x + w - 102, y + 8), "LANDFALL 8 AM", font=F(SANS_B, 10),
           fill=(255, 255, 255))
    d.text((x + 8, y + 30), "INDIA", font=F(SANS_B, 10), fill=(255, 255, 255))


def art_selloff(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 16, 20))
    # Grid.
    for gy in range(y + 16, y + h - 8, 16):
        d.line([x + 8, gy, x + w - 8, gy], fill=(38, 42, 50), width=1)
    # Candlesticks falling left to right.
    tops = [18, 24, 20, 32, 30, 42, 40, 52, 50, 62]
    for i, t in enumerate(tops):
        cx = x + 16 + i * 20
        col = (60, 180, 110) if i % 4 == 0 else (220, 60, 50)
        d.line([cx + 5, y + t - 8, cx + 5, y + t + 22], fill=col, width=1)
        d.rectangle([cx, y + t, cx + 10, y + t + 14], fill=col)
    # Falling trend line + arrow.
    pts = [(x + 14, y + 16), (x + 70, y + 30), (x + 130, y + 26),
           (x + 190, y + 52), (x + 250, y + 62), (x + 300, y + 82)]
    d.line(pts, fill=(255, 80, 70), width=3, joint="curve")
    d.polygon([(x + 300, y + 82), (x + 288, y + 78), (x + 294, y + 90)],
              fill=(255, 80, 70))
    # Ticker values.
    tick = [("TAIPEI", "-6.6%"), ("SEOUL", "-5.2%"), ("TOKYO", "-4.8%"),
            ("H. KONG", "-2.2%")]
    ty = y + 8
    for name, val in tick:
        d.text((x + w - 96, ty), name, font=F(SANS_B, 10),
               fill=(200, 200, 200))
        d.text((x + w - 40, ty), val, font=F(SANS_B, 10), fill=(255, 90, 80))
        ty += 15
    chip(d, x + 6, y + 6, "AI SELL-OFF", F(SANS_B, 13))
    d.rectangle([x + 6, y + h - 26, x + 118, y + h - 8], fill=(255, 255, 255))
    d.text((x + 11, y + h - 24), "FRIDAY'S CLOSE", font=F(SANS_B, 11),
           fill=(14, 16, 20))


# ---------------------------------------------------------------- card art
def art_ukeu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    # Union Jack (simplified) left.
    jx, jy, jw, jh = x + 8, y + 8, 62, 40
    d.rectangle([jx, jy, jx + jw, jy + jh], fill=(1, 33, 105))
    d.line([jx, jy, jx + jw, jy + jh], fill=(255, 255, 255), width=5)
    d.line([jx + jw, jy, jx, jy + jh], fill=(255, 255, 255), width=5)
    d.line([jx, jy, jx + jw, jy + jh], fill=(200, 16, 46), width=2)
    d.line([jx + jw, jy, jx, jy + jh], fill=(200, 16, 46), width=2)
    d.rectangle([jx + jw // 2 - 5, jy, jx + jw // 2 + 5, jy + jh],
                fill=(255, 255, 255))
    d.rectangle([jx, jy + jh // 2 - 5, jx + jw, jy + jh // 2 + 5],
                fill=(255, 255, 255))
    d.rectangle([jx + jw // 2 - 2, jy, jx + jw // 2 + 2, jy + jh],
                fill=(200, 16, 46))
    d.rectangle([jx, jy + jh // 2 - 2, jx + jw, jy + jh // 2 + 2],
                fill=(200, 16, 46))
    # EU flag right: blue + circle of stars.
    ex, ey, ew, eh = x + w - 78, y + 8, 70, 40
    d.rectangle([ex, ey, ex + ew, ey + eh], fill=(0, 51, 153))
    import math
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx = ex + ew / 2 + 22 * math.cos(a)
        sy = ey + eh / 2 + 13 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))
    # Handshake bar between.
    d.rectangle([x + 78, y + 20, x + w - 84, y + 36], fill=(46, 125, 79))
    d.text((x + 82, y + 22), "\u2713", font=F(SANS_B, 11), fill=(255, 255, 255))
    chip(d, x + 6, y + 4, "UK\u2013EU DEAL", F(SANS_B, 11))
    d.rectangle([x + w - 62, y + h - 18, x + w - 6, y + h - 4],
                fill=(255, 255, 255))
    d.text((x + w - 56, y + h - 17), "AGREED", font=F(SANS_B, 10), fill=INK)


def art_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 92, 96))
    # Globe.
    cx, cy = x + 34, y + h // 2 + 2
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(120, 190, 220))
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=(255, 255, 255),
              width=2)
    d.polygon([(cx - 14, cy - 6), (cx - 4, cy - 14), (cx + 6, cy - 8),
               (cx + 2, cy + 2), (cx - 8, cy + 4)], fill=(90, 170, 90))
    d.polygon([(cx + 2, cy + 8), (cx + 12, cy + 4), (cx + 14, cy + 14),
               (cx + 4, cy + 16)], fill=(90, 170, 90))
    d.arc([cx - 20, cy - 20, cx + 20, cy + 20], 90, 270,
          fill=(255, 255, 255), width=1)
    # Clock showing last day.
    kx, ky = x + w - 44, y + h // 2 + 2
    d.ellipse([kx - 17, ky - 17, kx + 17, ky + 17], fill=(255, 255, 255))
    d.ellipse([kx - 17, ky - 17, kx + 17, ky + 17], outline=INK, width=2)
    d.line([kx, ky, kx, ky - 11], fill=INK, width=2)
    d.line([kx, ky, kx + 9, ky + 3], fill=INK, width=2)
    d.ellipse([kx - 2, ky - 2, kx + 2, ky + 2], fill=RED)
    # Crossed-out fuel drop between.
    mx, my = x + w // 2 + 6, y + h // 2 + 2
    d.polygon([(mx, my - 12), (mx + 9, my + 2), (mx + 5, my + 10),
               (mx - 5, my + 10), (mx - 9, my + 2)], fill=(40, 40, 40))
    d.line([mx - 12, my - 14, mx + 12, my + 14], fill=RED, width=3)
    d.line([mx - 12, my + 14, mx + 12, my - 14], fill=RED, width=3)
    chip(d, x + 6, y + 4, "COP31: NO DEAL", F(SANS_B, 11))
    d.rectangle([x + w - 62, y + h - 18, x + w - 6, y + h - 4],
                fill=(255, 255, 255))
    d.text((x + w - 56, y + h - 17), "LAST DAY", font=F(SANS_B, 10), fill=INK)


def art_poland(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 214, 235))
    # Fields.
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(140, 190, 110))
    d.rectangle([x, y + h - 16, x + w // 2, y + h - 8], fill=(170, 205, 120))
    # Missile streak + impact smoke.
    d.line([x + 20, y + 8, x + w - 70, y + h - 22], fill=(90, 90, 90), width=2)
    for i in range(5):
        px = x + 24 + i * 22
        py = y + 10 + i * 6
        d.line([px, py, px + 10, py + 3], fill=(255, 255, 255), width=2)
    ix, iy = x + w - 60, y + h - 24
    for r, c in [(12, (120, 120, 120)), (8, (160, 160, 160)), (5, (255, 150, 50))]:
        d.ellipse([ix - r, iy - r, ix + r, iy + r], fill=c)
    # NATO jets (triangles).
    for jx, jy in [(x + 30, y + 30), (x + 52, y + 22)]:
        d.polygon([(jx, jy), (jx + 16, jy + 4), (jx, jy + 8)], fill=(30, 60, 120))
    chip(d, x + 6, y + 4, "POLAND: MISSILE", F(SANS_B, 11))
    d.rectangle([x + w - 92, y + h - 18, x + w - 6, y + h - 4],
                fill=(255, 255, 255))
    d.text((x + w - 86, y + h - 17), "NATO JETS UP", font=F(SANS_B, 10),
           fill=INK)


def art_italy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 244, 230))
    # Tricolour band.
    d.rectangle([x, y + h - 12, x + w // 3, y + h], fill=(0, 140, 70))
    d.rectangle([x + w // 3, y + h - 12, x + 2 * w // 3, y + h],
                fill=(255, 255, 255))
    d.rectangle([x + 2 * w // 3, y + h - 12, x + w, y + h], fill=(205, 30, 40))
    # Crowd silhouettes + placards.
    for i, px in enumerate(range(10, w - 14, 18)):
        d.ellipse([x + px, y + 22 + (i % 2) * 4, x + px + 8,
                   y + 30 + (i % 2) * 4], fill=(30, 30, 30))
        d.polygon([(x + px - 2, y + h - 12), (x + px + 2, y + 30 + (i % 2) * 4),
                   (x + px + 10, y + 30 + (i % 2) * 4), (x + px + 14, y + h - 12)],
                  fill=(30, 30, 30))
    for px, py, txt in [(26, 8, ""), (86, 6, ""), (140, 8, "")]:
        d.rectangle([x + px, y + py, x + px + 26, y + py + 10], fill=RED)
    chip(d, x + 6, y + 4, "ITALY: STRIKE", F(SANS_B, 11))
    d.rectangle([x + 6, y + h - 30, x + 132, y + h - 16], fill=(10, 10, 10))
    d.text((x + 10, y + h - 28), "SCIOPERO GENERALE", font=F(SANS_B, 9),
           fill=(255, 255, 255))
    d.rectangle([x + w - 72, y + h - 30, x + w - 6, y + h - 16],
                fill=(255, 255, 255))
    d.text((x + w - 66, y + h - 28), "100+ CITIES", font=F(SANS_B, 9),
           fill=INK)


def art_japan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 240, 230))
    # Rising sun + bars.
    d.ellipse([x + 16, y + 10, x + 52, y + 46], fill=(188, 0, 45))
    bars = [12, 18, 16, 24, 30]
    for i, bh in enumerate(bars):
        bx = x + 70 + i * 20
        d.rectangle([bx, y + h - 10 - bh, bx + 13, y + h - 10],
                    fill=(60, 60, 60) if i < 4 else RED)
    d.line([x + 66, y + h - 22, x + 168, y + h - 44], fill=RED, width=2)
    d.polygon([(x + 168, y + h - 44), (x + 158, y + h - 42),
               (x + 164, y + h - 34)], fill=RED)
    chip(d, x + 6, y + 4, "JAPAN: +2.3%", F(SANS_B, 11))


def art_seoul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 84, 138))
    # Courthouse: pediment + columns.
    d.polygon([(x + 14, y + 22), (x + w // 2, y + 8), (x + w - 14, y + 22)],
              fill=(235, 230, 215))
    d.rectangle([x + 14, y + 22, x + w - 14, y + 27], fill=(235, 230, 215))
    for i in range(5):
        cx = x + 26 + i * ((w - 52) // 4)
        d.rectangle([cx - 4, y + 28, cx + 4, y + h - 10],
                    fill=(235, 230, 215))
    d.rectangle([x + 10, y + h - 10, x + w - 10, y + h - 4],
                fill=(235, 230, 215))
    # Gavel mark.
    d.line([x + w - 34, y + 30, x + w - 18, y + 42], fill=(255, 220, 130),
           width=4)
    chip(d, x + 6, y + 4, "SEOUL: IMPEACH", F(SANS_B, 11))
    d.rectangle([x + w - 76, y + h - 18, x + w - 6, y + h - 4],
                fill=(255, 255, 255))
    d.text((x + w - 70, y + h - 17), "TOP JUDGE", font=F(SANS_B, 10), fill=INK)


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 125, 79))
    # Pitch strip + bat + ball.
    d.rectangle([x + 30, y + 6, x + w - 30, y + h - 6], fill=(214, 190, 138))
    d.rectangle([x + 44, y + 6, x + 52, y + h - 6], fill=(255, 255, 255))
    d.rectangle([x + w - 52, y + 6, x + w - 44, y + h - 6],
                fill=(255, 255, 255))
    # Stumps.
    for sx in (x + 58, x + 64, x + 70):
        d.rectangle([sx, y + 12, sx + 3, y + 30], fill=(240, 220, 150))
    d.ellipse([x + w - 78, y + 14, x + w - 66, y + 26], fill=(185, 28, 28))
    d.ellipse([x + w - 76, y + 16, x + w - 68, y + 24], fill=(220, 80, 70))
    # Big 118.
    d.text((x + 84, y + 8), "118", font=F(SANS_B, 30), fill=(255, 255, 255))
    chip(d, x + 6, y + 4, "PHILLIPS: 118", F(SANS_B, 11))
    d.rectangle([x + w - 58, y + h - 18, x + w - 6, y + h - 4],
                fill=(255, 255, 255))
    d.text((x + w - 52, y + h - 17), "v INDIA", font=F(SANS_B, 10), fill=INK)


def art_kenya(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 214, 140))
    # Sun + savanna.
    d.ellipse([x + w - 52, y + 6, x + w - 20, y + 38], fill=(255, 150, 40))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(150, 105, 60))
    # Oil derrick.
    dx = x + 26
    d.polygon([(dx, y + h - 14), (dx + 12, y + 10), (dx + 26, y + 10),
               (dx + 38, y + h - 14)], outline=(60, 40, 20), width=3)
    d.line([dx + 6, y + h - 22, dx + 32, y + h - 22], fill=(60, 40, 20),
           width=2)
    d.line([dx + 9, y + h - 30, dx + 29, y + h - 30], fill=(60, 40, 20),
           width=2)
    d.line([dx + 12, y + 10, dx + 26, y + 10], fill=(60, 40, 20), width=3)
    # Pumpjack.
    px = x + 84
    d.polygon([(px, y + h - 14), (px + 6, y + h - 30), (px + 12, y + h - 14)],
              fill=(60, 40, 20))
    d.line([px - 8, y + h - 32, px + 26, y + h - 38], fill=(60, 40, 20),
           width=3)
    d.line([px + 26, y + h - 38, px + 26, y + h - 16], fill=(60, 40, 20),
           width=2)
    # Acacia.
    ax = x + w - 74
    d.line([ax, y + h - 14, ax, y + h - 30], fill=(90, 60, 30), width=3)
    d.ellipse([ax - 18, y + h - 38, ax + 18, y + h - 26], fill=(90, 140, 60))
    chip(d, x + 6, y + 4, "KENYA: OIL", F(SANS_B, 11))
    d.rectangle([x + w - 76, y + h - 18, x + w - 6, y + h - 4],
                fill=(255, 255, 255))
    d.text((x + w - 70, y + h - 17), "FIRST WELL", font=F(SANS_B, 10),
           fill=INK)


def art_iraq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 240))
    # Sun + desert.
    d.ellipse([x + w - 44, y + 6, x + w - 20, y + 30], fill=(255, 200, 80))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(200, 175, 120))
    # Tank.
    tx, ty = x + 20, y + h - 30
    d.rectangle([tx, ty + 8, tx + 78, ty + 16], fill=(90, 100, 70))
    for wx in range(tx + 4, tx + 76, 12):
        d.ellipse([wx, ty + 9, wx + 8, ty + 15], fill=(60, 66, 46))
    d.rectangle([tx + 16, ty, tx + 56, ty + 9], fill=(90, 100, 70))
    d.rectangle([tx + 52, ty + 2, tx + 92, ty + 5], fill=(60, 66, 46))
    # Palm.
    px = x + w - 26
    d.line([px, y + h - 14, px + 4, y + h - 34], fill=(120, 85, 50), width=3)
    for a, ln in [(-30, 14), (-10, 16), (10, 16), (30, 14)]:
        import math
        ex = px + 4 + ln * math.sin(math.radians(a))
        ey = y + h - 34 - ln * math.cos(math.radians(a)) * 0.6
        d.line([px + 4, y + h - 34, ex, ey], fill=(60, 130, 60), width=2)
    # Checkpoint flag.
    d.line([x + 12, y + 12, x + 12, y + h - 14], fill=(60, 60, 60), width=2)
    d.rectangle([x + 12, y + 12, x + 34, y + 22], fill=(200, 30, 40))
    chip(d, x + 6, y + 4, "IRAQ: ARMY IN", F(SANS_B, 11))
    d.rectangle([x + w - 108, y + h - 18, x + w - 6, y + h - 4],
                fill=(255, 255, 255))
    d.text((x + w - 102, y + h - 17), "JURF AL-SAKHAR", font=F(SANS_B, 10),
           fill=INK)


ART = {"kyiv": art_kyiv, "akvan": art_akvan, "selloff": art_selloff,
       "ukeu": art_ukeu, "cop31": art_cop31, "poland": art_poland,
       "italy": art_italy, "japan": art_japan, "seoul": art_seoul,
       "cricket": art_cricket, "kenya": art_kenya, "iraq": art_iraq}


# ---------------------------------------------------------------- map
def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 50, 80))
    land = (217, 201, 163)
    # Schematic continents (hand-drawn polygons, equirect-ish).
    na = [(8, 18), (52, 6), (96, 10), (118, 26), (104, 52), (82, 58),
          (70, 84), (58, 96), (44, 78), (30, 62), (10, 44)]
    sa = [(66, 108), (96, 104), (112, 126), (104, 168), (88, 196),
          (74, 178), (64, 140)]
    eu = [(150, 22), (176, 14), (196, 24), (188, 44), (168, 50),
          (152, 40)]
    af = [(148, 62), (178, 56), (200, 74), (196, 110), (182, 140),
          (166, 132), (152, 100), (142, 78)]
    asia = [(196, 16), (252, 8), (306, 18), (318, 40), (296, 58),
            (262, 66), (238, 84), (222, 68), (206, 58), (196, 40)]
    au = [(268, 158), (306, 152), (318, 172), (300, 190), (272, 184)]
    for poly in (na, sa, eu, af, asia, au):
        sx, sy = w / 330, h / 210
        d.polygon([(x + px * sx, y + py * sy) for px, py in poly], fill=land)
    # Graticule.
    for gx in range(x + 40, x + w, 40):
        d.line([gx, y + 4, gx, y + h - 4], fill=(40, 70, 100), width=1)
    for gy in range(y + 40, y + h, 40):
        d.line([x + 4, gy, x + w - 4, gy], fill=(40, 70, 100), width=1)
    # Pins.
    f = F(SANS_B, 9)
    for num, (lon, lat, dx, dy) in sorted(PINS.items()):
        px = x + (lon + 180) / 360 * w + dx
        py = y + (90 - lat) / 180 * h + dy
        r = 7.5 if num < 10 else 8.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 5.5), t, font=f,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- layout
def draw_top_strip(d):
    f = F(SANS_B, 12)
    d.text((M, 8), "THE WORLD IN ONE DAY", font=f, fill=INK)
    r = "34 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    d.text((W - M - d.textlength(r, font=f), 8), r, font=f, fill=INK)
    d.line([M, 28, W - M, 28], fill=RULE, width=1)


def draw_masthead(d):
    f = F(SERIF, 50)
    t = "Friday 20 November 2026"
    d.text(((W - d.textlength(t, font=f)) / 2, 30), t, font=f, fill=INK)
    sf = F(ITALIC, 16)
    s = ("Russian missiles hit Kyiv's bridges \u00b7 Cyclone Akvan strikes India \u00b7 "
         "AI sell-off sinks Asia's markets \u00b7 UK and EU seal a deal")
    d.text(((W - d.textlength(s, font=sf)) / 2, 86), s, font=sf, fill=INK)
    d.line([M, 108, W - M, 108], fill=RULE, width=3)


def draw_stats(d):
    y0, y1 = 112, 154
    cell = CW / 6
    nf = F(SERIF, 20)
    cf = F(SANS, 9)
    for i, (num, cap) in enumerate(STATS):
        x = M + i * cell
        d.text((x + 4, y0), num, font=nf, fill=INK)
        cy = y0 + 22
        for line in cap.split("\n"):
            d.text((x + 4, cy), line, font=cf, fill=MUTED)
            cy += 10
        if i:
            d.line([x, y0 + 2, x, y1 - 2], fill=(200, 195, 180), width=1)
    d.line([M, y1, W - M, y1], fill=RULE, width=1)


def draw_region_bar(d):
    y0, y1 = 158, 176
    total = sum(c for _, c in REGIONS)
    x = M
    f = F(SANS_B, 10)
    for name, count in REGIONS:
        w = CW * count / total
        d.rectangle([x, y0, x + w, y1], fill=REGION_COLORS[name])
        label = f"{name} {count}"
        tw = d.textlength(label, font=f)
        d.text((x + (w - tw) / 2, y0 + 3), label, font=f,
               fill=(255, 255, 255))
        x += w


def draw_feature(d, x, y, w, art_h, text_h, item, hero=False):
    d.rectangle([x, y, x + w, y + art_h + text_h], fill=CARD_BG)
    d.rectangle([x, y, x + w, y + art_h + text_h], outline=(190, 185, 170),
                width=1)
    ART[item["art"]](d, x + 1, y + 1, w - 2, art_h - 2)
    ty = y + art_h + 6
    num_badge(d, x + 11, ty + 8, item["num"])
    kf = F(SANS_B, 10 if hero else 9)
    d.text((x + 24, ty + 1), item["kicker"], font=kf, fill=RED)
    hf = F(SERIF, 16 if hero else 13)
    hy = ty + (17 if hero else 16)
    for line in wrap(d, item["head"], hf, w - 8)[:2]:
        d.text((x + 5, hy), line, font=hf, fill=INK)
        hy += (19 if hero else 15)
    bf = F(SANS, 11 if hero else 10)
    by = hy + 1
    for line in wrap(d, item["body"], bf, w - 10):
        d.text((x + 5, by), line, font=bf, fill=(40, 40, 40))
        by += (13 if hero else 11)


def draw_list_item(d, x, y, width, num, place, rest):
    nf = F(SANS_B, 11)
    pf = F(SANS_B, 11)
    rf = F(SANS, 11)
    d.text((x, y), str(num), font=nf, fill=RED)
    nx = x + d.textlength(str(num) + " ", font=nf)
    avail = width - (nx - x)
    # Wrap place + rest as one paragraph, place rendered bold on line 1.
    full = place + " " + rest
    lines = wrap(d, full, rf, avail)
    # Line 1: bold place, then regular remainder.
    first = lines[0]
    d.text((nx, y), place, font=pf, fill=INK)
    rem = first[len(place):]
    d.text((nx + d.textlength(place, font=pf), y), rem, font=rf, fill=INK)
    ly = y + 12
    for line in lines[1:2]:
        d.text((nx, ly), line, font=rf, fill=INK)
        ly += 12
    return len(lines)


def draw_map_list(d):
    y_head = 658
    hf = F(SANS_B, 12)
    d.text((M, y_head), "WHERE IT HAPPENED", font=hf, fill=INK)
    d.text((356, y_head), "ALSO ON FRIDAY 20 NOVEMBER \u2014 22 MORE STORIES",
           font=hf, fill=INK)
    d.line([M, y_head + 16, W - M, y_head + 16], fill=RULE, width=1)
    y0 = 678
    map_w, map_h = 330, 248
    draw_map(d, M, y0, map_w, map_h)
    d.text((M + 6, y0 + map_h - 15),
           "Each number is that story on this page.",
           font=F(SANS, 9), fill=(220, 220, 220))
    # List: two columns x 11 rows.
    col_w = 321
    row_h = 23
    max_lines = 0
    for i, (num, place, rest) in enumerate(LIST_ITEMS):
        col = i // 11
        row = i % 11
        lx = 356 + col * (col_w + 12)
        ly = y0 + row * row_h
        n = draw_list_item(d, lx, ly, col_w, num, place, rest)
        max_lines = max(max_lines, n)
    return max_lines


def draw_date_check(d):
    y0, y1 = 936, 986
    d.rectangle([M, y0, W - M, y1], outline=RED, width=2)
    f = F(SANS, 10)
    lines = wrap(d, DATE_CHECK, f, CW - 20)
    ly = y0 + 6
    for line in lines:
        # Bold the "DATE CHECK —" lead on the first line.
        if ly == y0 + 6:
            lead = "DATE CHECK \u2014 "
            bf = F(SANS_B, 10)
            d.text((M + 10, ly), lead, font=bf, fill=RED)
            d.text((M + 10 + d.textlength(lead, font=bf), ly),
                   line[len(lead):], font=f, fill=INK)
        else:
            d.text((M + 10, ly), line, font=f, fill=INK)
        ly += 12
    return len(lines)


def draw_footer(d):
    f = F(SANS, 9)
    d.text((M, 992),
           "Every story here happened, or was first reported, on Friday 20 "
           "November 2026. Officials' counts are attributed.",
           font=f, fill=MUTED)
    r = "Sources named beside each story \u00b7 original drawings"
    d.text((W - M - d.textlength(r, font=f), 992), r, font=f, fill=MUTED)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top_strip(d)
    draw_masthead(d)
    draw_stats(d)
    draw_region_bar(d)
    # Heroes: 3 across.
    hw = int((CW - 2 * 12) / 3)
    for i, item in enumerate(HEROES):
        x = M + i * (hw + 12)
        draw_feature(d, x, 182, hw, 90, 100, item, hero=True)
    # Cards row 1: stories 4-8, 5 across.
    cw1 = int((CW - 4 * 10) / 5)
    for i, item in enumerate(CARDS[:5]):
        x = M + i * (cw1 + 10)
        draw_feature(d, x, 378, cw1, 48, 86, item)
    # Cards row 2: stories 9-12, 4 across.
    cw2 = int((CW - 3 * 10) / 4)
    for i, item in enumerate(CARDS[5:]):
        x = M + i * (cw2 + 10)
        draw_feature(d, x, 518, cw2, 48, 86, item)
    max_lines = draw_map_list(d)
    n_date = draw_date_check(d)
    draw_footer(d)
    return img, max_lines, n_date


if __name__ == "__main__":
    import hashlib
    import os
    img, max_lines, n_date = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")
    print(f"sha256: {h}")
    print(f"max list lines per item: {max_lines} (must be <= 2)")
    print(f"date-check lines: {n_date}")
