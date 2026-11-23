# Vendored pixelfx reference

This directory contains the 244 runnable effects listed by `node tools/list.mjs`, plus the core code and command-line tools needed to inspect, edit, check, and export them. It is based on [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) commit `5294518ce7c72e48b6100a744596e0acf57f2826` (2026-11-12). See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). The upstream gallery and its separately licensed Patch Pixel font are not included. This copy omits gallery build/serve commands and the unused `esbuild` dependency.

Run commands from this directory with Node 18 or newer:

```sh
node tools/list.mjs slash
node tools/render.mjs melee/sword-slash --all
node tools/act.mjs melee/sword-slash
node tools/check.mjs melee/sword-slash
node tools/render.mjs melee/sword-slash --sheet
```

Effect sources are in `src/fx/<category>/<name>.js`; shared code is in `src/core/`. You may modify an effect for a project's own style, then rerender and check it. New effects can start with `node tools/new.mjs <category>/<name>`. Generated previews go in ignored `records/`; exported sheets remain local until deliberately copied into a target project. `--mp4` requires ffmpeg. Read [docs/CATALOG.md](docs/CATALOG.md) to browse all 244 cases and [docs/AUTHORING.md](docs/AUTHORING.md) for the effect API.

Keep edits to this vendored copy attributable. If updating from upstream, compare the pinned commit and update this README, LICENSE, NOTICE, catalog, sources, and tools together. The examples are options to study or adapt; the target game's art direction, licenses, hitbox, and timing remain authoritative.
