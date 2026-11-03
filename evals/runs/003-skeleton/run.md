# 第三轮：全剧骨架

- 需求：[premises/003-skeleton.md](../../premises/003-skeleton.md)。给同一张选题卡《验尸官的婚礼》写全剧骨架：整部剧怎么走，用来管住后面的分集大纲和剧本。要拍成 60 集竖屏短剧，每集 1–2 分钟，全部由 AI 拍；只交骨架，不写分集大纲和剧本正文，3000 字以内。
- 运行时间：2026-10-31（北京时间）
- 环境：Claude Code 2.1.314，模型 claude-opus-5-5，推理强度 high。所有参赛者和对照组用同一个模型、同样的工具权限，唯一的变量是装了哪个 skill。
- 每个参赛者跑 3 次，63 次运行全部保留，没有挑选。
- 运行器：[evals/run.py](../../run.py)；评审：[evals/judge.py](../../judge.py)。任何人都可以用同样的命令复现。

## 和第二轮有什么不同

- **比全剧骨架，大家拿同一张选题卡。** 前两轮各写各的故事，比出来的差别有一半是故事本身。这一轮把选题定死，所有参赛者写同一个故事的骨架，比的只是怎么把它铺成 60 集。
- **前两轮的 20 个 skill 全部参加。** 第一轮的剧本 skill 和第二轮的选题 skill 合在一起，加不装 skill 的对照组，共 21 个参赛者。
- **入口照第二轮的规矩重选。** 仓库里有专门做全剧骨架（总纲、全剧大纲、系列圣经）的 skill 就用它，那一步只能从主入口的流程走到的就用主入口。有 7 个和前两轮不同，原因写在 [contestants.toml](contestants.toml) 各自那一行。
- **固定回复多了半句。** 「骨架之后的分集大纲和剧本不用写」：有几个 skill 默认做完骨架接着出全本细纲，这半句只是把需求里的「只交骨架」重说一遍，对所有参赛者一样。
- **评委提示词只写目标。** 不再列评分维度，也不列什么不扣分、什么不加分；只告诉评委骨架要交给 AI 写成 60 集、全部由 AI 拍，不考虑拍摄成本和难度，目标是选出观众更可能追到最后的那一份，怎么判由它自己定。全文见下面「怎么评」。
- **需求里限了篇幅。** 3000 字以内。超过 3000 字的稿子按 3000 字截断后再评。
- **不抽故事卡、不分组。** 大家写的是同一个故事，撞题和人名这一轮不看。

## 统一指令

每次运行用同一条开场指令，skill 停下来时用同一条固定回复，不额外加指令：

- 开场（有入口 skill 的）：`/<入口 skill> 我要给一部短剧写全剧骨架，要求在 premise.md 里，写好存成文件放在当前目录。`
- 开场（工具箱型仓库）：`我要用已安装的 skill 给一部短剧写全剧骨架，要求在 premise.md 里，写好存成文件放在当前目录。`
- 对照组：`我要给一部短剧写全剧骨架，要求在 premise.md 里，写好存成文件放在当前目录。`
- 固定回复：`如果要我在几个方案里选，就选你最推荐的那个；其他要我定的，都按你推荐的来，不用再问我。请继续，直到 premise.md 要的全剧骨架写成文件；骨架之后的分集大纲和剧本不用写。`

agent 在一轮里没有提问、也没有再改文件，就算写完；连续三轮没有动静也停；最多 12 轮。

## 安全隔离

- 开跑前用清单收录时那套安全检查脚本查了 20 个参赛仓库（不调模型，查二进制和压缩包、安装钩子、远程执行、读敏感文件）：16 个通过，4 个「要看」。逐个看过，被标出的是 Windows 启动脚本、抓榜单时读网页登录态的脚本，和一个本地工作台网页读自己的会话 cookie，不是恶意代码，在沙箱里也用不上。详见 [timeline.toml](timeline.toml)。
- 命令在 Claude Code 的系统沙箱里运行：不能联网，不能读主目录，也不能读其他参赛者的工作目录；只能写自己的工作目录。绕过沙箱的开关已关闭。Claude Code 比第二轮新了 10 个小版本，所以开跑前用一个便宜的模型把这些限制重新逐项试过，子 agent 同样受限。
- Read、Write、Edit 工具另外用权限规则限制在同样的范围内。不连任何 MCP，不能用网页搜索和抓取。

## 参赛名单

格子里是骨架的字数（去掉空白计）、轮数、用时和按 API 价格折算的花费。

| 项目 | 测试版本 | 入口 | 装了几个 skill | 第 1 次 | 第 2 次 | 第 3 次 |
|---|---|---|---|---|---|---|
| 对照组（不装 skill）| — | — | 0 | 2,993 字<br>3 轮 · 4 分钟 · $1.99<br>[产出](baseline/run-1/output/) · [记录](baseline/run-1/transcript.md) | 2,903 字<br>4 轮 · 4 分钟 · $2.28<br>[产出](baseline/run-2/output/) · [记录](baseline/run-2/transcript.md) | 2,397 字<br>3 轮 · 4 分钟 · $1.90<br>[产出](baseline/run-3/output/) · [记录](baseline/run-3/transcript.md) |
| [eternityspring/shuohao-skills](https://github.com/eternityspring/shuohao-skills) | [`5612d2a`](https://github.com/eternityspring/shuohao-skills/tree/5612d2a0bd5f19d978c3ee19d1e42840335e3b4b) | `/novel-outline` | 7 | 2,299 字<br>4 轮 · 5 分钟 · $3.81<br>[产出](eternityspring__shuohao-skills/run-1/output/) · [记录](eternityspring__shuohao-skills/run-1/transcript.md) | 2,077 字<br>3 轮 · 5 分钟 · $3.01<br>[产出](eternityspring__shuohao-skills/run-2/output/) · [记录](eternityspring__shuohao-skills/run-2/transcript.md) | 2,572 字<br>3 轮 · 7 分钟 · $3.25<br>[产出](eternityspring__shuohao-skills/run-3/output/) · [记录](eternityspring__shuohao-skills/run-3/transcript.md) |
| [zenstory-ai/drama-skills](https://github.com/zenstory-ai/drama-skills) | [`33eb7fe`](https://github.com/zenstory-ai/drama-skills/tree/33eb7fece523fb705869dff3f4c95c58ce9b577d) | `/short-drama-develop` | 12 | 2,852 字<br>4 轮 · 6 分钟 · $4.67<br>[产出](zenstory-ai__drama-skills/run-1/output/) · [记录](zenstory-ai__drama-skills/run-1/transcript.md) | 2,998 字<br>6 轮 · 7 分钟 · $8.55<br>[产出](zenstory-ai__drama-skills/run-2/output/) · [记录](zenstory-ai__drama-skills/run-2/transcript.md) | 2,989 字<br>6 轮 · 7 分钟 · $8.76<br>[产出](zenstory-ai__drama-skills/run-3/output/) · [记录](zenstory-ai__drama-skills/run-3/transcript.md) |
| [lixiaoxiao9888-create/manju-laoli-skill](https://github.com/lixiaoxiao9888-create/manju-laoli-skill) | [`6f16955`](https://github.com/lixiaoxiao9888-create/manju-laoli-skill/tree/6f16955c57053d77ea0ffbdbbf3a7985a3e0080a) | `/short-drama-director` | 13 | 2,946 字<br>3 轮 · 4 分钟 · $4.66<br>[产出](lixiaoxiao9888-create__manju-laoli-skill/run-1/output/) · [记录](lixiaoxiao9888-create__manju-laoli-skill/run-1/transcript.md) | 2,575 字<br>3 轮 · 4 分钟 · $4.89<br>[产出](lixiaoxiao9888-create__manju-laoli-skill/run-2/output/) · [记录](lixiaoxiao9888-create__manju-laoli-skill/run-2/transcript.md) | 3,241 字<br>3 轮 · 6 分钟 · $6.63<br>[产出](lixiaoxiao9888-create__manju-laoli-skill/run-3/output/) · [记录](lixiaoxiao9888-create__manju-laoli-skill/run-3/transcript.md) |
| [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) | [`51115f1`](https://github.com/jtydhr88/screenwriting-skills/tree/51115f18d160aa8b2ac5813e4432b6f0b425358f) | `/sw-series-engine-bible` | 26 | 2,741 字<br>4 轮 · 6 分钟 · $4.57<br>[产出](jtydhr88__screenwriting-skills/run-1/output/) · [记录](jtydhr88__screenwriting-skills/run-1/transcript.md) | 3,096 字<br>4 轮 · 6 分钟 · $4.50<br>[产出](jtydhr88__screenwriting-skills/run-2/output/) · [记录](jtydhr88__screenwriting-skills/run-2/transcript.md) | 2,962 字<br>6 轮 · 5 分钟 · $6.55<br>[产出](jtydhr88__screenwriting-skills/run-3/output/) · [记录](jtydhr88__screenwriting-skills/run-3/transcript.md) |
| [Shanyin-ai/shanyin-screenwriting-master](https://github.com/Shanyin-ai/shanyin-screenwriting-master) | [`ca20ce2`](https://github.com/Shanyin-ai/shanyin-screenwriting-master/tree/ca20ce245ae028e64418393d6cf4688b7dbe3d89) | `/screenwriting-master` | 1 | 2,998 字<br>3 轮 · 5 分钟 · $3.19<br>[产出](Shanyin-ai__shanyin-screenwriting-master/run-1/output/) · [记录](Shanyin-ai__shanyin-screenwriting-master/run-1/transcript.md) | 2,993 字<br>4 轮 · 6 分钟 · $5.50<br>[产出](Shanyin-ai__shanyin-screenwriting-master/run-2/output/) · [记录](Shanyin-ai__shanyin-screenwriting-master/run-2/transcript.md) | 3,357 字<br>3 轮 · 5 分钟 · $3.41<br>[产出](Shanyin-ai__shanyin-screenwriting-master/run-3/output/) · [记录](Shanyin-ai__shanyin-screenwriting-master/run-3/transcript.md) |
| [lixiaoxiao9888-create/short-drama-factory](https://github.com/lixiaoxiao9888-create/short-drama-factory) | [`33d9988`](https://github.com/lixiaoxiao9888-create/short-drama-factory/tree/33d9988f5b9d83963cf1010b49f321fc09ea5a22) | `/short-drama-factory` | 1 | 2,882 字<br>3 轮 · 5 分钟 · $3.21<br>[产出](lixiaoxiao9888-create__short-drama-factory/run-1/output/) · [记录](lixiaoxiao9888-create__short-drama-factory/run-1/transcript.md) | 2,992 字<br>2 轮 · 4 分钟 · $1.90<br>[产出](lixiaoxiao9888-create__short-drama-factory/run-2/output/) · [记录](lixiaoxiao9888-create__short-drama-factory/run-2/transcript.md) | 2,801 字<br>3 轮 · 5 分钟 · $2.93<br>[产出](lixiaoxiao9888-create__short-drama-factory/run-3/output/) · [记录](lixiaoxiao9888-create__short-drama-factory/run-3/transcript.md) |
| [adoria111/emma-screenwriting-skills](https://github.com/adoria111/emma-screenwriting-skills) | [`da3aaae`](https://github.com/adoria111/emma-screenwriting-skills/tree/da3aaae532a1509a3a4b70af994ceb4e89e80681) | `/em-story-architect` | 24 | 3,172 字<br>4 轮 · 6 分钟 · $4.54<br>[产出](adoria111__emma-screenwriting-skills/run-1/output/) · [记录](adoria111__emma-screenwriting-skills/run-1/transcript.md) | 2,871 字<br>3 轮 · 5 分钟 · $2.60<br>[产出](adoria111__emma-screenwriting-skills/run-2/output/) · [记录](adoria111__emma-screenwriting-skills/run-2/transcript.md) | 3,073 字<br>3 轮 · 5 分钟 · $2.81<br>[产出](adoria111__emma-screenwriting-skills/run-3/output/) · [记录](adoria111__emma-screenwriting-skills/run-3/transcript.md) |
| [zhu5859243-free/hongguo-shortdrama-screenwriting](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting) | [`d9c235a`](https://github.com/zhu5859243-free/hongguo-shortdrama-screenwriting/tree/d9c235a6bc0be67d7563018cf3db49bcf58e72ab) | `/hongguo-shortdrama-screenwriting` | 1 | 3,002 字<br>3 轮 · 5 分钟 · $2.99<br>[产出](zhu5859243-free__hongguo-shortdrama-screenwriting/run-1/output/) · [记录](zhu5859243-free__hongguo-shortdrama-screenwriting/run-1/transcript.md) | 2,940 字<br>2 轮 · 7 分钟 · $2.71<br>[产出](zhu5859243-free__hongguo-shortdrama-screenwriting/run-2/output/) · [记录](zhu5859243-free__hongguo-shortdrama-screenwriting/run-2/transcript.md) | 2,981 字<br>3 轮 · 7 分钟 · $4.30<br>[产出](zhu5859243-free__hongguo-shortdrama-screenwriting/run-3/output/) · [记录](zhu5859243-free__hongguo-shortdrama-screenwriting/run-3/transcript.md) |
| [catyiqian/qianqianwriting](https://github.com/catyiqian/qianqianwriting) | [`436088b`](https://github.com/catyiqian/qianqianwriting/tree/436088b3bb2ebeae5cf26663fa92525512460f5b) | `/qianqianwriting` | 1 | 2,987 字<br>3 轮 · 4 分钟 · $1.83<br>[产出](catyiqian__qianqianwriting/run-1/output/) · [记录](catyiqian__qianqianwriting/run-1/transcript.md) | 3,259 字<br>8 轮 · 6 分钟 · $8.43<br>[产出](catyiqian__qianqianwriting/run-2/output/) · [记录](catyiqian__qianqianwriting/run-2/transcript.md) | 2,492 字<br>3 轮 · 3 分钟 · $1.65<br>[产出](catyiqian__qianqianwriting/run-3/output/) · [记录](catyiqian__qianqianwriting/run-3/transcript.md) |
| [Hao0321/ai-short-drama](https://github.com/Hao0321/ai-short-drama) | [`a1a00d3`](https://github.com/Hao0321/ai-short-drama/tree/a1a00d3949fedd74edb6830a79d189a2c76920db) | `/ai-short-drama` | 1 | 2,900 字<br>5 轮 · 4 分钟 · $3.72<br>[产出](Hao0321__ai-short-drama/run-1/output/) · [记录](Hao0321__ai-short-drama/run-1/transcript.md) | 3,000 字<br>4 轮 · 6 分钟 · $4.44<br>[产出](Hao0321__ai-short-drama/run-2/output/) · [记录](Hao0321__ai-short-drama/run-2/transcript.md) | 2,989 字<br>6 轮 · 5 分钟 · $6.54<br>[产出](Hao0321__ai-short-drama/run-3/output/) · [记录](Hao0321__ai-short-drama/run-3/transcript.md) |
| [zenstory-ai/oh-story-claudecode](https://github.com/zenstory-ai/oh-story-claudecode) | [`cc6397f`](https://github.com/zenstory-ai/oh-story-claudecode/tree/cc6397f2b07179262287f4ca358d281b16205765) | `/story-long-write` | 14 | 2,822 字<br>3 轮 · 4 分钟 · $3.14<br>[产出](zenstory-ai__oh-story-claudecode/run-1/output/) · [记录](zenstory-ai__oh-story-claudecode/run-1/transcript.md) | 2,969 字<br>3 轮 · 6 分钟 · $3.54<br>[产出](zenstory-ai__oh-story-claudecode/run-2/output/) · [记录](zenstory-ai__oh-story-claudecode/run-2/transcript.md) | 2,654 字<br>2 轮 · 4 分钟 · $1.88<br>[产出](zenstory-ai__oh-story-claudecode/run-3/output/) · [记录](zenstory-ai__oh-story-claudecode/run-3/transcript.md) |
| [lingfengQAQ/webnovel-writer](https://github.com/lingfengQAQ/webnovel-writer) | [`b38056e`](https://github.com/lingfengQAQ/webnovel-writer/tree/b38056ec3ae288af613c0af162d648e4a4e8825c) | `/webnovel-init` | 8 | 2,771 字<br>4 轮 · 4 分钟 · $2.66<br>[产出](lingfengQAQ__webnovel-writer/run-1/output/) · [记录](lingfengQAQ__webnovel-writer/run-1/transcript.md) | 2,873 字<br>4 轮 · 5 分钟 · $3.30<br>[产出](lingfengQAQ__webnovel-writer/run-2/output/) · [记录](lingfengQAQ__webnovel-writer/run-2/transcript.md) | 2,469 字<br>5 轮 · 3 分钟 · $3.29<br>[产出](lingfengQAQ__webnovel-writer/run-3/output/) · [记录](lingfengQAQ__webnovel-writer/run-3/transcript.md) |
| [0xsline/short-drama](https://github.com/0xsline/short-drama) | [`8979a42`](https://github.com/0xsline/short-drama/tree/8979a428c31a865421d661bdb606e24314b683a0) | `/short-drama` | 1 | 2,717 字<br>3 轮 · 5 分钟 · $2.84<br>[产出](0xsline__short-drama/run-1/output/) · [记录](0xsline__short-drama/run-1/transcript.md) | 2,995 字<br>3 轮 · 4 分钟 · $2.82<br>[产出](0xsline__short-drama/run-2/output/) · [记录](0xsline__short-drama/run-2/transcript.md) | 2,883 字<br>3 轮 · 5 分钟 · $3.00<br>[产出](0xsline__short-drama/run-3/output/) · [记录](0xsline__short-drama/run-3/transcript.md) |
| [Tomsawyerhu/Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill) | [`96709f4`](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill/tree/96709f477f4b59be856ebb10bec052dd0452b846) | `/Chinese-WebNovel-Skill` | 1 | 2,992 字<br>2 轮 · 5 分钟 · $2.09<br>[产出](Tomsawyerhu__Chinese-WebNovel-Skill/run-1/output/) · [记录](Tomsawyerhu__Chinese-WebNovel-Skill/run-1/transcript.md) | 2,993 字<br>3 轮 · 8 分钟 · $4.36<br>[产出](Tomsawyerhu__Chinese-WebNovel-Skill/run-2/output/) · [记录](Tomsawyerhu__Chinese-WebNovel-Skill/run-2/transcript.md) | 2,963 字<br>6 轮 · 6 分钟 · $6.90<br>[产出](Tomsawyerhu__Chinese-WebNovel-Skill/run-3/output/) · [记录](Tomsawyerhu__Chinese-WebNovel-Skill/run-3/transcript.md) |
| [xindoo/sumeru](https://github.com/xindoo/sumeru) | [`ac32d4a`](https://github.com/xindoo/sumeru/tree/ac32d4a5d68bb30583f34867cb972da415e6badc) | `/sumeru-outline` | 8 | 2,995 字<br>3 轮 · 6 分钟 · $3.76<br>[产出](xindoo__sumeru/run-1/output/) · [记录](xindoo__sumeru/run-1/transcript.md) | 2,796 字<br>4 轮 · 4 分钟 · $2.90<br>[产出](xindoo__sumeru/run-2/output/) · [记录](xindoo__sumeru/run-2/transcript.md) | 3,559 字<br>4 轮 · 5 分钟 · $4.05<br>[产出](xindoo__sumeru/run-3/output/) · [记录](xindoo__sumeru/run-3/transcript.md) |
| [LanyXiaosheng/bookflow-skill](https://github.com/LanyXiaosheng/bookflow-skill) | [`eb56fb5`](https://github.com/LanyXiaosheng/bookflow-skill/tree/eb56fb5c66ace4e0dd98027291c6912a2062c079) | `/bookflow-skill` | 1 | 2,514 字<br>7 轮 · 4 分钟 · $4.89<br>[产出](LanyXiaosheng__bookflow-skill/run-1/output/) · [记录](LanyXiaosheng__bookflow-skill/run-1/transcript.md) | 2,526 字<br>4 轮 · 5 分钟 · $3.02<br>[产出](LanyXiaosheng__bookflow-skill/run-2/output/) · [记录](LanyXiaosheng__bookflow-skill/run-2/transcript.md) | 2,769 字<br>4 轮 · 5 分钟 · $3.39<br>[产出](LanyXiaosheng__bookflow-skill/run-3/output/) · [记录](LanyXiaosheng__bookflow-skill/run-3/transcript.md) |
| [dama-cyber/Distilled-Novel-Toolbox](https://github.com/dama-cyber/Distilled-Novel-Toolbox) | [`350f2bd`](https://github.com/dama-cyber/Distilled-Novel-Toolbox/tree/350f2bd2b23c7400509897742b22d0f2b139338d) | 不指定 | 13 | 2,914 字<br>6 轮 · 5 分钟 · $5.14<br>[产出](dama-cyber__Distilled-Novel-Toolbox/run-1/output/) · [记录](dama-cyber__Distilled-Novel-Toolbox/run-1/transcript.md) | 2,995 字<br>6 轮 · 6 分钟 · $7.49<br>[产出](dama-cyber__Distilled-Novel-Toolbox/run-2/output/) · [记录](dama-cyber__Distilled-Novel-Toolbox/run-2/transcript.md) | 2,730 字<br>3 轮 · 4 分钟 · $1.95<br>[产出](dama-cyber__Distilled-Novel-Toolbox/run-3/output/) · [记录](dama-cyber__Distilled-Novel-Toolbox/run-3/transcript.md) |
| [tance-mang/chinese-webnovel-skills](https://github.com/tance-mang/chinese-webnovel-skills) | [`ecf552f`](https://github.com/tance-mang/chinese-webnovel-skills/tree/ecf552f6930e769d8bbf17818ad3d5a864a7a70b) | `/outline` | 33 | 3,027 字<br>4 轮 · 5 分钟 · $3.41<br>[产出](tance-mang__chinese-webnovel-skills/run-1/output/) · [记录](tance-mang__chinese-webnovel-skills/run-1/transcript.md) | 3,249 字<br>4 轮 · 5 分钟 · $3.55<br>[产出](tance-mang__chinese-webnovel-skills/run-2/output/) · [记录](tance-mang__chinese-webnovel-skills/run-2/transcript.md) | 2,989 字<br>3 轮 · 4 分钟 · $2.01<br>[产出](tance-mang__chinese-webnovel-skills/run-3/output/) · [记录](tance-mang__chinese-webnovel-skills/run-3/transcript.md) |
| [xiaofeng-928/chinese-longnovel-skill](https://github.com/xiaofeng-928/chinese-longnovel-skill) | [`1277f1e`](https://github.com/xiaofeng-928/chinese-longnovel-skill/tree/1277f1e886ad1263562b0d85d828ece675c97417) | `/chinese-longnovel-skill` | 1 | 2,501 字<br>4 轮 · 4 分钟 · $2.56<br>[产出](xiaofeng-928__chinese-longnovel-skill/run-1/output/) · [记录](xiaofeng-928__chinese-longnovel-skill/run-1/transcript.md) | 2,997 字<br>3 轮 · 4 分钟 · $1.97<br>[产出](xiaofeng-928__chinese-longnovel-skill/run-2/output/) · [记录](xiaofeng-928__chinese-longnovel-skill/run-2/transcript.md) | 2,614 字<br>6 轮 · 4 分钟 · $4.63<br>[产出](xiaofeng-928__chinese-longnovel-skill/run-3/output/) · [记录](xiaofeng-928__chinese-longnovel-skill/run-3/transcript.md) |
| [qingyabailu-git/webfiction-write](https://github.com/qingyabailu-git/webfiction-write) | [`2c0128d`](https://github.com/qingyabailu-git/webfiction-write/tree/2c0128db58a608c27177b63d012ae4011f230967) | `/fiction` | 15 | 2,837 字<br>4 轮 · 5 分钟 · $3.33<br>[产出](qingyabailu-git__webfiction-write/run-1/output/) · [记录](qingyabailu-git__webfiction-write/run-1/transcript.md) | 2,414 字<br>3 轮 · 4 分钟 · $1.97<br>[产出](qingyabailu-git__webfiction-write/run-2/output/) · [记录](qingyabailu-git__webfiction-write/run-2/transcript.md) | 2,913 字<br>3 轮 · 4 分钟 · $2.20<br>[产出](qingyabailu-git__webfiction-write/run-3/output/) · [记录](qingyabailu-git__webfiction-write/run-3/transcript.md) |

63 次运行按 API 价格折算共 $238.77；Opus 评审另花 $212.08（1,260 场盲比 $162.79，去掉截断说明的 376 场对照 $49.29）。

## 没测的

这一轮只请前两轮测过的 20 个 skill，为的是三轮的参赛者一样，能对着看。清单里其他能写大纲的 skill 没有加进来。

## 这一轮的限制

- **只用了一个模型。** 结论只说明在 claude-opus-5-5 下这些 skill 的表现，换模型可能不同。
- **只评骨架本身。** 这一轮没测照着骨架往下写出来的剧本好不好。骨架好不好，最终要看照着它写出来、拍出来、上线以后的数据。
- **只有一个故事。** 所有参赛者写的都是《验尸官的婚礼》，换一张选题卡，名次可能不同。
- **篇幅。** 63 份里有 10 份超过 3000 字，最长 3559 字。
  - 超过 3000 字的稿子截到 3000 字再评，截断处接一行说明。截掉的部分不评，也不因为超字数另外扣分。
  - 截断以后，两位评委仍然更看好超字数的那几次。这 10 份的单场胜率，Opus 判 68.5%，GPT 判 62.5%；没超的 53 份分别是 46.5%、47.6%。
  - 这个差距不是 skill 本身的强弱造成的。只在同一个 skill 的几次运行之间比，也是超字数的那次赢得多：Opus 判 68.5% 对 49.3%，GPT 判 62.5% 对 46.4%。
  - 也不是那行说明造成的。去掉说明重判，两位评委判被截稿子的胜率变化都在 5 个百分点以内，见 [review.md](review.md) 的「截断说明的检查」。
  - 把超字数稿子参与的场次全部去掉重算，两位评委各自的前五名还是同样五个 skill，只是顺序有变。
  - 有超字数稿子、去掉后在任一位评委那边掉了 3 名以上的有 4 个：
    - chinese-webnovel-skills：Opus 第 9 → 第 14，GPT 第 10 → 第 21；
    - emma-screenwriting-skills：Opus 第 2 → 第 5。它 3 次里 2 次超字数，去掉以后只剩 17 对，但两位评委仍排它在前五；
    - manju-laoli-skill：GPT 第 7 → 第 14；
    - sumeru：GPT 第 6 → 第 9。
- **写得长的赢得多。** 两份都没超 3000 字的场次里，长的那份 Opus 判赢 59.2%，GPT 判赢 54.2%。需求只限了上限，这一轮不做调整。
- **长输出读不到。** 有 6 次运行一条命令连着读了好几份很长的参考文件，Claude Code 把太长的输出存到主目录下的会话目录里，那里被隔离规则拦着：0xsline/short-drama 3 次、drama-skills 2 次、shanyin-screenwriting-master 1 次。它们都改成直接读 skill 目录里的原文件接着做；0xsline 第 3 次改读时有几份只读了前几百行。
- **记忆写不进去。** 有 4 次运行（含对照组 1 次）想把固定回复里的要求记进 Claude Code 的记忆目录，那个目录在主目录下，被隔离规则拦下。不影响交付，每个参赛者条件相同。
- **评审是 AI。** 盲比由和写稿相同的模型（claude-opus-5-5）完成，它看不到稿子出自谁。结论只代表 AI 评审的判断，不等于观众的选择。又请 GPT（gpt-6-astra）用一字不差的提示词复核：
  - 逐场的判断 841/1,260 一致（67%）；
  - 每对的最终结果 332/630 一致（52.7%，第二轮是 68%），不一致的标「有争议」；
  - 两位评审排出的名次，相关系数 0.66（第二轮 0.87）。

  这一轮两位评审分歧比第二轮大，所以 [review.md](review.md) 的结论只写两位一致的部分。
- **评审有位置偏差。** 同一对换个先后顺序再判，两次判同一份赢的，Opus 占 70.8%，GPT 占 81.1%。两位偏的方向相反：
  - Opus 偏向后看的那份：两次都判后一份的 28.4%，都判前一份的 0.8%；
  - GPT 偏向先看的那份：两次都判前一份的 13.7%，都判后一份的 5.2%。

  两次判得不一样的算平，不偏向哪一份。

## 怎么评

1. **找交付文件**：每次运行都只交了一个 .md 文件，就是全剧骨架；其余是 skill 自己的状态和数据文件（json），不算交付。按篇幅和正文里提到的集数查过，没有哪份顺手写了分集大纲或剧本，所以没有按内容截取。见 [deliverables.toml](deliverables.toml)。
2. **截断**：超过 3000 字（去掉空白计，不算文件名那行）的骨架，评委只看前 3000 字：在不超过 3000 字的最后一个换行处截断，后面接一行「（超过 3000 字，后面截掉了）」。需求里写明了 3000 字以内，这是按需求办，不往评委提示词里加话。63 份里截了 10 份。全判后按理由逐场打了标签（标签由 claude-sonnet-5-5 打）：只有一份被截的 352 场里，Opus 有 78 场把「后面截掉了」当成被截那份的缺点，其中被截那份输了 34 场，但没有一场把截断当成主要理由；GPT 一场也没有。
3. **匿名**：骨架拼成匿名稿，去掉仓库名、skill 名和作者名，随机编成三位数编号；开头留着交付文件名（如「全剧骨架.md」），文件名里没有 skill 名。这一轮只抹掉了 2 处，是 screenwriting-skills 两份稿子里的英文词 story（和 oh-story 的一个 skill 同名）。对应关系见 [blind_key.json](blind_key.json)。
4. **盲比**：21 个参赛者（含对照组）两两比，每对比 3 次（第 n 次运行对第 n 次运行），每次把先后顺序对调再比一次，共 1,260 场。两次都判它赢才算赢，一胜一负算平；赢一次记 1 分，平一次记 0.5 分，按积分排名。评委每场看到选题卡和两份骨架，提示词全文：

   > 下面是同一张选题卡写出的两份全剧骨架，甲和乙，出自不同作者。
   > 骨架之后要交给 AI 写成 60 集竖屏短剧，再全部由 AI 拍出来：没有演员和片场，画面和声音都由模型生成。不考虑拍摄成本和难度：场景和人物多少、AI 好不好拍，都不算长处也不算短处。
   >
   > 目标：选出照着它写下去、拍出来以后，观众更可能一集接一集追到最后的那一份。
   >
   > 怎么判由你决定。理由里引用原文。

   后面接选题卡、甲、乙三段。评委先写理由，再判甲或乙，不能判平。见 [duels.jsonl](duels.jsonl)。
5. **试判**：全判之前，先挑 5 对、每对两种顺序各判一次，共 10 场，看理由里还有没有拿场景和人物多少、好不好拍来加分，被截的稿子判得正不正常。
6. **复核**：GPT（gpt-6-astra，经 Codex CLI，只读沙箱、空目录）用一字不差的提示词和输出格式重判全部盲比，见 [duels-gpt.jsonl](duels-gpt.jsonl)。两位评审每次调用的提示词指纹和原始返回都在 [judge-raw/](judge-raw/)。
7. **截断说明的对照**：全判后两位评委都更看好被截的稿子，就把有被截稿子的 188 对、376 场去掉那行说明（截法不变），两位评委各重判一次。判决见 [duels-nonote.jsonl](duels-nonote.jsonl)、[duels-nonote-gpt.jsonl](duels-nonote-gpt.jsonl)，原始返回在 [judge-raw-nonote/](judge-raw-nonote/)。结果怎么用在判之前就定好了，结果见 [review.md](review.md)。

## 原始记录和核对

- [logs/runs/](logs/runs/)：63 次正式运行的原始日志（Claude Code 的 stream-json 输出）。
- [logs/checks/](logs/checks/)：正式运行前的 1 次沙箱自检，为什么做、发现了什么见 [timeline.toml](timeline.toml)。这一轮没有单独试点：运行器的代码和第二轮相同，只换了需求和两句话。
- 日志公开前用 [clean_logs.py](../../clean_logs.py) 清理过：去掉本机路径、用户名、额度用量和 Claude Code 的内部记录，其余原样保留。
- [blind/](blind/)：评审看到的 63 份匿名稿，原样。
- [MANIFEST.sha256](MANIFEST.sha256)：这一轮每个文件的 sha256 指纹。在仓库根目录运行 `python3 evals/verify.py 003-skeleton`，会核对指纹、从匿名稿重建两位评审每一次调用的提示词（包括去掉截断说明的对照）并和记录比对，再把网页上的数字重算一遍（统计代码见 [evals/stats.py](../../stats.py)）。
- skill 作者如果觉得自己的 skill 装错了、跑错了或者记录有误，可以提 issue，我们会对着原始日志核对，公开答复。
