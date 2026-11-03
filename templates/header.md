# Awesome Short Drama Skills

**中文** · [English](README.en.md) · 网站：[shortdramaskills.com](https://shortdramaskills.com)

> AI 短剧 · 漫剧 Skill（技能包）精选：从小说改编、分集剧本到分镜、视频提示词和出片，装进千问、豆包、龙虾（OpenClaw）、WorkBuddy、Claude Code、Codex 等智能体就能用。
>
> A curated list of agent skills for AI short drama (micro drama / vertical drama) and AI manju: screenwriting, adaptation, storyboards, video prompts and production.

这里收录给 AI 智能体（agent）用的短剧 skill，覆盖小说改编、集纲、钩子和付费卡点、剧本审稿、分镜、角色资产，以及给 Seedance、MiniMax、可灵等视频模型的提示词。大多是标准 SKILL.md 格式，千问办公、豆包电脑版、龙虾（OpenClaw）、WorkBuddy、Kimi Code、Qwen Code、CodeBuddy、Trae、Qoder、Claude Code、Codex 等支持技能的智能体都能装，装法见[常见问题](#faq)。每个项目都经过人工核对，按类型、创作阶段和适配的视频模型整理。

收录 {{count}} 个 skill 项目 + {{platforms}} 个相关开源平台 · 元数据更新于 {{updated}}

## 写剧本装哪个

第一轮实测（2026-10-18）：10 个剧本 skill 和一个不装 skill 的对照组，各写 3 次同一道开放题，由两位 AI 评审（Opus 和 GPT）盲比。评审按交给 AI 从头拍成片来评，特效、群戏、场景多都不扣分。下面 4 个的剧本和人物大纲，两位评审都判三次全赢对照组：

| skill | 适合 | 要注意 |
|---|---|---|
| [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | 台词短，人物各有口气，情绪落在物件上 | 集尾钩子收得含蓄 |
| [Shanyin-ai/shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) | 对白短、有潜台词，情绪落在动作上 | 钩子偏收着，开场偏安静 |
| [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) | 情绪落在动作上，不靠心里话；配角有来路 | 集尾钩子有时不够猛 |
| [adoria111/emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills) | 台词克制，配角有动机也有转变 | 集尾钩子偏收着，付费卡点偏弱 |

[Hao0321/ai-short-drama](https://github.com/Hao0321/ai-short-drama) 的人物大纲也三次全赢，剧本不稳（Opus 一赢两平，GPT 两赢一输）。

这一轮的局限：
- 集尾钩子，Opus 认为常是对照组更强，GPT 看法相反。
- 另外 6 个 skill 的剧本，两位评审结论差得远。
- 只测了 claude-opus-5-5 一个模型。
- 每个 skill 的稿子都夹着编号和自检表，交给 AI 出片前要删掉。

全过程和逐个点评见[第一轮实测记录](https://shortdramaskills.com/evals/round-1/)。

## 定选题装哪个

第二轮实测（2026-10-20）：11 个网文和短剧的选题 skill 和一个不装 skill 的对照组，给同一个以后能写网文、也能拍短剧的爽文故事定选题，各定 3 次；所有参赛者两两盲比，按积分排名。评审看的是交给 AI 拍出来，观众会不会一直看下去。两位 AI 评审（Opus 和 GPT）排出的前三名是同样三个 skill，三个都三次全赢了对照组：

| skill | 名次（Opus / GPT） | 适合 | 要注意 |
|---|---|---|---|
| [Tomsawyerhu/Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill) | 1 / 2 | 少见的法律职业加身份翻转，一句话卖点就懂，爽点打在对手脸上 | 有一次是常见的扮猪吃虎；撑长篇有限 |
| [lingfengQAQ/webnovel-writer](https://github.com/lingfengQAQ/webnovel-writer) | 2 / 3 | 金手指配有代价的规则，主角的缺点和能力绑在一起 | 三次都是头顶能看见数字一类；中段容易重复 |
| [Hao0321/ai-short-drama](https://github.com/Hao0321/ai-short-drama) | 3 / 1 | 新意最强，异能都有规矩，钩子有画面 | 规矩把主角限得太被动，爽点来得慢 |

前两个收在[小说清单](https://github.com/UnderleveledBuilder/awesome-novel-skills)里。本清单的 [0xsline/short-drama](https://github.com/0xsline/short-drama) 排第 4 / 第 7，法条用得巧，一句话卖点偏长。

这一轮的局限：
- 不装 skill 的对照组，两位评审都排第 9，有 3 个 skill 排在它后面。
- 沙箱不能联网，要先扫榜的两个 skill 没拿到榜单，排在最后几名。
- 两位评审每对的结论，198 个里有 63 个不同，中间几名差得多。
- 只测了 claude-opus-5-5 一个模型。

全过程和逐个点评见[第二轮实测记录](https://shortdramaskills.com/evals/round-2/)。

## 写全剧骨架装哪个

第三轮实测（2026-10-31）：前两轮的 20 个 skill 和一个不装 skill 的对照组，给同一张选题卡写 60 集短剧的全剧骨架（整部剧怎么走，不写分集大纲和剧本），各写 3 次；所有参赛者两两盲比，按积分排名。评审只被告知目标：照着骨架写下去、全部由 AI 拍出来以后，观众更可能追到最后。两位 AI 评审（Opus 和 GPT）都排进前五、也都排在对照组前面的有 4 个：

| skill | 名次（Opus / GPT） | 适合 | 要注意 |
|---|---|---|---|
| [zhu5859243-free/hongguo-shortdrama-screenwriting](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting) | 1 / 4 | 每 3 到 5 集一个回合，写明证据、反制和回合尾，评审认为能直接拆给 AI 逐集写；三次出稿稳定 | 后段关键证据来得巧，推理有跳步 |
| [adoria111/emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills) | 2 / 2 | 先定一套硬规则：证据阶梯、每次赢都要付代价、观众和女主各在第几集知道什么 | 中段推进慢，具体回合要自己补 |
| [Tomsawyerhu/Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill) | 3 / 1 | 大卡点钉在具体集数，要求真换局，答案兑现得早 | 后段关键证据的来路要自己补 |
| [lixiaoxiao9888-create/short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) | 4 / 5 | 约 3 集一回合，付费卡点清楚，评审认为适合直接交给 AI 逐集扩写 | 前 21 集反复证明观众早知道的替身，凶手亮底早 |

两位评审都排在对照组后面的有 6 个，多是只写到段或幕的总纲，适合后面有编剧或 AI 逐集补细；本清单里的是 [catyiqian/qianqianwriting](https://github.com/catyiqian/qianqianwriting) 和 [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills)。

这一轮的局限：
- 两位评审分歧比第二轮大，630 对里 332 对结论一致；其余 10 个 skill 两位评审看法不一，比如 ai-short-drama，Opus 排第 13，GPT 排第 3。
- 只有一张选题卡（女频悬疑复仇），换个题材名次可能不同。
- 有 10 份超了 3000 字的上限，截断后再评；去掉它们参与的场次重算，两位评审各自的前五名不变。
- 只测了 claude-opus-5-5 一个模型。
- 只评骨架本身，没测照着它往下写出来的剧本好不好。

全过程和逐个点评见[第三轮实测记录](https://shortdramaskills.com/evals/round-3/)。

**图例**：🌟 精选 · 📝 提示词文件（非标准 skill）· 🧩 完整应用 · 🎬 适配的视频模型 · 💤 超过 180 天未更新 · 📦 已归档 · ⚠️ 仓库失效

**让 agent 帮你挑**：这份清单也是一个 skill。运行 `npx skills add UnderleveledBuilder/awesome-short-drama-skills` 装上 short-drama-skill-finder，再问你的 agent「我用 Codex 做小说改编短剧，装哪个 skill？」。

> [!NOTE]
> 「人工核对」指核对过仓库说明、目录结构和分类，不等于实测过效果，实测对比见 [evals/](evals/)。skill 可能附带脚本，安装前请先读一遍它的 SKILL.md。
