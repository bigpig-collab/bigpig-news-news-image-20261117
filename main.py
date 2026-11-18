#!/usr/bin/env python3
"""news-image-20261117: one-image newspaper front page for Tue 17 Nov 2026.

Stdlib only. Deterministic: fixed palette, fixed layout, seeded star field.
Writes entry.png (1024x1024) to $MAKEFUN_OUTPUT_DIR or /output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
INK = (16, 16, 20)
PAPER = (250, 247, 238)
NAVY = (13, 27, 62)
NAVY2 = (28, 58, 110)
RED = (178, 34, 34)
DARKRED = (120, 18, 18)
YELLOW = (255, 214, 64)
WHITE = (255, 255, 255)
GREY = (120, 124, 132)
LGREY = (226, 228, 232)
SEA = (18, 64, 92)
SEA2 = (30, 96, 128)
SKY = (186, 214, 235)
ORANGE = (255, 122, 26)
SMOKE = (150, 150, 156)
TEAL = (0, 128, 128)
GOLD = (201, 162, 39)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 strings of 5 chars, '#' = on.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "\u00b7": ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    "\u2192": ("00000", "00100", "00010", "11111", "00010", "00100", "00000"),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill(self, x0, y0, x1, y1, c):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        r, g, b = c
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def rect(self, x0, y0, x1, y1, c, t=1):
        self.fill(x0, y0, x1, y0 + t, c)
        self.fill(x0, y1 - t, x1, y1, c)
        self.fill(x0, y0, x0 + t, y1, c)
        self.fill(x1 - t, y0, x1, y1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(-(t // 2), t // 2 + 1):
                for b in range(-(t // 2), t // 2 + 1):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def ring(self, cx, cy, r, c, t=3):
        for y in range(cy - r - t, cy + r + t + 1):
            for x in range(cx - r - t, cx + r + t + 1):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if (r - t) ** 2 <= d <= (r + t) ** 2:
                    self.set(x, y, c)

    def poly(self, pts, c):
        # scanline fill, integer coords
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale, y + (row + 1) * scale, c)
            cx += 6 * scale

    def text_c(self, cx, y, s, scale, c):
        self.text(cx - text_w(s, scale) // 2, y, s, scale, c)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- scenes
def draw_lead(cv, x0, y0, x1, y1):
    # night sky gradient
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0))
        cv.fill(x0, y, x1, y + 1, lerp(NAVY, NAVY2, t))
    # stars: fixed LCG
    seed = 1234567
    for _ in range(70):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sx = x0 + 20 + seed % (x1 - x0 - 40)
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sy = y0 + 8 + seed % 150
        cv.set(sx, sy, WHITE)
        cv.set(sx + 1, sy, WHITE)
    # moon (below the headline band, in the sky)
    cv.circle(x1 - 90, y0 + 150, 26, (240, 236, 210))
    cv.circle(x1 - 98, y0 + 143, 22, NAVY2)
    # water
    wy = y1 - 118
    cv.fill(x0, wy, x1, y1, SEA)
    for k in range(6):
        yy = wy + 14 + k * 17
        cv.fill(x0 + 30 + (k % 2) * 90, yy, x1 - 40 - (k % 3) * 60, yy + 3, SEA2)
    # --- bridge: deck left, deck right, collapsed middle span ---
    deck_y = y0 + 250
    # towers
    cv.fill(x0 + 150, deck_y - 150, x0 + 168, deck_y + 6, (200, 200, 205))
    cv.fill(x0 + 780, deck_y - 150, x0 + 798, deck_y + 6, (200, 200, 205))
    cv.fill(x0 + 150, deck_y - 150, x0 + 168, deck_y - 138, (160, 160, 166))
    # intact deck left + right
    cv.fill(x0, deck_y, x0 + 430, deck_y + 16, (226, 228, 232))
    cv.fill(x0 + 610, deck_y, x1, deck_y + 16, (226, 228, 232))
    cv.fill(x0, deck_y + 16, x0 + 430, deck_y + 22, (120, 124, 132))
    cv.fill(x0 + 610, deck_y + 16, x1, deck_y + 22, (120, 124, 132))
    # road dashes
    for dx in range(x0 + 24, x0 + 420, 44):
        cv.fill(dx, deck_y + 6, dx + 22, deck_y + 10, YELLOW)
    for dx in range(x0 + 640, x1 - 30, 44):
        cv.fill(dx, deck_y + 6, dx + 22, deck_y + 10, YELLOW)
    # suspension cables from towers to broken ends: snapped cables sag
    # in two segments, midpoint hanging below the straight line
    cv.line(x0 + 159, deck_y - 148, x0 + 300, deck_y - 40, GREY, 2)
    cv.line(x0 + 300, deck_y - 40, x0 + 428, deck_y, GREY, 2)
    cv.line(x0 + 789, deck_y - 148, x0 + 700, deck_y - 40, GREY, 2)
    cv.line(x0 + 700, deck_y - 40, x0 + 612, deck_y, GREY, 2)
    # broken arch: two large jagged stubs hanging at the gap
    cv.poly([(x0 + 430, deck_y), (x0 + 452, deck_y - 84), (x0 + 472, deck_y - 66),
             (x0 + 486, deck_y - 88), (x0 + 500, deck_y - 52), (x0 + 488, deck_y - 20),
             (x0 + 462, deck_y - 28), (x0 + 448, deck_y + 2)], (170, 172, 178))
    cv.poly([(x0 + 610, deck_y), (x0 + 588, deck_y - 82), (x0 + 568, deck_y - 64),
             (x0 + 554, deck_y - 86), (x0 + 540, deck_y - 50), (x0 + 552, deck_y - 18),
             (x0 + 578, deck_y - 26), (x0 + 592, deck_y + 2)], (170, 172, 178))
    # collapsed span plunging into the water: one tilted plank, hinged at the
    # left break, low end ~70 px down at the waterline (~27 deg). Its top
    # edge is a diagonal, so a clear dark gap stays open between the two
    # deck ends at deck level.
    cv.poly([(x0 + 448, deck_y + 4), (x0 + 592, deck_y + 72), (x0 + 580, deck_y + 84),
             (x0 + 436, deck_y + 16)], (150, 152, 158))
    # submerged end of the span, continuing below the waterline
    cv.poly([(x0 + 540, wy + 18), (x0 + 592, wy + 18), (x0 + 576, wy + 64),
             (x0 + 524, wy + 64)], (110, 112, 118))
    # deck markings on the falling span: pale railing edges along the tilt
    cv.line(x0 + 454, deck_y + 12, x0 + 584, deck_y + 77, (226, 228, 232), 2)
    cv.line(x0 + 442, deck_y + 14, x0 + 574, deck_y + 80, (226, 228, 232), 2)
    # centre dashes, short and tilted with the span (no vertical dashes)
    cv.line(x0 + 500, deck_y + 39, x0 + 514, deck_y + 46, YELLOW, 2)
    cv.line(x0 + 532, deck_y + 55, x0 + 546, deck_y + 62, YELLOW, 2)
    cv.line(x0 + 562, deck_y + 70, x0 + 574, deck_y + 76, YELLOW, 2)
    cv.poly([(x0 + 560, wy + 30), (x0 + 596, wy + 44), (x0 + 580, wy + 58),
             (x0 + 552, wy + 46)], (130, 132, 138))
    cv.poly([(x0 + 430, wy + 44), (x0 + 462, wy + 34), (x0 + 472, wy + 52),
             (x0 + 442, wy + 60)], (130, 132, 138))
    # two more deck fragments breaking off the span (with road-marking flecks)
    cv.poly([(x0 + 596, wy + 66), (x0 + 626, wy + 58), (x0 + 634, wy + 74),
             (x0 + 606, wy + 82)], (150, 152, 158))
    cv.fill(x0 + 606, wy + 68, x0 + 620, wy + 72, YELLOW)
    cv.poly([(x0 + 424, wy + 78), (x0 + 450, wy + 70), (x0 + 458, wy + 86),
             (x0 + 432, wy + 92)], (130, 132, 138))
    # plume where the span meets the water: fan of white spray triangles
    # plus scattered droplets, at the water entry point (x0 + 582)
    cv.poly([(x0 + 566, wy + 8), (x0 + 574, wy - 34), (x0 + 582, wy + 8)], WHITE)
    cv.poly([(x0 + 584, wy + 6), (x0 + 596, wy - 26), (x0 + 604, wy + 8)], (210, 228, 238))
    cv.poly([(x0 + 550, wy + 6), (x0 + 556, wy - 20), (x0 + 564, wy + 8)], (210, 228, 238))
    cv.circle(x0 + 570, wy - 40, 3, WHITE)
    cv.circle(x0 + 592, wy - 32, 3, WHITE)
    cv.circle(x0 + 606, wy - 14, 2, WHITE)
    cv.circle(x0 + 552, wy - 26, 2, (210, 228, 238))
    cv.fill(x0 + 560, wy + 2, x0 + 606, wy + 8, WHITE)
    # explosion starbursts at both break points: jagged 12-point stars,
    # orange outer + yellow core
    def _burst(cx, cy, r_out, r_in, n=12):
        import math
        pts = []
        for k in range(2 * n):
            r = r_out if k % 2 == 0 else r_in
            a = math.pi * k / n
            pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
        return pts
    cv.poly(_burst(x0 + 436, deck_y - 6, 40, 20), ORANGE)
    cv.poly(_burst(x0 + 436, deck_y - 6, 24, 12), YELLOW)
    cv.poly(_burst(x0 + 606, deck_y - 6, 36, 18), ORANGE)
    cv.poly(_burst(x0 + 606, deck_y - 6, 21, 10), YELLOW)
    # smoke columns
    for (sx, sy, r) in [(x0 + 430, deck_y - 70, 26), (x0 + 452, deck_y - 108, 32),
                        (x0 + 420, deck_y - 140, 24), (x0 + 610, deck_y - 66, 24),
                        (x0 + 626, deck_y - 100, 28)]:
        cv.circle(sx, sy, r, SMOKE)
        cv.circle(sx - 8, sy - 6, r - 8, (170, 170, 176))
    # flame tongues licking sideways out of the blasts, clear of the smoke
    cv.poly([(x0 + 400, deck_y - 6), (x0 + 378, deck_y - 14), (x0 + 400, deck_y + 6)], ORANGE)
    cv.poly([(x0 + 472, deck_y - 6), (x0 + 494, deck_y - 14), (x0 + 472, deck_y + 6)], ORANGE)
    cv.poly([(x0 + 570, deck_y - 6), (x0 + 548, deck_y - 14), (x0 + 570, deck_y + 6)], ORANGE)
    cv.poly([(x0 + 642, deck_y - 6), (x0 + 664, deck_y - 14), (x0 + 642, deck_y + 6)], ORANGE)
    # headline band over the sky
    cv.fill(x0, y0 + 14, x1, y0 + 96, DARKRED)
    cv.text_c((x0 + x1) // 2, y0 + 18, "KERCH BRIDGE DOWN", 6, WHITE)
    cv.text_c((x0 + x1) // 2, y0 + 66, "ROAD SPAN COLLAPSED - RAIL DAMAGED", 2, YELLOW)
    # inset box: Kyiv bridges
    bx0, by0, bx1, by1 = x0 + 24, y1 - 108, x0 + 372, y1 - 22
    cv.fill(bx0, by0, bx1, by1, (10, 10, 14))
    cv.rect(bx0, by0, bx1, by1, YELLOW, 2)
    cv.text(bx0 + 14, by0 + 12, "KYIV: NORTH & SOUTH", 2, WHITE)
    cv.text(bx0 + 14, by0 + 34, "BRIDGES HIT SAME NIGHT", 2, WHITE)
    cv.text(bx0 + 14, by0 + 56, "7 BALLISTIC MISSILES", 2, YELLOW)


def draw_quad(cv, x0, y0, x1, y1):
    cv.fill(x0, y0, x1, y1, (235, 240, 248))
    cv.text_c((x0 + x1) // 2, y0 + 12, "QUAD IN MANILA", 4, NAVY)
    cv.text_c((x0 + x1) // 2, y0 + 46, "FIRST SUMMIT IN 2 YEARS", 2, RED)
    # four leaders behind a table
    skins = [(232, 190, 150), (190, 140, 100), (240, 205, 170), (225, 180, 140)]
    suits = [(30, 40, 70), (20, 60, 40), (70, 30, 50), (40, 50, 90)]
    hairs = [(40, 40, 44), (20, 20, 22), (70, 70, 74), (50, 42, 34)]
    names = ["TRUMP", "MODI", "TAKAICHI", "ALBANESE"]
    cy = y0 + 112
    for i in range(4):
        cx = x0 + 62 + i * 122
        cv.circle(cx, cy - 4, 24, hairs[i])          # hair cap
        cv.circle(cx, cy + 5, 21, skins[i])          # face
        # distinguishing hair per leader
        if i == 0:  # Trump: blond fringe swept to the side
            cv.poly([(cx - 22, cy - 6), (cx - 2, cy - 20), (cx + 22, cy - 10),
                     (cx + 18, cy - 2), (cx - 10, cy - 8)], (232, 200, 100))
        elif i == 1:  # Modi: white beard + white temples
            cv.poly([(cx - 15, cy + 6), (cx + 15, cy + 6), (cx + 12, cy + 24),
                     (cx - 12, cy + 24)], (245, 245, 245))
            cv.circle(cx - 19, cy - 4, 5, (245, 245, 245))
            cv.circle(cx + 19, cy - 4, 5, (245, 245, 245))
        elif i == 2:  # Takaichi: dark bob down both sides of the face
            cv.poly([(cx - 25, cy - 12), (cx - 14, cy - 12), (cx - 16, cy + 16),
                     (cx - 25, cy + 14)], (35, 35, 38))
            cv.poly([(cx + 25, cy - 12), (cx + 14, cy - 12), (cx + 16, cy + 16),
                     (cx + 25, cy + 14)], (35, 35, 38))
        else:  # Albanese: grey swept hair
            cv.poly([(cx - 21, cy - 8), (cx, cy - 19), (cx + 21, cy - 8),
                     (cx + 17, cy - 14), (cx - 17, cy - 14)], (168, 168, 173))
        cv.poly([(cx - 30, y1 - 78), (cx + 30, y1 - 78), (cx + 22, cy + 22),
                 (cx - 22, cy + 22)], suits[i])      # shoulders
    # table
    cv.fill(x0 + 16, y1 - 78, x1 - 16, y1 - 52, (120, 72, 40))
    cv.fill(x0 + 16, y1 - 52, x1 - 16, y1 - 48, (90, 52, 28))
    for i in range(4):
        cx = x0 + 62 + i * 122
        cv.text_c(cx, y1 - 42, names[i], 2, INK)
    # arrow to Shenzhen
    cv.text_c((x0 + x1) // 2, y1 - 22, "-> SHENZHEN THU: XI - TRUMP - PUTIN", 2, DARKRED)


def draw_gulf(cv, x0, y0, x1, y1):
    cv.fill(x0, y0, x1, y1, SKY)
    cv.text_c((x0 + x1) // 2, y0 + 12, "HORMUZ: TANKER HIT", 4, NAVY)
    cv.text_c((x0 + x1) // 2, y0 + 46, "7 NM OFF OMAN - CREW SAFE", 2, RED)
    wy = y1 - 78
    cv.fill(x0, wy, x1, y1, SEA)
    # tanker hull + superstructure + fire
    cv.poly([(x0 + 60, wy - 6), (x0 + 300, wy - 6), (x0 + 280, wy + 34),
             (x0 + 80, wy + 34)], (120, 30, 30))
    cv.fill(x0 + 250, wy - 46, x0 + 292, wy - 6, WHITE)
    cv.fill(x0 + 96, wy - 30, x0 + 130, wy - 6, (200, 200, 205))
    cv.circle(x0 + 150, wy - 34, 20, ORANGE)
    cv.circle(x0 + 150, wy - 34, 11, YELLOW)
    cv.circle(x0 + 150, wy - 56, 16, SMOKE)
    cv.circle(x0 + 138, wy - 76, 18, SMOKE)
    # three carriers (flat-top silhouettes)
    for i, cx in enumerate([x0 + 340, x0 + 392, x0 + 444]):
        cv.fill(cx - 26, wy + 8, cx + 26, wy + 22, (60, 66, 74))
        cv.fill(cx + 8, wy - 2, cx + 18, wy + 8, (60, 66, 74))
    cv.text_c((x0 + x1) // 2, y1 - 40, "3 US CARRIERS IN THE GULF", 2, WHITE)
    cv.text_c((x0 + x1) // 2, y1 - 20, "BAHRAIN: DRONES INTERCEPTED", 2, YELLOW)


def draw_japan(cv, x0, y0, x1, y1):
    cv.fill(x0, y0, x1, y1, SKY)
    cv.text_c((x0 + x1) // 2, y0 + 10, "JAPAN SCRAMBLE", 3, NAVY)
    # big aircraft (right) + fighter (left) intercepting, kept clear of the text
    cv.poly([(x0 + 190, y0 + 64), (x0 + 300, y0 + 52), (x0 + 300, y0 + 76),
             (x0 + 190, y0 + 82)], (90, 96, 104))
    cv.poly([(x0 + 300, y0 + 52), (x0 + 322, y0 + 62), (x0 + 300, y0 + 70)], (90, 96, 104))
    cv.poly([(x0 + 240, y0 + 52), (x0 + 252, y0 + 38), (x0 + 262, y0 + 52)], (90, 96, 104))
    cv.poly([(x0 + 40, y0 + 92), (x0 + 130, y0 + 80), (x0 + 130, y0 + 100),
             (x0 + 40, y0 + 106)], RED)
    cv.poly([(x0 + 130, y0 + 80), (x0 + 152, y0 + 88), (x0 + 130, y0 + 96)], RED)
    cv.poly([(x0 + 84, y0 + 80), (x0 + 96, y0 + 66), (x0 + 106, y0 + 80)], RED)
    cv.text_c((x0 + x1) // 2, y1 - 36, "2 RUSSIAN JETS - 04:07 JST", 2, INK)
    cv.text_c((x0 + x1) // 2, y1 - 18, "FIRST SINCE SEPT 2024", 2, DARKRED)


def draw_cyclone(cv, x0, y0, x1, y1):
    cv.fill(x0, y0, x1, y1, (210, 228, 240))
    cv.text_c((x0 + x1) // 2, y0 + 10, "CYCLONE AKVAN", 3, NAVY)
    cx, cy = (x0 + x1) // 2, y0 + 68
    for r, col in [(36, WHITE), (28, (140, 180, 210)), (20, WHITE),
                   (12, (90, 140, 190)), (5, NAVY)]:
        cv.circle(cx, cy, r, col)
    # spiral arms: curved 3-segment arms winding out from the eye
    for a in range(0, 360, 45):
        import math
        pts = []
        for k in range(4):
            ang = math.radians(a + k * 18)
            r = 7 + k * 8
            pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
        for j in range(len(pts) - 1):
            cv.line(pts[j][0], pts[j][1], pts[j + 1][0], pts[j + 1][1], WHITE, 4)
    # Bay of Bengal coastline down the right edge, below-right of the swirl
    # (the bottom band is taken by the two caption lines, so the coast
    # runs vertically at the panel's right edge instead)
    cv.line(x1 - 24, y0 + 52, x1 - 38, y0 + 78, TEAL, 3)
    cv.line(x1 - 38, y0 + 78, x1 - 22, y0 + 102, TEAL, 3)
    cv.text_c((x0 + x1) // 2, y1 - 36, "TO 130 KM/H - FRI 20 NOV", 2, INK)
    cv.text_c((x0 + x1) // 2, y1 - 18, "610 KM EAST OF CHENNAI", 2, DARKRED)


def draw_sanctions(cv, x0, y0, x1, y1):
    cv.fill(x0, y0, x1, y1, (244, 236, 224))
    cv.text_c((x0 + x1) // 2, y0 + 10, "UK SANCTIONS", 3, NAVY)
    cx, cy = (x0 + x1) // 2, y0 + 74
    # stamp moved to the panel's right edge and shrunk, so it no longer
    # crosses the headline; headline stays centred in the clear space.
    sx, sy = x1 - 46, y0 + 72
    cv.ring(sx, sy, 22, RED, 3)
    cv.line(sx - 19, sy - 17, sx + 19, sy + 17, RED, 3)
    cv.text_c(cx, cy - 12, "8 FIRMS", 2, RED)
    cv.text_c(cx, cy + 6, "FROZEN", 2, RED)
    cv.text_c((x0 + x1) // 2, y1 - 36, "SETTLEMENT BUILDERS", 2, INK)
    cv.text_c((x0 + x1) // 2, y1 - 18, "+ TZAV 9 AID-BLOCKERS", 2, DARKRED)


# ---------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.fill(0, 0, W, 96, NAVY)
    cv.fill(0, 92, W, 96, YELLOW)
    cv.text_c(W // 2, 8, "THE WORLD TODAY", 6, WHITE)
    cv.text_c(W // 2, 60, "TUESDAY 17 NOVEMBER 2026", 3, YELLOW)

    # lead panel
    draw_lead(cv, 16, 108, W - 16, 540)
    cv.rect(16, 108, W - 16, 540, INK, 3)

    # middle band: Quad | Gulf
    draw_quad(cv, 16, 552, 504, 780)
    cv.rect(16, 552, 504, 780, INK, 3)
    draw_gulf(cv, 520, 552, W - 16, 780)
    cv.rect(520, 552, W - 16, 780, INK, 3)

    # tertiary strip: Japan | Cyclone | Sanctions
    draw_japan(cv, 16, 792, 336, 928)
    cv.rect(16, 792, 336, 928, INK, 3)
    draw_cyclone(cv, 344, 792, 680, 928)
    cv.rect(344, 792, 680, 928, INK, 3)
    draw_sanctions(cv, 688, 792, W - 16, 928)
    cv.rect(688, 792, W - 16, 928, INK, 3)

    # bottom ticker
    cv.fill(0, 940, W, H, INK)
    cv.text_c(W // 2, 952, "MONGOLIA PRESIDENT RESIGNS - $25M CLAIM DENIED", 2, YELLOW)
    cv.text_c(W // 2, 984, "DHONI RETIRES FROM IPL - 5 TITLES, 278 MATCHES - CSK MENTOR 2027", 2, WHITE)
    return cv


# ---------------------------------------------------------------- PNG out
def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out, exist_ok=True)
    write_png(os.path.join(out, "entry.png"), build())


if __name__ == "__main__":
    main()
