<!-- 本文件由 scripts/build.py 生成，请勿手改。要改内容请编辑 data/ 或 templates/ 后重新生成。 -->

# Awesome Short Drama Skills

**中文** · [English](README.en.md) · 网站：[shortdramaskills.com](https://shortdramaskills.com)

> AI 短剧 · 漫剧 Skill（技能包）精选：从小说改编、分集剧本到分镜、视频提示词和出片，装进千问、豆包、龙虾（OpenClaw）、WorkBuddy、Claude Code、Codex 等智能体就能用。
>
> A curated list of agent skills for AI short drama (micro drama / vertical drama) and AI manju: screenwriting, adaptation, storyboards, video prompts and production.

这里收录给 AI 智能体（agent）用的短剧 skill，覆盖小说改编、集纲、钩子和付费卡点、剧本审稿、分镜、角色资产，以及给 Seedance、MiniMax、可灵等视频模型的提示词。大多是标准 SKILL.md 格式，千问办公、豆包电脑版、龙虾（OpenClaw）、WorkBuddy、Kimi Code、Qwen Code、CodeBuddy、Trae、Qoder、Claude Code、Codex 等支持技能的智能体都能装，装法见[常见问题](#faq)。每个项目都经过人工核对，按类型、创作阶段和适配的视频模型整理。

收录 82 个 skill 项目 + 14 个相关开源平台 · 元数据更新于 2026-10-17

**图例**：🌟 精选 · 📝 提示词文件（非标准 skill）· 🧩 完整应用 · 🎬 适配的视频模型 · 💤 超过 180 天未更新 · 📦 已归档 · ⚠️ 仓库失效

**让 agent 帮你挑**：这份清单也是一个 skill。运行 `npx skills add UnderleveledBuilder/awesome-short-drama-skills` 装上 short-drama-skill-finder，再问你的 agent「我用 Codex 做小说改编短剧，装哪个 skill？」。

> [!NOTE]
> 「人工核对」指核对过仓库说明、目录结构和分类，不等于实测过效果，实测对比见 [evals/](evals/)。skill 可能附带脚本，安装前请先读一遍它的 SKILL.md。

## 目录

- [本周新增](#new)（24）
- [推荐组合](#packs)
- [按类型](#by-group)
  - [全流程：剧本 → 分镜 → 成片](#group-pipeline)（23）
  - [编剧：剧本 · 改编 · 审稿](#group-writing)（9）
  - [分镜 · 视觉资产 · 视频提示词](#group-visual)（39）
  - [上游：IP 评估与故事拆解](#group-source)（3）
  - [编剧基本功](#group-craft)（5）
  - [配套：去 AI 味](#group-companion)（3）
  - [相关开源平台（完整应用，非 skill）](#group-platform)（14）
- [按创作阶段查找](#by-stage)
- [按视频模型查找](#by-model)
- [常见问题](#faq)
- [相关资源](#resources)
- [收录徽章](#badge)

<a id="new"></a>
## 本周新增

近 7 天新收录 24 个：

- [shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) ★1.3k：山音超级编剧大师：概念超短片、叙事短片、长片、多集剧集四种格式的人物、大纲、场景拆解和完整剧本
- [higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) ★750：Higgsfield 平台提示词：MCSLA 公式、Seedance 2.5 多参考导演、表演指导、Soul ID 角色一致性、镜头清单与失败诊断
- [zy-cinematic-realism](https://github.com/popopo-99/zy-cinematic-realism) ★590：造梦师：把剧本、故事或场景想法开发成有动机的叙事关键帧，编译成各生图模型的原生提示词，支持连续组图与结果修复
- [shanyin-director-master](https://github.com/Shanyin-ai/shanyin-director-master) ★586：山音超级导演大师：剧本 → 导演定调、节奏规划、剧本微调、分镜拆解，输出九列分镜表（xlsx），内置类型片导演风格模板
- [awesome-seedance-2.5-prompts-skills](https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills) ★239：Seedance 2.5 提示词库 + skill：按 T2V/R2V/I2V 选路线、Seedream 故事板、多参考与镜头连续性设计
- [ComfyUI-Agent-Kit](https://github.com/SlavaSexton/ComfyUI-Agent-Kit) ★106：驱动本地 ComfyUI 出图出视频，附 Seedance、MiniMax H3 视频提示词 skill：多镜头分镜、参考素材标注、翻车排查
- [fight-prompt-director](https://github.com/irenerachel/fight-prompt-director) ★58：AI 打戏提示词：角色差异化动作、交锋因果链、跨镜连续性，出高强度/慢节奏/中间型三版，适配 Seedance 与 H3
- [ai-short-drama](https://github.com/oiuv/ai-short-drama) ★44：雪风爽剧：一句话补全创作需求，按爽点模型写分集剧本并同步角色/场景/道具档案，再拆镜写 Seedance 2.0 提示词
- [seedance-skill](https://github.com/alchaincyf/seedance-skill) ★40：白模驱动的 Seedance 工作台：用 scene.json 渲染白模参考视频并做几何体检，可从照片反解白模，按白模几何写提示词
- [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) ★39：Acheng 导演引擎：剧本、分镜、文戏五轨表演、打戏因果链、特效与资产，编译成 MiniMax H3 / Seedance 提示词
- [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) ★35：Vibe Video：在 AutoDL 上跑开源 MiniMax H3 出片，短剧模板串起 Brief、分集概要、剧本台词、美术和视频，含 H3 提示词写法
- [storyboard-director](https://github.com/kevinchin12/storyboard-director) ★35：故事 → 分镜脚本，子代理并行生成逐镜线稿，HTML 审片板返修指定镜头，确认后汇总成按镜头排序的视频提示词
- [spark-video](https://github.com/JohnKeating1997/spark-video) ★34：一句梗概 → 剧本、分镜、角色/场景/道具一致性、渲染、逐镜 AI 质检到成片 mp4，每阶段设确认关卡
- [5min-drama-contest](https://github.com/SoloEnt-AI/5min-drama-contest) ★26：五分钟短剧剧本：一步一问锁定赛道、立意、结构原型和前 30 秒开场，四幕卡点大纲 → 正式剧本 → 分镜脚本
- [fight-scene-director](https://github.com/ZzzAloong/fight-scene-director) ★22：多画风打戏设计：动作编排、空间调度、镜头与特效规则，可先出站位图/轨迹图生图词，再按轨迹写视频提示词
- [ai-film-skills](https://github.com/nigo-studio/ai-film-skills) ★19：从 AI 动作片《CROW LINE》流程拆出的 skill：Seedance 2.5 参考生视频提示词导演，三联角色设定图保持跨镜一致
- [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) ★17：AI 漫剧工坊：一句创意到成片的八步流程，任务卡剧本、角色参考图库、风格锚、分镜、图/视频提示词、配音字幕与合成终检
- [hardcore-director](https://github.com/jlam00-dev/hardcore-director) ★17：硬核导演：影视与 AI 视频总控，按阶段路由编剧/短剧、角色场景、分镜、Seedance 2.5/Wan 3.0/H3 提示词、声音与剪辑模块
- [seedance-2-5-prompting](https://github.com/babicat4242-svg/seedance-2-5-prompting) ★16：Seedance 2.5 提示词：参考素材角色绑定、30 种运镜定义与冲突规则、R2V/白模、局部编辑与延长、多轮修改流程
- [Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director) ★14：MiniMax H3 漫剧导演：网文改分镜、核心/龙套资产分级、文戏长镜与武戏快切、动作连续性锁定、尾帧接力，一次出整集提示词
- [xiaxia](https://github.com/luanyi824-hash/xiaxia) ★14：夏夏：把确认剧本转成带时长预算、机位焦段、真实光源、调度与动作因果的导演分镜，可编译为 Seedance 2.5 任务
- [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) ★13：影视部门式 skill 包：编剧、导演、角色、美术、摄影、分镜、镜头表、提示词、声音、剪辑，由总监 skill 调度和质检
- [ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills) ★13：AI 漫剧导演：剧本 + 已有资产 → Seedance 2.0/2.5 分镜组提示词，含人物表演、导演摄影、场景资产、站位图、连续性与声音
- [chinese-epic-scene-director](https://github.com/zhouwei713/chinese-epic-scene-director) ★13：中国式宏大场景：把一句设定扩写成仙侠/神话短片故事，建连续性台账，按镜头成对输出图片和视频提示词

<a id="packs"></a>
## 推荐组合

> 初版组合依据仓库说明搭配，尚未实测，实测后会更新。

- **小说改编短剧**：手上有一本小说，要出剧本和分镜
  - 组合：[narrative-to-screen-reader](https://github.com/zhlmi/narrative-to-screen-reader) → [shuohao-skills](https://github.com/eternityspring/shuohao-skills) → [screenwriter-skill](https://github.com/Vi7QY/screenwriter-skill)
  - 思路：narrative-to-screen-reader 先判断故事能不能拍、怎么改，shuohao-skills 从拆角色跑到分镜，screenwriter-skill 最后按 38 条规则审稿
- **原创红果/抖音爆款剧本**：从一句创意写出能上线的分集剧本
  - 组合：[short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) → [qianqianwriting](https://github.com/catyiqian/qianqianwriting) → [screenwriter-skill](https://github.com/Vi7QY/screenwriter-skill)
  - 思路：short-drama-factory 管集数、付费卡点和钩子，qianqianwriting 补救猫咪节拍和爆款拆解，screenwriter-skill 审稿
- **用 Seedance 出片**：剧本已经有了，要变成 Seedance 能用的分镜和提示词
  - 组合：[Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator) → [lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit)
  - 思路：Seedance2-Storyboard-Generator 把剧本拆成多集分镜和提示词，lanshu 工具包提供 Seedance 提示词调试和模型选择
- **漫剧长线连载**：做几十集的漫剧，人设和伏笔不能崩
  - 组合：[ManjuForge](https://github.com/mengxiujie/ManjuForge) → [jingju-skills](https://github.com/jxshow/jingju-skills)
  - 思路：ManjuForge 用记忆文件和一致性检查管连载状态，jingju-skills 负责人设一致性提示词和 ComfyUI 批量出图

<a id="by-group"></a>
## 按类型

<a id="group-pipeline"></a>
### 全流程：剧本 → 分镜 → 成片

从一句话或一本小说一路跑到分镜、视频提示词甚至成片的完整工作流。

- 🌟 **[shuohao-skills](https://github.com/eternityspring/shuohao-skills)** · ★ 4.7k<br>短剧制作 skill 集：拆角色、改编大纲、场景与道具美术设定、剧本、分镜<br><sub>阶段：改编 · 人物 · 集纲 · 剧本 · 分镜</sub><br><sub>更新于 2026-10-15 · 多语言 · 7 个 skill · Apache-2.0</sub>

- 🌟 **[drama-skills](https://github.com/zenstory-ai/drama-skills)** · ★ 3k<br>短剧/漫剧全链路：拆小说、开发、剧本、角色资产、分镜、图/视频提示词、审查<br><sub>阶段：改编 · 人物 · 剧本 · 审稿 · 分镜 · 提示词</sub><br><sub>更新于 2026-10-15 · 中文 · 12 个 skill · MIT</sub>

- 🌟 **[manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill)** · ★ 1.4k<br>漫剧老李：AIGC 漫剧导演全流程，门控剧本、资产锁定、分镜、投喂提示词、规则化质检<br><sub>阶段：剧本 · 审稿 · 分镜 · 提示词</sub><br><sub>更新于 2026-10-16 · 中文 · 13 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦 · MiniMax H3</sub><br><sub>💡 作者标注为测试版，整合了其他开源内容</sub>

- **[OnlyShot](https://github.com/A-cat-with-carrots/OnlyShot)** · ★ 323<br>神仙鱼短剧流水线：一句话 → 剧本、分镜、分镜图、视频、剪辑五步，沉淀 17 种失败模式<br><sub>阶段：剧本 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-07-07 · 中文 · MIT</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[Micro-Drama-Skills](https://github.com/zhaihao118/Micro-Drama-Skills)** · ★ 322<br>短剧全流程自动化：剧本、角色设计、分镜、出图出视频与提交<br><sub>阶段：剧本 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-02-23 💤 · 中文 · 4 个 skill</sub>

- **[short-drama-production](https://github.com/suihe1/short-drama-production)** · ★ 183<br>短剧生产总控：小说大纲/人物/剧本、导演分镜、提示词、声音资产、粗剪与 QC（默认 16:9）<br><sub>阶段：改编 · 集纲 · 剧本 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-09-16 · 中文 · 8 个 skill · Apache-2.0</sub><br><sub>🎬 MiniMax H3</sub><br><sub>💡 5 个 novel-* skill 与 shuohao-skills 的文件结构和示例相同，仓库未注明来源</sub>

- **[workrally](https://github.com/Tencent/workrally)** · ★ 173<br>腾讯开源：面向 AI Agent 的 AIGC 漫剧视频创作全流程工具集<br><sub>阶段：剧本 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-09-29 · 中文</sub>

- **[infinite-creation](https://github.com/SwotAtmk/infinite-creation)** · ★ 76<br>提交小说或剧本，用本地 ComfyUI + MiniMax H3 + Agent 自动连续生产视频，不限时长<br><sub>阶段：改编 · 提示词 · 出片</sub><br><sub>更新于 2026-10-16 · 中文 · 30 个 skill · MIT</sub><br><sub>🎬 ComfyUI（本地） · MiniMax H3</sub><br><sub>💡 28 个 skill 里也有广告、宣传片类</sub>

- **[ai-film-skills](https://github.com/62656456/ai-film-skills)** · ★ 72<br>21 个独立模块：短剧制作、分镜导演、角色资产、国风/科幻等视觉风格导演，附 3D 预演<br><sub>阶段：人物 · 分镜 · 出片</sub><br><sub>更新于 2026-10-15 · 多语言 · 21 个 skill · Apache-2.0</sub><br><sub>💡 含少量市场分析等非影视模块</sub>

- **[ai-short-drama](https://github.com/Hao0321/ai-short-drama)** · ★ 71<br>把「重生、逆袭、隐藏大佬」等题材编译成有爽点和追更钩子的连载：题材调研、故事架构、镜头时间线、连续性校验<br><sub>阶段：选题 · 集纲 · 剧本 · 审稿 · 分镜</sub><br><sub>更新于 2026-08-13 · 中文 · MIT</sub><br><sub>💡 README 为繁体中文</sub>

- **[novel-to-manju](https://github.com/senmanx/novel-to-manju)** · ★ 59<br>小说转漫剧全流程：爆款改文 → 剧本 → 人物/场景三视图 → 分镜 → 视频提示词<br><sub>阶段：改编 · 人物 · 剧本 · 分镜 · 提示词</sub><br><sub>更新于 2026-08-17 · 中文</sub><br><sub>🎬 MiniMax H3</sub>

- **[ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill)** · ★ 52<br>Dramake：文字转 AI 短剧，串起剧本、分镜、配音、剪辑与质检，适配抖音/红果和横竖屏，自带 evals<br><sub>阶段：改编 · 剧本 · 审稿 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-08-29 · 中文 · MIT</sub><br><sub>🎬 通义万相 Wan · Seedance / 即梦 · MiniMax H3</sub>

- **[ai-short-drama](https://github.com/oiuv/ai-short-drama)** · ★ 44<br>雪风爽剧：一句话补全创作需求，按爽点模型写分集剧本并同步角色/场景/道具档案，再拆镜写 Seedance 2.0 提示词<br><sub>阶段：人物 · 集纲 · 剧本 · 分镜 · 提示词</sub><br><sub>更新于 2026-08-22 · 中文 · 5 个 skill</sub><br><sub>🎬 Seedance / 即梦</sub><br><sub>💡 随「雪风AI短剧工坊」应用发布，README 未写 agent 安装步骤；仓库无许可证</sub>

- **[muse-video-skill](https://github.com/LuoJiangYong/muse-video-skill)** · ★ 44<br>虚拟剧组：导演/编剧/摄影/美术/特效/声音六角色协作，创意 → 剧本、分镜、美术、提示词，38 个案例技法库<br><sub>阶段：剧本 · 审稿 · 分镜 · 提示词</sub><br><sub>更新于 2026-09-30 · 多语言 · MIT</sub>

- **[jingju-skills](https://github.com/jxshow/jingju-skills)** · ★ 37<br>鲸剧：AI 漫剧全流程，大纲、人设一致性、分集剧本、分镜、图/视频提示词、ComfyUI 批量出图<br><sub>阶段：人物 · 集纲 · 剧本 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-06-09 · 中文</sub><br><sub>🎬 ComfyUI（本地）</sub>

- **[open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill)** · ★ 35<br>Vibe Video：在 AutoDL 上跑开源 MiniMax H3 出片，短剧模板串起 Brief、分集概要、剧本台词、美术和视频，含 H3 提示词写法<br><sub>阶段：人物 · 集纲 · 剧本 · 提示词 · 出片</sub><br><sub>更新于 2026-09-11 · 多语言 · 9 个 skill</sub><br><sub>🎬 MiniMax H3 · ComfyUI（本地）</sub><br><sub>💡 依赖 AutoDL GPU 实例（按时计费）；短剧模板只管流程关卡，叙事部分较薄</sub>

- **[spark-video](https://github.com/JohnKeating1997/spark-video)** · ★ 34<br>一句梗概 → 剧本、分镜、角色/场景/道具一致性、渲染、逐镜 AI 质检到成片 mp4，每阶段设确认关卡<br><sub>阶段：人物 · 剧本 · 审稿 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-09-01 · 英文 · 7 个 skill</sub><br><sub>🎬 通义万相 Wan · Seedance / 即梦</sub><br><sub>💡 依赖阿里云百炼等付费视频 API；默认短剧模式，也有广告和科普示例</sub>

- **[novel-to-ai-short-drama-skill](https://github.com/muxia0396/novel-to-ai-short-drama-skill)** · ★ 33<br>从导演视角把小说改编成 AI 短剧：分镜、运镜、表演调度与时长<br><sub>阶段：改编 · 分镜</sub><br><sub>更新于 2026-09-04 · 中文 · MIT</sub>

- **[short-drama-director](https://github.com/UncleWang2088/short-drama-director)** · ★ 23<br>短剧导演专家包：剧本创作、平台标准审稿、镜头级分镜与表演指导，输出 Seedance 提示词<br><sub>阶段：剧本 · 审稿 · 分镜 · 提示词</sub><br><sub>更新于 2026-10-13 · 中文 · 9 个 skill</sub><br><sub>🎬 Seedance / 即梦</sub><br><sub>💡 整合了 0xsline/short-drama、Vi7QY/screenwriter-skill 等项目的修改版（README 已注明）；仓库无许可证</sub>

- **[ManjuForge](https://github.com/mengxiujie/ManjuForge)** · ★ 21<br>漫剧/短剧连载引擎：一句话 → 剧本、分镜、配音、提示词，7 个记忆文件 + 22 项一致性检查防人设崩坏<br><sub>阶段：集纲 · 剧本 · 审稿 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-10-13 · 中文 · MIT-0</sub>

- **[ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama)** · ★ 17<br>AI 漫剧工坊：一句创意到成片的八步流程，任务卡剧本、角色参考图库、风格锚、分镜、图/视频提示词、配音字幕与合成终检<br><sub>阶段：人物 · 集纲 · 剧本 · 审稿 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-09-17 · 多语言 · 2 个 skill · MIT</sub>

- **[hardcore-director](https://github.com/jlam00-dev/hardcore-director)** · ★ 17<br>硬核导演：影视与 AI 视频总控，按阶段路由编剧/短剧、角色场景、分镜、Seedance 2.5/Wan 3.0/H3 提示词、声音与剪辑模块<br><sub>阶段：人物 · 集纲 · 剧本 · 审稿 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-10-01 · 中文 · MIT</sub><br><sub>🎬 Seedance / 即梦 · 通义万相 Wan · MiniMax H3 · 可灵 Kling</sub><br><sub>💡 整合包：大部分模块是第三方 skill 快照（已注明来源），也覆盖广告和宣传片</sub>

- **[vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator)** · ★ 13<br>影视部门式 skill 包：编剧、导演、角色、美术、摄影、分镜、镜头表、提示词、声音、剪辑，由总监 skill 调度和质检<br><sub>阶段：人物 · 剧本 · 审稿 · 分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-10-07 · 英文 · 11 个 skill · MIT</sub><br><sub>🎬 Nano Banana · Sora · Veo · 可灵 Kling</sub><br><sub>💡 偏电影，不专做短剧</sub>


<details><summary>安装命令</summary>

```bash
# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准
# shuohao-skills
npx skills add eternityspring/shuohao-skills
# drama-skills
npx skills add zenstory-ai/drama-skills
# manju-laoli-skill
npx skills add lixiaoxiao9888-create/manju-laoli-skill
# OnlyShot
npx skills add A-cat-with-carrots/OnlyShot
# Micro-Drama-Skills
npx skills add zhaihao118/Micro-Drama-Skills
# short-drama-production
npx skills add suihe1/short-drama-production
# workrally
npx skills add Tencent/workrally
# infinite-creation
npx skills add SwotAtmk/infinite-creation
# ai-film-skills
npx skills add 62656456/ai-film-skills
# ai-short-drama
npx skills add Hao0321/ai-short-drama
# novel-to-manju
npx skills add senmanx/novel-to-manju
# ai-short-drama-skill
npx skills add xixihhhh/ai-short-drama-skill
# ai-short-drama
npx skills add oiuv/ai-short-drama
# muse-video-skill
npx skills add LuoJiangYong/muse-video-skill
# jingju-skills
npx skills add jxshow/jingju-skills
# open-source-video-gen-skill
npx skills add mini-yifan/open-source-video-gen-skill
# spark-video
npx skills add JohnKeating1997/spark-video
# novel-to-ai-short-drama-skill
npx skills add muxia0396/novel-to-ai-short-drama-skill
# short-drama-director
npx skills add UncleWang2088/short-drama-director
# ManjuForge
npx skills add mengxiujie/ManjuForge
# ai-manga-drama
npx skills add liuxiao20051106-prog/ai-manga-drama
# hardcore-director
npx skills add jlam00-dev/hardcore-director
# vision_art_creator
npx skills add ilkaydemiralay/vision_art_creator
```

</details>

<a id="group-writing"></a>
### 编剧：剧本 · 改编 · 审稿

专注剧本本身：集纲、钩子、付费卡点、对白、审稿。

- **[short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory)** · ★ 389<br>抖音/红果短剧工业化编剧：一句创意或一部网文 → 60–100 集带付费卡点的剧本，配钩子、断章、反转公式和机检规则<br><sub>阶段：改编 · 集纲 · 剧本 · 审稿</sub><br><sub>更新于 2026-10-16 · 中文 · MIT</sub>

- **[screenwriter-skill](https://github.com/Vi7QY/screenwriter-skill)** · ★ 79<br>短剧/漫剧剧本审稿：红果 Top100 操盘经验蒸馏的 38 条规则<br><sub>阶段：审稿</sub><br><sub>更新于 2026-04-12 💤 · 多语言 · MIT</sub>

- **[qianqianwriting](https://github.com/catyiqian/qianqianwriting)** · ★ 47<br>短剧/漫剧编剧：救猫咪方法论 + 31 部爆款短剧分析<br><sub>阶段：集纲 · 剧本</sub><br><sub>更新于 2026-03-05 💤 · 中文</sub>

- **[5min-drama-contest](https://github.com/SoloEnt-AI/5min-drama-contest)** · ★ 26<br>五分钟短剧剧本：一步一问锁定赛道、立意、结构原型和前 30 秒开场，四幕卡点大纲 → 正式剧本 → 分镜脚本<br><sub>阶段：人物 · 集纲 · 剧本</sub><br><sub>更新于 2026-08-29 · 中文</sub><br><sub>💡 灵蟹创作（SoloEnt）出品，面向其五分钟短剧大赛</sub>

- **[screenplay-review-checklist](https://github.com/zhlmi/screenplay-review-checklist)** · ★ 13<br>对抗式剧本踩雷诊断：拿 37 条判据只给你的故事找问题<br><sub>阶段：审稿</sub><br><sub>更新于 2026-08-15 · 中文</sub>

- **[write-screenplay-skill](https://github.com/egguy886/write-screenplay-skill)** · ★ 6<br>小说/设定转商业剧本，国内短剧与出海微短剧双模式<br><sub>阶段：改编 · 剧本</sub><br><sub>更新于 2026-09-06 · 中文 · MIT</sub>

- **[gushi-skill](https://github.com/pipivv/gushi-skill)** · ★ 5<br>从麦基《故事》蒸馏的短剧编剧方法<br><sub>阶段：集纲 · 剧本</sub><br><sub>更新于 2026-06-16 · 中文</sub>

- **[emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills)** · ★ 1<br>艾玛短剧技能组：结构拆解、改编、选题迭代、期待设计、逐集钩子、集纲扩写、对白诊断、剧本删减<br><sub>阶段：选题 · 改编 · 集纲 · 剧本 · 审稿</sub><br><sub>更新于 2026-10-13 · 中文 · 10 个 skill · MIT</sub>

- **[hongguo-shortdrama-screenwriting](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting)** · ★ 0<br>红果/抖音爆款短剧编剧：短剧工厂引擎 + 《短剧编剧第一课》01–10 期方法论<br><sub>阶段：集纲 · 剧本</sub><br><sub>更新于 2026-09-22 · 中文 · MIT</sub><br><sub>💡 基于 short-drama-factory v3.2 改编（README 已注明）；方法论来源为作者自述，未核实</sub>


<details><summary>安装命令</summary>

```bash
# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准
# short-drama-factory
npx skills add lixiaoxiao9888-create/short-drama-factory
# screenwriter-skill
npx skills add Vi7QY/screenwriter-skill
# qianqianwriting
npx skills add catyiqian/qianqianwriting
# 5min-drama-contest
npx skills add SoloEnt-AI/5min-drama-contest
# screenplay-review-checklist
npx skills add zhlmi/screenplay-review-checklist
# write-screenplay-skill
npx skills add egguy886/write-screenplay-skill
# gushi-skill
npx skills add pipivv/gushi-skill
# emma-screenwriting-skills
npx skills add adoria111/emma-screenwriting-skills
# hongguo-shortdrama-screenwriting
npx skills add zhu5859243-free/hongguo-shortdrama-screenwriting
```

</details>

<a id="group-visual"></a>
### 分镜 · 视觉资产 · 视频提示词

把剧本变成镜头：分镜、角色和场景资产、给视频模型的提示词。

- 🌟 **[Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator)** · ★ 2.6k<br>把小说或故事改成多集视频剧本和分镜，产出 Seedance 2.0 提示词<br><sub>阶段：改编 · 剧本 · 分镜 · 提示词</sub><br><sub>更新于 2026-09-21 · 中文</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[seedance2-skill](https://github.com/dexhunter/seedance2-skill)** · ★ 4.3k<br>为 Seedance 2.0 生成高质量视频提示词<br><sub>阶段：提示词</sub><br><sub>更新于 2026-09-19 · 多语言 · 2 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[awesome-seedance](https://github.com/LearnPrompt/awesome-seedance)** · ★ 2.1k<br>Seedance 2.5/2.0 提示词库：800+ 条可追溯原帖的案例、近 500 次跨模型复测，附 skill<br><sub>阶段：提示词</sub><br><sub>更新于 2026-10-17 · 多语言 · 15 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill)** · ★ 750<br>Higgsfield 平台提示词：MCSLA 公式、Seedance 2.5 多参考导演、表演指导、Soul ID 角色一致性、镜头清单与失败诊断<br><sub>阶段：人物 · 提示词</sub><br><sub>更新于 2026-09-27 · 英文 · 36 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦 · 可灵 Kling · Veo · 通义万相 Wan</sub><br><sub>💡 面向 Higgsfield 付费平台，也含广告营销模块</sub>

- **[make-prompt-seedance2](https://github.com/liangdabiao/make-prompt-seedance2)** · ★ 719<br>Seedance 2.0 结构化提示词写法与通用 skill<br><sub>阶段：提示词</sub><br><sub>更新于 2026-10-04 · 中文</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[seedance-2-5-video-director](https://github.com/liyue-aigc/seedance-2-5-video-director)** · ★ 706<br>Seedance 2.5 视频导演：提示词、脚本、诊断、人物锁定、续写、编辑、转场<br><sub>阶段：剧本 · 审稿 · 提示词</sub><br><sub>更新于 2026-08-26 · 中文 · MIT</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[zy-cinematic-realism](https://github.com/popopo-99/zy-cinematic-realism)** · ★ 590<br>造梦师：把剧本、故事或场景想法开发成有动机的叙事关键帧，编译成各生图模型的原生提示词，支持连续组图与结果修复<br><sub>阶段：提示词</sub><br><sub>更新于 2026-10-03 · 英文</sub><br><sub>🎬 Nano Banana</sub><br><sub>💡 README 为中文；主要面向静帧生图；CC BY-NC 4.0，商用需另行授权</sub>

- **[shanyin-director-master](https://github.com/Shanyin-ai/shanyin-director-master)** · ★ 586<br>山音超级导演大师：剧本 → 导演定调、节奏规划、剧本微调、分镜拆解，输出九列分镜表（xlsx），内置类型片导演风格模板<br><sub>阶段：审稿 · 分镜</sub><br><sub>更新于 2026-05-11 · 中文 · MIT</sub><br><sub>💡 面向 Claude App；可与山音超级编剧大师联用</sub>

- **[visual-skills](https://github.com/smixs/visual-skills)** · ★ 525<br>AI 电影导演：Murch 剪辑、走位、蒙太奇等戏剧法则 + Seedance 精确提示词语法<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-09-16 · 英文 · 2 个 skill · CC-BY-4.0</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[XiaoLuo-AI-Drama-Skill](https://github.com/zhurui0523/XiaoLuo-AI-Drama-Skill)** · ★ 477<br>小逻系列：剧本分析、原创改编、分镜脚本、角色三视图/服装/表情、场景布局<br><sub>阶段：改编 · 人物 · 剧本 · 分镜</sub><br><sub>更新于 2026-07-23 · 📝 提示词 · 中文</sub><br><sub>💡 一组提示词 .md，不是标准 SKILL.md</sub>

- **[ai-shortfilm-prompts](https://github.com/jnMetaCode/ai-shortfilm-prompts)** · ★ 475<br>把任意想法变成电影感、可直接投喂模型的视频提示词<br><sub>阶段：提示词</sub><br><sub>更新于 2026-10-12 · 多语言 · MIT</sub><br><sub>🎬 Sora · 可灵 Kling · Veo · Seedance / 即梦</sub>

- **[lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit)** · ★ 421<br>企业 AI 视频项目工具包：Seedance/可灵提示词、分镜、模型选择与调试，附 600 多条 prompt 和方法论<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-10-07 · 中文 · 7 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦 · 可灵 Kling</sub>

- **[minimax-h3-prompt-skill-T8](https://github.com/T8mars/minimax-h3-prompt-skill-T8)** · ★ 290<br>MiniMax H3 / Seedance 2.0 视频提示词案例库与可安装 skill，附视频浏览器<br><sub>阶段：提示词</sub><br><sub>更新于 2026-10-11 · 多语言 · 284 个 skill · MIT</sub><br><sub>🎬 MiniMax H3 · Seedance / 即梦</sub>

- **[awesome-seedance-2.5-prompts-skills](https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills)** · ★ 239<br>Seedance 2.5 提示词库 + skill：按 T2V/R2V/I2V 选路线、Seedream 故事板、多参考与镜头连续性设计<br><sub>阶段：提示词</sub><br><sub>更新于 2026-10-16 · 多语言 · 2 个 skill</sub><br><sub>🎬 Seedance / 即梦</sub><br><sub>💡 厂商仓库，执行默认走 Atlas Cloud 付费 API；提示词库以广告、电商类居多</sub>

- **[DirectorSKILL](https://github.com/wuwangzhang1216/DirectorSKILL)** · ★ 234<br>AI 拍片：镜头清单、关键帧与视频提示词，内置斯皮尔伯格等 20 种导演风格<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-08-31 · 多语言 · MIT</sub>

- **[qisi-video-remix](https://github.com/wyuzhi/qisi-video-remix)** · ★ 180<br>视频创意改编：参考视频 → 剧本 → 分镜 → 分段生成提示词<br><sub>阶段：改编 · 剧本 · 分镜 · 提示词</sub><br><sub>更新于 2026-09-11 · 中文 · MIT</sub>

- **[h3-storyboard-skill](https://github.com/phileiny/h3-storyboard-skill)** · ★ 178<br>MiniMax H3 分镜拆解与角色表演设计<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-10-03 · 英文 · MIT</sub><br><sub>🎬 MiniMax H3</sub>

- **[smy-seedance-storyboard](https://github.com/liangdabiao/smy-seedance-storyboard)** · ★ 177<br>故事 → 上美影复古手绘风格的短剧制作文档：剧本、分镜、资产生图提示词，附完整示例项目<br><sub>阶段：改编 · 剧本 · 分镜 · 提示词</sub><br><sub>更新于 2026-10-08 · 中文</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[film-studio-skills](https://github.com/machina-exm/film-studio-skills)** · ★ 153<br>剧本 → 锁定、可直接生成的镜头：7 个 skill 复刻商业 AI 视频制作流程<br><sub>阶段：剧本 · 分镜 · 提示词</sub><br><sub>更新于 2026-08-14 · 英文 · 7 个 skill</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[Seedance-ShotDesign-Skills](https://github.com/woodfantasy/Seedance-ShotDesign-Skills)** · ★ 123<br>Seedance 2.5 镜头设计<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-08-19 · 多语言 · MIT-0</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[ComfyUI-Agent-Kit](https://github.com/SlavaSexton/ComfyUI-Agent-Kit)** · ★ 106<br>驱动本地 ComfyUI 出图出视频，附 Seedance、MiniMax H3 视频提示词 skill：多镜头分镜、参考素材标注、翻车排查<br><sub>阶段：提示词 · 出片</sub><br><sub>更新于 2026-09-03 · 英文 · 4 个 skill · Apache-2.0</sub><br><sub>🎬 ComfyUI（本地） · Seedance / 即梦 · MiniMax H3</sub><br><sub>💡 主体是本地 ComfyUI 驱动工具；短剧可用的是其中的 Seedance、MiniMax H3 提示词 skill</sub>

- **[fight-video-create-skill](https://github.com/qualsenWeb/fight-video-create-skill)** · ★ 94<br>AI 打戏设计：从打斗构思到剧情、动作、分镜，带招式校验和参考库<br><sub>阶段：剧本 · 分镜</sub><br><sub>更新于 2026-09-29 · 多语言</sub><br><sub>💡 参考库和检索代码经加密，由混淆的 Python 加载器运行，内容无法审阅；许可证 CC BY-NC-ND 4.0</sub>

- **[short-drama-skills](https://github.com/YvonneMovingon/short-drama-skills)** · ★ 93<br>LuxReal 生产验证的短剧提示词：叙事拆解、情绪刻画、动态描述、剧情拆分、视频提示词润色<br><sub>阶段：改编 · 剧本 · 审稿 · 提示词</sub><br><sub>更新于 2026-07-01 · 📝 提示词 · 多语言 · MIT</sub><br><sub>💡 prompt.md 形式，不是标准 SKILL.md</sub>

- **[seedance-2-5-fight-director](https://github.com/liyue-aigc/seedance-2-5-fight-director)** · ★ 82<br>Seedance 2.5 高燃打戏导演：提示词与诊断<br><sub>阶段：提示词</sub><br><sub>更新于 2026-10-04 · 中文</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[fight-prompt-director](https://github.com/irenerachel/fight-prompt-director)** · ★ 58<br>AI 打戏提示词：角色差异化动作、交锋因果链、跨镜连续性，出高强度/慢节奏/中间型三版，适配 Seedance 与 H3<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-09-02 · 中文 · MIT</sub><br><sub>🎬 Seedance / 即梦 · MiniMax H3</sub>

- **[seedance-skill](https://github.com/alchaincyf/seedance-skill)** · ★ 40<br>白模驱动的 Seedance 工作台：用 scene.json 渲染白模参考视频并做几何体检，可从照片反解白模，按白模几何写提示词<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-10-13 · 中文 · MIT</sub><br><sub>🎬 Seedance / 即梦</sub><br><sub>💡 白模渲染需 Node、ffmpeg 与 hyperframes</sub>

- **[acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill)** · ★ 39<br>Acheng 导演引擎：剧本、分镜、文戏五轨表演、打戏因果链、特效与资产，编译成 MiniMax H3 / Seedance 提示词<br><sub>阶段：人物 · 剧本 · 审稿 · 分镜 · 提示词</sub><br><sub>更新于 2026-10-01 · 中文 · 11 个 skill · Apache-2.0</sub><br><sub>🎬 MiniMax H3 · Seedance / 即梦</sub><br><sub>💡 CC BY-NC-ND 4.0（禁商用、禁演绎）；附 132 段运镜白模视频，仓库体积较大</sub>

- **[storyboard-director](https://github.com/kevinchin12/storyboard-director)** · ★ 35<br>故事 → 分镜脚本，子代理并行生成逐镜线稿，HTML 审片板返修指定镜头，确认后汇总成按镜头排序的视频提示词<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-10-11 · 英文 · 5 个 skill · MIT</sub><br><sub>💡 README 为中文；逐镜线稿依赖 Codex 内置生图</sub>

- **[story-video-director](https://github.com/zlbigger/story-video-director)** · ★ 34<br>把任意故事变成图片素材、分镜、中文视听提示词与 API 调用清单<br><sub>阶段：人物 · 分镜 · 提示词</sub><br><sub>更新于 2026-10-07 · 中文 · MIT</sub>

- **[fight-scene-director](https://github.com/ZzzAloong/fight-scene-director)** · ★ 22<br>多画风打戏设计：动作编排、空间调度、镜头与特效规则，可先出站位图/轨迹图生图词，再按轨迹写视频提示词<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-09-06 · 英文 · MIT</sub><br><sub>🎬 Seedance / 即梦 · MiniMax H3</sub><br><sub>💡 skill 正文为英文，输出中文提示词</sub>

- **[ShortVideoDirector](https://github.com/wddxh/ShortVideoDirector)** · ★ 21<br>4 个子代理协作，把故事创意转成视频分镜和资产提示词，可调用即梦 CLI 出图、提交视频任务<br><sub>阶段：人物 · 集纲 · 分镜 · 提示词</sub><br><sub>更新于 2026-09-16 · 中文 · 35 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[ai-film-skills](https://github.com/nigo-studio/ai-film-skills)** · ★ 19<br>从 AI 动作片《CROW LINE》流程拆出的 skill：Seedance 2.5 参考生视频提示词导演，三联角色设定图保持跨镜一致<br><sub>阶段：人物 · 提示词</sub><br><sub>更新于 2026-08-23 · 英文 · 2 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦</sub><br><sub>💡 作者计划陆续发布故事、分镜、声音等其余阶段</sub>

- **[seedance-2-5-prompting](https://github.com/babicat4242-svg/seedance-2-5-prompting)** · ★ 16<br>Seedance 2.5 提示词：参考素材角色绑定、30 种运镜定义与冲突规则、R2V/白模、局部编辑与延长、多轮修改流程<br><sub>阶段：提示词</sub><br><sub>更新于 2026-09-25 · 英文 · MIT</sub><br><sub>🎬 Seedance / 即梦</sub><br><sub>💡 README 为韩文；示例偏产品广告</sub>

- **[Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director)** · ★ 14<br>MiniMax H3 漫剧导演：网文改分镜、核心/龙套资产分级、文戏长镜与武戏快切、动作连续性锁定、尾帧接力，一次出整集提示词<br><sub>阶段：改编 · 人物 · 分镜 · 提示词</sub><br><sub>更新于 2026-08-30 · 多语言 · 10 个 skill</sub><br><sub>🎬 MiniMax H3 · ComfyUI（本地）</sub><br><sub>💡 另附 9 个 MiniMax 官方 H3 skill 的搬运/中译版；README 开头有要求 agent 直接执行流程的指令</sub>

- **[xiaxia](https://github.com/luanyi824-hash/xiaxia)** · ★ 14<br>夏夏：把确认剧本转成带时长预算、机位焦段、真实光源、调度与动作因果的导演分镜，可编译为 Seedance 2.5 任务<br><sub>阶段：分镜 · 提示词</sub><br><sub>更新于 2026-09-08 · 中文</sub><br><sub>🎬 Seedance / 即梦</sub><br><sub>💡 视觉方法改编自 popopo-99/zy-cinematic-realism；CC BY-NC 4.0，商用需另行授权</sub>

- **[ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills)** · ★ 13<br>AI 漫剧导演：剧本 + 已有资产 → Seedance 2.0/2.5 分镜组提示词，含人物表演、导演摄影、场景资产、站位图、连续性与声音<br><sub>阶段：改编 · 人物 · 审稿 · 分镜 · 提示词</sub><br><sub>更新于 2026-10-11 · 中文 · 7 个 skill · MIT</sub><br><sub>🎬 Seedance / 即梦</sub>

- **[chinese-epic-scene-director](https://github.com/zhouwei713/chinese-epic-scene-director)** · ★ 13<br>中国式宏大场景：把一句设定扩写成仙侠/神话短片故事，建连续性台账，按镜头成对输出图片和视频提示词<br><sub>阶段：人物 · 剧本 · 分镜 · 提示词</sub><br><sub>更新于 2026-08-18 · 中文 · MIT</sub><br><sub>💡 分叙事运镜和视觉展览两种模式，后者偏氛围、景观展示</sub>

- **[visual-storytelling-skills](https://github.com/leynos/visual-storytelling-skills)** · ★ 9<br>从文字到画面：场景清单、镜头设计、视频模型提示词、视频生成<br><sub>阶段：分镜 · 提示词 · 出片</sub><br><sub>更新于 2026-10-10 · 英文 · 8 个 skill · ISC</sub><br><sub>🎬 可灵 Kling · Seedance / 即梦 · Nano Banana</sub>

- **[live-action-drama-16x9](https://github.com/momo5213/live-action-drama-16x9)** · ★ 1<br>16:9 真人精品短剧：剧本分析、分镜运镜、光影与细微表演、视频提示词、连续性审查<br><sub>阶段：审稿 · 分镜 · 提示词</sub><br><sub>更新于 2026-09-11 · 中文</sub>


<details><summary>安装命令</summary>

```bash
# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准
# Seedance2-Storyboard-Generator
npx skills add liangdabiao/Seedance2-Storyboard-Generator
# seedance2-skill
npx skills add dexhunter/seedance2-skill
# awesome-seedance
npx skills add LearnPrompt/awesome-seedance
# higgsfield-ai-prompt-skill
npx skills add OSideMedia/higgsfield-ai-prompt-skill
# make-prompt-seedance2
npx skills add liangdabiao/make-prompt-seedance2
# seedance-2-5-video-director
npx skills add liyue-aigc/seedance-2-5-video-director
# zy-cinematic-realism
npx skills add popopo-99/zy-cinematic-realism
# shanyin-director-master
npx skills add Shanyin-ai/shanyin-director-master
# visual-skills
npx skills add smixs/visual-skills
# ai-shortfilm-prompts
npx skills add jnMetaCode/ai-shortfilm-prompts
# lanshu-awesome-ai-video-kit
npx skills add cclank/lanshu-awesome-ai-video-kit
# minimax-h3-prompt-skill-T8
npx skills add T8mars/minimax-h3-prompt-skill-T8
# awesome-seedance-2.5-prompts-skills
npx skills add AtlasCloudAI/awesome-seedance-2.5-prompts-skills
# DirectorSKILL
npx skills add wuwangzhang1216/DirectorSKILL
# qisi-video-remix
npx skills add wyuzhi/qisi-video-remix
# h3-storyboard-skill
npx skills add phileiny/h3-storyboard-skill
# smy-seedance-storyboard
npx skills add liangdabiao/smy-seedance-storyboard
# film-studio-skills
npx skills add machina-exm/film-studio-skills
# Seedance-ShotDesign-Skills
npx skills add woodfantasy/Seedance-ShotDesign-Skills
# ComfyUI-Agent-Kit
/plugin marketplace add SlavaSexton/ComfyUI-Agent-Kit
# fight-video-create-skill
npx skills add qualsenWeb/fight-video-create-skill
# seedance-2-5-fight-director
npx skills add liyue-aigc/seedance-2-5-fight-director
# fight-prompt-director
npx skills add irenerachel/fight-prompt-director
# seedance-skill
npx skills add alchaincyf/seedance-skill
# acheng-director-skill
npx skills add AharaOoO/acheng-director-skill
# storyboard-director
npx skills add kevinchin12/storyboard-director
# story-video-director
npx skills add zlbigger/story-video-director
# fight-scene-director
npx skills add ZzzAloong/fight-scene-director
# ShortVideoDirector
npx skills add wddxh/ShortVideoDirector
# ai-film-skills
npx skills add nigo-studio/ai-film-skills
# seedance-2-5-prompting
npx skills add babicat4242-svg/seedance-2-5-prompting
# Comfy-H3-Director
npx skills add MIKA6941/Comfy-H3-Director
# xiaxia
npx skills add luanyi824-hash/xiaxia
# ai-comic-drama-director-skills
npx skills add djyy1031/ai-comic-drama-director-skills
# chinese-epic-scene-director
npx skills add zhouwei713/chinese-epic-scene-director
# visual-storytelling-skills
npx skills add leynos/visual-storytelling-skills
# live-action-drama-16x9
npx skills add momo5213/live-action-drama-16x9
```

</details>

<a id="group-source"></a>
### 上游：IP 评估与故事拆解

改编之前先判断：这个故事值不值得拍、怎么拆。

- **[screen-creative-skills](https://github.com/VanGong1999/screen-creative-skills)** · ★ 462<br>影视策划与评估：小说/IP 评估、情节点拆解、人物小传与关系、大纲、小说改编短剧或长剧<br><sub>阶段：选题 · 改编 · 人物 · 集纲</sub><br><sub>更新于 2026-10-12 · 中文 · 31 个 skill · MIT</sub><br><sub>💡 31 个 skill 在仓库里有两份副本</sub>

- **[narrative-to-screen-reader](https://github.com/zhlmi/narrative-to-screen-reader)** · ★ 122<br>把手上的故事翻译成影视开发语言：快速诊断、编剧改编读本、导演视听读本、演员读本、制片摘要<br><sub>阶段：选题 · 改编 · 人物</sub><br><sub>更新于 2026-10-01 · 中文</sub>

- **[analyze-hit-novel](https://github.com/ciel-oliver/analyze-hit-novel)** · ★ 11<br>爆款小说拆文：把爆款小说/漫剧拆成可验证的叙事系统，供改编参考<br><sub>阶段：选题 · 改编 · 集纲</sub><br><sub>更新于 2026-09-04 · 中文</sub>


<details><summary>安装命令</summary>

```bash
# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准
# screen-creative-skills
npx skills add VanGong1999/screen-creative-skills
# narrative-to-screen-reader
npx skills add zhlmi/narrative-to-screen-reader
# analyze-hit-novel
npx skills add ciel-oliver/analyze-hit-novel
```

</details>

<a id="group-craft"></a>
### 编剧基本功

不限于短剧的编剧理论：结构、场景、对白、人物。

- 🌟 **[screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills)** · ★ 1.7k<br>编剧理论最系统的一套：结构、Truby、场景、对白、剧集圣经、编剧室，含日韩法美与中国戏曲案例<br><sub>阶段：改编 · 人物 · 集纲 · 剧本 · 审稿</sub><br><sub>更新于 2026-10-03 · 中文 · 26 个 skill · MIT</sub><br><sub>💡 skill 正文为中文，README 有五种语言</sub>

- **[shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master)** · ★ 1.3k<br>山音超级编剧大师：概念超短片、叙事短片、长片、多集剧集四种格式的人物、大纲、场景拆解和完整剧本<br><sub>阶段：人物 · 集纲 · 剧本</sub><br><sub>更新于 2026-04-01 💤 · 中文 · MIT</sub><br><sub>💡 以 .skill 文件分发，不能用 npx skills 安装</sub>

- **[write-chinese-long-screenplay](https://github.com/mudden2380078550-creator/write-chinese-long-screenplay)** · ★ 23<br>Narrative Harness：中文小说与剧本创作的本地状态工具，旧版长剧本写作模板保留在 legacy/<br><sub>阶段：集纲 · 剧本</sub><br><sub>更新于 2026-09-12 · 中文 · 2 个 skill · GPL-3.0</sub>

- **[claude-screenwriting](https://github.com/e06084/claude-screenwriting)** · ★ 9<br>编剧知识引擎：把 Vogler/McKee/救猫咪落成 Obsidian 故事 wiki，15-beat 节奏、三层角色卡、结构诊断<br><sub>阶段：人物 · 集纲 · 审稿</sub><br><sub>更新于 2026-10-08 · 中文 · 8 个 skill · MIT</sub>

- **[kunka-screenwriting-master](https://github.com/geslie1/kunka-screenwriting-master)** · ★ 5<br>昆卡编剧大师：中文优先的编剧 skill 组，覆盖构思、改稿、连续性检查与剧集开发<br><sub>阶段：集纲 · 剧本 · 审稿</sub><br><sub>更新于 2026-09-10 · 中文 · 13 个 skill · MIT</sub>


<details><summary>安装命令</summary>

```bash
# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准
# screenwriting-skills
/plugin marketplace add jtydhr88/screenwriting-skills
# shanyin-screenwriting-master
# 下载仓库里的 .skill 文件，在 Claude App 的 Skills 中导入（另有通用 .md 版）
# write-chinese-long-screenplay
npx skills add mudden2380078550-creator/write-chinese-long-screenplay
# claude-screenwriting
npx skills add e06084/claude-screenwriting
# kunka-screenwriting-master
npx skills add geslie1/kunka-screenwriting-master
```

</details>

<a id="group-companion"></a>
### 配套：去 AI 味

让剧本和对白读起来不像 AI 写的。

- **[humanizer](https://github.com/blader/humanizer)** · ★ 57.6k<br>按维基百科「Signs of AI writing」清单去除 AI 写作痕迹<br><sub>阶段：审稿</sub><br><sub>更新于 2026-10-16 · 英文 · MIT</sub>

- **[human-writing](https://github.com/KKKKhazix/human-writing)** · ★ 4.1k<br>活人感写作：让 AI 写的中文像具体的人在说话，适合打磨对白和旁白<br><sub>阶段：审稿</sub><br><sub>更新于 2026-08-11 · 中文 · MIT</sub>

- **[sepia](https://github.com/Nanako0129/sepia)** · ★ 3.2k<br>面向小说的去 AI 味：修复叙事结构，按场合匹配文风规则，方法来自 StoryScope 论文<br><sub>阶段：审稿</sub><br><sub>更新于 2026-10-15 · 英文 · 6 个 skill · MIT</sub>


<details><summary>安装命令</summary>

```bash
# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准
# humanizer
npx skills add blader/humanizer
# human-writing
npx skills add KKKKhazix/human-writing
# sepia
npx skills add Nanako0129/sepia
```

</details>

<a id="group-platform"></a>
### 相关开源平台（完整应用，非 skill）

可自行部署的短剧/漫剧生产平台，不是 skill，供对照参考。更多见 [awesome-ai-video](https://github.com/zhaotoday/awesome-ai-video)。

- **[Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app)** · ★ 18k<br>Toonflow：开源 AI 短剧/漫剧平台，剧本、智能分镜、角色场景资产、图像和视频生成，无限画布 + Agent<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-10-16 · 🧩 应用 · 多语言 · 5 个 skill · MIT</sub>

- **[huobao-drama](https://github.com/chatfire-AI/huobao-drama)** · ★ 16.3k<br>火宝短剧：一句话生成完整短剧，从剧本到成片全自动<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-10-05 · 🧩 应用 · 多语言 · 7 个 skill</sub>

- **[waoowaoo](https://github.com/waooAI/waoowaoo)** · ★ 14.6k<br>AI 影视 Agent 工作台（预览版）：图片与视频创作，从短片到真人可控成片<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-09-21 · 🧩 应用 · 多语言 · 6 个 skill</sub><br><sub>💡 许可证为 Elastic 2.0：源码可见，但不是 OSI 认定的开源许可证</sub>

- **[ViMax](https://github.com/HKUDS/ViMax)** · ★ 12.7k<br>港大 ViMax：导演、编剧、制片、视频生成一体的 Agent 化视频生成<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-09-30 · 🧩 应用 · 英文 · MIT</sub>

- **[Jellyfish](https://github.com/Forget-C/Jellyfish)** · ★ 6.7k<br>AI 短剧端到端工作台：剧本输入、结构化分镜、一致性管理、视频生成<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-07-30 · 🧩 应用 · 多语言 · Apache-2.0</sub>

- **[dramaclaw](https://github.com/dramaclaw/dramaclaw)** · ★ 6.3k<br>通用 AIGC 视频引擎：剧本到成片一条流水线，覆盖漫剧、广告、电商、乙游<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-10-17 · 🧩 应用 · 多语言 · 6 个 skill</sub>

- **[ArcReel](https://github.com/ArcReel/ArcReel)** · ★ 5.5k<br>可自部署视频工作台：小说/剧本 → 角色场景道具资产、分镜、视频和剪映草稿，含跨镜头一致性与费用追踪<br><sub>阶段：改编 · 人物 · 分镜 · 出片</sub><br><sub>更新于 2026-10-16 · 🧩 应用 · 多语言 · 51 个 skill · AGPL-3.0</sub>

- **[printfilm](https://github.com/yi1108/printfilm)** · ★ 5.2k<br>PRINTFILM：AI 短视频营销与 AI 短剧创作平台<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-10-15 · 🧩 应用 · 多语言 · MIT</sub>

- **[BigBanana-AI-Director](https://github.com/shuyu-labs/BigBanana-AI-Director)** · ★ 2.3k<br>BigBanana AI 导演：短剧/漫剧一站式平台，「剧本 → 资产 → 关键帧」工业化流程<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-10-06 · 🧩 应用 · 中文</sub><br><sub>💡 仓库里只有文档和拉取预构建镜像的 docker-compose，README 称已停止同步源码</sub>

- **[LocalMiniDrama](https://github.com/xuanyustudio/LocalMiniDrama)** · ★ 2.1k<br>本地运行的 AI 短剧/漫剧工具：故事到成片，项目数据存在本机，图片和视频走云端 API，已接入 Seedance 2<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-10-16 · 🧩 应用 · 多语言 · 2 个 skill · MIT</sub>

- **[VideoClaw](https://github.com/HITsz-TMG/VideoClaw)** · ★ 1.9k<br>哈工大（深圳）VideoClaw：AI 视频员工，聊一个想法出一部片，覆盖短剧全流程<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-08-26 · 🧩 应用 · 多语言 · MIT</sub>

- **[ai_story](https://github.com/xhongc/ai_story)** · ★ 1.8k<br>AI 视频、动漫、短剧、漫剧自动化生成工具<br><sub>阶段：分镜 · 出片</sub><br><sub>更新于 2026-10-13 · 🧩 应用 · 中文</sub>

- **[ai-fusion-video](https://github.com/Stonewuu/ai-fusion-video)** · ★ 1.6k<br>融光：基于 Agent 的全流程 AI 短剧/漫剧/视频创作平台（Java + AgentScope）<br><sub>阶段：剧本 · 分镜 · 出片</sub><br><sub>更新于 2026-10-11 · 🧩 应用 · 多语言 · MIT</sub>

- **[lumenx](https://github.com/alibaba/lumenx)** · ★ 1.4k<br>阿里 LumenX Studio：小说到动态视频的短漫剧一站式生产，剧本分析、角色定制、分镜、视频合成<br><sub>阶段：改编 · 人物 · 分镜 · 出片</sub><br><sub>更新于 2026-08-11 · 🧩 应用 · 多语言 · MIT</sub>


<a id="by-stage"></a>
## 按创作阶段查找

卡在某一步时，从这里找能帮上忙的 skill。「专项」只覆盖 3 个以内的阶段，「综合」是全流程或多环节项目；各自按星数排序。

**选题 · IP 评估**（5）

- 专项（2）：[narrative-to-screen-reader](https://github.com/zhlmi/narrative-to-screen-reader) · [analyze-hit-novel](https://github.com/ciel-oliver/analyze-hit-novel)
- 综合（3）：[screen-creative-skills](https://github.com/VanGong1999/screen-creative-skills) · [ai-short-drama](https://github.com/Hao0321/ai-short-drama) · [emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills)

**改编（小说 → 剧本）**（21）

- 专项（5）：[narrative-to-screen-reader](https://github.com/zhlmi/narrative-to-screen-reader) · [infinite-creation](https://github.com/SwotAtmk/infinite-creation) · [novel-to-ai-short-drama-skill](https://github.com/muxia0396/novel-to-ai-short-drama-skill) · [analyze-hit-novel](https://github.com/ciel-oliver/analyze-hit-novel) · [write-screenplay-skill](https://github.com/egguy886/write-screenplay-skill)
- 综合（16）：[shuohao-skills](https://github.com/eternityspring/shuohao-skills) · [drama-skills](https://github.com/zenstory-ai/drama-skills) · [Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator) · [screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) · [XiaoLuo-AI-Drama-Skill](https://github.com/zhurui0523/XiaoLuo-AI-Drama-Skill) · [screen-creative-skills](https://github.com/VanGong1999/screen-creative-skills) · [short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) · [short-drama-production](https://github.com/suihe1/short-drama-production) · [qisi-video-remix](https://github.com/wyuzhi/qisi-video-remix) · [smy-seedance-storyboard](https://github.com/liangdabiao/smy-seedance-storyboard) · [short-drama-skills](https://github.com/YvonneMovingon/short-drama-skills) · [novel-to-manju](https://github.com/senmanx/novel-to-manju) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director) · [ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills) · [emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills)

**人物 · 角色资产**（26）

- 专项（8）：[shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) · [higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) · [narrative-to-screen-reader](https://github.com/zhlmi/narrative-to-screen-reader) · [ai-film-skills](https://github.com/62656456/ai-film-skills) · [story-video-director](https://github.com/zlbigger/story-video-director) · [5min-drama-contest](https://github.com/SoloEnt-AI/5min-drama-contest) · [ai-film-skills](https://github.com/nigo-studio/ai-film-skills) · [claude-screenwriting](https://github.com/e06084/claude-screenwriting)
- 综合（18）：[shuohao-skills](https://github.com/eternityspring/shuohao-skills) · [drama-skills](https://github.com/zenstory-ai/drama-skills) · [screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) · [XiaoLuo-AI-Drama-Skill](https://github.com/zhurui0523/XiaoLuo-AI-Drama-Skill) · [screen-creative-skills](https://github.com/VanGong1999/screen-creative-skills) · [novel-to-manju](https://github.com/senmanx/novel-to-manju) · [ai-short-drama](https://github.com/oiuv/ai-short-drama) · [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) · [jingju-skills](https://github.com/jxshow/jingju-skills) · [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [ShortVideoDirector](https://github.com/wddxh/ShortVideoDirector) · [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) · [ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills) · [chinese-epic-scene-director](https://github.com/zhouwei713/chinese-epic-scene-director)

**结构 · 集纲 · 钩子**（23）

- 专项（9）：[shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) · [qianqianwriting](https://github.com/catyiqian/qianqianwriting) · [5min-drama-contest](https://github.com/SoloEnt-AI/5min-drama-contest) · [write-chinese-long-screenplay](https://github.com/mudden2380078550-creator/write-chinese-long-screenplay) · [analyze-hit-novel](https://github.com/ciel-oliver/analyze-hit-novel) · [claude-screenwriting](https://github.com/e06084/claude-screenwriting) · [gushi-skill](https://github.com/pipivv/gushi-skill) · [kunka-screenwriting-master](https://github.com/geslie1/kunka-screenwriting-master) · [hongguo-shortdrama-screenwriting](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting)
- 综合（14）：[shuohao-skills](https://github.com/eternityspring/shuohao-skills) · [screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) · [screen-creative-skills](https://github.com/VanGong1999/screen-creative-skills) · [short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) · [short-drama-production](https://github.com/suihe1/short-drama-production) · [ai-short-drama](https://github.com/Hao0321/ai-short-drama) · [ai-short-drama](https://github.com/oiuv/ai-short-drama) · [jingju-skills](https://github.com/jxshow/jingju-skills) · [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) · [ManjuForge](https://github.com/mengxiujie/ManjuForge) · [ShortVideoDirector](https://github.com/wddxh/ShortVideoDirector) · [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills)

**剧本 · 对白**（41）

- 专项（11）：[shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) · [seedance-2-5-video-director](https://github.com/liyue-aigc/seedance-2-5-video-director) · [film-studio-skills](https://github.com/machina-exm/film-studio-skills) · [fight-video-create-skill](https://github.com/qualsenWeb/fight-video-create-skill) · [qianqianwriting](https://github.com/catyiqian/qianqianwriting) · [5min-drama-contest](https://github.com/SoloEnt-AI/5min-drama-contest) · [write-chinese-long-screenplay](https://github.com/mudden2380078550-creator/write-chinese-long-screenplay) · [write-screenplay-skill](https://github.com/egguy886/write-screenplay-skill) · [gushi-skill](https://github.com/pipivv/gushi-skill) · [kunka-screenwriting-master](https://github.com/geslie1/kunka-screenwriting-master) · [hongguo-shortdrama-screenwriting](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting)
- 综合（30）：[shuohao-skills](https://github.com/eternityspring/shuohao-skills) · [drama-skills](https://github.com/zenstory-ai/drama-skills) · [Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator) · [screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) · [manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) · [XiaoLuo-AI-Drama-Skill](https://github.com/zhurui0523/XiaoLuo-AI-Drama-Skill) · [short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) · [OnlyShot](https://github.com/A-cat-with-carrots/OnlyShot) · [Micro-Drama-Skills](https://github.com/zhaihao118/Micro-Drama-Skills) · [short-drama-production](https://github.com/suihe1/short-drama-production) · [qisi-video-remix](https://github.com/wyuzhi/qisi-video-remix) · [smy-seedance-storyboard](https://github.com/liangdabiao/smy-seedance-storyboard) · [workrally](https://github.com/Tencent/workrally) · [short-drama-skills](https://github.com/YvonneMovingon/short-drama-skills) · [ai-short-drama](https://github.com/Hao0321/ai-short-drama) · [novel-to-manju](https://github.com/senmanx/novel-to-manju) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [muse-video-skill](https://github.com/LuoJiangYong/muse-video-skill) · [ai-short-drama](https://github.com/oiuv/ai-short-drama) · [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) · [jingju-skills](https://github.com/jxshow/jingju-skills) · [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [short-drama-director](https://github.com/UncleWang2088/short-drama-director) · [ManjuForge](https://github.com/mengxiujie/ManjuForge) · [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) · [chinese-epic-scene-director](https://github.com/zhouwei713/chinese-epic-scene-director) · [emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills)

**审稿 · 质检 · 去 AI 味**（27）

- 专项（10）：[humanizer](https://github.com/blader/humanizer) · [human-writing](https://github.com/KKKKhazix/human-writing) · [sepia](https://github.com/Nanako0129/sepia) · [seedance-2-5-video-director](https://github.com/liyue-aigc/seedance-2-5-video-director) · [shanyin-director-master](https://github.com/Shanyin-ai/shanyin-director-master) · [screenwriter-skill](https://github.com/Vi7QY/screenwriter-skill) · [screenplay-review-checklist](https://github.com/zhlmi/screenplay-review-checklist) · [claude-screenwriting](https://github.com/e06084/claude-screenwriting) · [kunka-screenwriting-master](https://github.com/geslie1/kunka-screenwriting-master) · [live-action-drama-16x9](https://github.com/momo5213/live-action-drama-16x9)
- 综合（17）：[drama-skills](https://github.com/zenstory-ai/drama-skills) · [screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) · [manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) · [short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) · [short-drama-skills](https://github.com/YvonneMovingon/short-drama-skills) · [ai-short-drama](https://github.com/Hao0321/ai-short-drama) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [muse-video-skill](https://github.com/LuoJiangYong/muse-video-skill) · [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [short-drama-director](https://github.com/UncleWang2088/short-drama-director) · [ManjuForge](https://github.com/mengxiujie/ManjuForge) · [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) · [ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills) · [emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills)

**分镜 · 镜头设计**（46）

- 专项（18）：[shanyin-director-master](https://github.com/Shanyin-ai/shanyin-director-master) · [visual-skills](https://github.com/smixs/visual-skills) · [lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) · [DirectorSKILL](https://github.com/wuwangzhang1216/DirectorSKILL) · [h3-storyboard-skill](https://github.com/phileiny/h3-storyboard-skill) · [film-studio-skills](https://github.com/machina-exm/film-studio-skills) · [Seedance-ShotDesign-Skills](https://github.com/woodfantasy/Seedance-ShotDesign-Skills) · [fight-video-create-skill](https://github.com/qualsenWeb/fight-video-create-skill) · [ai-film-skills](https://github.com/62656456/ai-film-skills) · [fight-prompt-director](https://github.com/irenerachel/fight-prompt-director) · [seedance-skill](https://github.com/alchaincyf/seedance-skill) · [storyboard-director](https://github.com/kevinchin12/storyboard-director) · [story-video-director](https://github.com/zlbigger/story-video-director) · [novel-to-ai-short-drama-skill](https://github.com/muxia0396/novel-to-ai-short-drama-skill) · [fight-scene-director](https://github.com/ZzzAloong/fight-scene-director) · [xiaxia](https://github.com/luanyi824-hash/xiaxia) · [visual-storytelling-skills](https://github.com/leynos/visual-storytelling-skills) · [live-action-drama-16x9](https://github.com/momo5213/live-action-drama-16x9)
- 综合（28）：[shuohao-skills](https://github.com/eternityspring/shuohao-skills) · [drama-skills](https://github.com/zenstory-ai/drama-skills) · [Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator) · [manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) · [XiaoLuo-AI-Drama-Skill](https://github.com/zhurui0523/XiaoLuo-AI-Drama-Skill) · [OnlyShot](https://github.com/A-cat-with-carrots/OnlyShot) · [Micro-Drama-Skills](https://github.com/zhaihao118/Micro-Drama-Skills) · [short-drama-production](https://github.com/suihe1/short-drama-production) · [qisi-video-remix](https://github.com/wyuzhi/qisi-video-remix) · [smy-seedance-storyboard](https://github.com/liangdabiao/smy-seedance-storyboard) · [workrally](https://github.com/Tencent/workrally) · [ai-short-drama](https://github.com/Hao0321/ai-short-drama) · [novel-to-manju](https://github.com/senmanx/novel-to-manju) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [muse-video-skill](https://github.com/LuoJiangYong/muse-video-skill) · [ai-short-drama](https://github.com/oiuv/ai-short-drama) · [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) · [jingju-skills](https://github.com/jxshow/jingju-skills) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [short-drama-director](https://github.com/UncleWang2088/short-drama-director) · [ManjuForge](https://github.com/mengxiujie/ManjuForge) · [ShortVideoDirector](https://github.com/wddxh/ShortVideoDirector) · [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) · [ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills) · [chinese-epic-scene-director](https://github.com/zhouwei713/chinese-epic-scene-director)

**视频 / 图像提示词**（55）

- 专项（28）：[seedance2-skill](https://github.com/dexhunter/seedance2-skill) · [awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) · [higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) · [make-prompt-seedance2](https://github.com/liangdabiao/make-prompt-seedance2) · [seedance-2-5-video-director](https://github.com/liyue-aigc/seedance-2-5-video-director) · [zy-cinematic-realism](https://github.com/popopo-99/zy-cinematic-realism) · [visual-skills](https://github.com/smixs/visual-skills) · [ai-shortfilm-prompts](https://github.com/jnMetaCode/ai-shortfilm-prompts) · [lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) · [minimax-h3-prompt-skill-T8](https://github.com/T8mars/minimax-h3-prompt-skill-T8) · [awesome-seedance-2.5-prompts-skills](https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills) · [DirectorSKILL](https://github.com/wuwangzhang1216/DirectorSKILL) · [h3-storyboard-skill](https://github.com/phileiny/h3-storyboard-skill) · [film-studio-skills](https://github.com/machina-exm/film-studio-skills) · [Seedance-ShotDesign-Skills](https://github.com/woodfantasy/Seedance-ShotDesign-Skills) · [ComfyUI-Agent-Kit](https://github.com/SlavaSexton/ComfyUI-Agent-Kit) · [seedance-2-5-fight-director](https://github.com/liyue-aigc/seedance-2-5-fight-director) · [infinite-creation](https://github.com/SwotAtmk/infinite-creation) · [fight-prompt-director](https://github.com/irenerachel/fight-prompt-director) · [seedance-skill](https://github.com/alchaincyf/seedance-skill) · [storyboard-director](https://github.com/kevinchin12/storyboard-director) · [story-video-director](https://github.com/zlbigger/story-video-director) · [fight-scene-director](https://github.com/ZzzAloong/fight-scene-director) · [ai-film-skills](https://github.com/nigo-studio/ai-film-skills) · [seedance-2-5-prompting](https://github.com/babicat4242-svg/seedance-2-5-prompting) · [xiaxia](https://github.com/luanyi824-hash/xiaxia) · [visual-storytelling-skills](https://github.com/leynos/visual-storytelling-skills) · [live-action-drama-16x9](https://github.com/momo5213/live-action-drama-16x9)
- 综合（27）：[drama-skills](https://github.com/zenstory-ai/drama-skills) · [Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator) · [manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) · [OnlyShot](https://github.com/A-cat-with-carrots/OnlyShot) · [Micro-Drama-Skills](https://github.com/zhaihao118/Micro-Drama-Skills) · [short-drama-production](https://github.com/suihe1/short-drama-production) · [qisi-video-remix](https://github.com/wyuzhi/qisi-video-remix) · [smy-seedance-storyboard](https://github.com/liangdabiao/smy-seedance-storyboard) · [workrally](https://github.com/Tencent/workrally) · [short-drama-skills](https://github.com/YvonneMovingon/short-drama-skills) · [novel-to-manju](https://github.com/senmanx/novel-to-manju) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [muse-video-skill](https://github.com/LuoJiangYong/muse-video-skill) · [ai-short-drama](https://github.com/oiuv/ai-short-drama) · [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) · [jingju-skills](https://github.com/jxshow/jingju-skills) · [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [short-drama-director](https://github.com/UncleWang2088/short-drama-director) · [ManjuForge](https://github.com/mengxiujie/ManjuForge) · [ShortVideoDirector](https://github.com/wddxh/ShortVideoDirector) · [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) · [ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills) · [chinese-epic-scene-director](https://github.com/zhouwei713/chinese-epic-scene-director)

**出片 · 配音 · 剪辑**（16）

- 专项（4）：[ComfyUI-Agent-Kit](https://github.com/SlavaSexton/ComfyUI-Agent-Kit) · [infinite-creation](https://github.com/SwotAtmk/infinite-creation) · [ai-film-skills](https://github.com/62656456/ai-film-skills) · [visual-storytelling-skills](https://github.com/leynos/visual-storytelling-skills)
- 综合（12）：[OnlyShot](https://github.com/A-cat-with-carrots/OnlyShot) · [Micro-Drama-Skills](https://github.com/zhaihao118/Micro-Drama-Skills) · [short-drama-production](https://github.com/suihe1/short-drama-production) · [workrally](https://github.com/Tencent/workrally) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [jingju-skills](https://github.com/jxshow/jingju-skills) · [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [ManjuForge](https://github.com/mengxiujie/ManjuForge) · [ai-manga-drama](https://github.com/liuxiao20051106-prog/ai-manga-drama) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator)

<a id="by-model"></a>
## 按视频模型查找

仓库说明里明确提到适配的图像/视频模型（按星数排序）。

**Seedance / 即梦**（33）：[seedance2-skill](https://github.com/dexhunter/seedance2-skill) · [Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator) · [awesome-seedance](https://github.com/LearnPrompt/awesome-seedance) · [manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) · [higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) · [make-prompt-seedance2](https://github.com/liangdabiao/make-prompt-seedance2) · [seedance-2-5-video-director](https://github.com/liyue-aigc/seedance-2-5-video-director) · [visual-skills](https://github.com/smixs/visual-skills) · [ai-shortfilm-prompts](https://github.com/jnMetaCode/ai-shortfilm-prompts) · [lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) · [OnlyShot](https://github.com/A-cat-with-carrots/OnlyShot) · [minimax-h3-prompt-skill-T8](https://github.com/T8mars/minimax-h3-prompt-skill-T8) · [awesome-seedance-2.5-prompts-skills](https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills) · [smy-seedance-storyboard](https://github.com/liangdabiao/smy-seedance-storyboard) · [film-studio-skills](https://github.com/machina-exm/film-studio-skills) · [Seedance-ShotDesign-Skills](https://github.com/woodfantasy/Seedance-ShotDesign-Skills) · [ComfyUI-Agent-Kit](https://github.com/SlavaSexton/ComfyUI-Agent-Kit) · [seedance-2-5-fight-director](https://github.com/liyue-aigc/seedance-2-5-fight-director) · [fight-prompt-director](https://github.com/irenerachel/fight-prompt-director) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [ai-short-drama](https://github.com/oiuv/ai-short-drama) · [seedance-skill](https://github.com/alchaincyf/seedance-skill) · [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [short-drama-director](https://github.com/UncleWang2088/short-drama-director) · [fight-scene-director](https://github.com/ZzzAloong/fight-scene-director) · [ShortVideoDirector](https://github.com/wddxh/ShortVideoDirector) · [ai-film-skills](https://github.com/nigo-studio/ai-film-skills) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [seedance-2-5-prompting](https://github.com/babicat4242-svg/seedance-2-5-prompting) · [xiaxia](https://github.com/luanyi824-hash/xiaxia) · [ai-comic-drama-director-skills](https://github.com/djyy1031/ai-comic-drama-director-skills) · [visual-storytelling-skills](https://github.com/leynos/visual-storytelling-skills)

**MiniMax H3**（14）：[manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) · [minimax-h3-prompt-skill-T8](https://github.com/T8mars/minimax-h3-prompt-skill-T8) · [short-drama-production](https://github.com/suihe1/short-drama-production) · [h3-storyboard-skill](https://github.com/phileiny/h3-storyboard-skill) · [ComfyUI-Agent-Kit](https://github.com/SlavaSexton/ComfyUI-Agent-Kit) · [infinite-creation](https://github.com/SwotAtmk/infinite-creation) · [novel-to-manju](https://github.com/senmanx/novel-to-manju) · [fight-prompt-director](https://github.com/irenerachel/fight-prompt-director) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [acheng-director-skill](https://github.com/AharaOoO/acheng-director-skill) · [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) · [fight-scene-director](https://github.com/ZzzAloong/fight-scene-director) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director)

**可灵 Kling**（6）：[higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) · [ai-shortfilm-prompts](https://github.com/jnMetaCode/ai-shortfilm-prompts) · [lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) · [visual-storytelling-skills](https://github.com/leynos/visual-storytelling-skills)

**通义万相 Wan**（4）：[higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) · [ai-short-drama-skill](https://github.com/xixihhhh/ai-short-drama-skill) · [spark-video](https://github.com/JohnKeating1997/spark-video) · [hardcore-director](https://github.com/jlam00-dev/hardcore-director)

**ComfyUI（本地）**（5）：[ComfyUI-Agent-Kit](https://github.com/SlavaSexton/ComfyUI-Agent-Kit) · [infinite-creation](https://github.com/SwotAtmk/infinite-creation) · [jingju-skills](https://github.com/jxshow/jingju-skills) · [open-source-video-gen-skill](https://github.com/mini-yifan/open-source-video-gen-skill) · [Comfy-H3-Director](https://github.com/MIKA6941/Comfy-H3-Director)

**Nano Banana**（3）：[zy-cinematic-realism](https://github.com/popopo-99/zy-cinematic-realism) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator) · [visual-storytelling-skills](https://github.com/leynos/visual-storytelling-skills)

**Veo**（3）：[higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) · [ai-shortfilm-prompts](https://github.com/jnMetaCode/ai-shortfilm-prompts) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator)

**Sora**（2）：[ai-shortfilm-prompts](https://github.com/jnMetaCode/ai-shortfilm-prompts) · [vision_art_creator](https://github.com/ilkaydemiralay/vision_art_creator)

<a id="faq"></a>
## 常见问题

### 做 AI 短剧有哪些好用的 skill？

目前收录 82 个人工核对过的短剧 skill 项目（数据更新于 2026-10-17）。想从小说一路跑到分镜和视频提示词，先看[全流程](#group-pipeline)分组（23 个），星数最高的是 [shuohao-skills](https://github.com/eternityspring/shuohao-skills)、[drama-skills](https://github.com/zenstory-ai/drama-skills)、[manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill)；只缺某一步，就到[按创作阶段查找](#by-stage)里找对应阶段；不知道怎么搭配，可以从[推荐组合](#packs)开始。

### AI 短剧 skill（漫剧 skill）是什么？

给 AI 智能体（agent）装的能力包，也叫技能、技能包。一个 skill 就是一个文件夹，核心是一份 `SKILL.md` 说明，有的还带脚本和模板。装上之后，agent 会按里面的方法完成短剧制作的某一步，比如把小说拆成分集大纲、写竖屏短剧剧本、出分镜，或者给 Seedance 写视频提示词。

### Claude Code 或 Codex 能做 AI 短剧吗？

能。收录的 82 个项目里，80 个是标准 `SKILL.md` 格式，Claude Code、Codex 等支持 Agent Skills 的 agent 都能装；仓库里明确写了支持 Claude Code 的 25 个、支持 Codex 的 27 个。标准 skill 用 `npx skills add 作者/仓库名` 安装，每个分组末尾的「安装命令」里有现成命令。

### 能装进千问、豆包、龙虾（OpenClaw）、WorkBuddy 这些国产智能体吗？

能。标准 `SKILL.md` 格式的 skill，支持技能的智能体都能装：

- **千问办公**（阿里）：把 skill 文件夹放进 `~/.qwenworkcn/skills/`
- **豆包电脑版**（字节）：在「技能」页面点「+ 添加」，上传 skill 文件夹
- **龙虾 OpenClaw**：`npx skills add 作者/仓库名 -a openclaw`
- **WorkBuddy**（腾讯）：把 skill 文件夹放进 `~/.workbuddy/skills/`
- **Kimi Code、Qwen Code、CodeBuddy、Trae、Qoder、通义灵码、MiniMax Code**：`npx skills add 作者/仓库名 -a 名字`，名字依次是 `kimi-code-cli`、`qwen-code`、`codebuddy`、`trae`（国内版 `trae-cn`）、`qoder`（国内版 `qoder-cn`）、`lingma`、`minimax-code`

各条目只标仓库里明确写了的智能体，没标的不代表不能用。各家的安装目录见网站的[安装指南](https://shortdramaskills.com/guides/install/)。

### 有哪些适配 Seedance 的短剧 skill？

写明适配哪个视频模型的 42 个项目里，33 个适配 Seedance（即梦），是最多的；其次是 MiniMax H3 14 个、可灵 Kling 6 个。星数最高的 Seedance 项目是 [seedance2-skill](https://github.com/dexhunter/seedance2-skill)、[Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator)、[awesome-seedance](https://github.com/LearnPrompt/awesome-seedance)。完整对照见[按视频模型查找](#by-model)。

### 有短剧剧本 skill、分镜 skill 吗？

有。覆盖「剧本 · 对白」阶段的有 41 个，专做剧本的（只管 3 步以内）星数最高的是 [shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master)、[seedance-2-5-video-director](https://github.com/liyue-aigc/seedance-2-5-video-director)、[film-studio-skills](https://github.com/machina-exm/film-studio-skills)；覆盖「分镜 · 镜头设计」阶段的有 46 个，专做分镜的星数最高的是 [shanyin-director-master](https://github.com/Shanyin-ai/shanyin-director-master)、[visual-skills](https://github.com/smixs/visual-skills)、[lanshu-awesome-ai-video-kit](https://github.com/cclank/lanshu-awesome-ai-video-kit)。分组见[编剧：剧本 · 改编 · 审稿](#group-writing)和[分镜 · 视觉资产 · 视频提示词](#group-visual)。

### 小说转短剧：怎么用 AI 把小说改编成短剧剧本？

用改编类 skill，让 agent 按「拆小说 → 改编大纲 → 分集集纲和钩子 → 分集剧本 → 审稿」一步步做。收录的项目里覆盖「改编（小说 → 剧本）」阶段的有 21 个，星数最高的是 [shuohao-skills](https://github.com/eternityspring/shuohao-skills)、[drama-skills](https://github.com/zenstory-ai/drama-skills)、[Seedance2-Storyboard-Generator](https://github.com/liangdabiao/Seedance2-Storyboard-Generator)。改编前想先判断一本小说值不值得拍，看[上游：IP 评估与故事拆解](#group-source)（3 个）。

### skill 和扣子工作流、小云雀这类短剧智能体有什么区别？

扣子工作流、小云雀、LibTV 这类工具，流程在平台里搭、在平台里跑。skill 是装进你自己的智能体的一份方法说明，同一个 skill 可以在千问办公、豆包、龙虾、Claude Code 之间换着用，也能和别的 skill 组合、按自己的流程改。两者可以配合：用 skill 写剧本、拆分镜、写提示词，再到即梦、可灵、小云雀出片。能自己部署的开源短剧平台见[相关开源平台](#group-platform)。

### 这些 skill 安全吗？

收录前逐个核对过仓库说明、目录和文件。至今审过 198 个仓库：收录 82 个 skill 项目和 14 个开源平台，其余 102 个没收，原因逐条记在 [data/ignore.toml](data/ignore.toml)，其中有照搬热门 skill、再诱导下载安装包的仓库。正常的 skill 只是几份文本文件，用不着 exe 或 dmg。skill 可能附带脚本，安装前先读一遍它的 `SKILL.md`。

### 多久更新一次？

每周一自动刷新星数、最近更新时间和许可证，并搜索新仓库；新仓库人工核对后才收录，见[本周新增](#new)。

<a id="resources"></a>
## 相关资源

- [awesome-story-skills](https://github.com/UnderleveledBuilder/awesome-story-skills)：让大模型讲好故事的方法合集，剧本和故事这一侧（大纲、人物、审稿、去 AI 味）的方法看这里，附方法指南
- [PAMPAS-Lab/awesome-ai-short-drama](https://github.com/PAMPAS-Lab/awesome-ai-short-drama)：AI 短剧生产资源列表（英文），偏开源系统、研究论文和商业产品
- [zhaotoday/awesome-ai-video](https://github.com/zhaotoday/awesome-ai-video)：AI 视频生产资源全景，短剧平台、剪辑、ComfyUI、分发都有
- [anthropics/skills](https://github.com/anthropics/skills)：官方 Agent Skills 仓库，含规范和示例，想自己写 skill 可以从这里看起
- [vercel-labs/skills](https://github.com/vercel-labs/skills)：`npx skills` 安装工具，配套目录 [skills.sh](https://skills.sh)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)：通用 skill 聚合列表

## 参与贡献

推荐项目可以[提交 issue](../../issues/new?template=submit-skill.yml)，也可以直接改 `data/skills.toml` 发 PR，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。自己写的短剧 skill 也欢迎自荐。

<a id="badge"></a>
## 收录徽章

项目已被收录的作者，可以在自己的 README 里加上这个徽章：

[![收录于 Awesome Short Drama Skills](https://img.shields.io/badge/%E6%94%B6%E5%BD%95%E4%BA%8E-Awesome_Short_Drama_Skills-e8590c)](https://github.com/UnderleveledBuilder/awesome-short-drama-skills)

```markdown
[![收录于 Awesome Short Drama Skills](https://img.shields.io/badge/%E6%94%B6%E5%BD%95%E4%BA%8E-Awesome_Short_Drama_Skills-e8590c)](https://github.com/UnderleveledBuilder/awesome-short-drama-skills)
```

## 许可

[CC0 1.0](LICENSE)
