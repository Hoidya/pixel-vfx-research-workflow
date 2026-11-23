# Using pixelfx as a reference / 将 pixelfx 用作参考

[patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) is an optional MIT-licensed library and authoring reference, not a required dependency of this skill. Its most useful contribution here is a loop: find a relevant effect, render it, inspect the frames and acting, draft a project-specific version, and repeat after seeing the result. Read the upstream [README](https://github.com/patch-gg/pixelfx/blob/main/README.md), [authoring guide](https://github.com/patch-gg/pixelfx/blob/main/docs/AUTHORING.md), and [NOTICE](https://github.com/patch-gg/pixelfx/blob/main/NOTICE.md) when adapting code.

## Optional local study

Run these in a separate pixelfx checkout (Node 18+). Do not install its runtime into the target game just to study an effect.

```sh
node tools/list.mjs slash
node tools/render.mjs melee/sword-slash --all
node tools/act.mjs melee/sword-slash
node tools/act.mjs melee/sword-slash --mp4 # optional; requires ffmpeg
node tools/check.mjs melee/sword-slash
```

Choose a candidate from `tools/list.mjs` or the catalog; the identifier above is an example. Open the effect contact sheet, consecutive act frames, and playable clip when available. Note the silhouette, moment of release, actor pose, target reaction, layer depth, and decay. Mark each note as directly visible or inferred. Compare at the target game's native scale, with its actual actor if possible. pixelfx's stock actor, palette ramps, additive light, screen shake, and default timings are reference choices, not instructions to copy.

When a pixelfx effect is used as code rather than a visual reference, check its license and NOTICE, credit adapted source, and preserve the target project's original art direction. Its `--sheet` export can produce transparent PNG frames and JSON for engine import; validate pivot, frame size, duration, loops, transparency, and nearest filtering in the target engine. For Godot, pre-exported frames are usually more appropriate than adding the JavaScript renderer at runtime.

## Preview loop for any renderer

1. Save the current version and its baseline preview.
2. Render representative stills **and** consecutive frames or a playable clip at the project's frame rate.
3. View at native scale on the actual background; check caster, effect, hit area, and target together.
4. Name the most important visible failure, revise it, and render again. Use deterministic seeds when random details would obstruct before/after comparison.
5. Run available technical checks for bounds, loop seams, missing frames, and nondeterministic output, then check the effect in the game. Passing a renderer check does not prove visual quality.

Do not paste a pixelfx sprite sheet or another game's frames into a deliverable merely because the reference looks good. The transferable method is choreography plus visual inspection; the final asset must fit the chosen style and license.
