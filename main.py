#!/usr/bin/env python3
"""news-image-20261117 v2: one-image newspaper front page, Tue 17 Nov 2026.

Stdlib only (os/struct/zlib/math). Deterministic: fixed palette, fixed
geometry, no randomness, no time, no dict-order dependence in output.
Writes a 1024x1024 PNG (<=1 MiB) to $MAKEFUN_OUTPUT_DIR or /output.

Design: black-band masthead with the giant date, red ticker, three equal
illustrated leads, a 5x2 grid of illustrated stories 4-13, a world map,
a numbered ALSO ON TUESDAY list (14-40), a day-in-four-figures strip and
a source line. 40 stories, 13 illustrated. All facts from NEWS-v2.md.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
INK = (18, 18, 22)
PAPER = (250, 246, 234)
CREAM = (244, 238, 222)
BLACK = (10, 10, 12)
WHITE = (255, 255, 255)
RED = (176, 32, 32)
DARKRED = (122, 16, 16)
GOLD = (214, 168, 44)
YELLOW = (255, 214, 64)
NAVY = (16, 34, 68)
SKY = (183, 212, 234)
SEA = (24, 78, 110)
SEA2 = (38, 110, 148)
TEAL = (0, 128, 128)
ORANGE = (240, 110, 20)
SMOKE = (148, 148, 154)
GREY = (118, 122, 130)
LGREY = (228, 230, 234)
GREEN = (28, 120, 60)
GREEN2 = (52, 168, 88)
TAN = (226, 208, 168)
SAND = (238, 224, 192)
BROWN = (122, 74, 40)
BLUE = (40, 80, 160)
PINK = (220, 120, 140)

# ------------------------------------------------- vector stroke font
# Glyphs are polylines on a 9-wide x 13-tall grid (x 0..8, y 0..12).
# Drawn with thick segments, so they stay legible from thumbnail size up.
# This is a clean stroke face, deliberately unlike a 5x7 pixel font.
STROKES = {
    "A": [[(0, 12), (4, 0), (8, 12)], [(2, 8), (6, 8)]],
    "B": [[(0, 0), (0, 12)], [(0, 0), (5, 0), (7, 2), (5, 4), (0, 4)],
          [(0, 4), (5, 4), (8, 7), (8, 10), (5, 12), (0, 12)]],
    "C": [[(8, 2), (6, 0), (2, 0), (0, 2), (0, 10), (2, 12), (6, 12), (8, 10)]],
    "D": [[(0, 0), (0, 12)], [(0, 0), (5, 0), (8, 3), (8, 9), (5, 12), (0, 12)]],
    "E": [[(0, 0), (0, 12)], [(0, 0), (8, 0)], [(0, 6), (6, 6)], [(0, 12), (8, 12)]],
    "F": [[(0, 0), (0, 12)], [(0, 0), (8, 0)], [(0, 6), (6, 6)]],
    "G": [[(8, 2), (6, 0), (2, 0), (0, 2), (0, 10), (2, 12), (6, 12), (8, 10),
           (8, 6), (4, 6)]],
    "H": [[(0, 0), (0, 12)], [(8, 0), (8, 12)], [(0, 6), (8, 6)]],
    "I": [[(4, 0), (4, 12)], [(1, 0), (7, 0)], [(1, 12), (7, 12)]],
    "J": [[(8, 0), (8, 10), (6, 12), (2, 12), (0, 10)]],
    "K": [[(0, 0), (0, 12)], [(8, 0), (1, 6)], [(2, 6), (8, 12)]],
    "L": [[(0, 0), (0, 12)], [(0, 12), (8, 12)]],
    "M": [[(0, 12), (0, 0), (4, 6), (8, 0), (8, 12)]],
    "N": [[(0, 12), (0, 0), (8, 12), (8, 0)]],
    "O": [[(2, 0), (6, 0), (8, 2), (8, 10), (6, 12), (2, 12), (0, 10), (0, 2), (2, 0)]],
    "P": [[(0, 12), (0, 0)], [(0, 0), (6, 0), (8, 2), (8, 5), (6, 7), (0, 7)]],
    "Q": [[(2, 0), (6, 0), (8, 2), (8, 10), (6, 12), (2, 12), (0, 10), (0, 2), (2, 0)],
          [(5, 9), (8, 12)]],
    "R": [[(0, 12), (0, 0)], [(0, 0), (6, 0), (8, 2), (8, 5), (6, 7), (0, 7)],
          [(4, 7), (8, 12)]],
    "S": [[(8, 2), (6, 0), (2, 0), (0, 2), (0, 5), (2, 7), (6, 7), (8, 9),
           (8, 11), (6, 12), (2, 12), (0, 10)]],
    "T": [[(0, 0), (8, 0)], [(4, 0), (4, 12)]],
    "U": [[(0, 0), (0, 10), (2, 12), (6, 12), (8, 10), (8, 0)]],
    "V": [[(0, 0), (4, 12), (8, 0)]],
    "W": [[(0, 0), (2, 12), (4, 6), (6, 12), (8, 0)]],
    "X": [[(0, 0), (8, 12)], [(8, 0), (0, 12)]],
    "Y": [[(0, 0), (4, 6), (8, 0)], [(4, 6), (4, 12)]],
    "Z": [[(0, 0), (8, 0), (0, 12), (8, 12)]],
    "0": [[(2, 0), (6, 0), (8, 2), (8, 10), (6, 12), (2, 12), (0, 10), (0, 2), (2, 0)],
          [(6, 2), (2, 10)]],
    "1": [[(2, 2), (4, 0), (4, 12)], [(1, 12), (7, 12)]],
    "2": [[(0, 2), (2, 0), (6, 0), (8, 2), (8, 5), (0, 12), (8, 12)]],
    "3": [[(1, 1), (3, 0), (6, 0), (8, 2), (8, 5), (5, 6)],
          [(5, 6), (8, 7), (8, 10), (6, 12), (3, 12), (1, 11)]],
    "4": [[(5, 0), (5, 12)], [(0, 8), (8, 8)], [(5, 0), (0, 8)]],
    "5": [[(8, 0), (0, 0), (0, 6), (5, 6), (8, 8), (8, 11), (6, 12), (2, 12), (0, 10)]],
    "6": [[(7, 2), (5, 0), (2, 0), (0, 3), (0, 10), (2, 12), (6, 12), (8, 10),
           (8, 7), (6, 5), (2, 5)]],
    "7": [[(0, 0), (8, 0), (4, 12)]],
    "8": [[(2, 0), (6, 0), (8, 2), (8, 5), (6, 7), (2, 7), (0, 5), (0, 2), (2, 0)],
          [(2, 7), (6, 7), (8, 9), (8, 11), (6, 12), (2, 12), (0, 10), (0, 8), (2, 7)]],
    "9": [[(2, 0), (6, 0), (8, 2), (8, 9), (6, 12), (2, 12), (0, 10)],
          [(0, 3), (0, 6), (2, 7), (6, 7), (8, 5)]],
    " ": [],
    ".": [[(4, 11), (4, 12)]],
    ",": [[(4, 10), (3, 12)]],
    "-": [[(1, 6), (7, 6)]],
    ":": [[(4, 3), (4, 4)], [(4, 8), (4, 9)]],
    ";": [[(4, 3), (4, 4)], [(4, 8), (3, 12)]],
    "'": [[(4, 0), (4, 3)]],
    "!": [[(4, 0), (4, 8)], [(4, 11), (4, 12)]],
    "?": [[(1, 3), (2, 0), (6, 0), (8, 2), (8, 4), (6, 6), (4, 6)], [(4, 9), (4, 10)]],
    "/": [[(7, 0), (1, 12)]],
    "(": [[(6, 0), (3, 2), (3, 10), (6, 12)]],
    ")": [[(2, 0), (5, 2), (5, 10), (2, 12)]],
    "&": [[(6, 0), (2, 0), (0, 2), (0, 5), (3, 7), (8, 12)],
          [(8, 1), (4, 5), (0, 9), (2, 12), (6, 12), (8, 10)]],
    "%": [[(1, 1), (2, 1)], [(6, 11), (7, 11)], [(7, 0), (1, 12)]],
    "$": [[(4, 0), (4, 12)],
          [(7, 3), (5, 1), (2, 1), (1, 3), (1, 5), (3, 7), (7, 7), (8, 9),
           (8, 11), (6, 12), (3, 12), (1, 10)]],
    "+": [[(4, 2), (4, 10)], [(0, 6), (8, 6)]],
    "=": [[(0, 4), (8, 4)], [(0, 8), (8, 8)]],
    "\u2022": [[(4, 6), (4, 7)]],
    "\u2014": [[(0, 6), (8, 6)]],
}

ADV = 10.0  # glyph advance, in font units


def glyph_width(text, scale):
    return len(text) * ADV * scale - scale


def wrap_words(text, max_w, scale):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if glyph_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Page:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.paint(0, 0, w, h, bg)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def paint(self, x0, y0, x1, y1, c):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for y in range(y0, y1):
            s = (y * self.w + x0) * 3
            self.buf[s:s + len(row)] = row

    def outline(self, x0, y0, x1, y1, c, t=2):
        self.paint(x0, y0, x1, y0 + t, c)
        self.paint(x0, y1 - t, x1, y1, c)
        self.paint(x0, y0, x0 + t, y1, c)
        self.paint(x1 - t, y0, x1, y1, c)

    def segment(self, x0, y0, x1, y1, c, t=1):
        # Bresenham with a square brush of side t.
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, r = dx + dy, t // 2
        while True:
            for a in range(-r, r + 1):
                for b in range(-r, r + 1):
                    self.put(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            span = int(math.sqrt(max(0, r * r - dy * dy)))
            self.paint(cx - span, y, cx + span + 1, y + 1, c)

    def ringdisc(self, cx, cy, r, c, t=3):
        for y in range(cy - r - t, cy + r + t + 1):
            for x in range(cx - r - t, cx + r + t + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if (r - t) ** 2 <= d2 <= (r + t) ** 2:
                    self.put(x, y, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        top, bot = max(0, min(ys)), min(self.h - 1, max(ys))
        n = len(pts)
        for y in range(top, bot + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.paint(int(xs[k]), y, int(xs[k + 1]) + 1, y + 1, c)

    def vgrad(self, x0, y0, x1, y1, top, bot):
        span = max(1, y1 - y0)
        for y in range(y0, y1):
            t = (y - y0) / span
            col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            self.paint(x0, y, x1, y + 1, col)

    # -- stroke-font text --
    def glyph(self, x, y, ch, scale, c):
        thick = max(1, int(round(scale * 0.95)))
        for poly in STROKES.get(ch, STROKES[" "]):
            for (ax, ay), (bx, by) in zip(poly, poly[1:]):
                self.segment(int(round(x + ax * scale)), int(round(y + ay * scale)),
                             int(round(x + bx * scale)), int(round(y + by * scale)),
                             c, thick)

    def draw_text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, c)
            cx += ADV * scale

    def draw_centre(self, cx, y, s, scale, c):
        self.draw_text(int(cx - glyph_width(s, scale) / 2), y, s, scale, c)

    def draw_lines(self, x, y, lines, scale, c, leading=None):
        if leading is None:
            leading = int(13 * scale) + 2
        for ln in lines:
            self.draw_text(x, y, ln, scale, c)
            y += leading
        return y


# ---------------------------------------------------------------- helpers
def burst_pts(cx, cy, r_out, r_in, n=12):
    pts = []
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        a = math.pi * k / n
        pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
    return pts


def flag_us(pg, x, y, w, h):
    pg.paint(x, y, x + w, y + h, WHITE)
    for i in range(0, 7, 2):
        pg.paint(x, y + i * h // 13, x + w, y + (i + 1) * h // 13, RED)
    pg.paint(x, y, x + w * 2 // 5, y + h * 7 // 13, NAVY)
    for r in range(4):
        for c in range(5):
            pg.put(x + 3 + c * 5, y + 3 + r * 4, WHITE)


def flag_india(pg, x, y, w, h):
    pg.paint(x, y, x + w, y + h // 3, (255, 153, 51))
    pg.paint(x, y + h // 3, x + w, y + 2 * h // 3, WHITE)
    pg.paint(x, y + 2 * h // 3, x + w, y + h, (19, 136, 8))
    pg.ringdisc(x + w // 2, y + h // 2, h // 6, NAVY, 1)


def flag_japan(pg, x, y, w, h):
    pg.paint(x, y, x + w, y + h, WHITE)
    pg.disc(x + w // 2, y + h // 2, h // 4, RED)


def flag_aus(pg, x, y, w, h):
    pg.paint(x, y, x + w, y + h, (0, 40, 120))
    pg.paint(x, y, x + w // 2, y + h // 2, WHITE)
    pg.paint(x, y, x + w // 2, y + h // 2, (0, 40, 120))
    pg.disc(x + 3 * w // 4, y + h // 4, 2, WHITE)
    pg.disc(x + 3 * w // 4, y + 3 * h // 4, 2, WHITE)
    pg.disc(x + w // 2 + 8, y + h // 2, 2, WHITE)


# ---------------------------------------------------------------- leads
def scene_kerch(pg, x0, y0, x1, y1):
    # Scene box is only ~112 tall: sky top, deck mid-height, water bottom.
    pg.vgrad(x0, y0, x1, y1, (14, 28, 62), (30, 62, 112))
    wy = y1 - 26
    pg.paint(x0, wy, x1, y1, SEA)
    for k in range(2):
        yy = wy + 8 + k * 9
        pg.paint(x0 + 14 + (k % 2) * 40, yy, x1 - 20 - (k % 3) * 30, yy + 2, SEA2)
    deck = y0 + 58
    # towers + intact decks
    pg.paint(x0 + 52, deck - 38, x0 + 60, deck + 4, LGREY)
    pg.paint(x1 - 62, deck - 38, x1 - 54, deck + 4, LGREY)
    pg.paint(x0, deck, x0 + 132, deck + 7, LGREY)
    pg.paint(x1 - 132, deck, x1, deck + 7, LGREY)
    pg.paint(x0, deck + 7, x0 + 132, deck + 10, GREY)
    pg.paint(x1 - 132, deck + 7, x1, deck + 10, GREY)
    for dx in range(x0 + 10, x0 + 122, 22):
        pg.paint(dx, deck + 2, dx + 10, deck + 5, YELLOW)
    for dx in range(x1 - 122, x1 - 12, 22):
        pg.paint(dx, deck + 2, dx + 10, deck + 5, YELLOW)
    # sagging snapped cables
    pg.segment(x0 + 56, deck - 36, x0 + 96, deck - 12, GREY, 2)
    pg.segment(x0 + 96, deck - 12, x0 + 130, deck, GREY, 2)
    pg.segment(x1 - 58, deck - 36, x1 - 98, deck - 12, GREY, 2)
    pg.segment(x1 - 98, deck - 12, x1 - 132, deck, GREY, 2)
    # collapsed span plunging into the water
    mid = (x0 + x1) // 2
    pg.fill_poly([(x0 + 128, deck + 2), (mid + 48, deck + 26), (mid + 40, deck + 32),
                  (x0 + 118, deck + 10)], (150, 152, 158))
    pg.segment(x0 + 132, deck + 5, mid + 42, deck + 28, LGREY, 2)
    pg.segment(x0 + 148, deck + 14, mid + 28, deck + 24, YELLOW, 2)
    # spray where the span hits the water
    pg.fill_poly([(mid + 36, wy + 2), (mid + 42, wy - 14), (mid + 50, wy + 2)], WHITE)
    pg.fill_poly([(mid + 50, wy + 2), (mid + 58, wy - 10), (mid + 64, wy + 2)], (210, 228, 238))
    pg.paint(mid + 34, wy + 1, mid + 66, wy + 4, WHITE)
    # starburst explosions at both breaks + smoke above the deck
    pg.fill_poly(burst_pts(x0 + 134, deck, 20, 10), ORANGE)
    pg.fill_poly(burst_pts(x0 + 134, deck, 11, 5), YELLOW)
    pg.fill_poly(burst_pts(x1 - 134, deck, 19, 9), ORANGE)
    pg.fill_poly(burst_pts(x1 - 134, deck, 10, 5), YELLOW)
    for (sx, sy, r) in [(x0 + 128, deck - 24, 12), (x0 + 142, deck - 38, 14),
                        (x1 - 128, deck - 22, 11), (x1 - 140, deck - 36, 13)]:
        pg.disc(sx, sy, r, SMOKE)
        pg.disc(sx - 4, sy - 3, max(2, r - 5), (172, 172, 178))


def scene_hormuz(pg, x0, y0, x1, y1):
    pg.vgrad(x0, y0, x1, y1, SKY, (200, 224, 240))
    wy = y1 - 56
    pg.paint(x0, wy, x1, y1, SEA)
    for k in range(3):
        yy = wy + 12 + k * 13
        pg.paint(x0 + 12 + (k % 2) * 50, yy, x1 - 16, yy + 2, SEA2)
    # burning tanker, listing
    pg.fill_poly([(x0 + 28, wy - 8), (x0 + 210, wy - 8), (x0 + 196, wy + 26),
                  (x0 + 42, wy + 26)], (128, 28, 28))
    pg.paint(x0 + 168, wy - 34, x0 + 198, wy - 8, WHITE)
    pg.paint(x0 + 52, wy - 24, x0 + 76, wy - 8, (200, 200, 205))
    pg.disc(x0 + 96, wy - 26, 15, ORANGE)
    pg.disc(x0 + 96, wy - 26, 8, YELLOW)
    pg.disc(x0 + 92, wy - 44, 12, SMOKE)
    pg.disc(x0 + 82, wy - 60, 13, SMOKE)
    # three carriers, flat tops: larger, lighter hulls, staggered in
    # formation, each with a foam wake trailing behind the stern
    carriers = [(x0 + 238, 8), (x0 + 272, 2), (x0 + 302, 10)]
    for cx, off in carriers:
        top = wy + off
        pg.paint(cx - 40, top + 15, cx - 16, top + 17, (210, 228, 238))
        pg.paint(cx - 34, top + 18, cx - 16, top + 20, SEA2)
    for cx, off in carriers:
        top = wy + off
        pg.paint(cx - 18, top, cx + 18, top + 13, (96, 104, 114))
        pg.paint(cx - 18, top, cx + 18, top + 2, (150, 158, 168))
        pg.paint(cx + 6, top - 9, cx + 14, top, (96, 104, 114))
        pg.segment(cx - 2, top - 9, cx - 2, top - 14, (150, 158, 168), 1)
    pg.disc(x0 + 238, wy - 8, 3, WHITE)


def scene_quad(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (236, 240, 248))
    # four flags on poles across the top of the scene
    fw, fh = 56, 34
    flags = [flag_us, flag_india, flag_japan, flag_aus]
    for i, fn in enumerate(flags):
        fx = x0 + 18 + i * 76
        pg.paint(fx + 26, y0 + 6, fx + 28, y0 + 46, INK)
        fn(pg, fx, y0 + 8, fw, fh)
    # four leaders: shoulders + heads, distinct hair
    skins = [(232, 190, 150), (190, 140, 100), (240, 205, 170), (225, 180, 140)]
    suits = [(30, 40, 70), (20, 60, 40), (70, 30, 50), (40, 50, 90)]
    hairs = [(40, 40, 44), (20, 20, 22), (36, 36, 40), (88, 84, 80)]
    for i in range(4):
        cx = x0 + 46 + i * 76
        cy = y0 + 62
        pg.disc(cx, cy - 4, 13, hairs[i])
        pg.disc(cx, cy + 3, 12, skins[i])
        if i == 0:
            pg.fill_poly([(cx - 14, cy - 4), (cx - 1, cy - 13), (cx + 14, cy - 6),
                          (cx + 11, cy - 1), (cx - 6, cy - 5)], (232, 200, 100))
        elif i == 1:
            pg.fill_poly([(cx - 9, cy + 4), (cx + 9, cy + 4), (cx + 7, cy + 15),
                          (cx - 7, cy + 15)], WHITE)
        elif i == 2:
            pg.fill_poly([(cx - 15, cy - 8), (cx - 8, cy - 8), (cx - 10, cy + 10),
                          (cx - 15, cy + 8)], (36, 36, 40))
            pg.fill_poly([(cx + 15, cy - 8), (cx + 8, cy - 8), (cx + 10, cy + 10),
                          (cx + 15, cy + 8)], (36, 36, 40))
        else:
            pg.fill_poly([(cx - 13, cy - 5), (cx, cy - 12), (cx + 13, cy - 5),
                          (cx + 10, cy - 9), (cx - 10, cy - 9)], (168, 168, 173))
        # shoulders widen DOWNWARD from the chin to the table: the head
        # stays visible above the suit (never covered by it).
        pg.fill_poly([(cx - 15, cy + 12), (cx + 15, cy + 12), (cx + 22, y1 - 18),
                      (cx - 22, y1 - 18)], suits[i])
    pg.paint(x0 + 10, y1 - 18, x1 - 10, y1 - 14, (122, 74, 40))


# ---------------------------------------------------------------- mid scenes
def scene_japan(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, SKY)
    pg.disc(x1 - 22, y0 + 16, 10, (240, 236, 210))
    # big grey jet (right) and red interceptor (left)
    pg.fill_poly([(x0 + 96, y0 + 30), (x0 + 168, y0 + 22), (x0 + 168, y0 + 38),
                  (x0 + 96, y0 + 42)], (90, 96, 104))
    pg.fill_poly([(x0 + 168, y0 + 22), (x0 + 182, y0 + 30), (x0 + 168, y0 + 36)], (90, 96, 104))
    pg.fill_poly([(x0 + 128, y0 + 22), (x0 + 136, y0 + 10), (x0 + 142, y0 + 22)], (90, 96, 104))
    pg.fill_poly([(x0 + 14, y0 + 52), (x0 + 82, y0 + 44), (x0 + 82, y0 + 58),
                  (x0 + 14, y0 + 62)], RED)
    pg.fill_poly([(x0 + 82, y0 + 44), (x0 + 96, y0 + 50), (x0 + 82, y0 + 56)], RED)
    pg.fill_poly([(x0 + 44, y0 + 44), (x0 + 52, y0 + 34), (x0 + 58, y0 + 44)], RED)
    pg.segment(x0 + 96, y0 + 50, x0 + 118, y0 + 40, WHITE, 2)
    pg.disc(x0 + 30, y0 + 14, 3, WHITE)
    pg.disc(x0 + 60, y0 + 8, 2, WHITE)


def scene_cyclone(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (208, 226, 240))
    cx, cy = (x0 + x1) // 2, y0 + 38
    for r, col in [(30, WHITE), (23, (140, 180, 210)), (16, WHITE),
                   (10, (90, 140, 190)), (4, NAVY)]:
        pg.disc(cx, cy, r, col)
    for a in range(0, 360, 45):
        pts = []
        for k in range(4):
            ang = math.radians(a + k * 20)
            r = 6 + k * 7
            pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
        for j in range(len(pts) - 1):
            pg.segment(pts[j][0], pts[j][1], pts[j + 1][0], pts[j + 1][1], WHITE, 3)
    pg.segment(x1 - 16, y0 + 8, x1 - 26, y0 + 30, TEAL, 2)
    pg.segment(x1 - 26, y0 + 30, x1 - 14, y0 + 52, TEAL, 2)
    pg.disc(x0 + 14, y0 + 58, 3, WHITE)


def scene_serbia(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, CREAM)
    # parliament: pediment + columns + steps
    pg.fill_poly([(x0 + 30, y0 + 22), (x0 + 158, y0 + 22), ((x0 + x1) // 2, y0 + 6)], (190, 170, 130))
    pg.paint(x0 + 30, y0 + 22, x0 + 158, y0 + 28, (170, 150, 110))
    for i in range(5):
        cx = x0 + 42 + i * 26
        pg.paint(cx, y0 + 28, cx + 7, y0 + 58, WHITE)
        pg.paint(cx - 2, y0 + 26, cx + 9, y0 + 29, (200, 200, 205))
    pg.paint(x0 + 28, y0 + 58, x0 + 160, y0 + 62, (170, 150, 110))
    pg.paint(x0 + 22, y0 + 62, x0 + 166, y0 + 66, (150, 130, 95))
    # Serbian tricolour flag
    pg.paint(x1 - 34, y0 + 10, x1 - 10, y0 + 18, RED)
    pg.paint(x1 - 34, y0 + 18, x1 - 10, y0 + 26, BLUE)
    pg.paint(x1 - 34, y0 + 26, x1 - 10, y0 + 34, WHITE)
    pg.paint(x1 - 34, y0 + 6, x1 - 33, y0 + 40, INK)


def scene_prague(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (226, 232, 240))
    # bridge deck + two trains meeting head-on
    pg.paint(x0 + 8, y0 + 46, x1 - 8, y0 + 50, INK)
    pg.paint(x0 + 20, y0 + 50, x0 + 24, y0 + 66, INK)
    pg.paint(x1 - 24, y0 + 50, x1 - 20, y0 + 66, INK)
    pg.fill_poly([(x0 + 12, y0 + 26), (x0 + 84, y0 + 26), (x0 + 84, y0 + 46),
                  (x0 + 12, y0 + 46)], (200, 30, 30))
    pg.fill_poly([(x1 - 84, y0 + 26), (x1 - 12, y0 + 26), (x1 - 12, y0 + 46),
                  (x1 - 84, y0 + 46)], (30, 80, 160))
    for i in range(3):
        pg.paint(x0 + 20 + i * 22, y0 + 32, x0 + 36 + i * 22, y0 + 40, WHITE)
        pg.paint(x1 - 76 + i * 22, y0 + 32, x1 - 60 + i * 22, y0 + 40, WHITE)
    pg.fill_poly(burst_pts((x0 + x1) // 2, y0 + 36, 14, 7), ORANGE)
    pg.fill_poly(burst_pts((x0 + x1) // 2, y0 + 36, 8, 4), YELLOW)
    # red signal
    pg.paint(x1 - 18, y0 + 8, x1 - 15, y0 + 26, INK)
    pg.disc(x1 - 16, y0 + 10, 4, RED)


def scene_france(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (232, 238, 246))
    # French tricolour
    pg.paint(x0 + 14, y0 + 8, x0 + 38, y0 + 26, BLUE)
    pg.paint(x0 + 38, y0 + 8, x0 + 62, y0 + 26, WHITE)
    pg.paint(x0 + 62, y0 + 8, x0 + 86, y0 + 26, RED)
    pg.paint(x0 + 14, y0 + 6, x0 + 86, y0 + 8, INK)
    # Caesar gun / tank silhouette
    pg.fill_poly([(x0 + 30, y0 + 52), (x0 + 130, y0 + 52), (x0 + 130, y0 + 62),
                  (x0 + 30, y0 + 62)], (70, 78, 66))
    pg.segment(x0 + 120, y0 + 48, x0 + 172, y0 + 34, (70, 78, 66), 4)
    pg.paint(x0 + 52, y0 + 40, x0 + 96, y0 + 52, (90, 98, 86))
    for i in range(5):
        pg.disc(x0 + 42 + i * 20, y0 + 64, 4, INK)
    pg.disc(x1 - 18, y0 + 58, 5, GOLD)


def scene_nvidia(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, WHITE)
    base = y0 + 62
    pg.paint(x0 + 14, y0 + 8, x0 + 16, base, INK)
    pg.paint(x0 + 14, base, x1 - 10, base + 2, INK)
    vals = [14, 22, 18, 30, 44]
    for i, v in enumerate(vals):
        bx = x0 + 26 + i * 30
        col = GREEN2 if i == 4 else GREEN
        pg.paint(bx, base - v, bx + 20, base, col)
    pg.segment(x0 + 24, base - 18, x1 - 16, base - 48, GOLD, 3)
    pg.disc(x1 - 18, base - 48, 4, GOLD)


def scene_afcon(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (220, 238, 214))
    cx, cy = (x0 + x1) // 2, y0 + 36
    pg.disc(cx, cy, 26, WHITE)
    pg.outline(cx - 26, cy - 26, cx + 27, cy + 27, INK, 1)
    pg.fill_poly([(cx - 7, cy - 6), (cx + 7, cy - 6), (cx + 10, cy + 4),
                  (cx, cy + 10), (cx - 10, cy + 4)], INK)
    pg.segment(cx, cy - 26, cx - 7, cy - 6, INK, 1)
    pg.segment(cx, cy - 26, cx + 7, cy - 6, INK, 1)
    pg.segment(cx - 26, cy - 2, cx - 10, cy + 4, INK, 1)
    pg.segment(cx + 26, cy - 2, cx + 10, cy + 4, INK, 1)
    # trophy
    pg.paint(x1 - 34, y0 + 44, x1 - 22, y0 + 62, GOLD)
    pg.paint(x1 - 38, y0 + 62, x1 - 18, y0 + 66, GOLD)
    pg.paint(x1 - 40, y0 + 44, x1 - 34, y0 + 54, GOLD)
    pg.paint(x1 - 22, y0 + 44, x1 - 16, y0 + 54, GOLD)


def scene_dhoni(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (255, 244, 200))
    # pitch strip across the bottom of the scene
    pg.paint(x0 + 6, y0 + 44, x1 - 6, y1 - 2, (240, 222, 168))
    pg.paint(x0 + 6, y0 + 44, x1 - 6, y0 + 46, WHITE)
    pg.paint(x0 + 6, y1 - 4, x1 - 6, y1 - 2, WHITE)
    # popping creases at both ends
    pg.paint(x0 + 14, y0 + 52, x0 + 46, y0 + 54, WHITE)
    pg.paint(x1 - 46, y0 + 52, x1 - 14, y0 + 54, WHITE)
    # larger cricket bat, centre-left
    pg.fill_poly([(x0 + 56, y0 + 6), (x0 + 78, y0 + 6), (x0 + 86, y0 + 44),
                  (x0 + 64, y0 + 44)], (222, 184, 120))
    pg.paint(x0 + 64, y0 + 44, x0 + 78, y0 + 60, (180, 140, 80))
    pg.segment(x0 + 60, y0 + 10, x0 + 82, y0 + 40, (200, 160, 100), 1)
    # ball, top right
    pg.disc(x1 - 30, y0 + 20, 9, RED)
    pg.segment(x1 - 38, y0 + 14, x1 - 22, y0 + 26, WHITE, 1)
    # stumps at both ends, taller with bails
    for sx in [x0 + 18, x1 - 42]:
        for i in range(3):
            pg.paint(sx + i * 8, y0 + 40, sx + 3 + i * 8, y1 - 2, YELLOW)
        pg.paint(sx - 2, y0 + 38, sx + 24, y0 + 40, YELLOW)
    pg.disc(x0 + 130, y0 + 58, 4, WHITE)


def scene_cop(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (210, 232, 226))
    cx, cy = (x0 + x1) // 2, y0 + 36
    pg.disc(cx, cy, 26, (90, 160, 210))
    pg.fill_poly([(cx - 20, cy - 4), (cx - 6, cy - 12), (cx + 2, cy - 2),
                  (cx + 14, cy - 10), (cx + 20, cy + 2), (cx + 8, cy + 12),
                  (cx - 10, cy + 14), (cx - 20, cy + 6)], GREEN)
    pg.fill_poly([(cx - 14, cy + 8), (cx - 2, cy + 2), (cx + 12, cy + 10),
                  (cx - 2, cy + 16)], (40, 120, 70))
    # leaf
    pg.fill_poly([(x1 - 36, y0 + 10), (x1 - 16, y0 + 16), (x1 - 30, y0 + 28),
                  (x1 - 38, y0 + 20)], GREEN2)
    pg.segment(x1 - 36, y0 + 10, x1 - 18, y0 + 26, GREEN, 1)


def scene_riyadh(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, (238, 226, 208))
    # Riyadh skyline towers
    for (tx, tw, th) in [(14, 18, 34), (38, 14, 46), (58, 20, 28), (84, 14, 40),
                         (104, 18, 30), (128, 16, 44)]:
        pg.paint(x0 + tx, y0 + 66 - th, x0 + tx + tw, y0 + 66, (120, 110, 96))
    pg.paint(x0 + 14, y0 + 66, x1 - 10, y0 + 68, INK)
    # drone + intercept burst in the sky
    pg.fill_poly([(x0 + 96, y0 + 14), (x0 + 128, y0 + 14), (x0 + 128, y0 + 20),
                  (x0 + 96, y0 + 20)], (70, 72, 78))
    pg.segment(x0 + 92, y0 + 12, x0 + 100, y0 + 10, INK, 1)
    pg.segment(x0 + 124, y0 + 12, x0 + 132, y0 + 10, INK, 1)
    pg.fill_poly(burst_pts(x0 + 52, y0 + 20, 13, 6), ORANGE)
    pg.fill_poly(burst_pts(x0 + 52, y0 + 20, 7, 3), YELLOW)


# ---------------------------------------------------------------- panels
def fit_scale(text, max_w, cap):
    s = cap
    while s > 0.4 and glyph_width(text, s) > max_w:
        s -= 0.05
    return s


def lead_panel(pg, x0, y0, x1, y1, num, title, sub, scene_fn, facts):
    pg.paint(x0, y0, x1, y1, WHITE)
    pg.outline(x0, y0, x1, y1, INK, 2)
    inner = x1 - x0 - 16
    ts = fit_scale(title, inner, 1.7)
    pg.draw_centre((x0 + x1) // 2, y0 + 8, title, ts, INK)
    pg.paint(x0 + 10, y0 + 34, x1 - 10, y0 + 36, RED)
    pg.draw_centre((x0 + x1) // 2, y0 + 40, sub, 0.95, DARKRED)
    pg.paint(x0 + 8, y0 + 58, x0 + 30, y0 + 80, RED)
    pg.draw_centre(x0 + 19, y0 + 62, str(num), 1.0, WHITE)
    scene_fn(pg, x0 + 8, y0 + 60, x1 - 8, y1 - 52)
    fy = y1 - 48
    for fact in facts:
        fs = fit_scale(fact, inner, 0.95)
        pg.draw_centre((x0 + x1) // 2, fy, fact, fs, INK)
        fy += 15


def mid_panel(pg, x0, y0, x1, y1, num, region, title, scene_fn, facts):
    pg.paint(x0, y0, x1, y1, WHITE)
    pg.outline(x0, y0, x1, y1, INK, 2)
    pg.paint(x0, y0, x1, y0 + 20, BLACK)
    num_s = str(num)
    pg.draw_text(x0 + 6, y0 + 4, num_s, 0.95, YELLOW)
    # clear gap between the number and the region label: two-digit
    # numbers used to sit ~3 px from the label and read as one word
    # ("12CLIMATE"). Region now starts 10 px past the number's width.
    pg.draw_text(int(x0 + 6 + glyph_width(num_s, 0.95) + 10), y0 + 4,
                 region, 0.85, WHITE)
    inner = x1 - x0 - 12
    lines = wrap_words(title, inner, 1.0)
    pg.draw_lines(x0 + 6, y0 + 24, lines[:2], 1.0, INK, 14)
    scene_fn(pg, x0 + 6, y0 + 56, x1 - 6, y0 + 118)
    fy = y0 + 122
    for fact in facts:
        fs = fit_scale(fact, inner, 0.8)
        pg.draw_text(x0 + 6, fy, fact, fs, INK)
        fy += 13


# ---------------------------------------------------------------- map + list
MAP_DOTS = [
    # (number, x, y, colour) in map-box coords; centres kept >=19 px apart
    # so no two numbered dots overlap.
    (9, 55, 55, GREEN), (1, 275, 40, RED), (6, 242, 60, BLUE),
    (7, 230, 35, BLUE), (8, 208, 55, RED), (12, 260, 72, TEAL),
    (3, 308, 72, RED), (13, 292, 92, RED), (5, 338, 82, TEAL),
    (11, 322, 102, (120, 60, 160)), (2, 392, 98, BLUE), (4, 418, 52, RED),
    (10, 245, 108, (120, 60, 160)),
]

CONTINENTS = [
    [(20, 40), (70, 20), (130, 28), (140, 55), (110, 70), (80, 95), (50, 80), (25, 60)],
    [(95, 110), (125, 105), (140, 130), (125, 175), (105, 160), (95, 130)],
    [(215, 35), (250, 25), (275, 35), (265, 55), (240, 60), (220, 50)],
    [(215, 75), (255, 70), (280, 85), (270, 125), (245, 145), (225, 120), (212, 95)],
    [(280, 25), (360, 15), (420, 30), (430, 60), (380, 80), (330, 70), (295, 55), (280, 40)],
    [(370, 150), (410, 145), (425, 165), (400, 180), (375, 170)],
]


def draw_map(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, WHITE)
    pg.outline(x0, y0, x1, y1, INK, 2)
    pg.paint(x0, y0, x1, y0 + 24, BLACK)
    pg.draw_text(x0 + 8, y0 + 6, "WHERE IT HAPPENED", 1.05, WHITE)
    pg.draw_text(x1 - 118, y0 + 6, "13 MAPPED", 0.9, YELLOW)
    mx, my = x0 + 8, y0 + 30
    pg.paint(mx, my, mx + 444, my + 186, (198, 222, 238))
    for poly in CONTINENTS:
        shifted = [(mx + px, my + py) for (px, py) in poly]
        pg.fill_poly(shifted, SAND)
        pg.fill_poly([(mx + px + 3, my + py + 3) for (px, py) in poly], TAN)
    # region labels on the map
    pg.draw_text(mx + 30, my + 30, "N. AMERICA", 0.7, (90, 80, 60))
    pg.draw_text(mx + 92, my + 128, "S. AMERICA", 0.7, (90, 80, 60))
    pg.draw_text(mx + 205, my + 12, "EUROPE", 0.7, (90, 80, 60))
    pg.draw_text(mx + 210, my + 128, "AFRICA", 0.7, (90, 80, 60))
    pg.draw_text(mx + 330, my + 30, "ASIA", 0.7, (90, 80, 60))
    pg.draw_text(mx + 372, my + 158, "AUSTRALIA", 0.7, (90, 80, 60))
    for (num, dx, dy, col) in MAP_DOTS:
        pg.disc(mx + dx, my + dy, 9, col)
        pg.ringdisc(mx + dx, my + dy, 9, WHITE, 1)
        label = str(num)
        tw = glyph_width(label, 0.8)
        pg.draw_text(int(mx + dx - tw / 2), int(my + dy - 5), label, 0.8, WHITE)
    ly = y1 - 24
    pg.draw_text(x0 + 8, ly, "RED WAR  BLUE POLITICS  GREEN BUSINESS", 0.75, INK)
    pg.draw_text(x0 + 8, ly + 11, "TEAL CLIMATE  PURPLE SPORT", 0.75, INK)


ALSO = [
    "14 UK SANCTIONS: 8 FIRMS FROZEN",
    "15 MONGOLIA PRESIDENT RESIGNS",
    "16 THACI +17 MONTHS, TAMPERING",
    "17 EU CHARGES TEMU, FINE UP TO 6%",
    "18 RWANDA HUB: 5 EU STATES PLAN",
    "19 S&P -1.0%, SALESFORCE -9.5%",
    "20 ILO CHIEF RE-ELECTED 51 OF 56",
    "21 NIGERIA INFLATION 14.06%, LOW",
    "22 GUINEA: 224 SENTENCED, GOLD",
    "23 CALIFORNIA SUES OPENAI, ROGUE AI",
    "24 MONDLANE ON TRIAL, UP TO 24 YRS",
    "25 MEASLES: 5,412 CASES, STATUS LOST",
    "26 RUSSIAN PLANE DOWN, 19 KILLED",
    "27 EBOLA: 11,254 CASES, 5,505 DEAD",
    "28 HOUTHIS WITHIN 100 KM OF ADEN",
    "29 ISRAEL FREEZES E1 TENDER, 1,234",
    "30 KNESSET SPEAKER: OPPOSITION 66-52",
    "31 DEPARDIEU ACCEPTS CONVICTION",
    "32 AMAZON $7BN GREEN POWER, INDIA",
    "33 APPLE OUT: ICLOUD, PAY, STORE",
    "34 CHASE BUG HITS BANKS, 418 DELAYED",
    "35 INDIA BEAT PAKISTAN 2-1, SAFF 10TH",
    "36 USA 2-0 HAITI, POCHETTINO OUT",
    "37 ZVEREV INTO ATP FINALS LAST 4",
    "38 N. IRELAND UP TO LEAGUE A",
    "39 HAALAND 96TH-MIN PEN, NORWAY IN",
    "40 GQ MEN OF THE YEAR, LONDON",
]


def draw_list(pg, x0, y0, x1, y1):
    pg.paint(x0, y0, x1, y1, WHITE)
    pg.outline(x0, y0, x1, y1, INK, 2)
    pg.paint(x0, y0, x1, y0 + 24, BLACK)
    pg.draw_text(x0 + 8, y0 + 6, "ALSO ON TUESDAY", 1.05, WHITE)
    pg.draw_text(x1 - 92, y0 + 6, "14 - 40", 0.9, YELLOW)
    col_w = (x1 - x0 - 16) // 2
    for idx, item in enumerate(ALSO):
        col = idx // 14
        row = idx % 14
        ix = x0 + 8 + col * (col_w + 4)
        iy = y0 + 32 + row * 16
        fs = fit_scale(item, col_w, 0.8)
        pg.draw_text(ix, iy, item, fs, INK)
        if row < 13:
            pg.paint(ix, iy + 13, ix + col_w - 4, iy + 14, LGREY)


# ---------------------------------------------------------------- build
def build():
    pg = Page(W, H, PAPER)
    # masthead: black band, giant white date, paper name + count
    pg.paint(0, 0, W, 96, BLACK)
    pg.paint(0, 96, W, 100, GOLD)
    pg.draw_text(14, 10, "THE WORLD TODAY", 1.3, GOLD)
    right = "40 STORIES \u2022 6 CONTINENTS \u2022 ALL FROM TUESDAY"
    pg.draw_text(int(W - 14 - glyph_width(right, 1.0)), 12, right, 1.0, WHITE)
    pg.draw_centre(W // 2, 34, "TUESDAY 17 NOVEMBER 2026", 3.6, WHITE)
    # red ticker strip
    pg.paint(0, 100, W, 128, RED)
    ticker = ("NVIDIA $115.8BN \u2022 S&P -1.0% \u2022 EBOLA 11,254 CASES "
              "\u2022 MEASLES 5,412 \u2022 KERCH BRIDGE DOWN \u2022 QUAD MEETS IN MANILA")
    pg.draw_centre(W // 2, 108, ticker, fit_scale(ticker, W - 16, 1.0), WHITE)
    # three equal leads
    lead_panel(pg, 8, 134, 330, 358, 1, "KERCH BRIDGE DOWN",
               "UKRAINE STRIKES, RUSSIA HITS BACK", scene_kerch,
               ["ROAD SPAN COLLAPSED INTO THE SEA",
                "DRONES + NEPTUNE + FLAMINGO"])
    lead_panel(pg, 342, 134, 682, 358, 2, "HORMUZ: TANKER HIT",
               "STRAIT ON EDGE, CREW SAFE", scene_hormuz,
               ["TANKER HIT 7 NM OFF OMAN",
                "3 US CARRIERS IN THE GULF"])
    lead_panel(pg, 694, 134, 1016, 358, 3, "QUAD IN MANILA",
               "FIRST SUMMIT IN 2+ YEARS", scene_quad,
               ["TRUMP MODI TAKAICHI ALBANESE",
                "XI-TRUMP-PUTIN THU IN SHENZHEN"])
    # middle grid: 10 illustrated stories, 4-13
    mids = [
        (4, "ASIA", "JAPAN SCRAMBLE", scene_japan,
         ["2 RUSSIAN JETS, 04:07 JST", "FIRST SINCE SEPT 2024"]),
        (5, "ASIA", "CYCLONE AKVAN", scene_cyclone,
         ["TO 130 KM/H, FRI 20 NOV", "610 KM EAST OF CHENNAI"]),
        (6, "EUROPE", "SERBIA: STUDENTS SWORN IN", scene_serbia,
         ["140 OF 250 SEATS", "ENDS 14 YEARS OF SNS"]),
        (7, "EUROPE", "PRAGUE TRAIN CRASH", scene_prague,
         ["46 HURT, 4 SERIOUS", "NO DEATHS, 07:00"]),
        (8, "EUROPE", "FRANCE: SECRET TROOPS", scene_france,
         ["VOLIA SINCE SUMMER", "SEVERAL DOZEN"]),
        (9, "BUSINESS", "NVIDIA $115.8BN RECORD", scene_nvidia,
         ["Q3 REVENUE +103% YOY", "EPS $2.68"]),
        (10, "SPORT", "AFCON: SIX MORE QUALIFY", scene_afcon,
         ["9 OF 24 CONFIRMED", "19 JUN - 17 JUL 2027"]),
        (11, "SPORT", "DHONI RETIRES FROM IPL", scene_dhoni,
         ["5 TITLES, 278 MATCHES", "CSK MENTOR 2027"]),
        (12, "CLIMATE", "COP31: MINISTERS TAKE OVER", scene_cop,
         ["FOSSIL FUEL FIGHT", "CLOSES FRI 20 NOV"]),
        (13, "MIDEAST", "RIYADH DRONE SHOT DOWN", scene_riyadh,
         ["3RD IN 2 DAYS", "60 TARGETS HIT"]),
    ]
    for idx, (num, region, title, fn, facts) in enumerate(mids):
        col, row = idx % 5, idx // 5
        x0 = 8 + col * 203
        y0 = 364 + row * 158
        mid_panel(pg, x0, y0, x0 + 196, y0 + 150, num, region, title, fn, facts)
    # bottom: map left, list right
    draw_map(pg, 8, 680, 468, 940)
    draw_list(pg, 476, 680, 1016, 940)
    # day in four figures strip
    pg.paint(0, 948, W, 980, BLACK)
    figures = "40 STORIES  |  $115.8BN NVIDIA Q3  |  11,254 EBOLA CASES  |  5,412 MEASLES CASES"
    pg.draw_centre(W // 2, 956, figures, fit_scale(figures, W - 20, 1.15), YELLOW)
    # source line
    pg.draw_centre(W // 2, 990, "SOURCES: REUTERS, AP, AFP, BBC, IMD, GOV.UK, CRICBUZZ, PAHO, ILO",
                   0.85, INK)
    return pg


# ---------------------------------------------------------------- PNG out
def pack_chunk(typ, data):
    body = struct.pack(">I", len(data)) + typ + data
    return body + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def save_png(path, pg):
    raw = bytearray()
    for y in range(pg.h):
        raw.append(0)
        raw += pg.buf[y * pg.w * 3:(y + 1) * pg.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += pack_chunk(b"IHDR", struct.pack(">IIBBBBB", pg.w, pg.h, 8, 2, 0, 0, 0))
    png += pack_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += pack_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out, exist_ok=True)
    save_png(os.path.join(out, "entry.png"), build())


if __name__ == "__main__":
    main()
