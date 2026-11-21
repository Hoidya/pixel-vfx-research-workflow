# Example previews

Three original preview GIFs from a later pass of this workflow, plus the reference renderer scripts that produced them.

| File | Move (generic name) | Tier |
|---|---|---|
| [01_slime_slam.gif](01_slime_slam.gif) | Slime slam | Light / mid |
| [19_iaido_slash.gif](19_iaido_slash.gif) | Iaido slash | Climax |
| [23_flame_stomp.gif](23_flame_stomp.gif) | Flame stomp | Heavy |

Specs used here: 576×576, 30 fps, looping, integer pixels, nearest-neighbour scale, dither instead of alpha. The red warning still matches the hitbox; the brightest solid core of the effect stays in that hitbox; overflow VFX may extend past it.

Character and grass tiles are from **Ninja Adventure** by Pixel-boy & AAA (CC0). The attack shapes themselves are original drawings produced by the scripts, not copied from the cited packs or games. See [CREDITS.md](../CREDITS.md).

## Scripts

`gif_v4_slime.py`, `gif_v4_iaido.py`, and `gif_v4_stomp.py` are **reference renderers**: one independent script per move, so three people can work in parallel without editing a shared file. They are not a drop-in for this repository's tiny CC0 tile set. To run them you need:

- The full Ninja Adventure actor sheets (slime, samurai, fire giant, ninja) and a 12px pixel font
- A telegraph helper compatible with the library used by this repository (`tools/telegraph_lib.py`)
- Environment variables, or a short edit at the top of each script:

```text
TELEGRAPH_LIB              directory that contains telegraph_lib.py
NINJA_ADVENTURE_CONTENT    folder with character/ and map/ tiles
NINJA_ADVENTURE_ACTOR      folder with Actor/ character and monster sheets
VFX_PREVIEW_ROOT           output root (GIFs are written under out/)
VFX_FONT                   path to a 12px pixel font
```

Do not paste other people's VFX sheets into these scripts or into new GIFs.

Older preview versions, if you keep any, should stay on disk. These files are a later generation only.
