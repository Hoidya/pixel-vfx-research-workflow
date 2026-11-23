# pixel-vfx-research-workflow

**An Agent Skill for researching published attack VFX cases first, then redrawing 2D pixel skill effects.**

[中文说明](README.zh-CN.md)

Use this when a warning (telegraph) and hitbox are already fair, but the **hit animation** looks timid, technically correct but not bold, or unlike the move it is supposed to be. Choose the project's visual style, collect 8–12 **cited** cases for the move type, write a timeline scheme, **wait for approval before rendering**, then inspect both keyframes and continuous playback against the chosen style.

This workflow now includes the **244 editable effect cases** from [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) under [vendor/pixelfx/](vendor/pixelfx/README.md), with its core code and command-line preview/export tools. Search, render, inspect the full acted move, adapt the effect code to the chosen style, and check again. It remains an offline authoring tool, not a required game runtime dependency. See [pixelfx-method.md](pixelfx-method.md).

It is a companion to [pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph), which covers “warning == hitbox”. This skill covers **how the attack should look and feel** once that contract is in place.

Give the folder to your coding agent (Codex, Claude Code, Cursor, …) and ask it to follow [SKILL.md](SKILL.md).

## The six steps

1. **Confirm the style brief and restate the rules** — choose a visual reference when the project has not supplied one; record pixel scale, palette, outline, camera, and motion. Keep recognizable main shapes, readable timing, connected character acting, and move-appropriate feedback. See [rules.md](rules.md).
2. **Collect 8–12 specific cases** for this move type, each with a real source and a one-line drawing note. Search the 244 bundled pixelfx cases and independently published examples; choose for style fit, not merely by category. Start from [case-template.md](case-template.md).
3. **Write a timeline scheme** with [scheme-template.md](scheme-template.md), and contrast it with the previous version’s problems.
4. **Wait for the user to confirm** the scheme before touching pictures.
5. **Render or edit code** — adapt a bundled `src/fx/` effect or draw a new one, keep older previews and the project's pixel contract. Inspect a contact sheet and continuous motion with the caster and target, not just the isolated effect.
6. **Self-check** at native scale against the style brief, cited cases, and [checklist.md](checklist.md). Fix the largest visible issue and preview again; verify the integrated game scene when relevant. Ship with known limits stated honestly.

Do not copy another artist’s frames or asset-pack art into a deliverable. Cases are for structure, timing, and shape language only. Use generic public example names (a slime, a samurai, a fire giant, a wooden dummy).

## Try a bundled case

From `vendor/pixelfx` (Node 18+):

```sh
node tools/list.mjs slash
node tools/render.mjs melee/sword-slash --all
node tools/act.mjs melee/sword-slash
node tools/check.mjs melee/sword-slash
node tools/render.mjs melee/sword-slash --sheet
```

The editable source is `vendor/pixelfx/src/fx/melee/sword-slash.js`. Study the case, then adapt a copy or create a new effect for the chosen style. Run the previews and checker again after editing. The last command exports a transparent PNG sheet and JSON; validate them in the target engine before use. Generated `records/` are ignored. See [pixelfx-method.md](pixelfx-method.md) for the full workflow.

## Example previews

Original later-pass GIFs from this workflow. Characters are CC0 Ninja Adventure; the attack shapes are original.

| Slime slam (light / mid) | Iaido slash (climax) | Flame stomp (heavy) |
|---|---|---|
| ![slime slam](examples/01_slime_slam.gif) | ![iaido slash](examples/19_iaido_slash.gif) | ![flame stomp](examples/23_flame_stomp.gif) |

Specs used here: 576×576, 30 fps, looping. The red warning still matches the hitbox; overflow VFX may extend past it. Scripts and notes: [examples/](examples/).

## What’s in the repo

| Path | What |
|---|---|
| [SKILL.md](SKILL.md) | the agent workflow (frontmatter `name` / `description`, six steps, privacy rules) |
| [rules.md](rules.md) | general drawing rules (English + 中文) |
| [case-template.md](case-template.md) | blank case card + three filled type tables with real URLs |
| [scheme-template.md](scheme-template.md) | timeline scheme template |
| [checklist.md](checklist.md) | keyframe self-check list |
| [pixelfx-method.md](pixelfx-method.md) | bundled pixelfx search, editing, preview, and export workflow |
| [vendor/pixelfx/](vendor/pixelfx/README.md) | 244 editable cases and tools, pinned with upstream license and notices |
| [examples/](examples/) | preview GIFs and reference renderer scripts |

## Related: attack warnings

For designing the warning itself (shape, style, duration, cadence, budget) use **[Hoidya/pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph)**.

## License

Code and docs: [MIT](LICENSE). Character and grass tiles in the example GIFs: Ninja Adventure by Pixel-boy & AAA, CC0 — see [CREDITS.md](CREDITS.md).
