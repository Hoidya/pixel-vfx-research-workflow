# -*- coding: utf-8 -*-
"""V4 flame stomp only.

Standalone renderer for this one move.
Writes the preview GIF and
out/keyframes/. Does not overwrite earlier preview folders.
Telegraph pixels stay hitbox-accurate; brightest solid cores stay inside
the hitbox. Fire tongues may overflow. Heavy-tier wash, no full-screen
black/white invert.
"""

# Reference renderer for one preview GIF in this folder.
# Not a drop-in for an arbitrary project. Set the environment variables
# below (or edit the Path defaults) so they point at your assets and
# telegraph helper. Do not copy third-party VFX art into the output.
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_TELEGRAPH_LIB = Path(os.environ.get("TELEGRAPH_LIB", "tools"))
sys.path.insert(0, str(_TELEGRAPH_LIB))
import telegraph_lib as T
from telegraph_lib import Telegraph, CrackOverlay, frames_of, BAYER, hx

ROOT = Path(os.environ.get("VFX_PREVIEW_ROOT", "."))
OUT = ROOT / "out"
KEYDIR = OUT / "keyframes"
FRDIR = OUT / "_frames"
NA_CONTENT = Path(os.environ.get("NINJA_ADVENTURE_CONTENT", "assets/ninja-adventure"))
NA_ACTOR = Path(os.environ.get("NINJA_ADVENTURE_ACTOR", "assets/ninja-adventure"))
FONT_PATH = Path(os.environ.get("VFX_FONT", "fonts/fusion-pixel-12px-proportional-zh_hans.otf"))

FPS = 30
TILE = 16
SCALE = 3
W, H = 192, 160
IDLE_F = 8
TAIL_F = 8
LABEL_H = 32

# heavy tier (same feel as v3 stomp; no invert)
HITSTOP = 6
SHAKE = 3
SHAKE_N = 10
DISS = 15
BURST = 2
WIND = 14
SPARK_R = 20
OVERFLOW = 36
KB = 40

ROLE = {
    "damage": dict(
        edge_dark=hx("2b0a08"), main=hx("c0392b"), hi=hx("e8705f"),
        flash=hx("f6d2c4"), white=hx("ffffff"),
    ),
}
T.ROLE_COLORS.update(ROLE)

CAT_ZH = {"damage": "伤害", "control": "控制", "mixed": "混合", "support": "辅助"}
PHASE_COL = {
    "待机": (150, 150, 150), "蓄力": (201, 183, 156), "预警": (232, 112, 95),
    "生效": (255, 255, 255), "冲击": (255, 255, 255), "消散": (200, 180, 140),
    "收招": (241, 196, 15),
}

WHITE = hx("ffffff")
FIRE_PAL = [hx("2a0808"), hx("8a1008"), hx("e04010"), hx("f8a020"), hx("fff0a0"), WHITE]
ROCK_PAL = [hx("1a1008"), hx("3a2818"), hx("6a4a30"), hx("a08060"), hx("d8c090")]
SMOKE_PAL = [hx("141210"), hx("2a2824"), hx("4a4640"), hx("6e6860"), hx("8a8478")]
SCORCH_DARK = hx("1a0a08")
SCORCH_MID = hx("2e140c")
SCORCH_EMBER = hx("5a2010")
CRACK_LIT = hx("e07030")

# 8 uneven tongues (plus 2 short forks) — not 16-equal petals.
# ang, length_mul, root half-width (px), die_at (diss 0–1), fork (dang, len_mul) or None
TONGUES = [
    (0.18, 1.00, 5.6, 0.88, (0.34, 0.66)),
    (0.92, 0.74, 4.6, 0.38, None),
    (1.58, 0.94, 5.2, 0.72, None),
    (2.28, 0.60, 4.2, 0.28, None),
    (2.98, 1.06, 5.8, 0.92, (-0.28, 0.62)),
    (3.72, 0.68, 4.4, 0.44, None),
    (4.58, 0.90, 5.0, 0.78, None),
    (5.42, 0.52, 4.0, 0.22, None),
]

ninja_sheet = Image.open(NA_CONTENT / "character/ninja_blue/sprite.png").convert("RGBA")
shadow_img = Image.open(NA_CONTENT / "character/Shadow.png").convert("RGBA")
floor = Image.open(NA_CONTENT / "map/tileset_floor.png").convert("RGBA")
GRASS = [floor.crop((x, 192, x + 16, 208)) for x in (176, 192, 208, 224, 240)]
FONT = ImageFont.truetype(str(FONT_PATH), 12)
DATA = json.loads((ROOT / "examples.json").read_text(encoding="utf-8"))
SKILLS = {s["id"]: s for s in DATA["skills"]}
_sheet = {}


def load_sheet(rel):
    rel = rel.replace("\\", "/")
    if rel not in _sheet:
        _sheet[rel] = Image.open(NA_ACTOR / rel).convert("RGBA")
    return _sheet[rel]


def crop_cell(sheet, fw, fh, col, row):
    cols, rows = max(1, sheet.size[0] // fw), max(1, sheet.size[1] // fh)
    return sheet.crop(((int(col) % cols) * fw, (int(row) % rows) * fh,
                       (int(col) % cols) * fw + fw, (int(row) % rows) * fh + fh))


def ninja_frame(col, row):
    return ninja_sheet.crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))


def make_bg(w=W, h=H, seed=7):
    rnd = random.Random(seed)
    bg = Image.new("RGBA", (w, h))
    for ty in range(0, h, 16):
        for tx in range(0, w, 16):
            t = GRASS[0] if rnd.random() < 0.55 else rnd.choice(GRASS[1:])
            bg.paste(t, (tx, ty))
    px = bg.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            m = (r + g + b) / 3
            px[x, y] = (
                int((r * 0.6 + m * 0.4) * 0.55),
                int((g * 0.6 + m * 0.4) * 0.55),
                int((b * 0.6 + m * 0.4) * 0.55),
                255,
            )
    return bg


BG = make_bg()


class Canvas:
    def __init__(self):
        self.im = BG.copy()

    def put(self, x, y, c, fx=True):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H and (len(c) < 4 or c[3] >= 255):
            self.im.putpixel((x, y), tuple(c[:3]) + (255,))

    def blit(self, spr, x, y):
        x, y = int(round(x)), int(round(y))
        tmp = Image.new("RGBA", (W, H))
        tmp.paste(spr, (x, y), spr)
        self.im.alpha_composite(tmp)


def silhouette(spr, c):
    out = Image.new("RGBA", spr.size)
    p, q = spr.load(), out.load()
    col = c if len(c) == 4 else (c[0], c[1], c[2], 255)
    for y in range(spr.height):
        for x in range(spr.width):
            if p[x, y][3] > 0:
                q[x, y] = col
    return out


def outline_sprite(spr, col=WHITE, thick=1):
    out = Image.new("RGBA", (spr.width + 2 * thick, spr.height + 2 * thick))
    sil = silhouette(spr, col if len(col) == 4 else (col[0], col[1], col[2], 255))
    for dy in range(-thick, thick + 1):
        for dx in range(-thick, thick + 1):
            if abs(dx) + abs(dy) == 0:
                continue
            if thick == 1 and abs(dx) + abs(dy) > 1 and abs(dx) == abs(dy):
                continue
            out.alpha_composite(sil, (thick + dx, thick + dy))
    out.alpha_composite(spr, (thick, thick))
    return out


def scale_nn(spr, nw, nh):
    nw, nh = max(1, int(round(nw))), max(1, int(round(nh)))
    return spr if (nw, nh) == spr.size else spr.resize((nw, nh), Image.NEAREST)


def _line(cv, x0, y0, x1, y1, col):
    x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        cv.put(x0, y0, col)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _ang_diff(a, b):
    return (a - b + math.pi) % math.tau - math.pi


# ---------------------------------------------------------------------------
# Particles: rocks (gravity) and smoke puffs (rise, per-puff life)
# ---------------------------------------------------------------------------
class Rock:
    def __init__(self, x, y, vx, vy, vz, size, pal, life, g=0.38, bounce=0.22):
        self.x, self.y, self.z = float(x), float(y), 0.4
        self.vx, self.vy, self.vz = vx, vy, vz
        self.size = max(2, int(size))
        self.pal, self.life, self.age = pal, int(life), 0
        self.g, self.bounce = g, bounce
        self.broke = False

    def step(self):
        self.age += 1
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vz -= self.g
        if self.z <= 0:
            self.z = 0
            if self.vz < -0.6 and not self.broke:
                self.vz = -self.vz * self.bounce
                self.vx *= 0.45
                self.vy *= 0.45
                self.size = max(1, self.size - 1)
                self.broke = True
            else:
                self.vz = 0
                self.vx *= 0.62
                self.vy *= 0.62

    def alive(self):
        return self.age < self.life

    def draw(self, cv):
        remain = self.life - self.age
        if remain <= 3 and self.age % 2:
            return
        sx, sy = int(round(self.x)), int(round(self.y - self.z))
        s = self.size if remain > 5 else max(1, self.size - 1)
        dark, mid = self.pal[0], self.pal[min(2, len(self.pal) - 1)]
        hi = self.pal[min(3, len(self.pal) - 1)]
        if s == 1:
            cv.put(sx, sy, mid)
            return
        for dy in range(s):
            for dx in range(s):
                cv.put(sx + dx, sy + dy, mid if (dx + dy) % 2 == 0 else dark)
        cv.put(sx, sy, hi if self.age <= 4 else mid)
        if s >= 3:
            cv.put(sx + s - 1, sy + s - 1, dark)
            cv.put(sx - 1, sy + 1, dark)


class SmokePuff:
    def __init__(self, x, y, vx, vy, size, life, seed):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.size, self.life, self.age = int(size), int(life), 0
        self.seed = seed

    def step(self):
        self.age += 1
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.04  # rise (y is down, so negative)
        self.vx *= 0.92

    def alive(self):
        return self.age < self.life

    def draw(self, cv):
        t = self.age / max(self.life, 1)
        # cool: light gray → mid → dark; dither holes grow
        if t < 0.25:
            col = SMOKE_PAL[3]
        elif t < 0.5:
            col = SMOKE_PAL[2]
        elif t < 0.75:
            col = SMOKE_PAL[1]
        else:
            col = SMOKE_PAL[0]
        s = max(2, int(self.size * (1.05 + 0.35 * t)))
        sx, sy = int(round(self.x)), int(round(self.y))
        # two offset clumps for volume
        for ox, oy, rr in ((0, 0, s), (s // 3, -s // 4, max(2, s - 2))):
            for dy in range(-rr, rr + 1):
                for dx in range(-rr, rr + 1):
                    if dx * dx + dy * dy > rr * rr:
                        continue
                    # missing chunks grow with age — per-puff, not a global hash
                    h = ((sx + dx + self.seed * 3) * 17 + (sy + dy) * 11 + self.seed) & 255
                    if h < t * 200:
                        continue
                    if BAYER[(sy + dy) % 4][(sx + dx) % 4] < t * 10:
                        continue
                    cv.put(sx + dx + ox, sy + dy + oy, col)


def ease_fill(t):
    t = max(0.0, min(1.0, t))
    if t < 0.8:
        return (t / 0.8) ** 2 * 0.72
    u = (t - 0.8) / 0.2
    return 0.72 + u * u * 0.28


def draw_warning(cv, tel, t_ratio, frame, cracks=None):
    col = tel.col
    prog = ease_fill(t_ratio)
    skip = tel.border | tel.inner_border
    fw = tel.front_w
    for (x, y) in tel.cells:
        if (x, y) in skip:
            continue
        b = BAYER[y % 4][x % 4]
        m = tel.metric.get((x, y), 2)
        if m <= prog and m > prog - fw and prog < 1:
            if b < 11:
                cv.put(x, y, col["hi"])
        elif m <= prog:
            if b < 4:
                cv.put(x, y, col["main"])
        else:
            if b < 1:
                cv.put(x, y, col["main"])
    if cracks is not None:
        cracks.draw(cv, tel, prog, frame)
    flash = t_ratio >= 0.88 and not (t_ratio >= 0.96 and frame % 2)
    for (x, y) in tel.border:
        cv.put(x, y, WHITE if flash else col["edge_dark"])
    for (x, y) in tel.inner_border:
        cv.put(x, y, WHITE if flash else (col["hi"] if t_ratio >= 0.7 else col["main"]))


def draw_scorch(cv, cx, cy, cells, strength=1.0):
    """Irregular burn islands inside the hitbox, not a diagonal hatch or a disk."""
    if strength <= 0:
        return
    for (x, y) in cells:
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        rad = math.hypot(dx, dy)
        ix, iy = x // 7, y // 7
        island = (ix * 47 + iy * 31) & 255
        # only some 7px islands burn
        if island > int(90 + 70 * strength):
            continue
        cx_i, cy_i = ix * 7 + 3, iy * 7 + 3
        if math.hypot(x - cx_i, y - cy_i) > 2.4 + (island % 4) * 0.7:
            continue
        # denser / darker near the stomp
        if rad < 24:
            cv.put(x, y, SCORCH_DARK if island < 80 else SCORCH_MID)
        elif rad < 52:
            cv.put(x, y, SCORCH_MID if island > 40 else SCORCH_DARK)
        elif rad < 80 and island < 70:
            cv.put(x, y, SCORCH_MID)
        if strength > 0.75 and 14 < rad < 40 and island < 28:
            cv.put(x, y, SCORCH_EMBER)


def draw_hit_cracks(cv, cx, cy, cells, cracks, ember=False):
    """Keep warning cracks, now as dark scorch lines (ember edge early)."""
    pts = cracks.build(cracks._pts and cracks or cracks)
    pts = cracks.build.__self__.build(cracks) if False else cracks.build(
        type("T", (), {"cells": cells, "caster": (cx, cy), "p": {"radius": 80, "angle": 360, "shape": "circle"}, "ang": 0.0})()
    ) if False else cracks._pts
    # Use the overlay already built against the real telegraph
    if cracks._pts is None:
        return
    lit = CRACK_LIT if ember else SCORCH_MID
    for (x, y), d in cracks._pts.items():
        if (x, y) not in cells:
            continue
        cv.put(x, y, SCORCH_DARK)
        if (x, y + 1) not in cracks._pts and (x, y + 1) in cells:
            cv.put(x, y + 1, lit)


def draw_hollow_ring(cv, cx, cy, r, col_outer, col_inner, thick=2, gaps=()):
    """1–2px hollow ring, optional angular gaps. Never filled."""
    if r < 4:
        return
    r = int(round(r))
    thick = 1 if thick < 2 else 2
    for a in range(0, 360):
        rad = math.radians(a)
        skip = False
        for g0, gw in gaps:
            if abs(_ang_diff(rad, g0)) < gw:
                skip = True
                break
        if skip:
            continue
        x = int(round(cx + math.cos(rad) * r))
        y = int(round(cy + math.sin(rad) * r))
        cv.put(x, y, col_outer)
        if thick > 1:
            x2 = int(round(cx + math.cos(rad) * (r - 1)))
            y2 = int(round(cy + math.sin(rad) * (r - 1)))
            cv.put(x2, y2, col_inner)


def _tongue_list(diss, phase):
    """Living tongues + forks, each with its own life and retract."""
    out = []
    grow = 0.50 if phase == 0 else 1.0
    for ang, lmul, wid, die, fork in TONGUES:
        life = 0.0 if die <= 0 else max(0.0, min(1.0, diss / die))
        if life >= 1.0:
            continue
        reach = lmul * grow * (1.0 - 0.72 * life)
        # mid-life: punch a short gap along the tongue (缺段), not a spatial hash
        gap = (0.42, 0.12 + 0.10 * life) if life > 0.55 else None
        out.append(dict(ang=ang, reach=reach, wid=wid * (1.0 - 0.25 * life),
                        life=life, gap=gap, is_fork=False))
        if fork and life < 0.7 and phase == 1:
            dang, flen = fork
            # forks die a bit sooner
            flife = min(1.0, life / 0.85 + 0.15)
            if flife < 1.0:
                out.append(dict(
                    ang=ang + dang,
                    reach=lmul * flen * grow * (1.0 - 0.8 * flife),
                    wid=wid * 0.55 * (1.0 - 0.3 * flife),
                    life=flife, gap=None, is_fork=True,
                ))
    return out


def _cool_along(t, life, in_core):
    """Color along a tongue's own axis. White only inside the hitbox."""
    # life pushes the ramp toward darker / colder steps
    # palette: white, pale yellow, orange, red, dark
    steps = [FIRE_PAL[5], FIRE_PAL[4], FIRE_PAL[3], FIRE_PAL[2], FIRE_PAL[1], FIRE_PAL[0]]
    # drop bright steps as this tongue cools
    cut = 0
    if life > 0.15:
        cut += 1
    if life > 0.35:
        cut += 1
    if life > 0.55:
        cut += 1
    if life > 0.75:
        cut += 1
    steps = steps[cut:] or [FIRE_PAL[0]]
    # position along tongue
    if t < 0.22:
        idx = 0
    elif t < 0.42:
        idx = min(1, len(steps) - 1)
    elif t < 0.62:
        idx = min(2, len(steps) - 1)
    elif t < 0.82:
        idx = min(3, len(steps) - 1)
    else:
        idx = len(steps) - 1
    c = steps[min(idx, len(steps) - 1)]
    if (not in_core) and c == WHITE:
        c = steps[min(1, len(steps) - 1)]
        if c == WHITE:
            c = FIRE_PAL[3]
    return c


def draw_fire_tongues(cv, cx, cy, r_max, core_cells, diss, phase):
    """6–10 uneven hard-edged tongues. Color along each axis, not by radius."""
    tongues = _tongue_list(diss, phase)
    if not tongues:
        return tongues
    r_limit = r_max * max(t["reach"] for t in tongues) + 3
    x0, x1 = int(cx - r_limit), int(cx + r_limit)
    y0, y1 = int(cy - r_limit), int(cy + r_limit)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rad = math.hypot(dx, dy)
            if rad > r_limit:
                continue
            ang = math.atan2(dy, dx)
            best = None
            best_d = 1e9
            for tg in tongues:
                reach_px = r_max * tg["reach"]
                if rad > reach_px + 0.7:
                    continue
                t = rad / max(reach_px, 1)
                if tg["gap"] is not None:
                    g0, gw = tg["gap"]
                    if abs(t - g0) < gw:
                        continue
                da = abs(_ang_diff(ang, tg["ang"]))
                # taper to a point; slightly fatter near the root
                half = tg["wid"] * max(0.0, 1.0 - t) ** 0.85 * (1.15 if t < 0.22 else 1.0)
                dist = da * max(rad, 1.0)
                if dist <= half + 0.55 and dist < best_d:
                    best_d = dist
                    best = (tg, t, half, dist)
            if best is None:
                continue
            tg, t, half, dist = best
            in_core = (x, y) in core_cells
            c = _cool_along(t, tg["life"], in_core)
            cv.put(x, y, c)
    return tongues


def draw_hot_core(cv, cx, cy, r, core_cells, diss, phase):
    """Jagged white/yellow splat, only inside the hitbox. Not a smooth disk."""
    if diss > 0.62:
        return
    cool = min(1.0, diss * 1.4)
    grow = 0.78 if phase == 0 else 1.0
    r = r * grow * (1.0 - 0.55 * cool)
    x0, x1 = int(cx - r - 2), int(cx + r + 2)
    y0, y1 = int(cy - r - 2), int(cy + r + 2)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) not in core_cells:
                continue
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rad = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            # irregular edge: a few odd harmonics, not a circle
            jag = 1.0 + 0.28 * math.sin(ang * 5 + 0.4) + 0.16 * math.sin(ang * 3 - 0.8)
            jag += 0.10 * math.sin(ang * 9 + 1.2)
            edge = r * jag
            if rad > edge:
                continue
            t = rad / max(edge, 1)
            if cool < 0.25:
                c = WHITE if t < 0.45 else (FIRE_PAL[4] if t < 0.75 else FIRE_PAL[3])
            elif cool < 0.45:
                c = FIRE_PAL[4] if t < 0.5 else FIRE_PAL[3]
            else:
                c = FIRE_PAL[3] if t < 0.55 else FIRE_PAL[2]
            cv.put(x, y, c)


def draw_star(cv, cx, cy, r, pal, phase, n=6, diss=0.0):
    if phase >= 2 or diss > 0.7:
        for i in range(n):
            a = i * math.tau / n + 0.2
            rr = int(r * (0.7 - 0.3 * diss))
            cv.put(int(cx + math.cos(a) * rr), int(cy + math.sin(a) * rr),
                   pal[-1] if diss < 0.4 else pal[1])
        return
    scale = 0.72 if phase == 0 else 1.0
    r = max(3, r * scale * (1.0 - 0.25 * diss))
    dark, midc = pal[0], pal[min(1, len(pal) - 1)]
    hi, core = pal[min(2, len(pal) - 1)], pal[-1]
    x0, x1 = int(cx - r - 2), int(cx + r + 2)
    y0, y1 = int(cy - r - 2), int(cy + r + 2)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rad = math.hypot(dx, dy)
            if rad > r + 1:
                continue
            ang = math.atan2(dy, dx)
            wave = abs(math.cos(ang * n / 2))
            r_edge = r * (0.32 + 0.68 * wave)
            if rad > r_edge:
                continue
            t = rad / max(r_edge, 1)
            if t < 0.25:
                c = core
            elif t < 0.55:
                c = hi
            elif t < 0.82:
                c = midc
            else:
                c = dark
            cv.put(x, y, c)
    for s in range(int(r * 0.2), int(r) + 1):
        col = core if s < r * 0.4 else hi
        cv.put(int(cx + s), int(cy), col)
        cv.put(int(cx - s), int(cy), col)
        cv.put(int(cx), int(cy + s), col)
        cv.put(int(cx), int(cy - s), col)


def draw_speed_lines(cv, cx, cy, length, n, col):
    rnd = random.Random(21)
    for i in range(n):
        a = i * math.tau / n + 0.11 + (i % 3) * 0.04
        r0 = length * 0.48
        r1 = length * rnd.uniform(0.78, 1.06)
        _line(cv, cx + math.cos(a) * r0, cy + math.sin(a) * r0,
              cx + math.cos(a) * r1, cy + math.sin(a) * r1, col)


def apply_white_wash(im, amount_bayer=5):
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            lum = (r + g + b) // 3
            if lum > 70:
                r = min(255, r + 70)
                g = min(255, g + 60)
                b = min(255, b + 50)
            if BAYER[y % 4][x % 4] < amount_bayer and lum > 40:
                r = min(255, r + 80)
                g = min(255, g + 80)
                b = min(255, b + 80)
            px[x, y] = (r, g, b, 255)


def flash_border(im, col=(255, 255, 255, 255), thick=2):
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            if x < thick or y < thick or x >= w - thick or y >= h - thick:
                px[x, y] = col


# ---------------------------------------------------------------------------
# Actors
# ---------------------------------------------------------------------------
def flam_sprite(pose, tick):
    if pose == "hit":
        return crop_cell(load_sheet("Boss/GiantFlam/Hit.png"), 50, 50, min(2, tick), 0)
    return crop_cell(load_sheet("Boss/GiantFlam/Idle.png"), 50, 50, (tick // 3) % 5, 0)


def draw_shadow_at(cv, fx, fy):
    sw, sh = shadow_img.size
    cv.blit(shadow_img, int(round(fx - sw / 2)), int(round(fy - sh / 2 + 1)))


def draw_actor(cv, spr, cx, cy, flash=False, outline=None, ox=0, oy=0):
    if flash:
        spr = silhouette(spr, WHITE)
    if outline is not None:
        spr = outline_sprite(spr, outline, 1)
        ox -= 1
        oy -= 1
    sw, sh = spr.size
    draw_shadow_at(cv, cx + ox, cy + oy)
    cv.blit(spr, cx - sw / 2 + ox, cy - sh / 2 + oy)


def draw_flam_pose(cv, cx, cy, i, hit_at, wind, hitstop, diss_end):
    ox, oy, flash, outline = 0, 0, False, None
    spr = flam_sprite("idle", i)
    if hit_at - wind <= i < hit_at:
        k = min(1.0, (i - (hit_at - wind)) / max(wind - 4, 1))
        spr = scale_nn(spr, 48 - int(6 * k), 50 + int(16 * k))
        oy = -int(14 * k)
        if i >= hit_at - 6:
            outline = WHITE
    elif hit_at <= i < diss_end:
        e = i - hit_at
        if e <= hitstop:
            spr = scale_nn(flam_sprite("hit", 0), 66, 34)
            oy = 10
            flash = e <= 1
            if e == 0:
                outline = WHITE
        else:
            spr = flam_sprite("hit", min(2, 1 + (e - hitstop) // 3))
            oy = 3
    elif i >= diss_end:
        e = i - diss_end
        if e <= 2:
            spr = flam_sprite("hit", 2)
            oy = 1
        elif e == 3:
            spr = flam_sprite("idle", i)
            oy = -2
        else:
            spr = flam_sprite("idle", i)
    draw_actor(cv, spr, cx, cy, flash=flash, outline=outline, ox=ox, oy=oy)


def draw_ninja(cv, fx, fy, col=2, row=0, flash=False, squash=None):
    spr = ninja_frame(col, row)
    if squash:
        spr = scale_nn(spr, squash[0], squash[1])
    if flash:
        spr = silhouette(spr, WHITE)
    cv.blit(shadow_img, int(round(fx - 6)), int(round(fy - 2)))
    cv.blit(spr, fx - spr.width / 2, fy - spr.height / 2 - 1)


def draw_windup_dust(cv, cx, cy, k, rnd):
    """A few motes at the feet during late wind-up. Restrained."""
    n = 5
    for i in range(n):
        a = 0.4 + i * 0.9 + 0.2 * k
        rr = 10 + (i * 3) % 8
        x = int(round(cx + math.cos(a) * rr * (0.6 + 0.4 * k)))
        y = int(round(cy + 8 - k * 4 + math.sin(a) * 3))
        col = ROCK_PAL[2] if i % 2 == 0 else ROCK_PAL[3]
        if BAYER[y % 4][x % 4] < 8 + int(k * 6):
            cv.put(x, y, col)


# ---------------------------------------------------------------------------
# Compose / gif
# ---------------------------------------------------------------------------
class Frame:
    def __init__(self, cv, phase, shake=(0, 0), post=None):
        self.cv, self.phase, self.shake, self.post = cv, phase, shake, post


def header_strip(skill, phase, t):
    w, h = W, LABEL_H
    im = Image.new("RGB", (w, h), (18, 16, 14))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    title = f"{skill['_nn']:02d}  {skill['skill_name']} / {skill['skill_name_en']}"
    d.text((4, 2), title, font=FONT, fill=(201, 183, 156))
    ph_w = int(d.textlength(phase, font=FONT))
    d.text((w - 4 - ph_w, 2), phase, font=FONT, fill=PHASE_COL.get(phase, (255, 255, 255)))
    cat = CAT_ZH[skill["category"]]
    d.text((4, 16), f"{cat}  ·  预警 {skill['warning_duration']:.1f}s", font=FONT, fill=(140, 140, 140))
    ts = f"t={t:.2f}s"
    tw = int(d.textlength(ts, font=FONT))
    d.text((w - 4 - tw, 16), ts, font=FONT, fill=(200, 200, 200))
    return im.resize((w * SCALE, h * SCALE), Image.NEAREST)


def compose(skill, fr, i):
    im = fr.cv.im.copy()
    if fr.post == "wash":
        apply_white_wash(im, 4)
        flash_border(im, WHITE, 2)
    elif fr.post == "flash_edge":
        flash_border(im, WHITE, 2)
    if fr.shake != (0, 0):
        sh = BG.copy()
        sh.paste(im, fr.shake)
        im = sh
    big = im.convert("RGB").resize((W * SCALE, H * SCALE), Image.NEAREST)
    lab = header_strip(skill, fr.phase, i / FPS)
    out = Image.new("RGB", (W * SCALE, lab.height + H * SCALE))
    out.paste(lab, (0, 0))
    out.paste(big, (0, lab.height))
    return out


def write_gif(frames_dir, out_path, fps=FPS):
    pal = str(out_path) + ".pal.png"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-framerate", str(fps),
         "-i", f"{frames_dir}/%04d.png",
         "-vf", "palettegen=max_colors=256:stats_mode=full:reserve_transparent=0", pal],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-framerate", str(fps),
         "-i", f"{frames_dir}/%04d.png", "-i", pal,
         "-lavfi", "paletteuse=dither=none", "-loop", "0", str(out_path)],
        check=True,
    )
    os.remove(pal)


def tel_params(skill):
    sp = skill["size_params"]
    p = dict(shape=skill["shape"], style="standard", duration=skill["warning_duration"],
             anchor="caster", color_role="damage", track_time=0, direction=0.0)
    if "radius" in sp:
        p["radius"] = int(sp["radius"] * TILE)
    if "angle" in sp:
        p["angle"] = sp["angle"]
    return p


def ring_state(vis_age, diss, r_hit):
    """Hollow ring: appears on impact, max at peak, walks out 2–4 frames, then gone."""
    if vis_age < 0:
        return None
    if vis_age == 0:
        return dict(r=r_hit * 0.78, thick=2, gaps=((2.1, 0.18),),
                    outer=WHITE, inner=FIRE_PAL[4])
    if diss <= 0:
        return dict(r=r_hit + 8, thick=2,
                    gaps=((0.55, 0.14), (3.2, 0.12)),
                    outer=WHITE, inner=FIRE_PAL[4])
    # first ~4 dissipate frames (ease-out diss is front-loaded)
    if diss < 0.42:
        extra = 22 * (diss / 0.42)
        # more / wider gaps
        return dict(r=r_hit + 10 + extra, thick=1,
                    gaps=((0.4, 0.32), (2.35, 0.30), (4.4, 0.28), (5.6, 0.18)),
                    outer=FIRE_PAL[3] if diss < 0.25 else FIRE_PAL[2],
                    inner=FIRE_PAL[2] if diss < 0.25 else FIRE_PAL[1])
    return None


def render_stomp():
    sid = "s23_flame_stomp"
    nn, slug = 23, "flame_stomp"
    skill = dict(SKILLS[sid])
    skill["_nn"] = nn
    cx0, cy0 = 88, 80
    nx0, ny0 = 140, 84
    p = tel_params(skill)
    tel = Telegraph(p, (cx0, cy0), (nx0, ny0))
    tel.col = ROLE["damage"]
    assert tel.contains((nx0, ny0)), "player not in hitbox"

    warn_s = float(skill["warning_duration"])
    rec_s = float(skill["recovery_duration"])
    WARN = frames_of(warn_s)
    REC = frames_of(rec_s)
    hit_at = IDLE_F + WARN
    diss_start = hit_at + 1 + HITSTOP
    diss_end = diss_start + DISS
    rec_end = diss_end + max(REC - 4, 4)
    total = rec_end + TAIL_F
    r_hit = tel.p.get("radius", 80)
    r_max = r_hit + OVERFLOW

    cracks = CrackOverlay(seed=23, n_main=5, dark=hx("1a0808"), lit=CRACK_LIT)
    cracks.build(tel)

    rnd = random.Random(223)
    rocks = []
    smokes = []
    spawned_rocks = False
    tongues_seen_dead = set()
    frames = []
    nx, ny = float(nx0), float(ny0)
    ninja_flash = 0

    work = FRDIR
    if work.exists():
        for f in work.glob("*.png"):
            f.unlink()
    else:
        work.mkdir(parents=True, exist_ok=True)

    for i in range(total):
        cv = Canvas()
        shake = (0, 0)
        post = None
        if i < IDLE_F:
            phase, t_warn = "待机", -1
        elif i < hit_at:
            phase = "预警" if i < hit_at - WIND else "蓄力"
            t_warn = (i - IDLE_F) / max(WARN, 1)
        elif i < diss_start:
            e = i - hit_at
            phase = "冲击" if e <= 1 else "生效"
            t_warn = 1.0
        elif i < diss_end:
            phase, t_warn = "消散", 1.0
        elif i < rec_end:
            phase, t_warn = "收招", 1.0
        else:
            phase, t_warn = "待机", -1

        freeze = hit_at + 1 <= i < diss_start
        age_hit = i - hit_at
        if freeze:
            vis_age, diss, phase_shape = 1, 0.0, 1
        elif i >= hit_at and i < diss_end:
            vis_age = age_hit
            if i >= diss_start:
                raw = (i - diss_start) / max(DISS - 1, 1)
                diss = 1 - (1 - raw) * (1 - raw)
            else:
                diss = 0.0
            phase_shape = 0 if vis_age == 0 else 1
        else:
            vis_age, diss, phase_shape = -1, 1.0, 1

        # ground: warning, then scorch + cracks persist through recovery
        if IDLE_F <= i < hit_at:
            draw_warning(cv, tel, t_warn, i, cracks=cracks)
            if phase == "蓄力":
                k = min(1.0, (i - (hit_at - WIND)) / max(WIND - 1, 1))
                if k > 0.45:
                    draw_windup_dust(cv, cx0, cy0, k, rnd)
        elif i >= hit_at and i < rec_end + 3:
            # scorch stays after fire dies; slightly cooler late
            late = 0.0 if i < diss_end else min(0.25, (i - diss_end) / 10)
            draw_scorch(cv, cx0, cy0, tel.cells, strength=max(0.55, 1.0 - late * 0.6))
            ember = i < diss_start + 6
            if cracks._pts:
                lit = CRACK_LIT if ember else SCORCH_MID
                for (x, y), d in cracks._pts.items():
                    if (x, y) not in tel.cells:
                        continue
                    cv.put(x, y, SCORCH_DARK)
                    if (x, y + 1) not in cracks._pts and (x, y + 1) in tel.cells:
                        cv.put(x, y + 1, lit)

        # fire + ring + star (during attack and dissipate)
        living = []
        if i >= hit_at and i < diss_end:
            living = draw_fire_tongues(cv, cx0, cy0, r_max, tel.cells, diss, phase_shape)
            draw_hot_core(cv, cx0, cy0, 34, tel.cells, diss, phase_shape)
            rs = ring_state(vis_age, diss, r_hit)
            if rs:
                draw_hollow_ring(cv, cx0, cy0, rs["r"], rs["outer"], rs["inner"],
                                 thick=rs["thick"], gaps=rs["gaps"])
            if vis_age <= 2 and diss <= 0:
                draw_speed_lines(cv, cx0, cy0, r_max, 12, FIRE_PAL[4])
            if diss < 0.9:
                draw_star(cv, nx0, ny0, SPARK_R * (0.8 if phase_shape else 0.55),
                          FIRE_PAL, phase=min(2, 0 if vis_age == 0 else (1 if diss < 0.4 else 2)),
                          n=6, diss=diss)

        # spawn rocks on the impact frame; step once so they are off the ground on the peak
        if i == hit_at and not spawned_rocks:
            spawned_rocks = True
            for k in range(12):
                a = (k * 2.31 + 0.41) % math.tau
                sp = 1.8 + (k * 0.41) % 2.2
                rocks.append(Rock(
                    cx0 + math.cos(a) * 14,
                    cy0 + 8 + math.sin(a) * 6,
                    math.cos(a) * sp, math.sin(a) * sp * 0.9,
                    2.2 + (k * 0.33) % 2.0,
                    3 + (k % 2),
                    ROCK_PAL,
                    20 + (k * 3) % 10,
                ))
            for rk in rocks:
                rk.step()
                rk.step()  # clearly off the ground on the frozen peak

        # smoke: one puff when a main tongue first dies, during dissipate
        if (not freeze) and i >= diss_start and i < diss_end:
            for ti, (ang, lmul, wid, die, fork) in enumerate(TONGUES):
                if ti in tongues_seen_dead:
                    continue
                if diss >= die and len(smokes) < 6:
                    tongues_seen_dead.add(ti)
                    rr = 36 + lmul * 22
                    smokes.append(SmokePuff(
                        cx0 + math.cos(ang) * rr,
                        cy0 + math.sin(ang) * rr,
                        math.cos(ang) * 0.25, -0.35 - 0.12 * (ti % 3),
                        5 + (ti % 3),
                        16 + (ti * 2) % 8,
                        seed=11 + ti * 5,
                    ))

        # knockback / victim
        if i >= hit_at:
            if age_hit == 0:
                ninja_flash = 3
            nx = nx0 + KB
            ny = ny0
            if freeze:
                ny = ny0 + (1 if age_hit % 2 == 0 else -1)
            nx = max(8, min(W - 8, nx))
            ny = max(12, min(H - 8, ny))

        if not freeze:
            for rk in rocks:
                rk.step()
            rocks[:] = [rk for rk in rocks if rk.alive()]
            for sm in smokes:
                sm.step()
            smokes[:] = [sm for sm in smokes if sm.alive()]
        for sm in smokes:
            sm.draw(cv)

        draw_flam_pose(cv, cx0, cy0, i, hit_at, WIND, HITSTOP, diss_end)
        vic_flash = ninja_flash > 0
        vic_squash = None
        if i >= hit_at and i < diss_end:
            vic_squash = (12, 14) if i < diss_start else (14, 12)
        draw_ninja(cv, nx, ny, col=1, row=0, flash=vic_flash, squash=vic_squash)
        if (not freeze) and ninja_flash > 0 and (age_hit > 1 or i >= diss_start):
            ninja_flash -= 1

        for rk in rocks:
            rk.draw(cv)

        if i >= hit_at:
            k = i - hit_at
            if k < SHAKE_N:
                if k < HITSTOP + 1:
                    amp = SHAKE
                else:
                    amp = max(1, int(round(SHAKE * (1 - (k - HITSTOP) / max(SHAKE_N - HITSTOP, 1)))))
                sig = 1 if k % 2 == 0 else -1
                shake = (0, sig * amp)

        # short wash on the impact frame only; peak/hitstop stay readable
        if i == hit_at:
            post = "wash"
        elif freeze or i == hit_at + 1:
            post = "flash_edge"

        frames.append(Frame(cv, phase, shake, post))

    key_idx = {
        "windup": hit_at - 2,
        "impact0": hit_at,
        "peak": hit_at + 1,
        "dissipate": diss_start + 5,
        "scorch": diss_end + 1,
    }
    KEYDIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, fr in enumerate(frames):
        im = compose(skill, fr, i)
        im.save(work / f"{i:04d}.png")
        for tag, idx in key_idx.items():
            if i == idx:
                dest = KEYDIR / f"stomp_{tag}.png"
                im.save(dest)
                saved.append(dest)
    out_path = OUT / "23_flame_stomp.gif"
    write_gif(work, out_path)
    print(f"  -> {out_path}  frames={len(frames)}  size={Image.open(out_path).size}  "
          f"hit={hit_at + 1}  bytes={out_path.stat().st_size}")
    for pth in saved:
        print(f"     key {pth.name}")
    return out_path, hit_at + 1, len(frames)


if __name__ == "__main__":
    print("render v4 23_flame_stomp ...")
    render_stomp()
