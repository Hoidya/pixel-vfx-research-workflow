# -*- coding: utf-8 -*-
"""V4 Iaido Slash preview.

Standalone script. Does not modify gif_v3.py.
Output: gifs_v4/19_iaido_slash.gif (576x576, 30fps, loop).

Visual language from case_iaido.md:
  sheathed side stance + tsuba glint + faint aim line;
  step-in + 2-4 frames of a thin white-core / cyan-edge cut;
  hold the line 3-5 frames, flare a thin blade from the target, retract;
  resheath + koiguchi spark, and only then the target fully reacts.
Do not fill the fan.
Warning pixels stay inside the hitbox.
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
STRIKE_F = 3
HOLD_F = 4
FLARE_F = 3
HITSTOP_F = 8
RETRACT_F = 4

ROLE = {
    "damage": dict(
        edge_dark=hx("2b0a08"), main=hx("c0392b"), hi=hx("e8705f"),
        flash=hx("f6d2c4"), white=hx("ffffff"),
    ),
}

WHITE = hx("ffffff")
BLACK = hx("000000")
CYAN = hx("2ce8f5")
CYAN_MID = hx("3aa0c8")
CYAN_DK = hx("124e89")
VIOLET = hx("7a5cff")
STEEL_DK = hx("101018")
STEEL_MID = hx("3a3c48")
SCABBARD = hx("2a2010")
SCABBARD_HI = hx("5a4830")
GOLD = hx("f4e04a")
AFTER_RED = hx("6a1820")
AFTER_PALE = hx("d8dce8")
AIM = hx("8a4038")
AIM_HI = hx("c07068")
SPARK_PAL = [STEEL_DK, STEEL_MID, hx("9aa0b0"), CYAN, WHITE]

CAT_ZH = {"damage": "伤害", "control": "控制", "mixed": "混合", "support": "辅助"}
PHASE_COL = {
    "待机": (150, 150, 150), "蓄力": (201, 183, 156), "出刀": (255, 255, 255),
    "停刃": (200, 220, 230), "撑开": (255, 255, 255), "纳刀": (241, 196, 15),
    "收招": (200, 180, 140),
}

# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------
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

    def rect(self, x, y, w, h, c):
        for yy in range(int(round(y)), int(round(y)) + int(h)):
            for xx in range(int(round(x)), int(round(x)) + int(w)):
                self.put(xx, yy, c)

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


def dither_sil(spr, c, phase=0):
    """Opaque silhouette with Bayer holes (no semi-transparency)."""
    out = Image.new("RGBA", spr.size)
    p, q = spr.load(), out.load()
    col = c if len(c) == 4 else (c[0], c[1], c[2], 255)
    for y in range(spr.height):
        for x in range(spr.width):
            if p[x, y][3] > 0 and BAYER[(y + phase) % 4][(x + phase) % 4] < 12:
                q[x, y] = col
    return out


def outline_sprite(spr, col=WHITE, thick=1):
    out = Image.new("RGBA", (spr.width + 2 * thick, spr.height + 2 * thick))
    sil = silhouette(spr, col if len(col) == 4 else (col[0], col[1], col[2], 255))
    for dy in range(-thick, thick + 1):
        for dx in range(-thick, thick + 1):
            if abs(dx) + abs(dy) == 0:
                continue
            if thick == 1 and abs(dx) == abs(dy):
                continue
            out.alpha_composite(sil, (thick + dx, thick + dy))
    out.alpha_composite(spr, (thick, thick))
    return out


def scale_nn(spr, nw, nh):
    nw, nh = max(1, int(round(nw))), max(1, int(round(nh)))
    return spr if (nw, nh) == spr.size else spr.resize((nw, nh), Image.NEAREST)


def apply_invert(im):
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            px[x, y] = (255 - r, 255 - g, 255 - b, 255)


def apply_bw_punch(im, thresh=110):
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            lum = (r * 2 + g * 3 + b) // 6
            v = 255 if lum >= thresh else 0
            px[x, y] = (v, v, v, 255)


def flash_border(im, col=(255, 255, 255, 255), thick=3):
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            if x < thick or y < thick or x >= w - thick or y >= h - thick:
                px[x, y] = col


# ---------------------------------------------------------------------------
# Particles (accents only, along the cut)
# ---------------------------------------------------------------------------
class CoreChip:
    def __init__(self, x, y, vx, vy, vz, size, pal, life, g=0.3, bounce=0.35):
        self.x, self.y, self.z = float(x), float(y), 0.0
        self.vx, self.vy, self.vz = vx, vy, vz
        self.size = max(1, int(size))
        self.pal, self.life, self.age = pal, int(life), 0
        self.g, self.bounce = g, bounce

    def step(self):
        self.age += 1
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.vz -= self.g
        if self.z <= 0:
            self.z = 0
            if self.vz < -0.5:
                self.vz = -self.vz * self.bounce
                self.vx *= 0.5
                self.vy *= 0.5
            else:
                self.vz = 0
                self.vx *= 0.7
                self.vy *= 0.7

    def alive(self):
        return self.age < self.life

    def draw(self, cv, allow=None):
        remain = self.life - self.age
        if remain <= 3 and self.age % 2:
            return
        sx, sy = int(round(self.x)), int(round(self.y - self.z))
        if allow is not None and (sx, sy) not in allow:
            return
        s = self.size if remain > 4 else max(1, self.size - 1)
        mid = self.pal[min(2, len(self.pal) - 1)]
        hi, core = self.pal[min(3, len(self.pal) - 1)], self.pal[-1]
        if self.age <= 1:
            mid, hi = hi, core
        if s == 1:
            cv.put(sx, sy, hi if self.age <= 2 else mid)
            return
        for dx, dy in ((0, 0), (1, 0)):
            cv.put(sx + dx, sy + dy, mid)
        cv.put(sx, sy, core if self.age <= 3 else hi)


def burst_along(rnd, x, y, pal, n, ang, spread=0.6, speed=(0.6, 1.6),
                life=(8, 16), size=(1, 1)):
    out = []
    for _ in range(n):
        a = ang + rnd.uniform(-spread / 2, spread / 2)
        # mostly perpendicular spray, a little along the cut
        a2 = a + math.pi / 2 * (1 if rnd.random() < 0.5 else -1)
        sp = rnd.uniform(*speed)
        out.append(CoreChip(
            x, y, math.cos(a2) * sp, math.sin(a2) * sp,
            rnd.uniform(0.4, 1.4), rnd.randint(size[0], size[1]), pal,
            rnd.randint(*life),
        ))
    return out


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    l2 = dx * dx + dy * dy
    if l2 <= 1e-9:
        return math.hypot(px - x0, py - y0), 0.0
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / l2))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy)), t


def line_ends(cx, cy, ang, r, inset=6):
    """Start slightly in front of the hip, end at fan radius."""
    x0 = cx + math.cos(ang) * inset
    y0 = cy + math.sin(ang) * inset
    x1 = cx + math.cos(ang) * r
    y1 = cy + math.sin(ang) * r
    return x0, y0, x1, y1


# ---------------------------------------------------------------------------
# Warning: faint aim line + dashed fan edge, never a filled pie
# ---------------------------------------------------------------------------
def draw_warning(cv, tel, t_ratio, frame, cx, cy):
    col = tel.col
    # dashed / flashing border only — no filled pie
    flash = t_ratio >= 0.88 and not (t_ratio >= 0.96 and frame % 2)
    for (x, y) in tel.border:
        dashed = ((x + y + frame // 2) % 3) != 0
        if flash and dashed:
            cv.put(x, y, WHITE)
        elif dashed:
            cv.put(x, y, col["edge_dark"] if t_ratio < 0.7 else col["main"])
    # 1px aim line grows from hip to full radius (the real telegraph hero)
    r = tel.p.get("radius", 48)
    ang = tel.ang
    grow = min(1.0, t_ratio / 0.45) ** 0.7
    x0, y0, x1, y1 = line_ends(cx, cy, ang, r * grow, inset=6)
    for (x, y) in tel.cells:
        d, u = seg_dist(x + 0.5, y + 0.5, x0, y0, x1, y1)
        if u < 0 or u > 1:
            continue
        if d <= 0.55:
            cv.put(x, y, AIM_HI if t_ratio >= 0.7 else AIM)
        elif d <= 1.05 and t_ratio >= 0.55:
            # dim cyan-brown rim so the path reads without looking like the real cut
            if (x + y) % 2 == 0:
                cv.put(x, y, col["main"])


# ---------------------------------------------------------------------------
# The cut: thin white-core / cyan-edge line, optional flare at the target
# ---------------------------------------------------------------------------
def draw_cut(cv, tel, cx, cy, ang, r, target, flare=0.0, length=1.0, residual=0.0):
    """flare 0 = 1-2px hairline. flare 1 = ~5px thin blade, widest at the target.
    residual > 0: broken hairline (sparks of the path).
    Pixels stay inside tel.cells.
    """
    x0, y0, x1, y1 = line_ends(cx, cy, ang, r * length, inset=8)
    tx, ty = target
    # parameter of the target on the segment
    _, t_tgt = seg_dist(tx + 0.5, ty + 0.5, x0, y0, x1, y1)
    for (x, y) in tel.cells:
        d, u = seg_dist(x + 0.5, y + 0.5, x0, y0, x1, y1)
        if u < 0 or u > 1:
            continue
        # width envelope: 1px white core + 1px cyan rim; flare widens only near target
        # tighten the flare: widen only near the target, keep a hairline at the hip
        near = max(0.0, 1.0 - abs(u - t_tgt) / 0.28)
        half = 0.62 + flare * 1.15 * (near ** 1.4)
        if residual > 0:
            h = ((x * 31 + y * 17) & 255)
            if h < residual * 200 or d > 0.8:
                continue
            half = 0.62
        if d > half + 1.15:
            continue
        if d <= 0.62:
            cv.put(x, y, WHITE)
        elif d <= half + 1.05:
            edge = VIOLET if (flare > 0.45 and near > 0.55) else (CYAN if flare > 0.05 else CYAN_MID)
            cv.put(x, y, edge)
        elif d <= half + 1.15 and flare > 0.35 and near > 0.25:
            cv.put(x, y, CYAN_DK if (x + y) % 2 == 0 else CYAN_MID)


def draw_speed_ticks(cv, tel, cx, cy, ang, r, n=4):
    ca, sa = math.cos(ang), math.sin(ang)
    nx, ny = -sa, ca
    for k in range(n):
        u = 0.25 + k * 0.18
        px = cx + ca * (r * u)
        py = cy + sa * (r * u)
        length = 5 + (k % 2)
        for t in range(length):
            x = int(round(px - ca * t))
            y = int(round(py - sa * t + ny * (1 if k % 2 else -1)))
            if (x, y) in tel.cells:
                cv.put(x, y, WHITE)


def draw_scar(cv, tx, ty, ang, length=7, col=WHITE):
    ca, sa = math.cos(ang + 0.35), math.sin(ang + 0.35)
    for t in range(-length // 2, length // 2 + 1):
        cv.put(tx + ca * t, ty + sa * t - 1, col if abs(t) < length // 2 else CYAN_MID)


# ---------------------------------------------------------------------------
# Actors
# ---------------------------------------------------------------------------
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


def draw_ninja(cv, fx, fy, col=1, row=0, flash=False, squash=None, scar=False, ang=0.0):
    spr = ninja_frame(col, row)
    if squash:
        spr = scale_nn(spr, squash[0], squash[1])
    if flash:
        spr = silhouette(spr, WHITE)
    cv.blit(shadow_img, int(round(fx - 6)), int(round(fy - 2)))
    cv.blit(spr, fx - spr.width / 2, fy - spr.height / 2 - 1)
    if scar:
        draw_scar(cv, fx, fy, ang)


def samurai_sprite(pose, facing="right"):
    col = {"down": 0, "left": 1, "up": 2, "right": 3}.get(facing, 3)
    if pose == "attack":
        return crop_cell(load_sheet("Character/Samurai/SeparateAnim/Attack.png"), 16, 16, col, 0)
    if pose == "jump":
        return crop_cell(load_sheet("Character/Samurai/SeparateAnim/Jump.png"), 16, 16, col, 0)
    return crop_cell(load_sheet("Character/Samurai/SeparateAnim/Idle.png"), 16, 16, col, 0)


def draw_scabbard(cv, hx_, hy, pulled=0, flash=False, facing="down"):
    """A 2-3px sheathed blade at the hip, plus optional koiguchi / tsuba glint."""
    if facing == "down":
        # sit the saya just outside the left hip, not on the chest
        x, y = int(round(hx_ - 8 - pulled)), int(round(hy + 5))
        for i in range(5):
            cv.put(x - i, y + i // 2, SCABBARD_HI if i < 2 else SCABBARD)
            cv.put(x - i, y + i // 2 + 1, SCABBARD)
        gx, gy = x + 1, y
    else:
        x, y = int(round(hx_ - 8 - pulled)), int(round(hy + 4))
        for i in range(5):
            cv.put(x - i, y + (i + 1) // 2, SCABBARD_HI if i < 2 else SCABBARD)
            cv.put(x - i, y + (i + 1) // 2 + 1, SCABBARD)
        gx, gy = x + 1, y
    if flash:
        # plus-shaped spark so the 16px tsuba / koiguchi glint actually reads
        cv.rect(gx, gy, 2, 2, WHITE)
        cv.put(gx - 1, gy, WHITE)
        cv.put(gx + 2, gy, WHITE)
        cv.put(gx, gy - 1, WHITE)
        cv.put(gx + 1, gy + 2, WHITE)
        cv.put(gx + 3, gy + 1, CYAN)
        cv.put(gx - 2, gy + 1, CYAN)


def draw_afterimage(cv, spr, cx, cy, ox, oy, col, phase=0):
    sil = dither_sil(spr, col, phase)
    draw_shadow_at(cv, cx + ox, cy + oy)
    cv.blit(sil, cx - sil.width / 2 + ox, cy - sil.height / 2 + oy)


def draw_samurai(cv, cx, cy, phase, local, ang, glint=False, sheath_flash=False,
                 afterimages=0, step=0):
    """phase: idle / windup / strike / hold / flare / sheath / recover."""
    ox, oy, flash, outline = 0, 0, False, None
    facing = "right"
    spr = samurai_sprite("idle", facing)
    pulled = 0

    if phase == "windup":
        # side-on, hand on the hilt, almost still. No full-body outline.
        facing = "down"
        spr = samurai_sprite("idle", facing)
        ox, oy = -2, 1
        if local >= 0.72:
            spr = scale_nn(spr, 16, 14)
            ox, oy = -3, 2
            pulled = 1
    elif phase in ("strike", "hold", "flare"):
        facing = "right"
        spr = samurai_sprite("attack", facing)
        stretch = 22 if phase == "strike" else (20 if phase == "flare" else 18)
        spr = scale_nn(spr, stretch, 16)
        ox = step
        oy = 0
        # only the first strike frame may flash the body; never a gold/white halo
        flash = phase == "strike" and local < 0.34
    elif phase == "sheath":
        # turn slightly down as the blade goes back into the hip
        facing = "down" if local < 0.55 else "right"
        spr = scale_nn(samurai_sprite("idle", facing), 16, 14 if local < 0.7 else 16)
        ox, oy = (-3, 2) if local < 0.55 else (0, 0)
        pulled = 0
    else:
        facing = "right"
        spr = samurai_sprite("idle", facing)
        ox, oy = 0, 0

    # afterimages of the body along the cut (behind the current pose)
    if afterimages > 0 and phase in ("strike", "hold", "flare"):
        ca, sa = math.cos(ang), math.sin(ang)
        for k in range(afterimages, 0, -1):
            back = -k * 6
            col = AFTER_RED if k % 2 else AFTER_PALE
            draw_afterimage(cv, spr, cx, cy,
                            ox + int(round(ca * back)),
                            oy + int(round(sa * back)),
                            col, phase=k)

    draw_actor(cv, spr, cx, cy, flash=flash, outline=outline, ox=ox, oy=oy)

    # scabbard + glint / koiguchi
    if phase in ("idle", "windup", "sheath", "recover"):
        draw_scabbard(cv, cx + ox, cy + oy, pulled=pulled,
                      flash=glint or sheath_flash, facing=facing)
    elif sheath_flash:
        draw_scabbard(cv, cx + ox, cy + oy, pulled=0, flash=True, facing="right")
    return ox, oy


# ---------------------------------------------------------------------------
# Compose / gif
# ---------------------------------------------------------------------------
class Frame:
    def __init__(self, cv, phase, shake=(0, 0), post=None, cut_args=None):
        self.cv, self.phase, self.shake, self.post, self.cut_args = cv, phase, shake, post, cut_args


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


def punch_cut_black(im, tel, cx, cy, ang, r, target, length=1.0):
    """After a white invert, stroke the cut in black so it still reads."""
    px = im.load()
    x0, y0, x1, y1 = line_ends(cx, cy, ang, r * length, inset=5)
    for (x, y) in tel.cells:
        if not (0 <= x < im.size[0] and 0 <= y < im.size[1]):
            continue
        d, u = seg_dist(x + 0.5, y + 0.5, x0, y0, x1, y1)
        if 0 <= u <= 1 and d <= 1.15:
            px[x, y] = (0, 0, 0, 255)


def compose(skill, fr, i):
    im = fr.cv.im.copy()
    if fr.post == "invert":
        apply_invert(im)
        apply_bw_punch(im, 120)
        if fr.cut_args:
            punch_cut_black(im, **fr.cut_args)
        flash_border(im, WHITE, 3)
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


# ---------------------------------------------------------------------------
# Timeline + render
# ---------------------------------------------------------------------------
def render():
    skill = dict(SKILLS["s19_iaido_slash"])
    skill["_nn"] = 19
    cx0, cy0 = 64, 80
    nx0, ny0 = 96, 82
    sp = skill["size_params"]
    p = dict(shape=skill["shape"], style="standard", duration=skill["warning_duration"],
             anchor="caster", color_role="damage", track_time=0, direction=0.0,
             radius=int(sp["radius"] * TILE), angle=sp["angle"])
    tel = Telegraph(p, (cx0, cy0), (nx0, ny0))
    tel.col = ROLE["damage"]
    assert tel.contains((nx0, ny0)), "target not in hitbox"
    r_hit = tel.p["radius"]
    ang = tel.ang

    WARN = frames_of(float(skill["warning_duration"]))
    REC = frames_of(float(skill["recovery_duration"]))
    hit_at = IDLE_F + WARN                          # first strike frame
    hold_at = hit_at + STRIKE_F
    flare_at = hold_at + HOLD_F
    freeze_at = flare_at + FLARE_F                  # peak blade, then hitstop
    retract_at = freeze_at + HITSTOP_F
    sheath_at = retract_at + RETRACT_F
    rec_end = sheath_at + max(REC, 10)
    total = rec_end + TAIL_F

    # named keyframes (frame index -> filename stem)
    key_at = {
        IDLE_F - 1: "iaido_idle",
        hit_at - 12: "iaido_windup",         # mid charge, periodic glint
        hit_at - 2: "iaido_windup_late",     # held tsuba glint
        hit_at: "iaido_strike",              # invert + thin line
        hit_at + 2: "iaido_strike_step",     # afterimages + step
        hold_at + 2: "iaido_hold",
        freeze_at: "iaido_flare",
        sheath_at + 1: "iaido_sheath",
        rec_end + 2: "iaido_recover",
    }

    if FRDIR.exists():
        for f in FRDIR.glob("*.png"):
            f.unlink()
    else:
        FRDIR.mkdir(parents=True, exist_ok=True)
    KEYDIR.mkdir(parents=True, exist_ok=True)

    rnd = random.Random(19)
    chips = []
    spawned_flare = False
    spawned_sheath = False
    composed = []

    for i in range(total):
        cv = Canvas()
        post = None
        shake = (0, 0)
        nx, ny = float(nx0), float(ny0)
        vic_flash = False
        vic_squash = None
        vic_scar = False
        glint = False
        sheath_flash = False
        afterimages = 0
        step = 0
        line_on = False
        flare = 0.0
        length = 1.0
        residual = 0.0

        # ----- phase
        if i < IDLE_F:
            phase = "待机"
            pose = "idle"
            local = 0
        elif i < hit_at:
            phase = "蓄力"
            pose = "windup"
            local = (i - IDLE_F) / max(WARN - 1, 1)
            t_warn = (i - IDLE_F) / max(WARN, 1)
            draw_warning(cv, tel, t_warn, i, cx0, cy0)
            # periodic tsuba glint; last 0.20s (6 frames) holds bright
            if i >= hit_at - 6:
                glint = True
            elif (i - IDLE_F) % 9 < 2 and i - IDLE_F > 4:
                glint = True
        elif i < hold_at:
            phase = "出刀"
            pose = "strike"
            local = (i - hit_at) / max(STRIKE_F - 1, 1)
            line_on = True
            length = 1.0
            afterimages = 2 if i == hit_at else 3
            step = 6 + int(4 * local)
            if i == hit_at:
                post = "invert"
        elif i < flare_at:
            phase = "停刃"
            pose = "hold"
            local = (i - hold_at) / max(HOLD_F - 1, 1)
            line_on = True
            length = 1.0
            afterimages = 2 if i < hold_at + 2 else 1
            step = 10
            # target still looks intact (delayed reveal)
        elif i < retract_at:
            phase = "撑开"
            pose = "flare"
            if i < freeze_at:
                local = (i - flare_at) / max(FLARE_F - 1, 1)
                flare = 0.35 + 0.65 * local
            else:
                local = 1.0
                flare = 1.0
            line_on = True
            afterimages = 2
            step = 11
            # one-frame white flash, then the scar is the reveal
            vic_flash = (i == flare_at)
            vic_scar = True
            kb = 12
            j = 1 if (i % 2 == 0) else -1
            nx = nx0 + kb + (j if i >= freeze_at else 0)
            ny = ny0
            if i >= freeze_at:
                k = i - freeze_at
                amp = 3 if k < 4 else 2
                sig = 1 if k % 2 == 0 else -1
                shake = (sig * amp, 0)
            if i == flare_at + 1 and not spawned_flare:
                spawned_flare = True
                chips.extend(burst_along(rnd, nx0, ny0, SPARK_PAL, 5, ang))
        elif i < sheath_at:
            phase = "撑开"
            pose = "flare"
            local = 1.0 - (i - retract_at) / max(RETRACT_F, 1)
            # retract wide blade back to a hairline, then start breaking
            flare = max(0.0, local)
            line_on = True
            residual = 0.0 if local > 0.25 else (0.25 - local) * 2
            afterimages = 1
            step = 9
            vic_scar = True
            nx = nx0 + 12
            ny = ny0
        else:
            # sheath / recover
            in_sheath = i - sheath_at
            if in_sheath < max(REC, 10):
                phase = "纳刀"
                pose = "sheath"
                local = in_sheath / max(REC - 1, 1)
            else:
                phase = "收招"
                pose = "recover"
                local = 1.0
            # residual hairline fades in the first few sheath frames
            if in_sheath < 5:
                line_on = True
                residual = 0.45 + in_sheath * 0.12
                flare = 0.0
            # koiguchi click is the delayed-reveal trigger: flash one frame, then squash + scar
            if 0 <= in_sheath <= 2:
                sheath_flash = True
                vic_flash = in_sheath == 0
                vic_squash = (14, 12)
                vic_scar = True
                nx = nx0 + 16
                ny = ny0
            elif in_sheath <= 6:
                vic_scar = True
                vic_squash = (15, 13) if in_sheath <= 4 else None
                nx = nx0 + 16
                ny = ny0
            else:
                nx = nx0 + 16
                ny = ny0
            if in_sheath == 1 and not spawned_sheath:
                spawned_sheath = True
                chips.extend(burst_along(rnd, nx0, ny0, [STEEL_DK, CYAN_MID, WHITE], 3, ang,
                                         spread=0.5, speed=(0.4, 1.0), life=(6, 10)))

        # freeze chips during hitstop
        freeze = freeze_at <= i < retract_at
        if not freeze:
            for c in chips:
                c.step()
            chips[:] = [c for c in chips if c.alive()]
        for c in chips:
            c.draw(cv, allow=tel.cells)

        # ----- actors first, then the cut on top so the hairline reads across them
        sox, soy = draw_samurai(cv, cx0, cy0, pose, local, ang,
                     glint=glint, sheath_flash=sheath_flash,
                     afterimages=afterimages, step=step)
        nx = max(8, min(W - 8, nx))
        ny = max(12, min(H - 8, ny))
        draw_ninja(cv, nx, ny, col=1, row=0, flash=vic_flash,
                   squash=vic_squash, scar=vic_scar, ang=ang)

        cut_args = None
        if line_on:
            draw_cut(cv, tel, cx0, cy0, ang, r_hit, (nx0, ny0),
                     flare=flare, length=length, residual=residual)
            cut_args = dict(tel=tel, cx=cx0, cy=cy0, ang=ang, r=r_hit,
                            target=(nx0, ny0), length=length)

        # sheath / tsuba spark last, so the click sits on top of the cut
        # (already drawn with the samurai; redraw flash so it is not buried)
        if glint or sheath_flash:
            facing = "down" if pose in ("windup", "sheath") else "right"
            if pose == "sheath" and local >= 0.55:
                facing = "right"
            draw_scabbard(cv, cx0 + sox, cy0 + soy, pulled=1 if (pose == "windup" and local >= 0.72) else 0,
                          flash=True, facing=facing)

        fr = Frame(cv, phase, shake=shake, post=post, cut_args=cut_args)
        out = compose(skill, fr, i)
        path = FRDIR / f"{i:04d}.png"
        out.save(path)
        composed.append(path)
        if i in key_at:
            out.save(KEYDIR / f"{key_at[i]}.png")

    gif_path = OUT / "19_iaido_slash.gif"
    write_gif(FRDIR, gif_path)
    size = gif_path.stat().st_size
    # verify output size
    im0 = Image.open(composed[0])
    print(f"frames={total} size={im0.size} gif={gif_path} bytes={size}")
    print("keyframes:", ", ".join(key_at[k] for k in sorted(key_at)))
    print(f"hit_at={hit_at} hold_at={hold_at} flare_at={flare_at} "
          f"freeze_at={freeze_at} sheath_at={sheath_at} rec_end={rec_end}")
    return gif_path, size, total, key_at


if __name__ == "__main__":
    render()
