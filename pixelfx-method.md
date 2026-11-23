# Using pixelfx as a reference / 将 pixelfx 用作参考

[patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) is bundled in [vendor/pixelfx](vendor/pixelfx/README.md): 244 runnable effect cases, their editable source, core library, and preview/export tools. The useful loop is to find a relevant effect, render it, inspect the frames and acting, adapt or draft a project-specific version, then inspect it again. Read the bundled [catalog](vendor/pixelfx/docs/CATALOG.md), [authoring guide](vendor/pixelfx/docs/AUTHORING.md), [license](vendor/pixelfx/LICENSE), and [notices](vendor/pixelfx/NOTICE.md) before adapting code.

## Work with the bundled cases

Run these from `vendor/pixelfx` (Node 18+). No separate checkout or package installation is needed.

```sh
node tools/list.mjs slash
node tools/render.mjs melee/sword-slash --all
node tools/act.mjs melee/sword-slash
node tools/act.mjs melee/sword-slash --mp4 # optional; requires ffmpeg
node tools/check.mjs melee/sword-slash
node tools/render.mjs melee/sword-slash --sheet
```

Choose a candidate from `tools/list.mjs` or the catalog; the identifier above is an example. Open the effect contact sheet, consecutive act frames, and playable clip when available. Note the silhouette, moment of release, actor pose, target reaction, layer depth, and decay. Mark each note as directly visible or inferred. Compare at the target game's native scale, with its actual actor if possible. pixelfx's stock actor, palette ramps, additive light, screen shake, and default timings are reference choices, not instructions to copy.

To adapt a case, edit a copy or the selected `src/fx/<category>/<name>.js` and any necessary `src/core/` code; record which bundled case and upstream commit it came from. Keep prior previews before changing a shared case. For a new ID, use `node tools/new.mjs <category>/<name>`. Rerun render, act (when relevant), and check after code changes. Leave generated previews in ignored `records/`, and copy only deliberately selected final exports into a target game.

When a pixelfx effect is used as code rather than a visual reference, preserve its MIT and NOTICE attribution and the target project's original art direction. Its `--sheet` export produces transparent PNG frames and JSON for engine import; validate pivot, frame size, duration, loops, transparency, and nearest filtering in the target engine. For Godot, pre-exported frames are usually more appropriate than adding the JavaScript renderer at runtime.

## Preview loop for any renderer

1. Save the current version and its baseline preview.
2. Render representative stills **and** consecutive frames or a playable clip at the project's frame rate.
3. View at native scale on the actual background; check caster, effect, hit area, and target together.
4. Name the most important visible failure, revise it, and render again. Use deterministic seeds when random details would obstruct before/after comparison.
5. Run available technical checks for bounds, loop seams, missing frames, and nondeterministic output, then check the effect in the game. Passing a renderer check does not prove visual quality.

Do not paste a pixelfx sprite sheet or another game's frames into a deliverable merely because the reference looks good. The transferable method is choreography plus visual inspection; the final asset must fit the chosen style and license.
