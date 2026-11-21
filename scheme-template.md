# Scheme template / 画法方案模板

Copy this for each move after the case list is done. Write a scheme a 16px (or project) pixel pipeline can actually draw. Then **wait for user approval** before rendering.

## Header

- Move (generic public name):
- Family (slash / slam+fire / slime / other):
- Camera (top-down 16px, side view, …):
- Tier (light / mid / heavy / climax):
- Current version being replaced (do not overwrite it):
- Pixel contract (size, fps, dither, warning == hitbox):

## Keep / change

- Keep from the current version (poses, timing, telegraph, tier, …):
- Problems in the current version (compare to the cases):
- Shapes that must read at a glance (1–3):

## Timeline

Write in frames at the project's fps (examples used 30 fps).

### Telegraph / warning

- What is drawn, and only on hitbox pixels:
- What must *not* pre-fill the zone (no fire or goo inside the circle until the hit):

### Wind-up (long)

- Duration:
- Body: opposite-direction squash/stretch, pause at the extreme:
- Accents only (dust at the feet, a glint on a sheathed blade, …):

### Action frame 0 (1 frame)

- Impact treatment (wash / invert / none — according to tier):
- Brightest solid core (must sit in the hitbox, irregular is better than a disk):
- Ring / crack / first debris:
- Main shape at "bud" length, not yet the peak:

### Peak, then hitstop (freeze  this picture)

- Duration of the freeze (light 1–3, heavy about 4–6, climax may be longer but stay readable in a roguelike):
- The most exaggerated picture: full main shape, ring at its clearest, sparks, speed lines, victim silhouette and knockback:
- Do not keep animating a new color shell during the freeze:

### Dissipate (8–15 frames, fast then slow)

Give each object its own life (do not punch holes in the whole image with one spatial hash):

- Main shape (cools, retracts, missing chunks, some elements die first):
- Ring (walks out 2–4 frames, breaks, disappears):
- Debris (gravity, bounce or shatter):
- Smoke or drips (slower than the fire or blade):
- Ground marks that remain (scorch, cracks, goo decal):

### Recovery

- Caster returns to a readable idle:
- Victim holds the knocked pose for a beat:
- Ground marks may linger a few frames:

## Color (3–5 hard steps)

- Core (white / palest, hitbox only):
- Theme (second layer):
- Dark outer / cooled remainder:
- What you will not do (smooth radial ramps, alpha fade, …):

## Explicit non-goals

- No climax flash on a mid-tier move:
- No copying case art, only structure:
- Other:

## Success check (short)

- [ ] Big shape reads in one frame
- [ ] Core = hitbox, telegraph = hitbox
- [ ] Timing is uneven
- [ ] Dissipate is per-object, not a hashed disk
- [ ] Tier matches the move
