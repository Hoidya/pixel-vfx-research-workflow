---
name: vfx-research-workflow
description: Research published attack VFX cases first, then redraw 2D pixel skill effects. Use when an attack already has a correct telegraph or hitbox but the animation looks timid, technically right but not bold, or when remaking a slash, ground slam, fire burst, slime slap, or similar move. Follow a six-step loop: general rules, 8-12 cited cases, a timeline scheme, user approval before rendering, independent scripts that keep old versions, then keyframe self-check and one iteration if needed.
---

# VFX research workflow / 先研究案例再画技能特效

A reusable loop for **redrawing** 2D pixel-art attack effects after the warning (telegraph) and hitbox are already fair. It is a companion to [pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph), which covers "warning == hitbox". This skill covers **how the attack should look and feel** once that contract is in place.

把它用在「预警和判定已经正确，但出手特效看起来胆小、正确但不像那一招」的时候。先查已发表的案例，再写时间轴方案，**等用户确认后才渲图**。

Talk to the user in their language. Use generic public example names (a slime, a samurai, a fire giant, a wooden dummy). Never use a project's private game title, character names, or plot in notes, file names, or commits.

## When to use / 何时使用

- The user says the effects look rough, timid, or "technically fine but not bold".
- You are remaking a specific move type (iaido / quick-draw slash, ground slam + fire, slime slap, or a similar family).
- You are about to invent VFX by stacking more particles instead of studying how published games and tutorials stage the same move.

Do **not** use this skill to copy another artist's frames or asset-pack art into a deliverable. Cases are for structure, timing, and shape language only.

## The six steps / 六步流程

Follow these in order. Helper files in this folder hold the tables and templates.

### 1. Restate the general rules

Read [rules.md](rules.md). Before searching, write down (and obey) the shared rules:

- FX about **3–5×** the character, may overflow the hitbox; the **brightest solid core = the hitbox**; telegraph pixels still **= the hitbox**.
- A **recognizable big shape** first (crescent, star spark, shock ring, spike burst, lobed splat). Particles are accents. Heavy moves stay hard-edged.
- **Uneven timing**: long wind-up, **1–3 frames** of action, **8–15 frames** of dissipate (missing chunks / cooling / shattering, proportional).
- **Hit frames**: 1–2 frames of full-white / invert / high-contrast impact; **hitstop freezes the most exaggerated picture**.
- **Few ramps, high contrast**: white core → bright → dark outer, 3–5 hard steps; the theme color is the second layer.
- **Layer stack**: impact frame + main shape + star spark + speed lines + directional decaying shake + hitstop + victim silhouette + knockback.
- **Character poses are the skeleton**: clear opposite-direction squash/stretch on the wind-up, stretch/overshoot on the attack, victim flash and pose change.
- **Tier the feedback**: light/mid stays restrained; heavy boss moves can wash the screen and hitstop longer; a climax move may add a short screen flash and a longer freeze. Do not spend the climax vocabulary on every hit.

If the project already has a telegraph system, keep "warning pixels == hitbox" while VFX overflow is painted on a separate layer.

### 2. Collect 8–12 specific cases for this move type

Search for published, citable examples of **this** family (not generic juice). Aim for a mix of games, animation, tutorials, and (optionally) asset-pack **descriptions** — not the art itself.

For each case record, in [case-template.md](case-template.md):

- Name
- A **real URL** you actually opened (never invent a link)
- Drawing notes: wind-up, impact frame, main shape, rings/cracks/debris, fire or goo language, smoke, ground marks, dissipate, timing, color

This folder already has worked case tables for three families:

- Quick-draw / iaido slash
- Ground slam + fire / shockwave
- Slime slap / body slam

Use them as a starting point, then add or replace cases if the move differs. If a page only describes mechanics, say so; do not invent frame-by-frame color ramps.

### 3. Write a timeline scheme and contrast the old version

Using [scheme-template.md](scheme-template.md), write a scheme **segmented by time** (wind-up, frame 0, peak/hitstop, dissipate, recovery) that a 16px top-down (or the project's) pixel pipeline can actually draw.

Explicitly list what to **keep** from the current version and what is wrong (for example: a filled color bullseye instead of a hollow ring, a symmetric flower instead of irregular tongues, a spatial hash that chews blocky holes in the dissipate).

Keep the scheme in the project's agreed pixel rules: integer pixels, nearest-neighbour, dither instead of alpha unless the project says otherwise.

### 4. Wait for user approval before touching pictures

Show the scheme (and the case list if useful). **Do not generate or overwrite GIFs, sprites, or keyframes until the user confirms.** If they ask for research only, stop after step 3.

### 5. Render in parallel, one independent script per move, keep old versions

Once approved:

- New script per move (do not edit a shared renderer that other people are using in parallel).
- Write to a **new output folder**. Do not overwrite previous versions (`v1`, `v2`, …).
- Same canvas/pixel contract as the project (the examples here used 576×576, 30 fps, looping GIFs).
- Telegraph pixels remain the hitbox. Overflow VFX is allowed. Brightest solid core stays inside the hitbox.
- Tier feedback correctly (a mid slime slap should not get a climax-only full-screen invert).

The example preview GIFs and reference scripts live in [examples/](examples/).

### 6. Keyframe self-check, one iteration, ship with known limits

Save keyframes for at least **wind-up, impact, peak (the frozen picture), dissipate**. Open them and score against [checklist.md](checklist.md) and the cases — not only against "did the script run".

If the pictures are still timid or miss a stated rule, **iterate once**. Then deliver:

- Paths and file sizes
- 1–2 sentences per move on what changed
- Known limits (honest: blocky scorch, a ring that leaves the frame, a core hidden by sparks, and so on)

## Privacy and anti-plagiarism / 隐私与防抄袭

- No private game titles, novel titles, character names, or plot in any note, filename, commit, or GIF label. Use generic public names.
- No local machine paths, emails, or tokens in committed files.
- Do not paste another artist's frames, sprites, or asset-pack art into deliverables. Cite the page, then draw original shapes.
- Ninja Adventure art used in the example GIFs is CC0 (Pixel-boy & AAA). See [CREDITS.md](CREDITS.md).

## Files in this folder

| File | Role |
|---|---|
| [rules.md](rules.md) | General rules table (EN + 中文) |
| [case-template.md](case-template.md) | Blank case card + three filled type tables with real URLs |
| [scheme-template.md](scheme-template.md) | Timeline scheme template |
| [checklist.md](checklist.md) | Keyframe self-check list |
| [examples/](examples/) | v4 preview GIFs and reference renderer scripts |

## Related

For designing the warning itself (shape, style, duration, cadence, budget), use [pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph).
