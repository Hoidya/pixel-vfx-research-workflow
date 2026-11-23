# General rules / 通用规则

Start with the selected project's style brief and attack rules. The values below describe the original examples; adapt them to the game's native scale, frame rate, and feedback tier. Use the resulting contract in the scheme (step 3) and visual check (step 6).

| # | Rule (EN) | 规则（中文） |
|---|---|---|
| 1 | Choose effect size relative to the actor and camera at native scale. Visual overflow may extend beyond the hitbox without implying extra damage. Telegraph pixels still **= the hitbox**. | 按角色和镜头的实际尺寸决定特效大小；特效可溢出判定，但不能暗示额外伤害；预警像素仍 = 判定。 |
| 2 | A **recognizable big shape** first (crescent slash, star spark, shock ring, spike burst, lobed splat). Particles only accent. Heavy moves stay sharp and hard-edged. | 先有可辨认的大形状（新月刀光、星形火花、冲击环、尖刺爆炸、瓣状溅拍），粒子只点缀；重招保持尖、硬边。 |
| 3 | Stage anticipation, fast release, readable contact, and slower recovery. The attack design sets exact frames and active time. | 安排蓄力、快速释放、清楚的命中和较慢的收招；具体帧数与有效判定时间由招式设计决定。 |
| 4 | Give the hit a clear peak. If hitstop is used, freeze that readable peak. Full-white or invert is optional and reserved for appropriate tiers. | 命中应有清晰峰值；若使用顿帧，就定在可读的峰值画面。全白或反色仅在合适的档位使用。 |
| 5 | Use a limited palette with contrast appropriate to the chosen style. A white core and 3–5 hard steps are possible treatments, not universal requirements. | 按选定画风使用有限且有对比的配色；白芯和 3–5 阶硬边是可选画法，不是通用硬规则。 |
| 6 | Layer only the cues the move needs: main shape, optional sparks/debris, depth, directional feedback, and target reaction. Avoid hiding the player or warning. | 只叠加招式需要的主形、火花/碎屑、前后层次、受力反馈与目标反应；不要遮住玩家或预警。 |
| 7 | Connect caster pose, hand/weapon, effect origin, hit moment, and target reaction. Use the project's actor art and animation language. | 让施法姿势、手/武器、特效起点、命中时刻和受击反应一致；沿用项目角色画风与动作语言。 |
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
