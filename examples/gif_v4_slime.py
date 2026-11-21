# -*- coding: utf-8 -*-
"""V4 slime slam preview.

Independent of gif_v3.py (other skills are being redrawn in parallel).
Reuses telegraph_lib + the shared 192x160 / 3x nearest / header layout
so the output is 576x576 at 30fps. Telegraph pixels stay hitbox-accurate.
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
LABEL_H = 32
IDLE_F = 8
TAIL_F = 8

# Timeline (30 fps)
# idle 8 | warn 30 (telegraph + squash 19, takeoff 5, fall 3, then contact is hit)
# contact 1 | slam+hitstop 3 | dissipate 12 | recover 8 | tail 8
SQUASH_F = 19
TAKEOFF_F = 5
FALL_F = 3
# WARN = SQUASH + TAKEOFF + FALL + leftover intro = 30
WARN_INTRO = 3
WARN = WARN_INTRO + SQUASH_F + TAKEOFF_F + FALL_F  # 30
CONTACT_F = 1
HITSTOP = 3          # mid: 3 frames holding the slam (incl. peak)
FLASH_F = 2          # white only on highlight / pie core
DISS_F = 12
REC_F = 8

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
    "生效": (255, 255, 255), "冲击": (255, 255, 255), "接触": (255, 255, 255),
    "消散": (200, 180, 140), "收招": (241, 196, 15),
}

WHITE = hx("ffffff")
# four-tone slime + wet outline
SL_OUT = hx("1a3010")
SL_SH = hx("2d5a18")
SL_MID = hx("5a9a28")
SL_LIT = hx("8fc63a")
SL_HI = hx("d4f06a")
SL_PAL = [SL_OUT, SL_SH, SL_MID, SL_LIT, SL_HI, WHITE]
EYE_W = hx("f4f0e0")
EYE_P = hx("1a1810")
EYE_R = hx("c03028")
BELLY = hx("c8e878")

FONT = ImageFont.truetype(str(FONT_PATH), 12)
ninja_sheet = Image.open(NA_CONTENT / "character/ninja_blue/sprite.png").convert("RGBA")
floor = Image.open(NA_CONTENT / "map/tileset_floor.png").convert("RGBA")
GRASS = [floor.crop((x, 192, x + 16, 208)) for x in (176, 192, 208, 224, 240)]
DATA = json.loads((ROOT / "examples.json").read_text(encoding="utf-8"))
SKILLS = {s["id"]: s for s in DATA["skills"]}


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


def scale_nn(spr, nw, nh):
    nw, nh = max(1, int(round(nw))), max(1, int(round(nh)))
    return spr if (nw, nh) == spr.size else spr.resize((nw, nh), Image.NEAREST)


# ---------------------------------------------------------------------------
# Telegraph (same fill as v3, pixels == hitbox)
# ---------------------------------------------------------------------------
def ease_fill(t):
    t = max(0.0, min(1.0, t))
    if t < 0.8:
        return (t / 0.8) ** 2 * 0.72
    u = (t - 0.8) / 0.2
    return 0.72 + u * u * 0.28


def draw_warning(cv, tel, t_ratio, frame):
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
    flash = t_ratio >= 0.88 and not (t_ratio >= 0.96 and frame % 2)
    for (x, y) in tel.border:
        cv.put(x, y, WHITE if flash else col["edge_dark"])
    for (x, y) in tel.inner_border:
        cv.put(x, y, WHITE if flash else (col["hi"] if t_ratio >= 0.7 else col["main"]))


# ---------------------------------------------------------------------------
# Soft wave-crown (rounded lobes, never a pointed star)
# ---------------------------------------------------------------------------
def _crown_reach(ang, r, diss, seed_off=0.0):
    # very soft rounded lobes (no 8-harmonic spikes)
    s = (1.00
         + 0.08 * math.sin(5 * ang + 0.6 + seed_off)
         + 0.05 * math.sin(3 * ang + 1.8))
    # collapse faster so the puddle is small by recover
    return r * s * (1.0 - 0.62 * diss)


def draw_crown(cv, cx, cy, r, core_cells, diss=0.0, flash_core=False, phase=1):
    """Soft wavy disc. Solid fill is strictly inside the hitbox cells."""
    if diss >= 0.90:
        return
    r_now = r * (0.82 if phase == 0 else 1.0)
    # iterate hitbox cells only: telegraph pixels == hitbox
    for (x, y) in core_cells:
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        rad = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        reach = _crown_reach(ang, r_now, diss)
        if rad > reach + 0.35:
            continue
        t = rad / max(reach, 1.0)
        rim = 0.74 <= t <= 1.0
        # pie-core flash is a SMALL highlight, not a white band
        if t < 0.10 and flash_core:
            c = WHITE
        elif t < 0.22 and flash_core:
            c = SL_HI
        elif t < 0.28:
            c = SL_HI if diss < 0.35 else SL_LIT
        elif t < 0.55:
            c = SL_LIT
        elif rim and diss < 0.50:
            c = SL_LIT if t < 0.88 else SL_MID
        else:
            c = SL_MID if t < 0.88 else SL_SH
        if diss > 0.50 and BAYER[y % 4][x % 4] < int((diss - 0.50) * 28):
            continue
        cv.put(x, y, c)
        if t >= 0.93 and diss < 0.55:
            cv.put(x, y, SL_OUT)


# ---------------------------------------------------------------------------
# Teardrops with 1px strands; some fall back, some become puddles
# ---------------------------------------------------------------------------
class Tear:
    def __init__(self, x, y, vx, vy, vz, pal, life, back=False, size=2):
        self.x, self.y, self.z = float(x), float(y), 0.4
        self.vx, self.vy, self.vz = vx, vy, vz
        self.life, self.age = int(life), 0
        self.back = back
        self.size = size
        self.ox, self.oy = float(x), float(y)  # origin for the strand
        self.landed = False
        self.puddle = 0  # frames as a puddle after landing
        self.gone = False
        self.strand = True

    def step(self, cx, cy):
        if self.gone:
            return
        self.age += 1
        if self.landed:
            self.puddle += 1
            if self.puddle > 10:
                self.gone = True
            return
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vz -= 0.28
        # air drag
        self.vx *= 0.94
        self.vy *= 0.94
        if self.back and self.age >= 5:
            # arc back toward the body
            self.vx += (cx - self.x) * 0.08
            self.vy += (cy - self.y) * 0.08
        if self.z <= 0:
            self.z = 0
            if self.back:
                # merge back: hop toward body then vanish
                self.vx += (cx - self.x) * 0.2
                self.vy += (cy - self.y) * 0.2
                if math.hypot(self.x - cx, self.y - cy) < 6 or self.age > self.life:
                    self.gone = True
                    return
            self.landed = True
            self.strand = False
        if self.age > 8:
            self.strand = False
        if self.age > self.life and not self.landed:
            self.landed = True
            self.z = 0
            self.strand = False

    def draw(self, cv, cx, cy):
        if self.gone:
            return
        sx, sy = int(round(self.x)), int(round(self.y - self.z))
        if self.landed:
            # irregular little puddle, fades by dither
            pr = 2 if self.puddle < 5 else 1
            fade = self.puddle > 6 and (sx + sy + self.puddle) % 2
            if fade:
                return
            for dy in range(-pr, pr + 1):
                for dx in range(-pr - 1, pr + 2):
                    if (dx * dx) / ((pr + 1) ** 2) + (dy * dy) / (pr * pr + 0.4) <= 1.05:
                        c = SL_MID if abs(dx) + abs(dy) <= 1 else SL_SH
                        if abs(dx) + abs(dy) >= pr + 1:
                            c = SL_OUT
                        cv.put(sx + dx, sy + dy, c)
            cv.put(sx, sy, SL_LIT if self.puddle < 4 else SL_MID)
            return
        # teardrop: round head, thinning tail opposite velocity
        ang = math.atan2(self.vy - 0.15, self.vx) if (abs(self.vx) + abs(self.vy)) > 0.05 else -math.pi / 2
        ux, uy = math.cos(ang), math.sin(ang)
        head = WHITE if self.age <= 1 else SL_HI
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1)):
            cv.put(sx + dx, sy + dy, head if abs(dx) + abs(dy) <= 1 else SL_LIT)
        cv.put(sx, sy, head)
        tail_n = 5 if self.size >= 2 else 3
        for k in range(1, tail_n + 1):
            col = SL_LIT if k == 1 else (SL_MID if k <= 2 else (SL_SH if k <= 4 else SL_OUT))
            # tail gets thinner
            cv.put(sx - ux * k, sy - uy * k, col)
            if k <= 2 and self.size >= 2:
                cv.put(sx - ux * k + uy * 0.4, sy - uy * k - ux * 0.4, SL_MID)
        # 1px viscous strand, solid (no skipped pixels) while still close
        if self.strand and self.age <= 6:
            dist = math.hypot(self.x - self.ox, self.y - self.oy)
            if 2 < dist < 16:
                steps = max(2, int(dist))
                for i in range(1, steps):
                    t = i / steps
                    px = self.ox + (self.x - self.ox) * t
                    py = self.oy + (self.y - self.oy) * t - self.z * t
                    cv.put(px, py, SL_MID if i < 2 or i > steps - 2 else SL_SH)


def spawn_tears(rnd, cx, cy, r, n=9):
    out = []
    # irregular but even-ish around the crown
    base = rnd.uniform(0, math.tau)
    for i in range(n):
        a = base + i * math.tau / n + rnd.uniform(-0.18, 0.18)
        rr = r * rnd.uniform(0.86, 0.96)
        ox = cx + math.cos(a) * rr
        oy = cy + math.sin(a) * rr
        # start a few pixels out so the teardrop and strand are visible on frame 0
        x = ox + math.cos(a) * 4
        y = oy + math.sin(a) * 3
        sp = rnd.uniform(1.0, 2.0)
        vz = rnd.uniform(1.0, 2.0)
        back = i % 2 == 0  # half return, half puddle
        life = rnd.randint(10, 16) if not back else rnd.randint(9, 14)
        t = Tear(x, y, math.cos(a) * sp, math.sin(a) * sp, vz,
                 SL_PAL, life, back=back, size=2 if i % 3 else 1)
        t.ox, t.oy = ox, oy
        out.append(t)
    return out


# ---------------------------------------------------------------------------
# Ground puddles left after returning / leftover drips
# ---------------------------------------------------------------------------
def draw_residue(cv, puddles, diss):
    for p in puddles:
        if p["age"] <= 0:
            continue
        fade = p["age"] / p["life"]
        if fade < 0.2 and BAYER[p["y"] % 4][p["x"] % 4] < 8:
            continue
        pr = p["r"] if fade > 0.45 else max(1, p["r"] - 1)
        for dy in range(-pr, pr + 1):
            for dx in range(-pr - 1, pr + 2):
                if (dx * dx) / ((pr + 1.2) ** 2) + (dy * dy) / (max(pr, 1) ** 2 + 0.5) <= 1.0:
                    if fade < 0.35 and (dx + dy + p["x"]) % 2:
                        continue
                    c = SL_SH if abs(dx) + abs(dy) >= pr else SL_MID
                    cv.put(p["x"] + dx, p["y"] + dy, c)


# ---------------------------------------------------------------------------
# Procedural slime (dome, wet edge, hard highlight, eyes stay readable)
# ---------------------------------------------------------------------------
def _in_dome(lx, ly, bw, bh):
    """lx,ly in body space, origin at center, +y down. Round top, slightly flat base."""
    nx = (lx + 0.5) / max(bw * 0.5, 0.5)
    # lower half uses a slightly flatter ellipse so the slime sits, top stays a round onion
    if ly >= 0:
        ny = (ly + 0.5) / max(bh * 0.58, 0.5)
    else:
        ny = (ly + 0.5) / max(bh * 0.50, 0.5)
    return nx * nx + ny * ny <= 1.02


def draw_shadow(cv, cx, gy, bw, z):
    """Thin ground shadow that shrinks as the body leaves the ground."""
    k = max(0.0, min(1.0, z / 12.0))
    sw = max(3, int(round(bw * (0.50 - 0.28 * k))))
    sh = 1 if k > 0.55 else 2
    col = (22, 28, 16)
    for dy in range(-sh, sh + 1):
        for dx in range(-sw, sw + 1):
            rx = dx / max(sw, 1)
            ry = dy / max(sh, 0.7)
            if rx * rx + ry * ry <= 1.0:
                if rx * rx + ry * ry > 0.45 and BAYER[(gy + dy) % 4][(cx + dx) % 4] >= 6:
                    continue
                cv.put(cx + dx, gy + 1 + dy, col)


def draw_slime(cv, cx, gy, bw, bh, z, flash_hi=False, wobble_x=0):
    """Anchor gy is the ground / feet row. Body lifts by z pixels."""
    bw = max(6, int(round(bw)))
    bh = max(5, int(round(bh)))
    z = max(0, int(round(z)))
    cx = int(round(cx + wobble_x))
    gy = int(round(gy))
    draw_shadow(cv, cx, gy, bw, z)
    # body center: bottom sits at gy - z
    bottom = gy - z
    top = bottom - bh + 1
    cy_body = (top + bottom) // 2  # integer; float .5 + banker's round smeared rows
    # raster
    for ly in range(-(bh // 2) - 1, (bh + 1) // 2 + 1):
        for lx in range(-(bw // 2) - 1, (bw + 1) // 2 + 1):
            if not _in_dome(lx, ly, bw, bh):
                # wet 1px outline: neighbor inside
                ring = False
                for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    if _in_dome(lx + ox, ly + oy, bw, bh):
                        ring = True
                        break
                if ring:
                    cv.put(cx + lx, cy_body + ly, SL_OUT)
                continue
            # lighting: upper-left is lit, lower is shadow
            nx = (lx + 0.5) / (bw / 2)
            ny = (ly + 0.5) / (bh / 2)
            y_ratio = (ly + bh / 2) / max(bh, 1)
            lit = (-nx * 0.70 + -ny * 0.60)
            if lit > 0.50:
                c = SL_HI
            elif lit > 0.08:
                c = SL_LIT
            elif y_ratio > 0.84:
                c = SL_SH
            else:
                c = SL_MID
            # dither the tone edges
            b = BAYER[int(cy_body + ly) % 4][int(cx + lx) % 4]
            if 0.42 < lit <= 0.50 and b < 8:
                c = SL_HI
            elif 0.00 < lit <= 0.08 and b < 8:
                c = SL_LIT
            # hard 1–2px specular only; flash turns just this spot white
            if (lx in (-2, -1) and ly in (-bh // 2 + 1, -bh // 2 + 2)
                    and bw >= 10 and bh >= 8):
                c = WHITE if flash_hi else SL_HI
            cv.put(cx + lx, cy_body + ly, c)
    # eyes: stay readable at every squash. Facing right.
    # place in the upper-right quadrant of the body
    ex = cx + max(1, bw // 5)
    ey = int(round(cy_body - bh * 0.12))
    # white of the eye, 2x2 or 3x2 depending on size
    ew = 3 if bw >= 14 and bh >= 10 else 2
    eh = 2 if bh >= 9 else 1
    for dy in range(eh):
        for dx in range(ew):
            cv.put(ex + dx, ey + dy, EYE_W)
    # pupil
    cv.put(ex + ew - 1, ey, EYE_P if eh == 1 else EYE_P)
    if eh >= 2:
        cv.put(ex + ew - 1, ey, EYE_P)
    # red accent on the facing cheek (DQ / NA slime cue)
    cv.put(ex + ew + 1, ey, EYE_R)
    if bh >= 9:
        cv.put(ex + ew + 1, ey + 1, EYE_R)
    # tiny mouth on mid squashes so the face still reads
    if bh >= 10 and bw >= 12:
        cv.put(ex - 1, ey + eh + 1, SL_OUT)
        cv.put(ex, ey + eh + 1, SL_OUT)


# ---------------------------------------------------------------------------
# Ninja victim
# ---------------------------------------------------------------------------
def draw_ninja(cv, fx, fy, flash=False, squash=None, smear=0):
    spr = ninja_frame(1, 0)
    if squash:
        spr = scale_nn(spr, squash[0], squash[1])
    if flash:
        spr = silhouette(spr, WHITE)
    # tiny ground shadow under the ninja, also shrinks if we ever hop him (we don't)
    for dx in range(-4, 5):
        if abs(dx) >= 4 and (fx + dx + fy) % 2:
            continue
        cv.put(fx + dx, fy + 6, (18, 22, 14))
    cv.blit(spr, fx - spr.width / 2, fy - spr.height / 2 - 1)
    if smear > 0 and not flash:
        # a wet blob stuck to the chest / left side, fades by shrinking
        sx = int(round(fx - 3))
        sy = int(round(fy - 1))
        r = 2 if smear >= 4 else 1
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r + 0.4:
                    cv.put(sx + dx, sy + dy, SL_LIT if dx + dy <= 0 else SL_MID)
        cv.put(sx, sy, SL_HI if smear >= 5 else SL_LIT)


# ---------------------------------------------------------------------------
# Header / compose / gif
# ---------------------------------------------------------------------------
class Frame:
    def __init__(self, cv, phase, shake=(0, 0)):
        self.cv, self.phase, self.shake = cv, phase, shake


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


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------
# Body pose for a given frame
# ---------------------------------------------------------------------------
def body_pose(i, hit_at, diss_start, diss_end, rec_end):
    """Return bw, bh, z, flash_hi, wobble_x."""
    # rest size 16x16, area ~ constant
    if i < IDLE_F:
        # breathe
        ph = (i / 12.0) * math.tau
        return 16 + int(round(math.sin(ph))), 16 - int(round(math.sin(ph))), 0, False, 0

    warn_i = i - IDLE_F
    squash_start = WARN_INTRO
    take_start = squash_start + SQUASH_F
    fall_start = take_start + TAKEOFF_F

    if i < hit_at:
        if warn_i < squash_start:
            ph = (i / 12.0) * math.tau
            return 16 + int(round(math.sin(ph))), 16 - int(round(math.sin(ph))), 0, False, 0
        if warn_i < take_start:
            # compress to ~1.3x wide, ~0.8x tall, plus a slow jelly wobble
            u = smooth((warn_i - squash_start) / max(SQUASH_F - 1, 1))
            bw = lerp(16, 21, u)
            bh = lerp(16, 11, u)
            # one and a half slow wobbles toward the end
            if u > 0.45:
                w = 1.2 * math.sin((u - 0.45) / 0.55 * 3.2 * math.pi)
                bw += w
                bh -= w * 0.5
            return bw, bh, 0, False, 0
        if warn_i < fall_start:
            # takeoff: footprint shrinks, body stretches, z rises, shadow shrinks
            u = smooth((warn_i - take_start) / max(TAKEOFF_F - 1, 1))
            bw = lerp(21, 11, u)
            bh = lerp(11, 21, u)
            z = lerp(0, 11, u)
            return bw, bh, z, False, 0
        # fall: stretch along the drop, z comes down to just above the ground
        u = smooth((warn_i - fall_start) / max(FALL_F - 1, 1))
        bw = lerp(11, 14, u)
        bh = lerp(21, 18, u)
        z = lerp(11, 2, u)
        return bw, bh, z, False, 0

    if i == hit_at:
        # contact: rounded rest shape, just touching
        return 16, 16, 1, False, 0

    if i < diss_start:
        # slam pancake ~1.5x, held through hitstop
        e = i - hit_at  # 1, 2, 3
        flash = e <= FLASH_F
        return 24, 9, 0, flash, 0

    if i < diss_end:
        # 2–3 decaying wobbles, then settle toward the dome
        u = (i - diss_start) / max(DISS_F - 1, 1)
        # damped oscillator: starts from pancake, overshoots tall, etc.
        # y scale around 16: A0=7 (9 vs 16), decays
        amp = 7.0 * math.exp(-2.4 * u)
        # 2.5 cycles over the dissipate window
        osc = math.cos(u * 2.5 * math.tau)
        # pancake is wide+short (osc=+1 at u=0: wait cos0=1 -> want short)
        # at u=0: bh=9, bw=24.  bh = 16 - amp*cos, bw = 16 + amp*cos * 1.15
        bh = 16 - amp * osc
        bw = 16 + amp * osc * 1.2
        z = max(0.0, 1.5 * max(0, -osc) * (amp / 7.0))  # tiny hop on the tall peaks
        return bw, bh, z, False, 0

    if i < rec_end:
        e = i - diss_end
        u = smooth(e / max(REC_F - 1, 1))
        # last small settle
        bw = lerp(17, 16, u)
        bh = lerp(15, 16, u)
        return bw, bh, 0, False, 0

    ph = (i / 12.0) * math.tau
    return 16 + int(round(math.sin(ph))), 16 - int(round(math.sin(ph))), 0, False, 0


def tel_params(skill):
    sp = skill["size_params"]
    p = dict(shape=skill["shape"], style="standard", duration=skill["warning_duration"],
             anchor="caster", color_role="damage", track_time=0, direction=0.0)
    if "radius" in sp:
        p["radius"] = int(sp["radius"] * TILE)
    return p


def render():
    skill = dict(SKILLS["s01_slime_slam"])
    skill["_nn"] = 1
    cx0, cy0 = 72, 80
    nx0, ny0 = 108, 80
    tel = Telegraph(tel_params(skill), (cx0, cy0), (nx0, ny0))
    tel.col = ROLE["damage"]
    assert tel.contains((nx0, ny0)), "player not in hitbox"
    r_hit = int(tel.p.get("radius", 48))

    hit_at = IDLE_F + WARN          # 38
    diss_start = hit_at + CONTACT_F + HITSTOP
    diss_end = diss_start + DISS_F
    rec_end = diss_end + REC_F
    total = rec_end + TAIL_F

    if FRDIR.exists():
        for f in FRDIR.glob("*.png"):
            f.unlink()
    else:
        FRDIR.mkdir(parents=True, exist_ok=True)
    KEYDIR.mkdir(parents=True, exist_ok=True)

    rnd = random.Random(401)
    tears = []
    spawned = False
    residue = []
    frames = []
    nx, ny = float(nx0), float(ny0)
    ninja_flash = 0
    smear = 0
    kb = int(skill.get("knockback_px", 24))

    for i in range(total):
        cv = Canvas()
        shake = (0, 0)
        warn_i = i - IDLE_F

        if i < IDLE_F:
            phase, t_warn = "待机", -1
        elif i < hit_at:
            if warn_i < WARN_INTRO + SQUASH_F:
                phase = "预警" if warn_i < WARN_INTRO + 4 else "蓄力"
            elif warn_i < WARN_INTRO + SQUASH_F + TAKEOFF_F:
                phase = "蓄力"
            else:
                phase = "蓄力"
            t_warn = warn_i / max(WARN, 1)
        elif i == hit_at:
            phase, t_warn = "接触", 1.0
        elif i < diss_start:
            phase, t_warn = "冲击", 1.0
        elif i < diss_end:
            phase, t_warn = "消散", 1.0
        elif i < rec_end:
            phase, t_warn = "收招", 1.0
        else:
            phase, t_warn = "待机", -1

        freeze = (hit_at + CONTACT_F) < i < diss_start
        # freeze holds the slam peak (first slam frame = hit_at+1)
        vis_i = (hit_at + CONTACT_F) if freeze else i

        # ground telegraph during the warning
        if IDLE_F <= i < hit_at:
            draw_warning(cv, tel, t_warn, i)

        # crown + residue after contact
        if i >= hit_at and i < rec_end:
            if i == hit_at:
                # contact: no crown yet (rounded body just touching)
                pass
            else:
                if freeze:
                    diss = 0.0
                    phase_shape = 1
                    flash_core = True  # first held frames include pie-core flash
                    # only first 2 slam frames
                    flash_core = (vis_i - hit_at) <= FLASH_F and (i - hit_at) <= FLASH_F
                    # during hold past flash, no core flash
                    if i - hit_at > FLASH_F:
                        flash_core = False
                elif i < diss_start:
                    diss = 0.0
                    phase_shape = 1
                    flash_core = (i - hit_at) <= FLASH_F
                else:
                    diss = (i - diss_start) / max(DISS_F - 1, 1)
                    diss = 1 - (1 - diss) * (1 - diss)
                    phase_shape = 1
                    flash_core = False
                # slightly smaller than r_hit so the wet lip stays in the hitbox
                draw_crown(cv, cx0, cy0, r_hit - 0.5, tel.cells,
                           diss=diss, flash_core=flash_core, phase=phase_shape)
                draw_residue(cv, residue, diss)

        # spawn tears on the first slam frame
        if i == hit_at + CONTACT_F and not spawned:
            spawned = True
            tears = spawn_tears(rnd, cx0, cy0, r_hit - 1, n=9)

        if i >= hit_at + CONTACT_F:
            age = i - hit_at
            if age == CONTACT_F:
                ninja_flash = 2
                smear = 8
            # knockback snaps on the slam, jitter during hitstop
            nx = nx0 + kb
            ny = ny0
            if hit_at + CONTACT_F <= i < diss_start:
                nx = nx0 + kb + (1 if age % 2 == 0 else -1)
            nx = max(8, min(W - 8, nx))
            ny = max(12, min(H - 8, ny))
        elif i >= hit_at:
            # contact: ninja still in place, not yet flashed
            nx, ny = float(nx0), float(ny0)

        # body
        pose_i = vis_i if (freeze or i == hit_at + CONTACT_F) else i
        # during freeze use the slam pose (hit_at+1)
        if freeze:
            pose_i = hit_at + CONTACT_F
        bw, bh, z, flash_hi, wob = body_pose(pose_i, hit_at, diss_start, diss_end, rec_end)
        # flash only on slam frames 1–2, not on contact, not after
        if i == hit_at:
            flash_hi = False
        elif hit_at < i and (i - hit_at) <= FLASH_F:
            flash_hi = True
        elif freeze and (i - hit_at) <= FLASH_F:
            flash_hi = True
        else:
            flash_hi = False
        draw_slime(cv, cx0, cy0, bw, bh, z, flash_hi=flash_hi, wobble_x=wob)

        vic_flash = ninja_flash > 0
        vic_squash = (14, 12) if (i >= hit_at and i < diss_end) else None
        draw_ninja(cv, nx, ny, flash=vic_flash, squash=vic_squash, smear=smear)
        if (not freeze) and ninja_flash > 0 and i > hit_at:
            ninja_flash -= 1
        if (not freeze) and i >= diss_start and smear > 0:
            smear -= 1
        elif (not freeze) and i > hit_at + FLASH_F and smear > 5:
            smear -= 1

        # tears (frozen during hitstop)
        if not freeze:
            for t in tears:
                t.step(cx0, cy0)
            # convert finished returners / leftover into residue puddles
            new = []
            for t in tears:
                if t.gone and t.back:
                    continue
                if t.gone:
                    continue
                if t.landed and t.puddle == 1 and not t.back:
                    residue.append({"x": int(round(t.x)), "y": int(round(t.y)),
                                    "r": 2 if t.size >= 2 else 1,
                                    "life": 14, "age": 14})
                new.append(t)
            tears = new
            for p in residue:
                p["age"] -= 1
            residue[:] = [p for p in residue if p["age"] > 0]
        for t in tears:
            t.draw(cv, cx0, cy0)

        # mild directional shake on slam, decays quickly (mid, 1px)
        if i >= hit_at + CONTACT_F:
            k = i - (hit_at + CONTACT_F)
            if k < 5:
                amp = 1
                shake = (amp if k % 2 == 0 else -amp, 0)

        frames.append(Frame(cv, phase, shake))

    # keyframes (named as requested)
    take_start = IDLE_F + WARN_INTRO + SQUASH_F
    key_idx = {
        "idle": 3,
        "windup": IDLE_F + WARN_INTRO + SQUASH_F - 3,   # deep pancake
        "takeoff": take_start + TAKEOFF_F - 2,
        "contact": hit_at,
        "slam": hit_at + CONTACT_F,                     # first slam / crown
        "wobble": diss_start + 3,                       # first tall overshoot
        "dissipate": diss_start + 7,
        "recover": diss_end + 3,
    }

    saved = []
    for i, fr in enumerate(frames):
        im = compose(skill, fr, i)
        im.save(FRDIR / f"{i:04d}.png")
        for tag, idx in key_idx.items():
            if i == idx:
                dest = KEYDIR / f"slime_{tag}.png"
                im.save(dest)
                saved.append((tag, dest, i))

    out_path = OUT / "01_slime_slam.gif"
    write_gif(FRDIR, out_path)
    print("GIF", out_path, out_path.stat().st_size)
    print("frames", len(frames), "hit_at", hit_at, "diss_start", diss_start,
          "diss_end", diss_end, "total", total)
    print("size", compose(skill, frames[0], 0).size)
    print("keys", saved)
    return out_path, frames, key_idx, hit_at, diss_start, diss_end


if __name__ == "__main__":
    render()
