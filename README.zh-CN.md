# pixel-vfx-research-workflow

**一套 Agent Skill：先研究已发表的出手特效案例，再重画 2D 像素技能动画。**

[English](README.md)

用在预警（telegraph）和判定已经公平，但**命中动画**看起来胆小、技术上正确但不像那一招的时候。流程是：先确认项目案例画风，为这一类招式搜集 8–12 个**可核对出处**的案例，写好按时间轴分段的方案，**等确认后再渲图**，然后同时检查关键帧和连续动作。

本技能结合了 [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) 的有效方法：检索候选特效、渲染预览、观察施法者与受击者的完整动作、修正最明显的问题并再次预览。pixelfx 可作为参考或离线精灵表来源，不是必装的游戏运行时依赖。见 [pixelfx-method.md](pixelfx-method.md)。

它是 [pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph) 的配套技能。预警仓库管「预警就是判定」；本仓库管判定已经正确之后，**这一招应该长什么样、节奏该怎么走**。

把整个文件夹交给编码助手（Codex、Claude Code、Cursor 等），让它按 [SKILL.md](SKILL.md) 做。

## 六步流程

1. **确认画风并写规则** — 尚未指定时先问用户案例画风，记录像素尺寸、配色、轮廓、视角和动作语言；保持可辨认的主形、清楚的节奏、角色与特效联动，以及符合招式档位的反馈。见 [rules.md](rules.md)。
2. **按招式类型搜 8–12 个具体案例**，每条都要有你真正打开过的 URL，并写一行画法特点。可从 [case-template.md](case-template.md) 里已填好的三类表开始（拔刀斩、砸地火焰、黏液拍击）。
3. **写时间轴分段的画法方案**（模板：[scheme-template.md](scheme-template.md)），并对照旧版指出问题。
4. **等用户确认方案后才动图**。
5. **作画** — 每招一个独立脚本，保留旧版与项目像素规范；同时预览关键帧和包含施法者、目标的连续动作。
6. **在原生尺寸下对照画风与案例自查**（清单：[checklist.md](checklist.md)）。修正最明显的问题后重新预览，适用时进入游戏场景检查；交付时写明已知不足。

不要把别人的帧、精灵或素材包画直接贴进成品。案例只用来学结构、节奏和形。示例角色用通用名（史莱姆、武士、火焰巨人、木头人）。

## 示例预览

本流程一轮迭代后的原创预览 GIF。角色来自 CC0 的 Ninja Adventure；攻击形是原创绘制。

| 黏液拍击（轻 / 中） | 拔刀斩（高潮档） | 烈焰践踏（重） |
|---|---|---|
| ![黏液拍击](examples/01_slime_slam.gif) | ![拔刀斩](examples/19_iaido_slash.gif) | ![烈焰践踏](examples/23_flame_stomp.gif) |

规格：576×576，30 fps，循环。红色预警仍与判定重合；特效可以画出判定外。脚本与说明见 [examples/](examples/)。

## 包里有什么

| 路径 | 内容 |
|---|---|
| [SKILL.md](SKILL.md) | 助手流程（frontmatter 的 `name` / `description`、六步、隐私规则） |
| [rules.md](rules.md) | 通用画法规则（中英对照） |
| [case-template.md](case-template.md) | 空白案例卡 + 三类已填表（含真实链接） |
| [scheme-template.md](scheme-template.md) | 时间轴方案模板 |
| [checklist.md](checklist.md) | 关键帧自查清单 |
| [pixelfx-method.md](pixelfx-method.md) | 可选的 pixelfx 参考、预览和导出方法 |
| [examples/](examples/) | 预览 GIF 与参考渲染脚本 |

## 相关：攻击预警

设计预警本身（形状、画法、时长、节奏、攻击名额）请用 **[Hoidya/pixel-attack-telegraph](https://github.com/Hoidya/pixel-attack-telegraph)**。

## 许可

代码和文档：[MIT](LICENSE)。示例 GIF 中的角色与草地：Ninja Adventure（作者 Pixel-boy 和 AAA），CC0，见 [CREDITS.md](CREDITS.md)。
