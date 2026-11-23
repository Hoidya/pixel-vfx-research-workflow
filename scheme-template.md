# Scheme template / 画法方案模板

Copy this for each move after the case list is done. Write a scheme the selected project's pixel pipeline can actually draw. Then **wait for user approval** before rendering.

## Header

- Move (generic public name):
- Family (slash / slam+fire / slime / other):
- Camera (top-down 16px, side view, …):
- Tier (light / mid / heavy / climax):
- Current version being replaced (do not overwrite it):
- Pixel contract (size, fps, dither, warning == hitbox):
- Chosen style reference and approved palette/scale/outline:
- Actual gameplay contact time and active hit window:

## Keep / change

- Keep from the current version (poses, timing, telegraph, tier, …):
- Problems in the current version (compare to the cases):
- Shapes that must read at a glance (1–3):

## Timeline

Write in frames at the project's fps (examples used 30 fps).

### Telegraph / warning

- What is drawn, and only on hitbox pixels:
- What must *not* pre-fill the zone (no fire or goo inside the circle until the hit):

### Wind-up

- Duration:
- Body: readable preparation in the chosen actor style:
- Accents only (dust at the feet, a glint on a sheathed blade, …):
- Effect origin relative to hand, weapon, body, or ground:

### Release and contact

- Impact treatment (contrast / wash / invert / none — according to style and tier):
- Focal shape and its relation to the hitbox:
- Ring / crack / first debris:
- Main shape at release, before its clearest peak:

### Peak, then optional hitstop

- Duration of the freeze, if used (follow project combat timing):
- The clearest picture, with only the needed accents and target response:
- Do not keep animating a new color shell during the freeze:
- Target reaction at the same moment (if applicable):

### Dissipate (duration from the move and material)

Give each object its own life (do not punch holes in the whole image with one spatial hash):

- Main shape (cools, retracts, missing chunks, some elements die first):
- Ring (walks out 2–4 frames, breaks, disappears):
- Debris (gravity, bounce or shatter):
- Smoke or drips (slower than the fire or blade):
- Ground marks that remain (scorch, cracks, goo decal):

### Recovery

- Caster returns to a readable idle:
- Victim's recovery, if applicable:
- Ground marks may linger a few frames:

## Color (match the selected style)

- Brightest accent and its relation to the hitbox:
- Theme color:
- Dark outer / cooled remainder, if applicable:
- Treatments the selected style rules out:

## Explicit non-goals

- No climax flash on a mid-tier move:
- No copying case art, only structure:
- Other:

## Success check (short)

- [ ] Big shape reads in one frame
- [ ] Telegraph = hitbox; effect overflow does not suggest extra damage
- [ ] Timing is uneven
- [ ] Dissipate is per-object, not a hashed disk
- [ ] Tier matches the move
- [ ] Caster, effect origin, hit and target reaction agree in space and time
- [ ] Contact sheet and consecutive playback both read at native scale
