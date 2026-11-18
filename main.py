#!/usr/bin/env python3
"""bigpig-news v3 — one front page summing up Tuesday 17 November 2026.

Draws a single deterministic 1024x1024 PNG with PIL only (no network, no
randomness): black-band masthead with a giant bold date, red ticker, three
equal illustrated leads, a 5x2 grid of illustrated stories, a world map with
leader-line numbers, a numbered ALSO list, a figures strip and a source line.
40 verified stories, 13 illustrated. All facts come from the NEWS-v2 dossier
(40 stories, each verified on 2+ sources). Output: entry.png in
$MAKEFUN_OUTPUT_DIR, else /output, else ./out.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
M = 10

CREAM = (247, 241, 222)
PAPER = (255, 253, 244)
INK = (22, 19, 14)
BLACK = (17, 17, 17)
GOLD = (201, 162, 39)
GOLD_LT = (226, 196, 90)
RED = (180, 35, 24)
RED_DK = (140, 24, 16)
NAVY = (31, 56, 100)
BLUE = (31, 78, 121)
SKY = (186, 220, 238)
SKY_DK = (140, 185, 215)
SEA = (52, 110, 150)
SEA_DK = (30, 80, 120)
GREEN = (30, 107, 58)
TEAL = (14, 124, 123)
PURPLE = (108, 63, 160)
GREY = (120, 118, 110)
WHITE = (255, 255, 255)

REGION_COLORS = {
    "WAR": RED,
    "POLITICS": BLUE,
    "BUSINESS": GREEN,
    "CLIMATE": TEAL,
    "SPORT": PURPLE,
    "ASIA": (176, 92, 20),
    "EUROPE": BLUE,
    "MIDEAST": RED,
}


def font(size):
    return ImageFont.load_default(size=size)


def text_w(draw, s, fnt):
    left, top, right, bottom = draw.textbbox((0, 0), s, font=fnt)
    return right - left


def draw_text(draw, x, y, s, fnt, fill, bold=False, anchor_left=True):
    """Draw text; bold fakes a heavier weight by overprinting offsets."""
    if not anchor_left:
        x -= text_w(draw, s, fnt)
    if bold:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            draw.text((x + dx, y + dy), s, font=fnt, fill=fill)
    else:
        draw.text((x, y), s, font=fnt, fill=fill)


def heavy_text(draw, x, y, s, fnt, fill):
    """Extra-heavy weight for the giant masthead date."""
    for dx, dy in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)):
        draw.text((x + dx, y + dy), s, font=fnt, fill=fill)


def wrap(draw, s, fnt, max_w):
    words = s.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def center_text(draw, cx, y, s, fnt, fill, bold=False):
    x = cx - text_w(draw, s, fnt) // 2
    draw_text(draw, x, y, s, fnt, fill, bold=bold)


def sky_bands(draw, box, colors):
    x0, y0, x1, y1 = box
    n = len(colors)
    h = (y1 - y0) / n
    for i, c in enumerate(colors):
        draw.rectangle([x0, y0 + i * h, x1, y0 + (i + 1) * h + 1], fill=c)


def sun_disc(draw, cx, cy, r, fill=(245, 196, 66)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    for k in range(8):
        ang = k * math.pi / 4
        x1 = cx + int((r + 2) * math.cos(ang))
        y1 = cy + int((r + 2) * math.sin(ang))
        x2 = cx + int((r + 8) * math.cos(ang))
        y2 = cy + int((r + 8) * math.sin(ang))
        draw.line([x1, y1, x2, y2], fill=fill, width=2)


def cloud(draw, x, y, s, fill=(255, 255, 255)):
    draw.ellipse([x, y, x + int(1.6 * s), y + int(0.7 * s)], fill=fill)
    draw.ellipse([x + int(0.3 * s), y - int(0.4 * s), x + int(1.3 * s), y + int(0.5 * s)], fill=fill)
    draw.ellipse([x + int(0.9 * s), y - int(0.2 * s), x + int(1.9 * s), y + int(0.7 * s)], fill=fill)


def sea_waves(draw, box, base, line=(255, 255, 255)):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=base)
    for j, yy in enumerate(range(y0 + 8, y1, 12)):
        off = 6 if j % 2 else 0
        pts = []
        for xx in range(x0 + off, x1, 14):
            pts.append((xx, yy))
            pts.append((xx + 7, yy - 3))
        draw.line(pts, fill=line, width=1)


def smoke(draw, x, y, s):
    for i, (dx, dy, r, c) in enumerate(
        ((0, 0, s, (110, 108, 102)), (-s // 2, -s, int(s * 0.8), (140, 138, 130)),
         (s // 3, -int(s * 1.8), int(s * 0.6), (170, 168, 160)))):
        draw.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=c)


def burst(draw, cx, cy, r):
    outer = []
    inner = []
    for k in range(24):
        ang = k * math.pi / 12
        rr = r if k % 2 == 0 else int(r * 0.45)
        outer.append((cx + int(rr * math.cos(ang)), cy + int(rr * math.sin(ang))))
        rr2 = int(r * 0.62) if k % 2 == 0 else int(r * 0.3)
        inner.append((cx + int(rr2 * math.cos(ang)), cy + int(rr2 * math.sin(ang))))
    draw.polygon(outer, fill=(232, 90, 20))
    draw.polygon(inner, fill=(245, 196, 66))
    draw.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], fill=(255, 236, 150))


def person(draw, x, y, s, skin=(216, 178, 140), suit=NAVY):
    draw.ellipse([x - s // 2, y - s // 2, x + s // 2, y + s // 2], fill=skin)
    draw.ellipse([x - s, y + s // 2, x + s, y + int(s * 1.9)], fill=suit)
    draw.rectangle([x - 2, y + s // 2, x + 2, y + int(s * 1.2)], fill=WHITE)


def flag_us(draw, x, y, w, h):
    for i in range(13):
        c = (178, 34, 52) if i % 2 == 0 else WHITE
        draw.rectangle([x, y + i * h // 13, x + w, y + (i + 1) * h // 13 + 1], fill=c)
    draw.rectangle([x, y, x + int(w * 0.4), y + int(h * 0.54)], fill=(40, 60, 120))
    for r in range(3):
        for c in range(4):
            draw.ellipse([x + 4 + c * 9, y + 3 + r * 7, x + 8 + c * 9, y + 7 + r * 7], fill=WHITE)


def flag_india(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h // 3], fill=(255, 153, 51))
    draw.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=WHITE)
    draw.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(19, 136, 8))
    cx, cy, r = x + w // 2, y + h // 2, h // 6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 56, 147), width=2)


def flag_japan(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=WHITE)
    draw.ellipse([x + w // 2 - h // 4, y + h // 4, x + w // 2 + h // 4, y + 3 * h // 4], fill=(188, 0, 45))


def flag_aus(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(0, 40, 120))
    draw.rectangle([x, y, x + w // 2, y + h // 2], fill=(200, 30, 40))
    draw.line([x, y, x + w // 2, y + h // 2], fill=WHITE, width=2)
    draw.line([x + w // 2, y, x, y + h // 2], fill=WHITE, width=2)
    for sx, sy in ((int(w * 0.72), int(h * 0.3)), (int(w * 0.85), int(h * 0.62)), (int(w * 0.68), int(h * 0.75))):
        draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=WHITE)


def flag_pole(draw, x, y, h, fn, w=34):
    draw.line([x, y, x, y + h], fill=INK, width=2)
    draw.ellipse([x - 2, y - 3, x + 2, y + 1], fill=GOLD)
    fn(draw, x + 2, y, w, int(h * 0.62))


# ---------------- LEAD SCENES (rich, layered) ----------------

def scene_kerch(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(16, 24, 58), (26, 40, 86), (38, 58, 108)])
    for sx, sy in ((18, 10), (60, 22), (120, 8), (180, 18), (240, 8), (290, 20), (90, 30), (210, 28)):
        draw.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    draw.ellipse([x + w - 52, y + 8, x + w - 28, y + 32], fill=(235, 230, 210))
    sea_waves(draw, (x, y + h - 34, x + w, y + h), (24, 68, 104))
    deck_y = y + h - 52
    draw.rectangle([x, y + h - 56, x + w, y + h - 50], fill=(200, 198, 188))
    for tx in (x + 46, x + w - 66):
        draw.rectangle([tx, y + 34, tx + 10, deck_y], fill=(200, 198, 188))
        draw.rectangle([tx - 4, y + 30, tx + 14, y + 36], fill=(180, 178, 168))
    draw.line([x + 51, y + 34, x + w // 2 - 40, deck_y], fill=(160, 158, 148), width=1)
    draw.line([x + w - 61, y + 34, x + w // 2 + 40, deck_y], fill=(160, 158, 148), width=1)
    cx = x + w // 2
    draw.line([cx - 52, deck_y, cx - 18, deck_y + 22], fill=(200, 198, 188), width=7)
    draw.line([cx + 52, deck_y, cx + 18, deck_y + 22], fill=(200, 198, 188), width=7)
    burst(draw, cx, deck_y - 8, 20)
    smoke(draw, cx + 8, deck_y - 26, 9)
    draw.polygon([(x + 40, y + h - 8), (x + 62, y + h - 8), (x + 56, y + h - 18), (x + 48, y + h - 18)], fill=(220, 220, 210))
    draw.rectangle([x + 46, y + h - 24, x + 58, y + h - 18], fill=(220, 220, 210))


def scene_hormuz(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(186, 220, 238), (205, 230, 240)])
    sun_disc(draw, x + w - 40, y + 22, 12)
    cloud(draw, x + 16, y + 12, 14)
    cloud(draw, x + 120, y + 6, 11)
    sea_waves(draw, (x, y + h - 44, x + w, y + h), (52, 110, 150))
    ship_y = y + h - 52
    draw.polygon([(x + 250, ship_y - 26), (x + 292, ship_y - 26), (x + 292, ship_y - 8),
                  (x + 278, ship_y + 2), (x + 250, ship_y + 2)], fill=(110, 112, 116))
    draw.rectangle([x + 258, ship_y - 36, x + 272, ship_y - 26], fill=(90, 92, 96))
    draw.rectangle([x + 262, ship_y - 44, x + 268, ship_y - 36], fill=(90, 92, 96))
    hx, hy = x + 60, y + h - 58
    draw.polygon([(hx, hy), (hx + 190, hy), (hx + 176, hy + 26), (hx + 14, hy + 26)], fill=(150, 32, 24))
    draw.rectangle([hx + 30, hy - 16, hx + 92, hy], fill=(200, 200, 195))
    draw.rectangle([hx + 100, hy - 12, hx + 130, hy], fill=(200, 200, 195))
    draw.rectangle([hx + 138, hy - 22, hx + 150, hy], fill=(120, 120, 115))
    draw.rectangle([hx + 142, hy - 30, hx + 146, hy - 22], fill=(90, 90, 88))
    burst(draw, hx + 118, hy - 18, 15)
    smoke(draw, hx + 124, hy - 34, 8)
    for wx in range(hx + 10, hx + 180, 22):
        draw.rectangle([wx, hy + 8, wx + 12, hy + 14], fill=(255, 255, 255))
    draw.ellipse([x + 210, y + 16, x + 228, y + 26], fill=(90, 92, 96))
    draw.line([x + 200, y + 18, x + 238, y + 18], fill=(60, 60, 62), width=2)
    draw.line([x + 219, y + 26, x + 219, y + 32], fill=(60, 60, 62), width=2)


def scene_quad(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(250, 224, 150), (240, 205, 130), (232, 190, 120)])
    sun_disc(draw, x + w - 46, y + 24, 14, fill=(255, 220, 120))
    for bx, bw, bh in ((8, 34, 46), (48, 26, 62), (80, 40, 38), (126, 24, 56), (156, 30, 42),
                       (250, 28, 58), (282, 22, 40)):
        draw.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26], fill=(120, 84, 52))
        for wy in range(y + h - 22 - bh, y + h - 30, 10):
            for wx in range(x + bx + 5, x + bx + bw - 4, 9):
                draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 220, 120))
    draw.rectangle([x, y + h - 30, x + w, y + h - 26], fill=(96, 62, 38))
    draw.rectangle([x + 30, y + h - 22, x + w - 30, y + h - 14], fill=(110, 72, 40))
    draw.rectangle([x + 30, y + h - 22, x + w - 30, y + h - 18], fill=(140, 96, 54))
    flag_pole(draw, x + 52, y + 8, 44, flag_us)
    flag_pole(draw, x + 122, y + 8, 44, flag_india)
    flag_pole(draw, x + 192, y + 8, 44, flag_japan)
    flag_pole(draw, x + 262, y + 8, 44, flag_aus)
    for px, suit in ((86, (30, 60, 110)), (156, (40, 90, 60)), (226, (90, 40, 60)), (292, (60, 40, 90))):
        person(draw, x + px, y + h - 48, 11, suit=suit)


# ---------------- GRID SCENES ----------------

def scene_japan(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(186, 220, 238), (168, 205, 228)])
    draw.ellipse([x + 130, y + 10, x + 168, y + 48], fill=(200, 40, 50))
    cloud(draw, x + 8, y + 12, 10)
    cloud(draw, x + 100, y + 52, 9)
    sea_waves(draw, (x, y + h - 22, x + w, y + h), (52, 110, 150))
    for jx, jy, s in ((30, 34, 1), (105, 52, -1)):
        draw.polygon([(x + jx, y + jy), (x + jx + 52 * s, y + jy + 8), (x + jx + 40 * s, y + jy + 14),
                      (x + jx + 8 * s, y + jy + 12)], fill=(90, 94, 100))
        draw.polygon([(x + jx + 30 * s, y + jy - 8), (x + jx + 44 * s, y + jy + 6),
                      (x + jx + 34 * s, y + jy + 8)], fill=(70, 74, 80))
        for cx in range(0, 30, 8):
            draw.ellipse([x + jx - cx * s, y + jy + 12, x + jx - cx * s + 6, y + jy + 15], fill=WHITE)
    draw.polygon([(x + 150, y + h - 22), (x + 196, y + h - 22), (x + 196, y + h - 6), (x + 168, y + h - 6)],
                 fill=(60, 90, 60))


def scene_cyclone(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(150, 190, 220), (170, 205, 228)])
    cx, cy = x + 78, y + 48
    for k in range(5):
        r = 12 + k * 7
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=40 + k * 55, end=300 + k * 55,
                 fill=(255, 255, 255), width=3)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(240, 240, 235))
    for rx in range(8, w, 18):
        draw.line([x + rx, y + 6, x + rx - 6, y + 20], fill=(140, 170, 200), width=1)
    draw.polygon([(x + 150, y + h), (x + 196, y + h - 30), (x + 196, y + h), (x + 150, y + h)],
                 fill=(90, 130, 80))
    draw.polygon([(x + 150, y + h - 30), (x + 168, y + h - 44), (x + 196, y + h - 30)],
                 fill=(120, 160, 100))
    for ax in (20, 60, 110):
        draw.line([x + ax, y + h - 12, x + ax + 26, y + h - 12], fill=RED, width=2)
        draw.polygon([(x + ax + 26, y + h - 17), (x + ax + 34, y + h - 12), (x + ax + 26, y + h - 7)], fill=RED)


def scene_serbia(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(232, 220, 190), (220, 205, 175)])
    draw.polygon([(x + 48, y + 26), (x + 148, y + 26), (x + 98, y + 8)], fill=(150, 130, 95))
    draw.ellipse([x + 90, y + 10, x + 106, y + 26], fill=(120, 100, 70))
    draw.rectangle([x + 48, y + 26, x + 148, y + 30], fill=(170, 150, 115))
    for cx in range(56, 148, 18):
        draw.rectangle([x + cx, y + 30, x + cx + 8, y + 66], fill=(210, 195, 165))
        draw.rectangle([x + cx - 2, y + 26, x + cx + 10, y + 30], fill=(190, 175, 140))
    draw.rectangle([x + 48, y + 66, x + 148, y + 72], fill=(170, 150, 115))
    draw.rectangle([x + 88, y + 44, x + 108, y + 66], fill=(90, 70, 50))
    draw.line([x + 164, y + 14, x + 164, y + 62], fill=INK, width=2)
    for i, c in enumerate(((200, 40, 50), (255, 255, 255), (30, 70, 140))):
        draw.rectangle([x + 166, y + 14 + i * 6, x + 188, y + 20 + i * 6], fill=c)
    for i in range(12):
        draw.ellipse([x + 12 + i * 14, y + h - 14, x + 20 + i * 14, y + h - 6], fill=(60, 60, 90))


def scene_prague(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(200, 210, 220), (220, 224, 228)])
    draw.rectangle([x, y + h - 30, x + w, y + h - 24], fill=(140, 130, 115))
    for px in range(10, w, 26):
        draw.rectangle([x + px, y + h - 24, x + px + 6, y + h - 12], fill=(120, 110, 95))
    ty = y + h - 52
    draw.rectangle([x + 6, ty, x + 82, ty + 18], fill=(190, 30, 30))
    draw.rectangle([x + 114, ty, x + 190, ty + 18], fill=(30, 80, 160))
    for wx in range(12, 78, 14):
        draw.rectangle([x + wx, ty + 4, x + wx + 9, ty + 11], fill=(220, 235, 245))
    for wx in range(120, 186, 14):
        draw.rectangle([x + wx, ty + 4, x + wx + 9, ty + 11], fill=(220, 235, 245))
    draw.ellipse([x + 82, ty + 2, x + 96, ty + 16], fill=(220, 220, 210))
    burst(draw, x + 98, ty + 6, 13)
    draw.line([x + 170, y + 8, x + 170, ty], fill=INK, width=2)
    draw.ellipse([x + 164, y + 6, x + 176, y + 18], fill=RED)
    draw.ellipse([x + 167, y + 9, x + 173, y + 15], fill=(255, 120, 110))
    cloud(draw, x + 10, y + 8, 9)


def scene_france(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(210, 225, 235), (225, 232, 238)])
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=(110, 140, 80))
    for tx, th in ((12, 22), (170, 26), (150, 18)):
        draw.rectangle([x + tx + 5, y + h - 26 - th + 12, x + tx + 9, y + h - 26], fill=(90, 70, 40))
        draw.ellipse([x + tx - 4, y + h - 26 - th, x + tx + 18, y + h - 14], fill=(50, 110, 50))
    tx, ty = x + 56, y + h - 52
    draw.rectangle([tx, ty, tx + 88, ty + 20], fill=(80, 95, 60))
    draw.rectangle([tx + 22, ty - 12, tx + 58, ty], fill=(70, 85, 52))
    draw.rectangle([tx + 52, ty - 8, tx + 96, ty - 4], fill=(60, 75, 46))
    for wx in range(tx + 4, tx + 84, 12):
        draw.ellipse([wx, ty + 20, wx + 9, ty + 29], fill=(40, 42, 38))
    draw.line([x + 20, y + 8, x + 20, y + 44], fill=INK, width=2)
    for i, c in enumerate(((0, 60, 160), (255, 255, 255), (220, 30, 40))):
        draw.rectangle([x + 22, y + 8 + i * 8, x + 46, y + 16 + i * 8], fill=c)
    cloud(draw, x + 110, y + 6, 10)


def scene_nvidia(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PAPER)
    draw.rectangle([x, y, x + w, y + h], outline=GREY, width=1)
    base = y + h - 14
    draw.line([x + 14, y + 8, x + 14, base], fill=INK, width=2)
    draw.line([x + 14, base, x + w - 8, base], fill=INK, width=2)
    bars = [14, 22, 30, 42, 56, 72]
    for i, bh in enumerate(bars):
        bx = x + 24 + i * 22
        draw.rectangle([bx, base - bh, bx + 16, base], fill=(30, 140, 70) if i < 5 else (20, 170, 80))
    pts = [(x + 32 + i * 22, base - bh - 6) for i, bh in enumerate(bars)]
    draw.line(pts, fill=GOLD, width=3)
    draw.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 12, pts[-1][1] + 2), (pts[-1][0] - 2, pts[-1][1] + 10)],
                 fill=GOLD)
    draw.rectangle([x + w - 52, y + 8, x + w - 14, y + 46], fill=(30, 34, 40))
    draw.rectangle([x + w - 44, y + 16, x + w - 22, y + 38], fill=(20, 170, 80))
    for px in range(w - 52, w - 12, 8):
        draw.line([x + px, y + 8, x + px, y + 12], fill=GOLD, width=1)
        draw.line([x + px, y + 42, x + px, y + 46], fill=GOLD, width=1)


def scene_afcon(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(70, 150, 70))
    draw.rectangle([x + 8, y + 8, x + w - 8, y + h - 8], outline=WHITE, width=2)
    draw.line([x + w // 2, y + 8, x + w // 2, y + h - 8], fill=WHITE, width=2)
    draw.ellipse([x + w // 2 - 16, y + h // 2 - 16, x + w // 2 + 16, y + h // 2 + 16],
                 outline=WHITE, width=2)
    draw.rectangle([x + 8, y + h // 2 - 22, x + 34, y + h // 2 + 22], outline=WHITE, width=2)
    draw.line([x + 8, y + 16, x + 8, y + h - 16], fill=WHITE, width=4)
    draw.line([x + 8, y + 16, x + 26, y + 16], fill=WHITE, width=3)
    draw.line([x + 8, y + h - 16, x + 26, y + h - 16], fill=WHITE, width=3)
    draw.ellipse([x + 120, y + 58, x + 136, y + 74], fill=WHITE)
    draw.polygon([(x + 128, y + 60), (x + 132, y + 64), (x + 130, y + 70), (x + 125, y + 68), (x + 125, y + 63)],
                 fill=INK)
    draw.polygon([(x + 158, y + 18), (x + 184, y + 18), (x + 180, y + 40), (x + 162, y + 40)], fill=GOLD)
    draw.rectangle([x + 166, y + 40, x + 176, y + 52], fill=GOLD)
    draw.rectangle([x + 156, y + 52, x + 186, y + 56], fill=GOLD)
    draw.ellipse([x + 60, y + 20, x + 76, y + 36], fill=(255, 255, 255))
    draw.ellipse([x + 68, y + 28, x + 84, y + 44], fill=(240, 240, 235))


def scene_dhoni(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(240, 225, 180), (250, 240, 205)])
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=(90, 150, 80))
    draw.rectangle([x + 20, y + h - 62, x + w - 20, y + h - 34], fill=(210, 190, 140))
    draw.rectangle([x + 20, y + h - 62, x + w - 20, y + h - 58], fill=(240, 235, 220))
    for sx in range(30, w - 10, 26):
        draw.ellipse([x + sx, y + 8, x + sx + 10, y + 18], fill=(200, 120, 90))
        draw.ellipse([x + sx + 4, y + 22, x + sx + 14, y + 32], fill=(90, 120, 180))
    for gx in (28, 52):
        draw.line([x + gx, y + h - 56, x + gx, y + h - 40], fill=(230, 200, 60), width=3)
    draw.line([x + 28, y + h - 58, x + 55, y + h - 58], fill=(230, 200, 60), width=2)
    draw.rectangle([x + 120, y + h - 52, x + 128, y + h - 22], fill=(150, 100, 50))
    draw.ellipse([x + 150, y + h - 56, x + 162, y + h - 44], fill=(200, 30, 30))
    draw.ellipse([x + 154, y + h - 52, x + 158, y + h - 48], fill=(255, 255, 255))
    draw.rectangle([x + 96, y + 44, x + 108, y + 62], fill=(200, 200, 190))
    draw.rectangle([x + 100, y + 38, x + 104, y + 44], fill=(200, 200, 190))


def scene_cop31(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(190, 225, 240), (210, 235, 245)])
    sun_disc(draw, x + w - 26, y + 18, 10)
    cx, cy, r = x + 88, y + 48, 34
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 140, 200))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 90, 150), width=2)
    draw.polygon([(cx - 22, cy - 8), (cx - 6, cy - 18), (cx + 2, cy - 4), (cx - 10, cy + 6)], fill=GREEN)
    draw.polygon([(cx + 6, cy + 4), (cx + 24, cy - 2), (cx + 20, cy + 16), (cx + 2, cy + 20)], fill=GREEN)
    draw.polygon([(cx - 18, cy + 14), (cx - 2, cy + 10), (cx - 6, cy + 26), (cx - 22, cy + 24)], fill=(40, 120, 70))
    for lx, ly, ang in ((150, 18, -30), (168, 34, 20), (150, 62, -15)):
        draw.ellipse([x + lx, y + ly, x + lx + 18, y + ly + 9], fill=GREEN)
        draw.line([x + lx, y + ly + 4, x + lx + 18, y + ly + 4], fill=(20, 90, 40), width=1)
    for fx in range(20, 60, 12):
        draw.rectangle([x + fx, y + h - 8, x + fx + 6, y + h - 4], fill=(30, 90, 150))


def scene_riyadh(draw, x, y, w, h):
    sky_bands(draw, (x, y, x + w, y + h), [(30, 40, 70), (50, 62, 95)])
    for sx, sy in ((20, 8), (70, 16), (140, 6), (170, 20)):
        draw.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    towers = [(10, 46, 26, 62), (44, 34, 22, 74), (72, 52, 30, 56), (110, 28, 24, 80),
              (142, 44, 26, 64), (172, 58, 18, 50)]
    for bx, by, bw, bh in towers:
        draw.rectangle([x + bx, y + h - 14 - bh, x + bx + bw, y + h - 14], fill=(70, 78, 100))
        for wy in range(y + h - 10 - bh, y + h - 18, 10):
            for wx in range(x + bx + 4, x + bx + bw - 4, 8):
                draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 210, 110))
    draw.rectangle([x, y + h - 14, x + w, y + h], fill=(24, 28, 44))
    dx, dy = x + 150, y + 22
    draw.rectangle([dx - 8, dy - 3, dx + 8, dy + 3], fill=(180, 180, 175))
    for rx, ry in ((-14, -8), (14, -8), (-14, 8), (14, 8)):
        draw.line([dx + rx - 8, dy + ry, dx + rx + 8, dy + ry], fill=(140, 140, 135), width=2)
        draw.line([dx, dy, dx + rx, dy + ry], fill=(120, 120, 115), width=1)
    burst(draw, x + 108, y + 30, 11)
    smoke(draw, x + 112, y + 16, 6)


# ---------------- WORLD MAP (leader-line numbers, declustered) ----------------

CONTINENTS = [
    [(18, 18), (70, 8), (118, 14), (132, 26), (108, 44), (92, 66), (60, 58), (34, 44), (14, 30)],
    [(128, 4), (148, 4), (146, 14), (130, 12)],
    [(92, 76), (118, 72), (138, 88), (128, 118), (104, 132), (88, 104)],
    [(212, 22), (238, 14), (258, 20), (252, 36), (232, 44), (214, 38)],
    [(216, 52), (248, 48), (268, 60), (262, 92), (240, 112), (222, 96), (210, 70)],
    [(262, 18), (330, 8), (400, 12), (430, 26), (420, 52), (380, 58), (340, 66), (300, 58), (272, 40)],
    [(372, 96), (410, 92), (424, 104), (404, 122), (378, 116)],
]

# (number, dot x, dot y, badge x, badge y, region)
MAP_POINTS = [
    (1, 272, 30, 294, 12, "WAR"),
    (2, 308, 48, 322, 28, "WAR"),
    (3, 398, 62, 410, 86, "POLITICS"),
    (4, 420, 30, 434, 54, "WAR"),
    (5, 340, 58, 364, 82, "CLIMATE"),
    (6, 238, 34, 254, 16, "POLITICS"),
    (7, 226, 26, 222, 8, "POLITICS"),
    (8, 212, 30, 194, 12, "WAR"),
    (9, 64, 34, 86, 60, "BUSINESS"),
    (10, 238, 78, 212, 112, "SPORT"),
    (11, 322, 52, 338, 78, "SPORT"),
    (12, 258, 38, 246, 58, "CLIMATE"),
    (13, 296, 44, 282, 66, "WAR"),
]


def draw_map(draw, ox, oy):
    draw.rectangle([ox, oy, ox + 456, oy + 142], fill=(178, 214, 232))
    for poly in CONTINENTS:
        pts = [(ox + px, oy + py) for px, py in poly]
        draw.polygon(pts, fill=(232, 214, 170), outline=(190, 170, 125))
    draw_text(draw, ox + 8, oy + 4, "N. AMERICA", font(10), (90, 90, 85))
    draw_text(draw, ox + 96, oy + 108, "S. AMERICA", font(10), (90, 90, 85))
    draw_text(draw, ox + 196, oy + 46, "EUROPE", font(10), (90, 90, 85))
    draw_text(draw, ox + 216, oy + 128, "AFRICA", font(10), (90, 90, 85))
    draw_text(draw, ox + 330, oy + 4, "ASIA", font(10), (90, 90, 85))
    draw_text(draw, ox + 372, oy + 128, "AUSTRALIA", font(10), (90, 90, 85))
    for num, dx, dy, bx, by, region in MAP_POINTS:
        c = REGION_COLORS[region]
        draw.line([ox + dx, oy + dy, ox + bx, oy + by], fill=(60, 60, 55), width=1)
        draw.ellipse([ox + dx - 3, oy + dy - 3, ox + dx + 3, oy + dy + 3], fill=c, outline=WHITE, width=1)
        draw.ellipse([ox + bx - 8, oy + by - 8, ox + bx + 8, oy + by + 8], fill=c, outline=WHITE, width=1)
        label = str(num)
        tw = text_w(draw, label, font(11))
        draw_text(draw, ox + bx - tw // 2, oy + by - 6, label, font(11), WHITE, bold=True)


# ---------------- PANELS ----------------

def lead_panel(draw, x, y, w, h, headline, sub, caption, scene_fn):
    draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=2)
    lines = wrap(draw, headline, font(20), w - 16)
    ly = y + 8
    for ln in lines[:2]:
        draw_text(draw, x + 8, ly, ln, font(20), INK, bold=True)
        ly += 23
    draw.rectangle([x + 8, ly + 1, x + w - 8, ly + 3], fill=RED)
    draw_text(draw, x + 8, ly + 7, sub, font(12), RED, bold=True)
    scene_fn(draw, x + 6, ly + 26, w - 12, 104)
    cy = ly + 26 + 104 + 6
    for ln in wrap(draw, caption, font(12), w - 16)[:2]:
        draw_text(draw, x + 8, cy, ln, font(12), INK)
        cy += 14


def grid_panel(draw, x, y, w, h, num, region, headline, caption, scene_fn):
    draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + 18], fill=BLACK)
    draw_text(draw, x + 6, y + 3, str(num), font(11), GOLD_LT, bold=True)
    draw_text(draw, x + 26, y + 3, region, font(11), WHITE, bold=True)
    lines = wrap(draw, headline, font(14), w - 12)
    ly = y + 22
    for ln in lines[:2]:
        draw_text(draw, x + 6, ly, ln, font(14), INK, bold=True)
        ly += 17
    scene_fn(draw, x + 6, y + 62, w - 12, 92)
    cy = y + 158
    for ln in wrap(draw, caption, font(11), w - 12)[:2]:
        draw_text(draw, x + 6, cy, ln, font(11), INK)
        cy += 13


ALSO_ITEMS = [
    (14, "UK SANCTIONS: 8 FIRMS FROZEN"),
    (15, "MONGOLIA PRESIDENT RESIGNS"),
    (16, "THACI +17 MONTHS, TAMPERING"),
    (17, "EU CHARGES TEMU, FINE TO 6%"),
    (18, "RWANDA HUB: 5 EU STATES PLAN"),
    (19, "S&P -1.0%, SALESFORCE -9.5%"),
    (20, "ILO CHIEF RE-ELECTED 51 OF 56"),
    (21, "NIGERIA INFLATION 14.06%, LOW"),
    (22, "GUINEA: 224 SENTENCED, GOLD"),
    (23, "CALIFORNIA SUES OPENAI"),
    (24, "MONDLANE ON TRIAL, UP TO 24 YRS"),
    (25, "MEASLES: 5,412 CASES, STATUS LOST"),
    (26, "RUSSIAN PLANE DOWN, 19 KILLED - MINISTRY"),
    (27, "EBOLA: 11,254 CASES, 5,505 DEAD"),
    (28, "HOUTHIS WITHIN 100 KM OF ADEN"),
    (29, "ISRAEL FREEZES E1 TENDER, 1,234"),
    (30, "KNESSET SPEAKER: OPPOSITION 66-52"),
    (31, "DEPARDIEU ACCEPTS CONVICTION"),
    (32, "AMAZON $7BN GREEN POWER, INDIA"),
    (33, "APPLE OUT: ICLOUD, PAY, STORE"),
    (34, "CHASE BUG HITS US BANKS"),
    (35, "INDIA BEAT PAKISTAN 2-1, SAFF 10TH"),
    (36, "USA 2-0 HAITI, POCHETTINO OUT"),
    (37, "ZVEREV INTO ATP FINALS LAST 4"),
    (38, "N. IRELAND UP TO LEAGUE A"),
    (39, "HAALAND 96TH-MIN PEN, NORWAY IN"),
    (40, "GQ MEN OF THE YEAR, LONDON"),
]


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # Masthead: black band, gold paper name, giant bold white date.
    d.rectangle([0, 0, W, 86], fill=BLACK)
    draw_text(d, 14, 8, "THE WORLD TODAY", font(16), GOLD, bold=True)
    right = "40 STORIES  ·  6 CONTINENTS  ·  ALL FROM TUESDAY"
    draw_text(d, W - 14, 10, right, font(13), WHITE, anchor_left=False)
    heavy_text(d, 14, 28, "TUESDAY 17 NOVEMBER 2026", font(56), WHITE)
    d.rectangle([0, 84, W, 86], fill=GOLD)

    # Red ticker, verified figures only; shrink until it fits the page.
    d.rectangle([0, 86, W, 110], fill=RED)
    ticker = "NVIDIA $115.8BN  ·  S&P -1.0%  ·  EBOLA 11,254 CASES  ·  MEASLES 5,412  ·  KERCH BRIDGE DOWN  ·  QUAD MEETS IN MANILA"
    tsize = 15
    while text_w(d, ticker, font(tsize)) > W - 20 and tsize > 9:
        tsize -= 1
    center_text(d, W // 2, 92, ticker, font(tsize), WHITE, bold=True)

    # Three equal leads.
    leads = [
        ("KERCH BRIDGE DOWN", "UKRAINE STRIKES, RUSSIA HITS BACK",
         "ROAD SPAN COLLAPSED INTO THE SEA - DRONES + NEPTUNE + FLAMINGO", scene_kerch),
        ("HORMUZ: TANKER HIT", "STRAIT ON EDGE, CREW SAFE",
         "TANKER HIT 7 NM OFF OMAN - 3 US CARRIERS IN THE GULF", scene_hormuz),
        ("QUAD IN MANILA", "FIRST SUMMIT IN 2+ YEARS",
         "TRUMP MODI TAKAICHI ALBANESE - XI-TRUMP-PUTIN THU IN SHENZHEN", scene_quad),
    ]
    for i, (head, sub, cap, fn) in enumerate(leads):
        lead_panel(d, 10 + i * 338, 114, 328, 230, head, sub, cap, fn)

    # 5x2 grid of illustrated stories 4-13.
    grid = [
        (4, "ASIA", "JAPAN SCRAMBLE", "2 RUSSIAN JETS, 04:07 JST - FIRST SINCE SEPT 2024", scene_japan),
        (5, "ASIA", "CYCLONE AKVAN", "TO 130 KM/H, FRI 20 NOV - 610 KM EAST OF CHENNAI", scene_cyclone),
        (6, "EUROPE", "SERBIA: STUDENTS SWORN IN", "140 OF 250 SEATS - ENDS 14 YEARS OF SNS", scene_serbia),
        (7, "EUROPE", "PRAGUE TRAIN CRASH", "46 HURT, 4 SERIOUS - NO DEATHS, 07:00", scene_prague),
        (8, "EUROPE", "FRANCE: SECRET TROOPS", "VOLIA SINCE SUMMER - SEVERAL DOZEN", scene_france),
        (9, "BUSINESS", "NVIDIA $115.8BN RECORD", "Q3 REVENUE +103% YOY - EPS $2.68", scene_nvidia),
        (10, "SPORT", "AFCON: SIX MORE QUALIFY", "9 OF 24 CONFIRMED - 19 JUN-17 JUL 2027", scene_afcon),
        (11, "SPORT", "DHONI RETIRES FROM IPL", "5 TITLES, 278 MATCHES - CSK MENTOR 2027", scene_dhoni),
        (12, "CLIMATE", "COP31: MINISTERS TAKE OVER", "FOSSIL FUEL FIGHT - CLOSES FRI 20 NOV", scene_cop31),
        (13, "MIDEAST", "RIYADH DRONE SHOT DOWN", "3RD IN 2 DAYS - 60 TARGETS HIT", scene_riyadh),
    ]
    for i, (num, region, head, cap, fn) in enumerate(grid):
        row, col = divmod(i, 5)
        grid_panel(d, 10 + col * 202, 348 + row * 202, 196, 198, num, region, head, cap, fn)

    # Bottom-left: world map with leader-line numbers.
    d.rectangle([10, 752, 466, 946], fill=PAPER, outline=INK, width=2)
    d.rectangle([10, 752, 466, 776], fill=BLACK)
    draw_text(d, 18, 757, "WHERE IT HAPPENED", font(13), WHITE, bold=True)
    draw_text(d, 458, 757, "13 MAPPED", font(13), GOLD_LT, bold=True, anchor_left=False)
    draw_map(d, 10, 778)
    legend = "RED WAR  ·  BLUE POLITICS  ·  GREEN BUSINESS  ·  TEAL CLIMATE  ·  PURPLE SPORT"
    lsize = 10
    while text_w(d, legend, font(lsize)) > 440 and lsize > 8:
        lsize -= 1
    center_text(d, 238, 926, legend, font(lsize), INK)

    # Bottom-right: ALSO ON TUESDAY numbered list 14-40.
    d.rectangle([470, 752, 1014, 946], fill=PAPER, outline=INK, width=2)
    d.rectangle([470, 752, 1014, 776], fill=BLACK)
    draw_text(d, 478, 757, "ALSO ON TUESDAY", font(13), WHITE, bold=True)
    draw_text(d, 1006, 757, "14-40", font(13), GOLD_LT, bold=True, anchor_left=False)
    for i, (num, text) in enumerate(ALSO_ITEMS):
        col, row = divmod(i, 14)
        lx = 478 + col * 268
        ly = 782 + row * 12
        size = 11
        num_s = str(num) + " "
        while text_w(d, num_s + text, font(size)) > 258 and size > 9:
            size -= 1
        draw_text(d, lx, ly, num_s, font(size), RED, bold=True)
        draw_text(d, lx + text_w(d, num_s, font(size)), ly, text, font(size), INK)

    # Figures strip + source line.
    d.rectangle([0, 950, W, 982], fill=BLACK)
    figures = "40 STORIES  ·  $115.8BN NVIDIA Q3  ·  11,254 EBOLA CASES  ·  5,412 MEASLES CASES"
    fsize = 16
    while text_w(d, figures, font(fsize)) > W - 20 and fsize > 10:
        fsize -= 1
    center_text(d, W // 2, 958, figures, font(fsize), GOLD_LT, bold=True)
    center_text(d, W // 2, 990, "SOURCES: REUTERS, AP, AFP, BBC, IMD, GOV.UK, CRICBUZZ, PAHO, ILO",
                font(12), INK)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), "PNG")
    print("wrote", os.path.join(out_dir, "entry.png"), img.size)


if __name__ == "__main__":
    main()
