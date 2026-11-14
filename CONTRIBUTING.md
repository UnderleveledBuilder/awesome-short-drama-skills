# 参与贡献

## 收录标准

满足以下全部条件：

1. **服务短剧/漫剧创作**：选题、改编、剧本、审稿、分镜、视觉资产、视频提示词、出片，或直接服务这些环节的配套工具（如去 AI 味、通用编剧理论）。
2. **能装进 agent 使用**：标准 `SKILL.md`、Claude Code 插件，或结构清晰的提示词工作流。提示词形式的项目会标 📝。完整应用只收进「相关开源平台」，门槛是 1000★；应用里附带的 SKILL.md 如果能单独装进 agent 使用，可以按 skill 收录。
3. **有说明**：README 写清楚做什么、怎么装。
4. **还在维护**：近 6 个月有更新，或者内容足够稳定、不需要更新。
5. **不涉及真实个人**：不收以真实个人为对象生成内容的项目。

星数不是门槛，冷门但有独到方法的项目同样欢迎。fork 和高度重合的派生版不收，收原版。

## 怎么提交

**不想动代码**：[提交 issue](../../issues/new?template=submit-skill.yml)，填仓库地址和推荐理由即可。

**直接发 PR**：

1. 在 `data/skills.toml` 对应类型的分组下追加一条（字段见下文）。
2. 本地运行（需要 Python 3.11+，无第三方依赖）：

   ```bash
   python3 scripts/refresh.py --only owner/repo   # 抓取星数、许可证等元数据
   python3 scripts/build.py                       # 重新生成 README.md 和英文版 README.en.md
   ```

   跳过这一步也可以，合并后维护者会刷新并生成。
3. 提交 PR。CI 会校验数据格式。

## 字段说明

```toml
[[skills]]
repo    = "owner/repo"            # 必填，GitHub 仓库
desc    = "一句话说清做什么"         # 必填，≤ 80 字，写具体能力，少用形容词
desc_en = "One-line English desc"  # 可选，英文版用，≤ 260 个字符；不填时英文版显示中文
group   = "writing"               # 必填，类型，取值见 data/taxonomy.toml [groups]
stages  = ["drafting", "prompt"]  # 必填，覆盖的创作阶段，见 [stages]
format  = "skill"                 # 必填，skill / prompts / app
lang    = "zh"                    # 必填，zh / en / multi（指 skill 正文的语言）
agents  = ["claude-code"]         # 可选，仓库明确说明支持的 agent，见 [agents]
models  = ["seedance"]            # 可选，仓库明确说明适配的图像/视频模型，见 [models]
install = "npx skills add ..."    # 可选，默认生成 npx skills add owner/repo
name    = "显示名"                 # 可选，默认取仓库名
tier    = "featured"              # 可选，精选；默认 listed
note    = "需要注意的地方"           # 可选，显示在简介下方
note_en = "English note"          # 可选，note 的英文版
skill_paths = ["skills/"]         # 可选，只给 format = "app" 用：只把这些目录下的 SKILL.md 列到网站上
checked = 2026-10-13              # 可选，人工核对日期（TOML 日期，不加引号）
```

`agents` 和 `models` 只填仓库里明确写了的，不要推测。星数、许可证、最近更新时间、skill 数量由 `scripts/refresh.py` 自动抓取，不用手填。

网站项目页另有两份数据：`data/overviews.toml` 是每个项目的编者说明（中英文，写怎么用、具体做法和前提，只写从仓库核实过的事实）；`data/translations.json` 是仓库简介和 SKILL.md 说明的英文译文，以原文为键，原文变了就要重新翻译，没有译文的段落在英文页暂不显示，`build_site.py` 会提示还差几段。

英文版 README.en.md 的分类名和简介在 `data/taxonomy.toml` 的 `*_en` 字段，界面文字在 `scripts/build.py` 的 `UI`。PR 里不会写英文简介也没关系，维护者合并时补上。

## 收录徽章

项目被收录后，可以在自己的 README 里加上收录徽章，代码见 [README 的「收录徽章」一节](README.md#badge)。

## 不收录的项目

看过但决定不收的项目记在 `data/ignore.toml`，并写明原因，这样 `discover.py` 不会再把它们列为候选。

## 维护者工作流

| 脚本 | 作用 |
|---|---|
| `scripts/refresh.py` | 刷新元数据，报告改名、失效、归档、久未更新的仓库 |
| `scripts/build.py` | 生成 README.md 和 README.en.md；`--check` 检查是否最新，`--validate` 只校验数据 |
| `scripts/discover.py` | 按 taxonomy.toml 里的关键词搜候选项目，输出待审清单 |
| `scripts/index_skills.py` | 抓取每个仓库的 SKILL.md 名字和说明，写入 `data/skill_index.json` |
| `scripts/text_changes.py` | 列出本次刷新里新增或改动的仓库简介和 SKILL.md 说明（网站会直接展示），每周开成 issue 供人工过目 |
| `scripts/build_site.py` | 生成网站 [shortdramaskills.com](https://shortdramaskills.com) 到 `web/dist/`；`--serve` 本地预览 |
| `functions/_middleware.js` | 网站访问日志，写入 Cloudflare Analytics Engine（绑定名 `CRAWL_LOG`）；爬虫记 UA 和 IP，真人只记页面、来源、国家和网络运营商 |

每周一自动刷新元数据和 SKILL.md 索引、重新生成 README，并把新候选和第三方文字的变化开成 issue；网站在 Cloudflare Pages 上随每次推送重新生成。
