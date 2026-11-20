#!/usr/bin/env python3
"""Generate entry.png: the front page of Friday 20 November 2026.

Six stories, drawn from scratch with PIL: no photos, no copied artwork.
Masthead names the day; each story is a panel with a short headline, one
supporting line, and a small drawn pictogram.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (246, 241, 231)
NAVY = (22, 35, 63)
GOLD = (201, 162, 39)
RED = (185, 28, 28)
INK = (26, 26, 26)
MUTED = (85, 85, 85)
CARD = (255, 255, 255)
LINE = (200, 192, 175)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, fill, max_w, leading=None):
    lines = wrap(draw, text, fnt, max_w)
    lh = leading or int(fnt.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


# ---------- pictograms ----------

def draw_globe(draw, cx, cy, r, outline=NAVY, width=4):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=outline, width=width)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 228, 244))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=outline, width=width)
    draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=outline, width=3)
    draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 160, fill=outline, width=3)
    draw.line([cx - r, cy, cx + r, cy], fill=outline, width=3)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=outline, width=3)


def draw_flag_us(draw, x, y, w, h):
    stripe = h / 13.0
    for i in range(13):
        c = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=c)
    cw, ch = w * 0.4, stripe * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(30, 58, 95))
    for r in range(4):
        for c in range(5):
            px = x + 6 + c * (cw - 12) / 4
            py = y + 5 + r * (ch - 10) / 3
            draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(255, 255, 255))


def draw_flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.18, y + h * 0.28
    r = h * 0.14
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.4
        pts.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    draw.polygon(pts, fill=(255, 222, 0))
    for sx, sy in [(0.42, 0.18), (0.52, 0.32), (0.52, 0.52), (0.42, 0.66)]:
        px, py = x + w * sx, y + h * sy
        rr = h * 0.07
        pts = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            r2 = rr if i % 2 == 0 else rr * 0.4
            pts.append((px + r2 * math.cos(ang), py - r2 * math.sin(ang)))
        draw.polygon(pts, fill=(255, 222, 0))


def draw_flag_ru(draw, x, y, w, h):
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        draw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)


def draw_scales(draw, cx, cy, s, color=NAVY):
    draw.line([cx, cy - s, cx, cy + s], fill=color, width=5)
    draw.line([cx - s, cy - s * 0.55, cx + s, cy - s * 0.55], fill=color, width=5)
    draw.line([cx, cy - s * 1.25, cx, cy - s], fill=color, width=5)
    draw.ellipse([cx - 5, cy - s * 1.32, cx + 5, cy - s * 1.18], fill=GOLD)
    for sx in (-1, 1):
        px = cx + sx * s
        draw.line([px, cy - s * 0.55, px, cy - s * 0.1], fill=color, width=3)
        draw.polygon([(px - s * 0.42, cy - s * 0.1), (px + s * 0.42, cy - s * 0.1),
                      (px, cy + s * 0.45)], outline=color, width=3)
    draw.rectangle([cx - s * 0.55, cy + s * 0.95, cx + s * 0.55, cy + s * 1.1],
                   fill=color)


def draw_satellite(draw, cx, cy, s, color=NAVY):
    draw.line([cx - s * 1.3, cy + s * 0.9, cx + s * 1.3, cy - s * 0.9],
              fill=color, width=3)
    draw.rectangle([cx - s * 0.45, cy - s * 0.2, cx + s * 0.45, cy + s * 0.2],
                   fill=(70, 110, 170), outline=color, width=3)
    draw.polygon([(cx - s * 1.25, cy + s * 0.55), (cx - s * 0.75, cy + s * 0.1),
                  (cx - s * 0.55, cy + s * 0.35), (cx - s * 1.05, cy + s * 0.8)],
                 fill=(201, 162, 39), outline=color)
    draw.polygon([(cx + s * 1.25, cy - s * 0.55), (cx + s * 0.75, cy - s * 0.1),
                  (cx + s * 0.55, cy - s * 0.35), (cx + s * 1.05, cy - s * 0.8)],
                 fill=(201, 162, 39), outline=color)
    for sx, sy in [(-1.6, -0.9), (-1.1, -1.2), (1.5, 0.8), (0.9, 1.3)]:
        draw.ellipse([cx + sx * s - 2, cy + sy * s - 2,
                      cx + sx * s + 2, cy + sy * s + 2], fill=GOLD)


def draw_cyclone(draw, cx, cy, r, color=(30, 90, 140)):
    for k in range(3):
        pts = []
        for t in range(0, 200):
            a = t / 200.0 * math.pi * 3.2 + k * 2.1
            rr = r * (0.15 + 0.85 * t / 200.0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.8))
        draw.line(pts, fill=color, width=4)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)


def draw_talks(draw, cx, cy, s, color=NAVY):
    draw.rounded_rectangle([cx - s, cy - s * 0.75, cx + s * 0.1, cy + s * 0.25],
                           radius=12, fill=(255, 255, 255), outline=color, width=4)
    draw.rounded_rectangle([cx - s * 0.1, cy - s * 0.25, cx + s, cy + s * 0.75],
                           radius=12, fill=(214, 228, 244), outline=color, width=4)
    for dx, dy in [(-0.6, -0.35), (0, -0.35), (0.6, -0.35)]:
        draw.ellipse([cx + dx * s - 4, cy + dy * s - 4,
                      cx + dx * s + 4, cy + dy * s + 4], fill=color)
    for dx, dy in [(-0.6, 0.35), (0, 0.35), (0.6, 0.35)]:
        draw.ellipse([cx + dx * s - 4, cy + dy * s - 4,
                      cx + dx * s + 4, cy + dy * s + 4], fill=color)


def draw_calendar(draw, cx, cy, s, color=NAVY):
    draw.rounded_rectangle([cx - s, cy - s * 0.7, cx + s, cy + s * 0.8],
                           radius=10, fill=(255, 255, 255), outline=color, width=4)
    draw.rectangle([cx - s, cy - s * 0.7, cx + s, cy - s * 0.2],
                   fill=RED)
    draw.line([cx - s * 0.5, cy - s * 0.95, cx - s * 0.5, cy - s * 0.45],
              fill=color, width=5)
    draw.line([cx + s * 0.5, cy - s * 0.95, cx + s * 0.5, cy - s * 0.45],
              fill=color, width=5)
    draw.text((cx, cy + s * 0.28), "2027", font=font(FB, int(s * 0.62)),
              fill=color, anchor="mm")


# ---------- compose ----------

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 154], fill=GOLD)
    f_small = font(FB, 30)
    size = 92
    while d.textlength("20 NOVEMBER 2026", font=font(FB, size)) > 980 and size > 40:
        size -= 2
    f_date = font(FB, size)
    d.text((512, 26), "FRIDAY", font=f_small, fill=GOLD, anchor="ma")
    d.text((512, 56), "20 NOVEMBER 2026", font=f_date, fill=(255, 255, 255),
           anchor="ma")
    d.text((512, 168), "THE WORLD IN ONE PICTURE  ·  SIX STORIES THAT DEFINED THE DAY",
           font=font(FB, 22), fill=MUTED, anchor="ma")

    # ---- Lead story: the summit ----
    x0, y0, x1, y1 = 28, 200, 996, 440
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=CARD, outline=LINE, width=2)
    d.rectangle([x0, y0 + 14, x0 + 8, y1 - 14], fill=RED)
    draw_globe(d, 150, 320, 74)
    fx, fy, fw, fh = 268, 262, 92, 58
    draw_flag_us(d, fx, fy, fw, fh)
    draw_flag_cn(d, fx + 104, fy, fw, fh)
    draw_flag_ru(d, fx + 208, fy, fw, fh)
    d.text((268, 334), "THREE FLAGS, ONE TABLE", font=font(FB, 20),
           fill=MUTED)
    tx = 596
    y = text_block(d, tx, 216, "TRUMP, XI & PUTIN MEET", font(FB, 44), INK, 380)
    y = text_block(d, tx, y + 8, "First-ever three-way summit ends in a "
                   "'Peace Declaration'.", font(FR, 25), (60, 60, 60), 380)
    d.text((tx, y + 10), "SHENZHEN, CHINA", font=font(FB, 20), fill=RED)

    # ---- Second story: ICJ ----
    x0, y0, x1, y1 = 28, 452, 996, 596
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=CARD, outline=LINE, width=2)
    d.rectangle([x0, y0 + 12, x0 + 8, y1 - 12], fill=NAVY)
    draw_scales(d, 128, 524, 52)
    y = text_block(d, 216, 470, "MYANMAR COMMITTED GENOCIDE",
                   font(FB, 34), INK, 760)
    y = text_block(d, 216, y + 6, "World court rules 9–6 — the first state ever found "
               "guilty of genocide. Reparations ordered for the Rohingya.",
               font(FR, 24), (60, 60, 60), 760)
    d.text((980, 546), "THE HAGUE", font=font(FB, 20), fill=RED, anchor="ra")

    # ---- Four small panels ----
    panels = [
        ("IRAN DECISION PUSHED TO 2027",
         "Trump: 'no rush' on an Iran war decision.",
         "calendar", "WASHINGTON"),
        ("VOYAGER 1: A LIGHT-DAY AWAY",
         "NASA: a signal now takes 24 hours to reach it.",
         "satellite", "DEEP SPACE"),
        ("CYCLONE AKVAN HITS ODISHA",
         "300,000 evacuated as the storm nears the coast.",
         "cyclone", "INDIA"),
        ("EUROPE OPEN TO RUSSIA TALKS",
         "Leaders ready to discuss ending the Ukraine war.",
         "talks", "BERLIN"),
    ]
    pw, ph, gap = 472, 163, 24
    for i, (head, sub, pic, tag) in enumerate(panels):
        px = 28 + (i % 2) * (pw + gap)
        py = 608 + (i // 2) * (ph + gap)
        d.rounded_rectangle([px, py, px + pw, py + ph], radius=12, fill=CARD,
                            outline=LINE, width=2)
        cx, cy = px + 72, py + ph // 2
        if pic == "calendar":
            draw_calendar(d, cx, cy, 42)
        elif pic == "satellite":
            draw_satellite(d, cx, cy, 42)
        elif pic == "cyclone":
            draw_cyclone(d, cx, cy, 46)
        else:
            draw_talks(d, cx, cy, 42)
        tx = px + 148
        y = text_block(d, tx, py + 14, head, font(FB, 25), INK, pw - 168)
        y = text_block(d, tx, y + 4, sub, font(FR, 20), (60, 60, 60), pw - 168)
        d.text((tx, py + ph - 26), tag, font=font(FB, 18), fill=RED)

    # Footer
    d.rectangle([0, 962, W, H], fill=NAVY)
    d.text((512, 975), "20 NOVEMBER 2026  ·  SOURCES: REUTERS · BBC · THE HINDU · NASA",
           font=font(FB, 21), fill=(255, 255, 255), anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
