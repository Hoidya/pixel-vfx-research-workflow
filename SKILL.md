---
name: vfx-research-workflow
description: Research and refine 2D pixel attack VFX when the telegraph and hitbox are sound but the animation lacks force or style fit. Choose the project's reference style, study cited move cases, plan the full action, then render and inspect stills and continuous motion before delivery.
---

# VFX research workflow / 先研究案例再画技能特效

A reusable loop for **redrawing** 2D pixel-art attack effects after the warning (telegraph) and hitbox are already fair. It is a companion to [pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph), which covers "warning == hitbox". This skill covers **how the attack should look and feel** once that contract is in place.

把它用在「预警和判定已经正确，但出手特效看起来胆小、正确但不像那一招」的时候。先确认案例画风，查已发表案例，写时间轴方案，**等用户确认后才渲图**，最后检查逐帧和连续动作。

Talk to the user in their language. Use generic public example names (a slime, a samurai, a fire giant, a wooden dummy). Never use a project's private game title, character names, or plot in notes, file names, or commits.

## When to use / 何时使用

- The user says the effects look rough, timid, or "technically fine but not bold".
- You are remaking a specific move type (iaido / quick-draw slash, ground slam + fire, slime slap, or a similar family).
- You are about to invent VFX by stacking more particles instead of studying how published games and tutorials stage the same move.

Do **not** use this skill to copy another artist's frames or asset-pack art into a deliverable. Cases are for structure, timing, and shape language only.

## The six steps / 六步流程

Follow these in order. Helper files in this folder hold the tables and templates.

Before step 1, establish a **style brief**. Ask the user which visual style or existing game art should guide the cases when it has not already been chosen. Record the reference, native character/tile scale, camera angle, outline, palette, texture, motion, and any asset/license constraints. A named style (for example Ninja Adventure) guides selection and adaptation; it does not license copying another artist's frames. If the project already has an art direction, use it without asking again. The project's attack timing, hitbox, and accessibility rules override example numbers below.

### 1. Restate the general rules

Read [rules.md](rules.md). Before searching, write down (and obey) the shared rules:

- The main shape must read at the project's native scale. Size and brightness relative to the actor are style- and move-dependent; visual overflow must not imply extra damage. Telegraph pixels still **= the hitbox**.
- A **recognizable big shape** first (crescent, star spark, shock ring, spike burst, lobed splat). Particles are accents. Heavy moves stay hard-edged.
- **Uneven timing**: anticipation, fast release, readable contact, and slower recovery; choose frame counts from the move design and project's frame rate.
- **Hit frames**: use a peak with contrast appropriate to the move. If hitstop is used, freeze its clearest picture; full-white/invert frames are optional, high-tier accents.
- **Few ramps, high contrast** relative to the chosen style; do not impose a white core, smooth glow, or another library's palette on it.
- **Layer only what helps**: a main shape, selective accents, clear depth, and target response. Shake, hitstop, and flashes depend on the move's tier and project style.
- **Character acting is the skeleton**: readable wind-up, release, contact reaction, and recovery using the project's own actor frames. Check that the hand/weapon, effect origin, and target reaction agree in time and place.
- **Tier the feedback**: light/mid stays restrained; heavy boss moves can wash the screen and hitstop longer; a climax move may add a short screen flash and a longer freeze. Do not spend the climax vocabulary on every hit.

If the project already has a telegraph system, keep "warning pixels == hitbox" while VFX overflow is painted on a separate layer.

### 2. Collect 8–12 specific cases for this move type

Search for published, citable examples of **this** family (not generic juice). Prioritize cases compatible with the chosen camera, pixel scale, and style; use distant styles only for a specific transferable principle. Aim for a mix of games, animation, tutorials, and (optionally) asset-pack **descriptions** — not the art itself.

For each case record, in [case-template.md](case-template.md):

- Name
- A **real URL** you actually opened (never invent a link)
- Drawing notes: wind-up, impact frame, main shape, rings/cracks/debris, fire or goo language, smoke, ground marks, dissipate, timing, color

This folder already has worked case tables for three families:

- Quick-draw / iaido slash
- Ground slam + fire / shockwave
- Slime slap / body slam

Use them as a starting point, then add or replace cases if the move differs. If a page only describes mechanics, say so; do not invent frame-by-frame color ramps.

The [pixelfx catalog](https://github.com/patch-gg/pixelfx/blob/main/docs/CATALOG.md) can supply *candidate* examples. Render and inspect a candidate before describing its frames. Record what transfers to the selected project style and what must be rejected. See [pixelfx-method.md](pixelfx-method.md) for the optional reference and export workflow.

### 3. Write a timeline scheme and contrast the old version

Using [scheme-template.md](scheme-template.md), write a scheme **segmented by time** (wind-up, release, contact, dissipate, recovery) that the project's pixel pipeline can actually draw. Include caster and target acting, effect origin, layering, and the actual gameplay contact time.

Explicitly list what to **keep** from the current version and what is wrong (for example: a filled color bullseye instead of a hollow ring, a symmetric flower instead of irregular tongues, a spatial hash that chews blocky holes in the dissipate).

Keep the scheme in the project's agreed pixel rules: integer pixels, nearest-neighbour, dither instead of alpha unless the project says otherwise.

### 4. Wait for user approval before touching pictures

Show the scheme (and the case list if useful). **Do not generate or overwrite GIFs, sprites, or keyframes until the user confirms.** If they ask for research only, stop after step 3.

### 5. Render in parallel, one independent script per move, keep old versions

Once approved:

- New script per move (do not edit a shared renderer that other people are using in parallel).
- Write to a **new output folder**. Do not overwrite previous versions (`v1`, `v2`, …).
- Same canvas/pixel contract as the project (the examples here used 576×576, 30 fps, looping GIFs; these are not defaults).
- Telegraph pixels remain the hitbox. Overflow VFX is allowed, but must not look like an untelegraphed damaging region.
- Tier feedback correctly (a mid slime slap should not get a climax-only full-screen invert).
- Render a contact sheet of representative frames and a continuous playback preview. Review both at native game scale, with the actual actor and target when available. An isolated effect sheet cannot prove the whole attack reads well.

The example preview GIFs and reference scripts live in [examples/](examples/).

### 6. Check stills and motion, refine, ship with known limits

Save keyframes for at least **wind-up, release, contact/peak, dissipate**. Open them, play the full sequence, and score against [checklist.md](checklist.md), the style brief, and the cases — not only against "did the script run". Check the real engine scene when integrating game assets.

If the pictures or motion still miss the agreed brief, fix the largest observed problem and preview again. Stop when the agreed checks pass or state the remaining limitation. Then deliver:

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
| [pixelfx-method.md](pixelfx-method.md) | Optional pixelfx reference, preview, and export workflow |
| [examples/](examples/) | v4 preview GIFs and reference renderer scripts |

## Related

For designing the warning itself (shape, style, duration, cadence, budget), use [pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph).
