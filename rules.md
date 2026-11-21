# General rules / 通用规则

These rules apply to every move before you search for type-specific cases.
Use them as a contract in the scheme (step 3) and the keyframe check (step 6).

| # | Rule (EN) | 规则（中文） |
|---|---|---|
| 1 | Attack FX about **3–5×** the character. They may overflow the hitbox, but the **brightest solid core = the hitbox**. Telegraph pixels still **= the hitbox**. | 出手特效约角色的 3–5 倍，可溢出判定，但最亮实心核 = 判定；预警像素仍 = 判定。 |
| 2 | A **recognizable big shape** first (crescent slash, star spark, shock ring, spike burst, lobed splat). Particles only accent. Heavy moves stay sharp and hard-edged. | 先有可辨认的大形状（新月刀光、星形火花、冲击环、尖刺爆炸、瓣状溅拍），粒子只点缀；重招保持尖、硬边。 |
| 3 | **Uneven timing**: long wind-up, **1–3 frames** of action, **8–15 frames** of dissipate with missing chunks / cooling / shattering, in proportion. | 节奏不均：长蓄力，出手 1–3 帧，消散 8–15 帧，按比例缺块、变冷、变碎。 |
| 4 | **Hit frames**: 1–2 frames of full-white, invert, or high-contrast impact. **Hitstop freezes the most exaggerated picture.** | 命中帧 1–2 帧全白 / 反色 / 高对比冲击；顿帧冻住最夸张的那一画。 |
| 5 | **Few ramps, high contrast**: white core → bright → dark outer, 3–5 hard steps. The theme color is the second layer, not a smooth gradient. | 少色阶、高对比：白芯 → 亮色 → 深外圈，3–5 阶硬边；主题色是第二层，不要光滑渐变。 |
| 6 | **Layer stack**: impact frame + main shape + star spark + speed lines + shake along the force (fast decay) + hitstop + victim silhouette and knockback. | 多层叠加：冲击帧 + 主形 + 星形火花 + 速度线 + 顺受力方向、快速衰减的震屏 + 顿帧 + 受击者换剪影并击退。 |
| 7 | **Character motion is the skeleton**: a clear opposite-direction squash/stretch on the wind-up, stretch/overshoot on the attack, victim flash and pose change. | 角色动作是骨架：蓄力明显反向后拉或压扁拉伸，出手拉伸过冲，受击者闪白并换姿势。 |
| 8 | **Tier the feedback**. Light/mid = restrained (short hitstop, little or no screen flash). Heavy/boss = stronger wash, longer freeze, bigger shake. Climax = optional short screen flash and a longer hitstop. Do not spend climax vocabulary on every hit. | 分档：轻/中档反馈收敛；重档 / Boss 招更强洗亮、更长顿帧、更强震屏；最高档才可短屏闪和长顿帧。不要每下都用最高档。 |

## Pixel contract (examples in this folder)

Unless the project says otherwise:

- Integer pixels, nearest-neighbour scale, dither or hard holes instead of semi-transparent fade.
- Warning (telegraph) pixels remain an exact match for the hitbox.
- Overflow VFX is a separate layer and must not be treated as extra damage area.
- Do not overwrite older preview versions; write `vN+1` (or a new folder) instead.

## What "bold" is not

- Filling the telegraph with a smooth color pie is correct, not bold.
- More particles will not fix a missing silhouette.
- A long smear held through hitstop looks like a sticker, not a hit.
- A radial color bullseye is not the same thing as a hollow shock ring.
