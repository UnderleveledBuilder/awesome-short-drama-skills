"""实测记录页：/evals/<轮次>/ 下的总览、每次运行、每场盲比、故事卡、评审体检和过程记录。只出中文页。

由 build_site.py 调用。页面上的数字都是生成网站时从 evals/runs/<轮次>/ 现算的（见 evals/stats.py），
日志、匿名稿和评审提示词也都从仓库里的文件读，不手抄。只用标准库。
"""
from __future__ import annotations

import datetime as dt
import functools
import hashlib
import html
import json
import re
import sys
import tomllib
from pathlib import Path

from lib import ROOT

sys.path.insert(0, str(ROOT / "evals"))
import judge  # noqa: E402
import run as runner  # noqa: E402
from stats import Round, pct, wilson  # noqa: E402

e = functools.partial(html.escape, quote=True)
BJ = dt.timezone(dt.timedelta(hours=8))
TRACK = {"script": "剧本", "outline": "人物大纲"}
TRACK_PARTS = {"script": "第 1–3 集剧本", "outline": "人物小传和分集大纲"}
JUDGE_NAME = {"opus": "Opus（主评）", "gpt": "GPT（复核）"}
JUDGE_SHORT = {"opus": "Opus", "gpt": "GPT"}
JUDGE_MODEL = {"opus": f"{judge.MODEL}，推理强度 {judge.EFFORT}，经 Claude Code 无头模式，不给任何工具",
               "gpt": f"{judge.GPT_MODEL}，推理强度 {judge.GPT_EFFORT}，经 Codex CLI，只读沙箱、空目录"}
WTL = {"W": "赢", "T": "平", "L": "输"}
BLOCKED = re.compile(r"Permission to use \w+ has been denied|denied by your permission settings|Operation not permitted"
                     r"|deny network-outbound")
LOG_NAMES = {"pilot": "试点", "check": "沙箱自检"}


def bj(ts: str) -> dt.datetime:
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(BJ)


def hm(ts: str) -> str:
    return bj(ts).strftime("%H:%M")


def doc(text: str, cls: str = "doc") -> str:
    return f'<pre class="{cls}">{e(text)}</pre>'


def money(x: float) -> str:
    return f"${x:,.2f}"


def ci(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{pct(k, n)}（95% 区间 {lo:.0%}–{hi:.0%}）"


def wtl(rec: list[int] | None) -> str:
    return "-".join(map(str, rec or [0, 0, 0]))


def block_text(content) -> str:
    """工具返回的正文：字符串，或者一串文字块和图片块。"""
    if isinstance(content, str):
        return content
    out = []
    for b in content or []:
        if b.get("type") == "text":
            out.append(b["text"])
        elif b.get("type") == "image":
            out.append("（图片）")
        else:
            out.append(json.dumps(b, ensure_ascii=False))
    return "\n".join(out)


class Record:
    def __init__(self, site, premise: str, slug: str, title: str, repo_url: str, repo_path, display_name) -> None:
        self.site = site
        self.r = Round(premise)
        self.sp = self.r.sp
        self.tracks = TRACK
        self.premise = premise
        self.base = f"/evals/{slug}/"
        self.title = title
        self.repo_url = repo_url
        self.raw = f"{repo_url}/blob/main/evals/runs/{premise}/"
        self.tree = f"{repo_url}/tree/main/evals/runs/{premise}/"
        self.repo_path, self.display_name = repo_path, display_name
        self.deliv = tomllib.loads((self.r.dir / "deliverables.toml").read_text(encoding="utf-8"))
        self.timeline = tomllib.loads((self.r.dir / "timeline.toml").read_text(encoding="utf-8"))["event"]
        self.repos = [c["repo"] for c in self.r.roster["contestants"]]
        self.entry = {c["repo"]: c.get("entry") for c in self.r.roster["contestants"]}
        self.meta = {}
        for repo in self.repos:
            s = repo.replace("/", "__")
            for n in range(1, self.r.runs_per + 1):
                d = self.r.dir / s / f"run-{n}"
                self.meta[f"{s}.run-{n}"] = json.loads((d / "run.json").read_text(encoding="utf-8"))
        # 评审调用的原始返回和提示词指纹；第一轮只存了 GPT 的，第二轮起两位评审都有
        self.raw_calls = {j: {p.stem: json.loads(p.read_text(encoding="utf-8"))
                              for p in sorted((self.r.dir / "judge-raw" / j).glob("*.json"))} for j in JUDGE_NAME}

    # ── 名字和链接 ──

    def name(self, slug: str) -> str:
        if slug == "baseline":
            return "对照组（不装 skill）"
        s = self.site.d.by_repo.get(slug.replace("__", "/").lower())
        return self.display_name(s) if s else slug.replace("__", "/")

    def run_url(self, run: str) -> str:
        slug, n = run.rsplit(".", 1)
        return f"{self.base}runs/{slug.lower()}/{n}/"

    def run_link(self, run: str, text: str | None = None) -> str:
        slug, n = run.rsplit(".", 1)
        return f'<a href="{self.run_url(run)}">{e(text or self.name(slug) + " · 第 " + n.split("-")[1] + " 次")}</a>'

    def duel_url(self, track: str, run: str) -> str:
        return f"{self.base}duels/{track}-{self.r.code_of[run]}-{self.r.code_of['baseline.' + run.rsplit('.', 1)[1]]}/"

    def page(self, path: str, title: str, description: str, body: str, crumbs: list[tuple[str, str]] = (),
             wide: bool = False) -> None:
        trail = [("实测", "/evals/"), (self.title + "记录", self.base), *crumbs]
        if path == self.base:
            trail = trail[:2]
        self.site.page("zh", path, title=title, description=description, body=body, crumbs=trail,
                       zh_only=True, wide=wide)

    # ── 总览 ──

    def overview(self) -> None:
        r = self.r
        n_runs = len(self.meta)
        cost = sum(self.run_cost(k) for k in self.meta)
        prem = (ROOT / "evals" / "premises" / f"{self.premise}.md").read_text(encoding="utf-8")
        groups = {j: len(g) for j, g in r.groups.items()}
        n_calls = {j: len(d) for j, d in r.duels.items()}
        steps = [
            ("#input", "需求", "一份开放题：只写篇幅和三项交付，不给题材、人物和情节"),
            ("#runs", f"运行 {n_runs} 次", f"{len(self.repos) - 1} 个 skill 加 1 个不装 skill 的对照组，各跑 {r.runs_per} 次，"
                                         f"同一个模型、同一条开场指令和固定回复，按 API 价格折算共 {money(cost)}"),
            ("#runs", "找出三项交付", "每次运行可能写出很多文件，先认出哪个是人物小传、分集大纲、剧本，人工核对"),
            (f"{self.tree}blind", f"匿名打包 {len(list((r.dir / 'blind').glob('*.md')))} 份",
             "每次运行拆成小传、大纲、剧本三份，随机三位编号，抹掉 skill 名、仓库名和作者名"),
            (f"{self.base}stories/", f"故事卡 {len(r.cards)} 张，分组",
             "每份稿子抽一张故事卡，再按「换个名字就是同一个故事」分组："
             + "，".join(f"{JUDGE_NAME[j][:-4]} 分 {g} 组" for j, g in groups.items())),
            (f"{self.base}duels/", f"盲比 {len(r.verdicts('opus'))} 对",
             "每个 skill 的第 n 次运行和对照组的第 n 次比，剧本和人物大纲两项，甲乙对调各比一次："
             + "，".join(f"{JUDGE_NAME[j]} {c} 次" for j, c in n_calls.items())),
            ("#results", "汇总", "两种顺序都判它赢才算赢，都判对照组赢才算输，其余算平"),
            (f"{self.base}checks/", "评审体检", "换序是否一致、偏不偏甲、偏不偏长稿、引文找不找得到、两位评审合不合"),
            (f"{self.base}timeline/", "过程记录", "试点、自检、中途改过什么，按时间排，附原始日志"),
        ]
        flow = "".join(f'<li><a href="{h}"><b>{i}. {e(t)}</b><span>{e(s)}</span></a></li>'
                       for i, (h, t, s) in enumerate(steps, 1))
        body = [f"<h1>{e(self.title)}实测记录：剧本类 skill · 开放题</h1>",
                '<p class="lead">这一页把第一轮实测的全过程摆出来：给了 agent 什么、每次运行它做了什么、评审看到了什么、'
                '怎么判的。每一步都能点开看原始的输入和输出。页面上的数字都是生成网站时从仓库里的原始数据现算的。</p>',
                f'<p class="sub">结论和逐个点评见<a href="/evals/#round-1">实测页</a>。这里只放过程和证据。</p>',
                f'<ol class="flow">{flow}</ol>']

        body.append('<h2 id="input">给 agent 的全部输入</h2>'
                    '<p>每次运行都在一个新建的空目录里，目录里只有这份需求（premise.md）和装好的 skill。</p>'
                    f'<h3>需求原文（premise.md）</h3>{doc(prem)}'
                    '<h3>开场指令</h3><ul>'
                    f'<li>对照组：<code>{e(runner.TASK)}</code></li>'
                    f'<li>有入口 skill 的：<code>/入口skill名 {e(runner.TASK)}</code>，入口写在 '
                    f'<a href="{self.raw}contestants.toml">contestants.toml</a></li>'
                    f'<li>工具箱型、没有单一入口的：<code>{e(runner.TASK_TOOLKIT)}</code></li></ul>'
                    '<h3>之后每一轮的固定回复</h3>'
                    f'{doc(runner.REPLY.replace("{k}", "n"))}'
                    '<p>n 是运行编号：第 1 次运行选第 1 个方案，第 2 次选第 2 个，第 3 次选第 3 个。skill 不给方案就自己定。</p>'
                    '<h3>什么时候停</h3>'
                    f'<p>一轮结束后，如果 agent 没在提问、这一轮也没再改文件，而且目录里已经有产出，就算写完；'
                    f'连续三轮没改文件也停；最多 {runner.MAX_TURNS} 轮。代码见 '
                    f'<a href="{self.repo_url}/blob/main/evals/run.py">evals/run.py</a>。</p>')

        body.append(self.env_html())

        body.append(self.runs_html())

        body.append('<h2 id="results">汇总：和对照组比</h2>'
                    '<p>每格是三次运行的「赢-平-输」。一次运行算赢，要两种先后顺序都判它赢；都判对照组赢算输；其余算平。'
                    '主结果以 Opus 为准，GPT 是复核；两位评审结论不同的对子在<a href="'
                    f'{self.base}duels/">盲比列表</a>里标「有争议」。</p>')
        body.append(self.results_table())
        body.append(self.pooled())

        body.append(self.verify_html())
        self.page(self.base, f"{self.title}实测记录：10 个短剧剧本 skill 的全部运行、盲比和评审过程",
                  f"AI 短剧 skill {self.title}实测的完整记录：给 agent 的全部输入、{n_runs} 次运行的每一步、"
                  "匿名稿、每一场盲比的提示词和判决、评审体检和过程记录，数字从原始数据现算。", "".join(body))

    def env_html(self) -> str:
        """总览页的「环境和权限」一节。"""
        body: list[str] = []
        allow, deny = runner.ALLOWED + ["Edit(/<工作目录>/**)", "Write(/<工作目录>/**)"], runner.DENIED + [
            "Read(/<其他参赛者的工作目录>/**)", "Read(/<克隆的仓库>/**)", "Read(/<日志目录>/**)"]
        settings = {"sandbox": {"enabled": True, "failIfUnavailable": True, "autoAllowBashIfSandboxed": True,
                                "allowUnsandboxedCommands": False,
                                "network": {"allowedDomains": [], "allowLocalBinding": False},
                                "filesystem": {"denyRead": ["~/", "<所有工作目录的上一级>"], "allowRead": ["<工作目录>"]}}}
        m0 = next(iter(self.meta.values()))
        body.append('<h2 id="env">环境和权限</h2><dl class="facts">'
                    f'<dt>agent</dt><dd>Claude Code {e(m0["claude_code"].split()[0])}，无头模式（claude -p），'
                    f'模型 {e(m0["model"])}，推理强度 {e(m0["effort"])}</dd>'
                    '<dt>设置来源</dt><dd>只读工作目录里的项目设置（--setting-sources project），不连任何 MCP，'
                    '不读运行者本机的个人指令和记忆</dd>'
                    '<dt>权限模式</dt><dd>dontAsk：不在允许清单里的工具一律拒绝，不会停下来问人</dd>'
                    f'<dt>允许</dt><dd>{"、".join(f"<code>{e(a)}</code>" for a in allow)}</dd>'
                    f'<dt>拒绝</dt><dd>{"、".join(f"<code>{e(d)}</code>" for d in deny)}</dd>'
                    '<dt>命令行</dt><dd>python3 3.14、node 26 可用，没装 matplotlib 之类的第三方库；沙箱里不能联网，装不了包</dd>'
                    '</dl><p>Bash 全部放行，但每条命令都关在系统沙箱（macOS Seatbelt）里：不能联网，不能读运行者的主目录，'
                    '不能读别的参赛者的目录，只能写自己的工作目录。沙箱设置（尖括号是每次运行的实际路径）：</p>'
                    f'{doc(json.dumps(settings, ensure_ascii=False, indent=2), "code")}'
                    f'<p>这套设置是怎么定下来的、试过哪些不行，见<a href="{self.base}timeline/">过程记录</a>。</p>')
        return "".join(body)

    def runs_html(self) -> str:
        """总览页的运行列表：每个参赛者每次运行一格。"""
        body: list[str] = []
        r, n_runs = self.r, len(self.meta)
        body.append(f'<h2 id="runs">{n_runs} 次运行</h2><p>点进去能看到这次运行的每一轮、每一次工具调用和它的返回、'
                    '写出的全部文件。</p><table class="tbl"><thead><tr><th>参赛者</th>'
                    + "".join(f"<th>第 {n} 次</th>" for n in range(1, r.runs_per + 1)) + "</tr></thead><tbody>")
        for repo in self.repos:
            s = repo.replace("/", "__")
            cells = []
            for n in range(1, r.runs_per + 1):
                k = f"{s}.run-{n}"
                m = self.meta[k]
                cells.append(f'<td><a href="{self.run_url(k)}">{e(self.story_title(k))}</a><br><small>{m["turns"]} 轮 · '
                             f'{self.minutes(m)} 分钟 · {money(self.run_cost(k))}</small></td>')
            body.append(f"<tr><th>{self.name_cell(s)}</th>{''.join(cells)}</tr>")
        body.append("</tbody></table>")
        return "".join(body)

    def verify_html(self) -> str:
        """总览页的「怎么核对」一节。"""
        body: list[str] = []
        body.append('<h2 id="verify">怎么核对</h2><ul>'
                    f'<li>全部原始数据在 <a href="{self.tree}">GitHub</a>：每次运行的产出、问答记录、原始日志（logs/）、'
                    f'评审看到的匿名稿（blind/）、编号和出处的对应表（blind_key.json）、{self.raw_files}。</li>'
                    f'<li>原始日志公开前用 <a href="{self.repo_url}/blob/main/evals/clean_logs.py">clean_logs.py</a> 清理过：'
                    '去掉本机路径、用户名、额度用量和 Claude Code 的内部记录，其余原样保留。删了什么写在脚本开头。</li>'
                    f'<li><a href="{self.raw}MANIFEST.sha256">MANIFEST.sha256</a> 记着这一轮每个文件的 sha256 指纹。'
                    f'运行 <code>python3 evals/verify.py {e(self.premise)}</code> 会逐个核对指纹，重建每一场评审的提示词，'
                    f'{self.fingerprints}，再把本页的数字重算一遍。</li>'
                    '<li>skill 作者如果觉得自己的 skill 装错了、跑错了或者记录有误，'
                    f'可以在 <a href="{self.repo_url}/issues/new">GitHub 提 issue</a>，我们会对着原始日志核对，公开答复。</li></ul>')
        return "".join(body)

    def name_cell(self, slug: str) -> str:
        if slug == "baseline":
            return "对照组<br><small>不装 skill</small>"
        s = self.site.d.by_repo.get(slug.replace("__", "/").lower())
        return f'<a href="{self.repo_path(s)}">{e(self.name(slug))}</a>' if s else e(self.name(slug))

    def story_title(self, run: str) -> str:
        code = self.r.code_of[run]
        card = next(c for c in self.r.cards if c["code"] == code)
        return f"《{card['title']}》"

    def minutes(self, m: dict) -> int:
        return round((dt.datetime.fromisoformat(m["finished"]) - dt.datetime.fromisoformat(m["started"])).seconds / 60)

    @functools.cache
    def events(self, run: str) -> list[dict]:
        return [json.loads(l) for l in (self.r.dir / "logs" / "runs" / f"{run}.jsonl").open(encoding="utf-8")]

    def run_cost(self, run: str) -> float:
        return sum(ev.get("total_cost_usd") or 0 for ev in self.events(run) if ev["type"] == "result")

    def results_table(self) -> str:
        r = self.r
        rec = {j: r.record(j) for j in r.duels}
        disputed = r.disputed()
        head = "".join(f"<th>{TRACK[t]}<br><small>{JUDGE_NAME[j]}</small></th>" for t in TRACK for j in rec)
        rows = []
        for repo in self.repos[1:]:
            s = repo.replace("/", "__")
            cells = "".join(f"<td>{wtl(rec[j].get((s, t)))}</td>" for t in TRACK for j in rec)
            n_disp = sum(1 for t, run in disputed if run.startswith(s + "."))
            rows.append(f"<tr><th>{self.name_cell(s)}</th>{cells}<td>{n_disp or ''}</td></tr>")
        return (f'<table class="tbl"><thead><tr><th>参赛者</th>{head}<th>有争议</th></tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table><p class="sub">按参赛名单的顺序排列，不是名次。</p>')

    def pooled(self) -> str:
        r = self.r
        lines = []
        for j in r.duels:
            outs = r.outcomes(j)
            for t in TRACK:
                vs = [o for (tt, _), o in outs.items() if tt == t]
                w, n = vs.count("W"), len(vs)
                lines.append(f"<li>{JUDGE_NAME[j]}，{TRACK[t]}：{n} 对里 skill 赢 {w} 对，赢的比例 {ci(w, n)}，"
                             f"平 {vs.count('T')}，输 {vs.count('L')}</li>")
        lo, hi = wilson(3, 3)
        return ("<h3>误差有多大</h3>"
                f"<p>每个 skill 只跑了 {r.runs_per} 次。三次全赢，95% 置信区间也只能说到 {lo:.0%}–{hi:.0%}："
                "能看出方向，分不出名次，所以这里不排名。把 10 个 skill 合在一起看：</p>"
                f"<ul>{''.join(lines)}</ul>")

    # ── 每次运行 ──

    def run_pages(self) -> None:
        for run in self.meta:
            self.run_page(run)

    def prompts(self, run: str) -> list[str]:
        slug, n = run.rsplit(".", 1)
        md = (self.r.dir / slug / n / "transcript.md").read_text(encoding="utf-8")
        return [m.group(1) for m in re.finditer(r"## 第 \d+ 轮\n\n\*\*用户：\*\*\n\n(.*?)\n\n\*\*", md, re.S)]

    def run_page(self, run: str) -> None:
        slug, n = run.rsplit(".", 1)
        m = self.meta[run]
        r = self.r
        code = r.code_of[run]
        d = r.dir / slug / n
        events = self.events(run)
        tools = sum(1 for ev in events if ev["type"] == "assistant"
                    for b in ev["message"]["content"] if b.get("type") == "tool_use")
        repo = m["repo"]
        src = (f'<a href="https://github.com/{e(repo)}/tree/{e(m["commit"])}">{e(repo)}@{e(m["commit"][:8])}</a>'
               if m.get("commit") else "不装 skill")
        installed = "、".join(f"<code>{e(x)}</code>" for x in m.get("installed", [])) or "无"
        card = next((c for c in r.cards if c["code"] == code), None)  # 第三轮不抽故事卡
        duels = self.run_duels(run)
        body = [f"<h1>{e(self.name(slug))} · 第 {n.split('-')[1]} 次运行</h1>",
                f'<p class="lead">{self.run_lead(run, card)}</p>',
                '<dl class="facts">'
                f"<dt>skill</dt><dd>{src}</dd><dt>装进工作目录的 skill</dt><dd>{installed}</dd>"
                f"<dt>时间</dt><dd>{bj(m['started']).strftime('%Y-%m-%d %H:%M')}–{bj(m['finished']).strftime('%H:%M')}（北京时间），"
                f"{self.minutes(m)} 分钟</dd>"
                f"<dt>轮数</dt><dd>{m['turns']} 轮，工具调用 {tools} 次，按 API 价格折算 {money(self.run_cost(run))}</dd>"
                f'<dt>匿名编号</dt><dd>{code}（评审只看到这个编号）'
                + (f'· <a href="{self.base}stories/#card-{code}">故事卡</a>' if card else "") + "</dd>"
                f"{duels}"
                f'<dt>原始文件</dt><dd><a href="{self.tree}{e(slug)}/{n}">产出和问答记录</a> · '
                f'<a href="{self.raw}logs/runs/{e(run)}.jsonl">原始日志</a></dd></dl>']
        body.append(self.outputs(run, d))
        body.append("<h2>过程</h2><p class=\"sub\">按时间顺序。点开工具调用能看到完整的输入和返回；"
                    "思考的内容 Claude Code 不对外输出，日志里只有「在这里思考过多久」。</p>")
        body.append(self.render(events, self.prompts(run)))
        self.page(self.run_url(run), f"{self.name(slug)} 第 {n.split('-')[1]} 次运行 · {self.title}实测记录",
                  f"{self.name(slug)}在{self.title}实测里第 {n.split('-')[1]} 次运行的完整过程：每一轮的输入、"
                  "每一次工具调用和返回、写出的文件。", "".join(body), [("运行", self.base + "#runs")])

    def run_lead(self, run: str, card: dict) -> str:
        return f"写了{e(self.story_title(run))}。{e(card['logline'])}"

    def run_duels(self, run: str) -> str:
        """运行页上「这次运行参加了哪几场盲比」那一行。"""
        slug, n = run.rsplit(".", 1)
        return "" if slug == "baseline" else (
            "<dt>盲比</dt><dd>" + " · ".join(f'<a href="{self.duel_url(t, run)}">{TRACK[t]}：和对照组第 {n.split("-")[1]} 次比</a>'
                                            for t in TRACK) + "</dd>")

    deliv_label = "三项交付"
    fingerprints = "和 GPT 调用时记下的提示词指纹比对"
    raw_files = "故事卡、分组和每一场比较的判决"
    show_quotes = True
    length_rule = "提示词写明「篇幅长不加分」。"

    def outputs(self, run: str, d: Path) -> str:
        role = {}
        for part, files in self.deliv.get(run, {}).items():
            for f in files:
                role.setdefault(f, []).append(self.sp.parts[part])
        rows = []
        for p in sorted((d / "output").rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(d / "output"))
            tag = "".join(f'<span class="badge feat">{e(x)}</span>' for x in role.get(rel, []))
            if p.suffix.lower() in judge.TEXT:
                text = p.read_text(encoding="utf-8", errors="replace")
                rows.append(f'<details class="ev"><summary><code>{e(rel)}</code> {tag} <small>{len(text):,} 字</small>'
                            f'</summary><div>{doc(text)}</div></details>')
            else:
                rows.append(f'<p class="ev"><code>{e(rel)}</code> {tag} <small>非文本文件，'
                            f'<a href="{self.raw}{e(run.rsplit(".", 1)[0])}/{run.rsplit(".", 1)[1]}/output/{e(rel)}">在 GitHub 上看</a></small></p>')
        return (f"<h2>写出的文件</h2><p class=\"sub\">标了标签的是认定为{self.deliv_label}、拿去匿名打包的文件"
                f"（<a href=\"{self.raw}deliverables.toml\">deliverables.toml</a>）。</p>{''.join(rows)}")

    def render(self, events: list[dict], prompts: list[str] = ()) -> str:
        """把一份日志画成时间线。stream-json 里没有用户输入，按轮次从 prompts 补；会话记录里的用户输入原样画。"""
        results = {}
        for ev in events:
            if ev["type"] == "user" and isinstance(ev["message"]["content"], list):
                for b in ev["message"]["content"]:
                    if b.get("type") == "tool_result":
                        results[b["tool_use_id"]] = b
        out, turn = [], 0

        def start_turn(text: str) -> None:
            nonlocal turn
            turn += 1
            out.append(f'<h3 id="turn-{turn}">第 {turn} 轮</h3><div class="prompt"><b>输入：</b>{doc(text)}</div>')

        for ev in events:
            kind = ev["type"]
            sub = ' sub' if ev.get("parent_tool_use_id") else ""
            who = '<span class="badge">子 agent</span> ' if sub else ""
            if kind == "system" and ev.get("subtype") == "init":
                start_turn(prompts[turn] if turn < len(prompts) else "（输入没有记录）")
            elif kind == "system" and ev.get("subtype") in ("task_started", "task_notification"):
                verb = "开始" if ev["subtype"] == "task_started" else "结束"
                out.append(f'<p class="ev think">后台子 agent「{e(ev.get("description") or ev.get("summary") or "")}」{verb}</p>')
            elif kind == "attachment":
                out.append(f'<details class="ev"><summary>Claude Code 写进上下文的沙箱说明</summary>'
                           f'<div>{doc(ev["attachment"].get("content", ""))}</div></details>')
            elif kind == "user":
                c = ev["message"]["content"]
                texts = [c] if isinstance(c, str) else [b["text"] for b in c if b.get("type") == "text"]
                if not texts:
                    continue
                if ev.get("isMeta") or ev.get("isSynthetic"):
                    out.append(f'<details class="ev{sub}"><summary>Claude Code 自动加进对话的内容（多为 skill 正文）'
                               f'<small> {sum(map(len, texts)):,} 字</small></summary><div>{doc(chr(10).join(texts))}</div></details>')
                else:
                    start_turn("\n".join(texts))
            elif kind == "assistant":
                for b in ev["message"]["content"]:
                    t = b.get("type")
                    if t == "thinking":
                        ms = ev.get("thinking_duration_ms")
                        out.append(f'<p class="ev think{sub}">{who}思考{f" {ms / 1000:.0f} 秒" if ms and ms >= 1000 else ""}</p>')
                    elif t == "text" and b["text"].strip():
                        out.append(f'<div class="ev say{sub}">{who}<b>Agent：</b>{doc(b["text"])}</div>')
                    elif t == "tool_use":
                        out.append(self.tool(b, results.get(b["id"]), sub, who))
            elif kind == "result":
                bits = []
                if ev.get("duration_ms"):
                    bits.append(f"耗时 {ev['duration_ms'] / 60000:.1f} 分钟")
                if ev.get("total_cost_usd"):
                    bits.append(f"按 API 价格折算 {money(ev['total_cost_usd'])}")
                out.append(f'<p class="ev end">这一轮结束{"：" + "，".join(bits) if bits else ""}</p>')
        return "".join(out)

    def tool(self, b: dict, res: dict | None, sub: str, who: str) -> str:
        inp = b.get("input", {})
        name = b["name"]
        brief = {"Bash": inp.get("description") or inp.get("command", ""), "Read": inp.get("file_path", ""),
                 "Write": inp.get("file_path", ""), "Edit": inp.get("file_path", ""), "Skill": inp.get("skill", ""),
                 "Agent": inp.get("description", ""), "Glob": inp.get("pattern", ""), "Grep": inp.get("pattern", ""),
                 "TodoWrite": f"更新待办（{len(inp.get('todos', []))} 项）"}.get(name, json.dumps(inp, ensure_ascii=False))
        brief = re.sub(r"/scratch/[\w.-]+/ws/[\w.-]+/[\w.-]+/run-\d+/?", "./", str(brief)).splitlines()[0] if brief else ""
        text = block_text(res.get("content")) if res else "（没有记录到返回）"
        bad = bool(res) and bool(BLOCKED.search(text))
        flag = '<span class="badge bad">被拦下</span> ' if bad else '<span class="badge">报错</span> ' if res and res.get("is_error") else ""
        if name == "Bash":
            shown = inp.get("command", "")
        elif name in ("Write",):
            shown = f"{inp.get('file_path')}\n\n{inp.get('content', '')}"
        elif name == "Edit":
            shown = f"{inp.get('file_path')}\n\n—— 原文 ——\n{inp.get('old_string', '')}\n\n—— 改成 ——\n{inp.get('new_string', '')}"
        elif name == "Agent":
            shown = inp.get("prompt", "")
        else:
            shown = json.dumps(inp, ensure_ascii=False, indent=1)
        return (f'<details class="ev tool{sub}" id="t-{e(b["id"])}"><summary>{who}{flag}<b>{e(name)}</b> '
                f'{e(brief[:140])}</summary><div><p class="sub">输入</p>{doc(shown, "code")}'
                f'<p class="sub">返回</p>{doc(text, "code")}</div></details>')

    # ── 试点和自检的日志 ──

    def log_pages(self) -> None:
        for p in sorted((self.r.dir / "logs").glob("[pc]*/*.jsonl")):
            events = [json.loads(l) for l in p.open(encoding="utf-8")]
            title = self.log_title(p.stem)
            ts = [ev["timestamp"] for ev in events if ev.get("timestamp")]
            when = f"{bj(ts[0]).strftime('%Y-%m-%d %H:%M')}–{hm(ts[-1])}（北京时间）" if ts else ""
            models = sorted({ev["message"].get("model") for ev in events if ev["type"] == "assistant"} - {None})
            body = (f"<h1>{e(title)}</h1><p class=\"lead\">{when}，模型 {e('、'.join(models))}。为什么做、发现了什么，见"
                    f'<a href="{self.base}timeline/">过程记录</a>。这次的产出不进评审。</p>'
                    f'<p class="sub"><a href="{self.raw}logs/{p.parent.name}/{p.name}">原始日志</a>'
                    "（Claude Code 自己留的会话记录，清理方式和正式运行相同）</p>"
                    + self.render(events))
            self.page(f"{self.base}logs/{p.stem.lower()}/", f"{title} · {self.title}实测记录",
                      f"{self.title}实测正式开始前的{title}的完整日志。", body, [("过程记录", self.base + "timeline/")])

    def log_title(self, stem: str) -> str:
        kind, rest = stem.split("-", 1)
        num, _, who = rest.partition(".")
        return f"{LOG_NAMES[kind]} {num}" + (f" · {self.name(who)}" if who else "")

    # ── 盲比 ──

    def duel_pages(self) -> None:
        r = self.r
        rec = {j: r.verdicts(j) for j in r.duels}
        outs = {j: r.outcomes(j) for j in r.duels}
        disputed = r.disputed()
        rows = {t: [] for t in TRACK}
        for (t, run) in sorted(rec["opus"], key=lambda k: (self.repos.index(k[1].rsplit(".", 1)[0].replace("__", "/")), k[1])):
            self.duel_page(t, run, {j: rec[j].get((t, run), []) for j in rec}, {j: outs[j].get((t, run)) for j in outs},
                           (t, run) in disputed)
            cells = "".join(f"<td>{WTL.get(outs[j].get((t, run)), '—')}"
                            f"<br><small>{' / '.join(WTL[v] for _, v in rec[j].get((t, run), []))}</small></td>" for j in rec)
            flag = '<span class="badge bad">有争议</span>' if (t, run) in disputed else ""
            rows[t].append(f'<tr><td><a href="{self.duel_url(t, run)}">{r.code_of[run]} 对 '
                           f'{r.code_of["baseline." + run.rsplit(".", 1)[1]]}</a></td><td>{self.run_link(run)}</td>{cells}<td>{flag}</td></tr>')
        a = r.agreement()
        body = [f"<h1>盲比：{len(rec['opus'])} 对，每对两种顺序</h1>",
                '<p class="lead">每个 skill 的第 n 次运行，和对照组的第 n 次运行比；剧本和人物大纲分开比。'
                '每对甲乙对调各比一次。评审只看到匿名稿和三位编号。</p>'
                f'<p>主评审是 {e(JUDGE_MODEL["opus"])}；复核评审是 {e(JUDGE_MODEL["gpt"])}，'
                '用一字不差的提示词和输出格式重判一遍。'
                + (f"两位评审逐场判断一致 {a['same']}/{a['calls']}，最终结果一致 {a['pairs_same']}/{a['pairs']} 对，"
                   f"不一致的 {len(disputed)} 对标「有争议」，主结果仍以 Opus 为准。" if a else "") + "</p>"
                '<p class="sub">每格先写最终结果（参赛 skill 的赢、平、输），下面小字是两种顺序各自的判决。</p>']
        for t in TRACK:
            head = "".join(f"<th>{JUDGE_NAME[j]}</th>" for j in rec)
            body.append(f'<h2 id="{t}">{TRACK[t]}</h2><table class="tbl"><thead><tr><th>编号</th><th>参赛的这次运行</th>'
                        f'{head}<th></th></tr></thead><tbody>{"".join(rows[t])}</tbody></table>')
        self.page(f"{self.base}duels/", f"盲比列表 · {self.title}实测记录",
                  f"{self.title}实测全部盲比：每个 skill 和对照组两两比剧本和人物大纲，两种顺序、两位评审的判决。",
                  "".join(body), [("盲比", self.base + "duels/")])

    def duel_page(self, track: str, run: str, pairs: dict[str, list], final: dict[str, str | None], disputed: bool) -> None:
        r = self.r
        x = r.code_of[run]
        base_run = "baseline." + run.rsplit(".", 1)[1]
        y = r.code_of[base_run]
        sides = "".join(
            f'<article class="side" data-code="{c}"><h3>稿子 {c} <small>{len(r.packet(c, track)):,} 字</small></h3>'
            f'{doc(r.packet(c, track), "doc scroll")}</article>' for c in (x, y))
        body = [f"<h1>{TRACK[track]}盲比：稿子 {x} 对 {y}</h1>",
                f'<p class="lead">评审比的是两份{TRACK_PARTS[track]}。下面是评审看到的原文，编号随机，看不出出处；'
                '出处在页面最后揭晓。</p>',
                f'<section class="duel" data-round="{e(self.premise)}" data-track="{track}" data-a="{x}" data-b="{y}">'
                f'<div class="pair">{sides}</div></section>',
                "<h2>判决</h2>"]
        for a, b in ((x, y), (y, x)):
            calls = {j: next((d for d, _ in pairs[j] if d["a"] == a), None) for j in pairs}
            body.append(f"<h3>甲 = {a}，乙 = {b}</h3>")
            dims = list(judge.track_dims(track))
            head = "".join(f"<th>{JUDGE_NAME[j]}</th>" for j in calls)

            def mark(v: str | None) -> str:
                return {"甲": f"甲（{a}）", "乙": f"乙（{b}）", "平": "平"}.get(v, "—")

            trs = "".join(f"<tr><th>{e(dm)}</th>" + "".join(f"<td>{mark(c and c['dims'].get(dm))}</td>" for c in calls.values())
                          + "</tr>" for dm in dims)
            trs += "<tr><th>总体</th>" + "".join(f"<td><b>{mark(c and c['winner'])}</b></td>" for c in calls.values()) + "</tr>"
            body.append(f'<table class="tbl"><thead><tr><th>维度</th>{head}</tr></thead><tbody>{trs}</tbody></table>')
            for j, c in calls.items():
                if c:
                    body.append(f"<p><b>{JUDGE_NAME[j]}的理由：</b>{e(c['reason'])}</p>")
            body.append(self.prompt_box(track, a, b))
        verdict = " · ".join(f"{JUDGE_NAME[j]}：{self.name(run.rsplit('.', 1)[0])} {WTL.get(o, '—')}"
                             for j, o in final.items())
        body.append(f'<h2>结果</h2><p>{e(verdict)}{" <span class=\"badge bad\">有争议</span>" if disputed else ""}</p>'
                    '<p class="sub">两种顺序都判它赢才算赢，都判对照组赢才算输，其余算平。</p>')
        body.append(f'<details class="ev reveal"><summary><b>揭晓出处</b></summary><div><ul>'
                    f"<li>稿子 {x}：{self.run_link(run)}</li><li>稿子 {y}：{self.run_link(base_run)}</li></ul></div></details>")
        self.page(self.duel_url(track, run), f"{TRACK[track]}盲比 {x} 对 {y} · {self.title}实测记录",
                  f"{self.title}实测的一场{TRACK[track]}盲比：两份匿名稿原文、评审收到的完整提示词、两种顺序和两位评审的判决。",
                  "".join(body), [("盲比", self.base + "duels/")], wide=True)

    def prompt_box(self, track: str, a: str, b: str) -> str:
        prompt = self.r.prompt(track, a, b)
        sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        check = ""
        for j, calls in self.raw_calls.items():
            raw = calls.get(f"duel.{track}.{a}.{b}")
            if raw:
                ok = raw["prompt_sha256"] == sha
                check += (f"{JUDGE_SHORT[j]} 调用时记下的指纹 {'一致' if ok else '不一致'}；"
                          f'<a href="{self.raw}judge-raw/{j}/duel.{track}.{a}.{b}.json">{JUDGE_SHORT[j]} 的原始返回</a>。')
        schema = json.dumps(judge.duel_schema(track, self.sp), ensure_ascii=False, indent=1)
        return (f'<details class="ev"><summary>评审收到的完整提示词 <small>sha256 {sha[:12]}…</small></summary><div>'
                f'<p class="sub">系统提示：{e(self.sp.duel_system)}</p>{doc(prompt)}'
                f'<p class="sub">要求的输出格式（JSON Schema）</p>{doc(schema, "code")}'
                f'<p class="sub">这份提示词由 judge.py 的 duel_prompt() 从匿名稿重建，sha256 {sha}。{check}'
                + ("两位评审用的是同一段代码。" if self.raw_calls["opus"] else
                   "Opus 两边用的是同一段代码；Opus 当时只存了解析后的判决，没存原始返回。") + "</p></div></details>")

    # ── 故事卡和分组 ──

    def stories(self) -> None:
        r = self.r
        cards = {c["code"]: c for c in r.cards}
        body = [f"<h1>故事卡和故事类型</h1>",
                f'<p class="lead">每份匿名稿抽一张故事卡，只摘稿子里有的内容，不评好坏；再把 {len(cards)} 张卡按'
                '「换个名字和细节就差不多是同一个故事」分组，看同一个 skill 的几次、不同 skill 之间，故事像不像。</p>']
        body.append('<h2 id="method">怎么抽、怎么分</h2>'
                    f'<p>抽卡（{e(JUDGE_MODEL["opus"])}）：系统提示「你负责如实摘录信息。」，提示词是下面这段，后面接这份稿子的'
                    '人物小传、分集大纲和剧本全文。</p>' + doc(judge.CARD.replace("{text}", "<三项交付全文>"))
                    + '<p>分组：系统提示「' + e(judge.CLUSTER_SYSTEM) + '」，提示词如下，每部剧一行：编号、剧名、题材、一句话梗概、主角、核心设定。</p>'
                    + doc(judge.CLUSTER.replace("{n}", str(len(cards))).replace("{lines}", "<每部剧一行>"))
                    + '<p class="sub">GPT 复核时，各行按编号排序后用固定种子（20261018）打乱，谁都能重建出一样的提示词；'
                      'Opus 分组时各行的顺序没有固定，也没存下来，所以 Opus 那次的提示词只能确定内容、确定不了顺序。</p>')
        for j, groups in r.groups.items():
            s = r.same_type(j)
            body.append(f'<h2 id="groups-{j}">{JUDGE_NAME[j]}分出的 {len(groups)} 种故事类型</h2>'
                        f"<p>同一个参赛者的几次运行，两两落进同一种类型：{s['within']}/{s['within_n']} 对（{pct(s['within'], s['within_n'])}）；"
                        f"不同参赛者之间：{s['between']}/{s['between_n']} 对（{pct(s['between'], s['between_n'])}）。</p>")
            items = []
            for g in sorted(groups, key=lambda g: -len(g["codes"])):
                members = "、".join(f'<a href="#card-{c}">{c}</a>（{self.run_link(r.key[c], self.name(r.key[c].rsplit(".", 1)[0]))}）'
                                   for c in g["codes"])
                items.append(f'<li><b>{e(g["name"])}</b>（{len(g["codes"])} 部）：{e(g["pattern"])}<br><small>{members}</small></li>')
            body.append(f'<ul class="groups">{"".join(items)}</ul>')
        agree = r.cluster_agreement()
        if agree is not None:
            body.append(f"<p>两位评审的分组有多像：调整兰德指数 {agree:.2f}（1 是完全一样，0 是和随机分组一样）。"
                        "分组本来就有松紧之分，所以看的是两边是否都得出「同一个 skill 内部更像」。</p>")
        n, who = r.name_count("小满")
        pw = r.paywalls()
        body.append('<h2 id="defaults">换哪个 skill 都在的默认选择</h2><ul>'
                    f"<li>故事卡人名里有「小满」的：{n} 份，{len(self.repos)} 个参赛组里有 {who} 个写过。</li>"
                    + "".join(f"<li>故事卡人名里有「{x}」的：{r.name_count(x)[0]} 份。</li>" for x in ("国栋", "顾承泽"))
                    + f"<li>第一个付费卡点：" + "，".join(f"第 {k} 集 {v} 份" for k, v in sorted(pw.items(), key=lambda kv: str(kv[0])))
                    + "。</li></ul>")
        body.append(f'<h2 id="cards">{len(cards)} 张故事卡</h2>')
        fields = [("genre", "题材"), ("logline", "梗概"), ("era_place", "时代地点"), ("hook_device", "核心设定"),
                  ("protagonist", "主角"), ("opening", "第 1 集开场"), ("first_paywall_episode", "第一个付费卡点"),
                  ("ending", "结局")]
        for code in sorted(cards, key=lambda c: r.key[c]):
            c = cards[code]
            dl = "".join(f"<dt>{lab}</dt><dd>{e(str(c[k]))}</dd>" for k, lab in fields)
            dl += f"<dt>人名</dt><dd>{e('、'.join(c['names']))}</dd>"
            body.append(f'<details class="ev" id="card-{code}"><summary><b>{code}</b> 《{e(c["title"])}》 '
                        f'<small>{self.name(r.key[code].rsplit(".", 1)[0])} · 第 {r.key[code].rsplit("-", 1)[1]} 次</small></summary>'
                        f'<div><dl class="facts">{dl}</dl><p class="sub">{self.run_link(r.key[code], "这次运行")} · '
                        + " · ".join(f'<a href="{self.raw}blind/{code}.{p}.md">匿名稿·{judge.PARTS[p]}</a>' for p in judge.PARTS)
                        + "</p></div></details>")
        body.append(f'<p class="sub">原始数据：<a href="{self.raw}cards.jsonl">cards.jsonl</a> · '
                    + " · ".join(f'<a href="{self.raw}{f}">{f}</a>' for f in ("clusters.json", "clusters-gpt.json")
                                 if (r.dir / f).exists()) + "</p>")
        self.page(f"{self.base}stories/", f"故事卡和故事类型 · {self.title}实测记录",
                  f"{self.title}实测 {len(cards)} 份稿子的故事卡和故事类型分组：同一个 skill 的几次运行和不同 skill 之间，故事有多像。",
                  "".join(body), [("故事卡", self.base + "stories/")])

    # ── 评审体检 ──

    def checks(self) -> None:
        r = self.r
        body = ["<h1>评审体检</h1>",
                '<p class="lead">AI 评审也会偏心：偏向先看到的那份、偏向写得长的、编造引文。这一页把能查的都查一遍，'
                '数字从判决记录现算。</p>']
        rows = []
        for j in r.duels:
            for t in self.tracks:
                c, p, ln = r.consistency(j, t), r.position(j, t), r.length(j, t)
                dec = p["甲"] + p["乙"]
                rows.append(f"<tr><th>{JUDGE_NAME[j]} · {self.tracks[t]}</th><td>{c.get('same', 0)}/{c['pairs']}"
                            f"<br><small>完全翻转 {c.get('flip', 0)}</small></td>"
                            f"<td>甲 {p['甲']} · 乙 {p['乙']} · 平 {p['平']}<br><small>判甲 {ci(p['甲'], dec)}</small></td>"
                            f"<td>{ln['longer']}/{ln['decided']}<br><small>{ci(ln['longer'], ln['decided'])}</small></td></tr>")
        body.append('<h2 id="bias">换序、位置、篇幅</h2>'
                    '<ul><li><b>换序一致</b>：同一对稿子甲乙对调后，结论不变的对数。「完全翻转」是两次各判一边赢，'
                    '说明这对稿子评审自己也拿不准，按规则算平。</li>'
                    '<li><b>位置</b>：判甲、判乙各多少次。每对稿子两种顺序都比过，不偏的评审判甲应该接近一半。</li>'
                    f'<li><b>篇幅</b>：分出胜负的比较里，判长的那份赢的次数。{self.length_rule}</li></ul>'
                    f'<table class="tbl"><thead><tr><th></th><th>换序一致</th><th>位置</th><th>判长的赢</th></tr></thead>'
                    f'<tbody>{"".join(rows)}</tbody></table>' + self.length_note())
        if self.show_quotes:
            body.append(self.quotes_html())
        a = r.agreement()
        if a:
            dims = "".join(f"<li>{e(k)}：{v[0]}/{v[1]}（{pct(*v)}）</li>" for k, v in a["dims"].items())
            disp = "".join(f'<li><a href="{url}">{e(label)}</a></li>' for url, label in self.disputed_items())
            body.append('<h2 id="agreement">两位评审合不合</h2>'
                        f'<p>同一批提示词，Opus 和 GPT 各判一遍。</p><ul>'
                        f"<li>逐场（{a['calls']} 场）总体判断一致：{a['same']}/{a['calls']}（{pct(a['same'], a['calls'])}），"
                        f"Cohen's kappa {a['kappa']:.2f}（扣掉碰巧一致的部分；1 是完全一致，0 是和瞎猜一样）。</li>"
                        f"<li>每对的最终结果（赢、平、输）一致：{a['pairs_same']}/{a['pairs']}，kappa {a['pairs_kappa']:.2f}。</li>"
                        + (f"<li>分维度逐场一致：<ul>{dims}</ul></li>" if dims else "") + "</ul>"
                        f'<h3>有争议的 {len(r.disputed())} 对</h3><ul>{disp}</ul>')
        body.append('<h2 id="limits">查不出来的</h2><ul>' + "".join(f"<li>{x}</li>" for x in self.limits()) + "</ul>")
        body.append(self.blocked())
        self.page(f"{self.base}checks/", f"评审体检 · {self.title}实测记录",
                  f"{self.title}实测的评审体检：换序一致率、位置偏差、篇幅偏差、引文核对、两位评审的一致度和有争议的对子。",
                  "".join(body), [("评审体检", self.base + "checks/")])

    def quotes_html(self) -> str:
        """评审体检的「引文核对」一节。"""
        qrows, misses = [], []
        for j in self.r.duels:
            q = self.r.quotes(j)
            qrows.append(f"<li>{JUDGE_NAME[j]}：{q['found']}/{q['total']} 条找得到（{pct(q['found'], q['total'])}）</li>")
            for d, text in q["misses"][:40]:
                misses.append(f'<li><small>{JUDGE_NAME[j]} · <a href="{self.duel_link(d)}">'
                              f'{self.tracks[d["track"]]} {d["a"]} 对 {d["b"]}</a></small>「{e(text[:80])}」</li>')
        return ('<h2 id="quotes">引文核对</h2><p>提示词要求「理由要引用原文」。把理由里加了引号的话拿去两份稿子里找'
                '（不计空白，省略号两边分开找，四个字以下的不算）：</p>'
                f'<ul>{"".join(qrows)}</ul><p class="sub">找不到的大多是评审把几句话缩成一句、改了标点，或者引的是自己的概括；'
                '也可能有记错的。前 40 条列在下面，可以点进去对照原文。</p>'
                f'<details class="ev"><summary>找不到的引文</summary><div><ul>{"".join(misses)}</ul></div></details>')

    def duel_link(self, d: dict) -> str:
        """一条判决记录所在的盲比页。"""
        return self.duel_url(d["track"], d["a_run"] if not d["a_run"].startswith("baseline.") else d["b_run"])

    def disputed_items(self) -> list[tuple[str, str]]:
        return [(self.duel_url(t, run), f'{TRACK[t]}：{self.name(run.rsplit(".", 1)[0])} 第 {run.rsplit("-", 1)[1]} 次')
                for t, run in sorted(self.r.disputed())]

    def length_note(self) -> str:
        return ('<p class="sub">剧本项目里评审更常判短的赢，和提示词要求「按每集 1–2 分钟衡量，超时算缺点」一致；'
                '人物大纲项目里长的更常赢。这两个数字说明不了谁对，只说明篇幅和结论有关，读结果时要记得。</p>')

    def limits(self) -> list[str]:
        return ["主评审和写稿的是同一个模型（claude-opus-5-5）。它可能偏爱自己的写法；对照组也是它写的，"
                "所以这个偏差对 skill 和对照组大致相同，但不能排除。GPT 复核就是为了看换一个模型结论会不会变。",
                f"每个 skill 只跑了 {self.r.runs_per} 次，区间很宽，只能看方向。",
                "没有请人类编剧盲评。两位评审都是 AI，判的是「AI 认为的好」。",
                "评审只比和对照组的胜负，skill 之间没有直接比过，所以不排名次。"]

    def blocked(self) -> str:
        items = []
        for run in self.meta:
            uses = {}
            for ev in self.events(run):
                if ev["type"] == "assistant":
                    for b in ev["message"]["content"]:
                        if b.get("type") == "tool_use":
                            uses[b["id"]] = b
                elif ev["type"] == "user" and isinstance(ev["message"]["content"], list):
                    for b in ev["message"]["content"]:
                        if b.get("type") == "tool_result" and BLOCKED.search(block_text(b["content"])):
                            u = uses.get(b["tool_use_id"], {})
                            target = u.get("input", {}).get("file_path") or u.get("input", {}).get("command", "")
                            items.append(f'<li>{self.run_link(run)}：<a href="{self.run_url(run)}#t-{e(b["tool_use_id"])}">'
                                         f'{e(u.get("name", ""))}</a> <code>{e(target.splitlines()[0][:90])}</code></li>')
        return ('<h2 id="blocked">运行中被拦下的调用</h2>'
                f'<p>{len(items)} 次，没有一次是想联网或者读别的参赛者。大多是 agent 想读 Claude Code 存长输出的文件：'
                '工具返回太长时，Claude Code 把全文存到主目录下的一个文件里，而权限规则和沙箱都不让读主目录。'
                '这是规则的副作用，没有为它单独开口子，每个参赛者条件相同。</p>' + f"<ul>{''.join(items)}</ul>")

    # ── 过程记录 ──

    def timeline_page(self) -> None:
        items = []
        for ev in self.timeline:
            t = dt.datetime.fromisoformat(ev["time"])
            links = []
            for ref in ev.get("evidence", []):
                kind, _, target = ref.partition(":")
                if kind == "log":
                    links.append(f'<a href="{self.base}logs/{target.lower()}/">{e(self.log_title(target))}</a>')
                elif kind == "file":
                    links.append(f'<a href="{self.repo_url}/blob/main/{e(target)}">{e(target.rsplit("/", 1)[-1])}</a>')
                elif kind == "page":
                    links.append(f'<a href="{self.base}{e(target)}">本记录的{e(ev.get("page_label", "相关页"))}</a>')
            ev_html = f'<p class="sub">证据：{" · ".join(links)}</p>' if links else ""
            items.append(f'<li><time datetime="{ev["time"]}">{t.strftime("%m-%d %H:%M")}</time>'
                         f'<div><b>{e(ev["title"])}</b><p>{e(ev["body"])}</p>{ev_html}</div></li>')
        body = ("<h1>过程记录</h1>"
                '<p class="lead">正式运行之前做过哪些试点和自检，中途改过什么、为什么改，按时间排（北京时间）。'
                '试点和自检的产出都不进评审，日志照样公开。</p>'
                f'<ol class="timeline">{"".join(items)}</ol>')
        self.page(f"{self.base}timeline/", f"过程记录 · {self.title}实测记录",
                  f"{self.title}实测的过程记录：试点、沙箱自检、正式运行和评审各步的时间，中途的调整和原因，附原始日志。",
                  body, [("过程记录", self.base + "timeline/")])

    def build(self) -> None:
        self.overview()
        self.run_pages()
        self.log_pages()
        self.duel_pages()
        self.stories()
        self.checks()
        self.timeline_page()


def short_title(title: str) -> str:
    """选题常同时起网文名和短剧名，故事卡里的书名一栏会带上备选。列表里只用第一个名字。"""
    m = re.search(r"《([^》]+)》", title)
    return m.group(1) if m else re.split(r"[（(；;]", title, maxsplit=1)[0].strip()


class PairRecord(Record):
    """所有参赛者（含对照组）两两比、按积分排名的轮次，第二轮起。页面结构和第一轮一样，
    这里只重写和配对方式、交付有关的部分。"""

    deliv_label = "选题交付"
    kind = "选题"
    topic = "选题类 skill · 网文和短剧共用一道题"
    input_step = "一道开放题：给一个新的爽文故事定选题，以后能写成网文、也能拍成竖屏短剧；不给题材，不限篇幅"
    deliv_step = ("找出选题交付", "每次运行可能写出好几个文件，先认出哪些是一句话卖点和选题说明，人工核对")
    entry_note = "仓库里有专门做选题的 skill，入口就用它；没有就用仓库的主入口"
    reply_note = ("第一轮的固定回复是「第 n 次运行选第 n 个方案」，为的是让三次运行写不同的故事。这一轮比的就是选题，"
                  "从几个方案里挑出最好的那个，本来就是选题 skill 的本事，所以改成让它选自己最推荐的。")
    checks_step = "换序是否一致、偏不偏甲、偏不偏长稿、引文找不找得到、两位评审合不合"
    site_desc = "AI 写小说和短剧的选题 skill"
    extras = "撞题、"

    def name(self, slug: str) -> str:
        """这一轮的参赛者来自短剧和小说两个清单，一律写「作者/仓库」，免得简称撞名。"""
        return "对照组（不装 skill）" if slug == "baseline" else slug.replace("__", "/")

    def name_cell(self, slug: str) -> str:
        """收在本站的链到项目页，其余（小说清单里的）链到 GitHub。"""
        if slug == "baseline":
            return super().name_cell(slug)
        s = self.site.d.by_repo.get(slug.replace("__", "/").lower())
        href = self.repo_path(s) if s else f"https://github.com/{slug.replace('__', '/')}"
        return f'<a href="{href}">{e(self.name(slug))}</a>'
    fingerprints = "和两位评审调用时记下的提示词指纹比对"

    def __init__(self, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self.tracks = {t: "、".join(self.sp.parts[p] for p in parts) for t, parts in self.sp.tracks.items()}
        self.said = runner.wording(self.premise)
        self.order = {repo.replace("/", "__"): i for i, repo in enumerate(self.repos)}

    # ── 链接 ──

    def duel_url(self, track: str, x: str, y: str) -> str:
        """一对稿子的盲比页。x、y 是两次运行，按运行名排先后，和 stats.Round.pairs 一致。"""
        x, y = sorted((x, y))
        return f"{self.base}duels/{track}-{self.r.code_of[x]}-{self.r.code_of[y]}/"

    def duel_link(self, d: dict) -> str:
        return self.duel_url(d["track"], d["a_run"], d["b_run"])

    def opponents(self, run: str) -> list[str]:
        n = run.rsplit(".", 1)[1]
        return [o for o in (f"{repo.replace('/', '__')}.{n}" for repo in self.repos) if o != run]

    def winner(self, x: str, y: str, outcome: str | None) -> str:
        """前一位的赢平输换成「谁赢」。"""
        if outcome is None:
            return "—"
        if outcome == "T":
            return "平"
        return f"{self.name((x if outcome == 'W' else y).rsplit('.', 1)[0])} 赢"

    def run_lead(self, run: str, card: dict) -> str:
        return f"定的选题是{e(self.story_title(run))}。{e(card['logline'])}"

    def story_title(self, run: str) -> str:
        card = next(c for c in self.r.cards if c["code"] == self.r.code_of[run])
        return "（没起名）" if card["title"].strip() in ("", "无") else f"《{short_title(card['title'])}》"

    def run_duels(self, run: str) -> str:
        links = " · ".join(f'<a href="{self.duel_url(t, run, o)}">{e(self.name(o.rsplit(".", 1)[0]))}</a>'
                           for t in self.tracks for o in self.opponents(run))
        return (f"<dt>盲比</dt><dd>和另外 {len(self.repos) - 1} 个参赛者的第 {run.rsplit('-', 1)[1]} 次运行"
                f"各比一场：{links}</dd>")

    # ── 总览 ──

    def overview(self) -> None:
        r = self.r
        n_runs = len(self.meta)
        n_skills = len(self.repos) - 1
        cost = sum(self.run_cost(k) for k in self.meta)
        prem = (ROOT / "evals" / "premises" / f"{self.premise}.md").read_text(encoding="utf-8")
        groups = {j: len(g) for j, g in r.groups.items()}
        n_calls = {j: len(d) for j, d in r.duels.items()}
        steps = [
            ("#input", "需求", self.input_step),
            ("#runs", f"运行 {n_runs} 次", f"{n_skills} 个 skill 加 1 个不装 skill 的对照组，各跑 {r.runs_per} 次，"
                                         f"同一个模型、同一条开场指令和固定回复，按 API 价格折算共 {money(cost)}"),
            ("#runs", *self.deliv_step),
            (f"{self.tree}blind", f"匿名打包 {len(list((r.dir / 'blind').glob('*.md')))} 份",
             "随机三位编号，抹掉 skill 名、仓库名和作者名"),
            *([(f"{self.base}stories/", f"故事卡 {len(r.cards)} 张，分组，查撞题",
                "每份选题抽一张故事卡，再按「换个名字就是同一个故事」分组："
                + "，".join(f"{JUDGE_NAME[j][:-4]} 分 {g} 组" for j, g in groups.items()))] if r.cards else []),
            (f"{self.base}duels/", f"盲比 {len(r.pairs('opus'))} 对",
             f"{len(self.repos)} 个参赛者（含对照组）两两比，第 n 次运行对第 n 次运行，甲乙对调各比一次："
             + "，".join(f"{JUDGE_NAME[j]} {c} 次" for j, c in n_calls.items())),
            ("#results", "积分", "两种顺序都判它赢才算赢，记 1 分；都判对方赢算输；其余算平，记 0.5 分"),
            (f"{self.base}checks/", "评审体检", self.checks_step),
            (f"{self.base}timeline/", "过程记录", "安全检查、沙箱自检、试点，按时间排，附原始日志"),
        ]
        flow = "".join(f'<li><a href="{h}"><b>{i}. {e(t)}</b><span>{e(s)}</span></a></li>'
                       for i, (h, t, s) in enumerate(steps, 1))
        body = [f"<h1>{e(self.title)}实测记录：{e(self.topic)}</h1>",
                f'<p class="lead">这一页把{e(self.title)}实测的全过程摆出来：给了 agent 什么、每次运行它做了什么、评审看到了什么、'
                '怎么判的。每一步都能点开看原始的输入和输出。页面上的数字都是生成网站时从仓库里的原始数据现算的。</p>',
                f'<p class="sub">结论和逐个点评见<a href="/evals/#{e(self.base.strip("/").rsplit("/", 1)[-1])}">实测页</a>。'
                '这里只放过程和证据。</p>',
                f'<ol class="flow">{flow}</ol>']

        body.append('<h2 id="input">给 agent 的全部输入</h2>'
                    '<p>每次运行都在一个新建的空目录里，目录里只有这份需求（premise.md）和装好的 skill。</p>'
                    f'<h3>需求原文（premise.md）</h3>{doc(prem)}'
                    '<h3>开场指令</h3><ul>'
                    f'<li>对照组：<code>{e(self.said["task"])}</code></li>'
                    f'<li>有入口 skill 的：<code>/入口skill名 {e(self.said["task"])}</code>，入口写在 '
                    f'<a href="{self.raw}contestants.toml">contestants.toml</a>。{e(self.entry_note)}</li>'
                    f'<li>工具箱型、没有单一入口的：<code>{e(self.said["toolkit"])}</code></li></ul>'
                    '<h3>之后每一轮的固定回复</h3>'
                    f'{doc(self.said["reply"])}'
                    f'<p>{e(self.reply_note)}</p>'
                    '<h3>什么时候停</h3>'
                    f'<p>一轮结束后，如果 agent 没在提问、这一轮也没再改文件，而且目录里已经有产出，就算写完；'
                    f'连续三轮没改文件也停；最多 {runner.MAX_TURNS} 轮。代码见 '
                    f'<a href="{self.repo_url}/blob/main/evals/run.py">evals/run.py</a>。</p>')
        body.append(self.env_html())
        body.append(self.runs_html())

        body.append('<h2 id="results">积分：所有参赛者两两比</h2>'
                    f'<p>每个参赛者和另外 {len(self.repos) - 1} 个各比 {r.runs_per} 次（第 n 次运行对第 n 次运行），'
                    '一共 ' + str((len(self.repos) - 1) * r.runs_per) + ' 次。一次比较里，两种先后顺序都判它赢才算赢，'
                    '记 1 分；都判对方赢算输；其余算平，记 0.5 分。名次以主评审 Opus 为准，GPT 是复核；'
                    f'两位评审结论不同的对子在<a href="{self.base}duels/">盲比列表</a>里标「有争议」。</p>')
        body.append(self.standings_table())
        body.append(self.matrix())
        body.append(self.verify_html())
        self.page(self.base, f"{self.title}实测记录：{n_skills} 个{self.kind} skill 两两盲比的全部运行和评审过程",
                  f"{self.site_desc} {self.title}实测的完整记录：给 agent 的全部输入、{n_runs} 次运行的每一步、"
                  f"匿名稿、每一场盲比的提示词和判决、积分、{self.extras}评审体检和过程记录，数字从原始数据现算。", "".join(body))

    def standings_table(self) -> str:
        r = self.r
        t = next(iter(self.tracks))
        rows_by = {j: r.standings(j, t) for j in r.duels}
        rank_of = {}
        for j, rows in rows_by.items():
            last, place = None, 0
            for i, (s, _, pts) in enumerate(rows, 1):
                if pts != last:
                    place, last = i, pts
                rank_of[j, s] = place
        rec = {j: {s: (wtl_, pts) for s, wtl_, pts in rows} for j, rows in rows_by.items()}
        vs_base = r.head_to_head("opus", t)
        disputed = r.disputed()
        head = "".join(f"<th>{JUDGE_NAME[j]}<br><small>赢-平-输 · 积分 · 名次</small></th>" for j in rows_by)
        trs = []
        for s, w, pts in rows_by["opus"]:
            cells = "".join(f"<td>{wtl(rec[j][s][0])} · {rec[j][s][1]:g} · 第 {rank_of[j, s]}</td>" for j in rows_by)
            n = sum(w)
            share = ci(w[0], n) if n else "—"
            base = "—" if s == "baseline" else wtl(vs_base.get((s, "baseline")))
            n_disp = sum(1 for _, x, y in disputed if s in (x.rsplit(".", 1)[0], y.rsplit(".", 1)[0]))
            trs.append(f"<tr><td>{rank_of['opus', s]}</td><th>{self.name_cell(s)}</th>{cells}"
                       f"<td>{share}</td><td>{base}</td><td>{n_disp or ''}</td></tr>")
        return (f'<table class="tbl"><thead><tr><th>名次</th><th>参赛者</th>{head}<th>赢的比例（Opus）</th>'
                f'<th>和对照组（Opus）</th><th>有争议</th></tr></thead><tbody>{"".join(trs)}</tbody></table>'
                '<p class="sub">按 Opus 的积分排，同分并列。「赢的比例」是赢的次数占全部比较的比例，括号里是 95% 置信区间：'
                '区间重叠很多的两个参赛者，名次先后说明不了太多。</p>')

    def matrix(self) -> str:
        r = self.r
        t = next(iter(self.tracks))
        h2h = r.head_to_head("opus", t)
        order = [s for s, _, _ in r.standings("opus", t)]
        head = "".join(f"<th><small>{e(self.name(s))}</small></th>" for s in order)
        trs = []
        for s in order:
            cells = "".join("<td>—</td>" if s == o else f"<td>{wtl(h2h.get((s, o)))}</td>" for o in order)
            trs.append(f"<tr><th>{self.name_cell(s)}</th>{cells}</tr>")
        return ('<h3 id="matrix">对阵表（Opus）</h3><p>每格是行里的参赛者对列里的参赛者，三次比较的「赢-平-输」。'
                f'每一场的稿子和判决在<a href="{self.base}duels/">盲比列表</a>。</p>'
                f'<table class="tbl"><thead><tr><th></th>{head}</tr></thead>'
                f'<tbody>{"".join(trs)}</tbody></table>')

    # ── 盲比 ──

    def duel_pages(self) -> None:
        r = self.r
        pairs = {j: r.pairs(j) for j in r.duels}
        outs = {j: r.pair_outcomes(j) for j in r.duels}
        disputed = r.disputed()

        def sort_key(k):
            _, x, y = k
            return self.order[x.rsplit(".", 1)[0]], self.order[y.rsplit(".", 1)[0]], x

        rows = {t: [] for t in self.tracks}
        for k in sorted(pairs["opus"], key=sort_key):
            t, x, y = k
            self.pair_page(t, x, y, {j: pairs[j].get(k, []) for j in pairs}, {j: outs[j].get(k) for j in outs},
                           k in disputed)
            cells = "".join(f"<td>{e(self.winner(x, y, outs[j].get(k)))}<br><small>"
                            f"{' / '.join(WTL[v] for _, v in pairs[j].get(k, []))}</small></td>" for j in pairs)
            flag = '<span class="badge bad">有争议</span>' if k in disputed else ""
            rows[t].append(f'<tr><td><a href="{self.duel_url(t, x, y)}">{r.code_of[x]} 对 {r.code_of[y]}</a></td>'
                           f"<td>{self.run_link(x)}</td><td>{self.run_link(y)}</td>{cells}<td>{flag}</td></tr>")
        a = r.agreement()
        n_pairs = len(pairs["opus"])
        body = [f"<h1>盲比：{n_pairs} 对，每对两种顺序</h1>",
                f'<p class="lead">{len(self.repos)} 个参赛者（含对照组）两两比：甲的第 n 次运行对乙的第 n 次运行，'
                '每对甲乙对调各比一次。评审只看到匿名稿和三位编号。</p>'
                f'<p>主评审是 {e(JUDGE_MODEL["opus"])}；复核评审是 {e(JUDGE_MODEL["gpt"])}，'
                '用一字不差的提示词和输出格式重判一遍。'
                + (f"两位评审逐场判断一致 {a['same']}/{a['calls']}，最终结果一致 {a['pairs_same']}/{a['pairs']} 对，"
                   f"不一致的 {len(disputed)} 对标「有争议」，积分仍以 Opus 为准。" if a else "") + "</p>"
                '<p class="sub">每格先写最终结果，下面小字是两种顺序各自的判决，从「前一位」（左边那次运行）看。</p>']
        for t in self.tracks:
            head = "".join(f"<th>{JUDGE_NAME[j]}</th>" for j in pairs)
            body.append(f'<h2 id="{t}">{self.tracks[t]}</h2><table class="tbl"><thead><tr><th>编号</th><th>前一位</th>'
                        f'<th>后一位</th>{head}<th></th></tr></thead><tbody>{"".join(rows[t])}</tbody></table>')
        self.page(f"{self.base}duels/", f"盲比列表 · {self.title}实测记录",
                  f"{self.title}实测全部盲比：所有参赛者两两比{self.kind}，两种顺序、两位评审的判决。",
                  "".join(body), [("盲比", self.base + "duels/")])

    def pair_page(self, track: str, x: str, y: str, pairs: dict[str, list], final: dict[str, str | None],
                  disputed: bool) -> None:
        r = self.r
        cx, cy = r.code_of[x], r.code_of[y]
        sides = "".join(
            f'<article class="side" data-code="{c}"><h3>稿子 {c} <small>{len(r.packet(c, track)):,} 字</small></h3>'
            f'{doc(r.packet(c, track), "doc scroll")}</article>' for c in (cx, cy))
        body = [f"<h1>{self.tracks[track]}盲比：稿子 {cx} 对 {cy}</h1>",
                f'<p class="lead">评审比的是两份{self.tracks[track]}。下面是评审看到的原文，编号随机，看不出出处；'
                '出处在页面最后揭晓。</p>',
                f'<section class="duel" data-round="{e(self.premise)}" data-track="{track}" data-a="{cx}" data-b="{cy}">'
                f'<div class="pair">{sides}</div></section>',
                "<h2>判决</h2>"]
        for a, b in ((cx, cy), (cy, cx)):
            calls = {j: next((d for d, _ in pairs[j] if d["a"] == a), None) for j in pairs}
            body.append(f"<h3>甲 = {a}，乙 = {b}</h3>")
            dims = list(judge.track_dims(track, self.sp))
            head = "".join(f"<th>{JUDGE_NAME[j]}</th>" for j in calls)

            def mark(v: str | None) -> str:
                return {"甲": f"甲（{a}）", "乙": f"乙（{b}）", "平": "平"}.get(v, "—")

            trs = "".join(f"<tr><th>{e(dm)}</th>" + "".join(f"<td>{mark(c and c['dims'].get(dm))}</td>" for c in calls.values())
                          + "</tr>" for dm in dims)
            trs += "<tr><th>总体</th>" + "".join(f"<td><b>{mark(c and c['winner'])}</b></td>" for c in calls.values()) + "</tr>"
            body.append(f'<table class="tbl"><thead><tr><th>维度</th>{head}</tr></thead><tbody>{trs}</tbody></table>')
            for j, c in calls.items():
                if c:
                    body.append(f"<p><b>{JUDGE_NAME[j]}的理由：</b>{e(c['reason'])}</p>")
            body.append(self.prompt_box(track, a, b))
        verdict = " · ".join(f"{JUDGE_NAME[j]}：{self.winner(x, y, o)}" for j, o in final.items())
        body.append(f'<h2>结果</h2><p>{e(verdict)}{" <span class=\"badge bad\">有争议</span>" if disputed else ""}</p>'
                    '<p class="sub">两种顺序都判同一份赢才算赢，其余算平。</p>')
        body.append(f'<details class="ev reveal"><summary><b>揭晓出处</b></summary><div><ul>'
                    f"<li>稿子 {cx}：{self.run_link(x)}</li><li>稿子 {cy}：{self.run_link(y)}</li></ul></div></details>")
        self.page(self.duel_url(track, x, y), f"{self.tracks[track]}盲比 {cx} 对 {cy} · {self.title}实测记录",
                  f"{self.title}实测的一场{self.tracks[track]}盲比：两份匿名稿原文、评审收到的完整提示词、两种顺序和两位评审的判决。",
                  "".join(body), [("盲比", self.base + "duels/")], wide=True)

    # ── 故事卡、分组和撞题 ──

    def stories(self) -> None:
        r = self.r
        cards = {c["code"]: c for c in r.cards}
        body = ["<h1>故事卡、故事类型和撞题</h1>",
                f'<p class="lead">每份选题抽一张故事卡，只摘稿子里有的内容，不评好坏；再把 {len(cards)} 张卡按'
                '「换个名字和细节就差不多是同一个故事」分组。同一组里有别的参赛者，就算撞题。</p>']
        part_names = "、".join(self.sp.parts.values())
        body.append('<h2 id="method">怎么抽、怎么分</h2>'
                    f'<p>抽卡（{e(JUDGE_MODEL["opus"])}）：系统提示「你负责如实摘录信息。」，提示词是下面这段，后面接这份'
                    f'{e(part_names)}的全文。</p>' + doc(self.sp.card.replace("{text}", f"<{part_names}全文>"))
                    + '<p>分组：系统提示「' + e(self.sp.cluster_system) + '」，提示词如下，每份选题一行：编号、书名或剧名、题材、'
                    '一句话梗概、主角、核心设定。</p>'
                    + doc(self.sp.cluster.replace("{n}", str(len(cards))).replace("{lines}", "<每份选题一行>"))
                    + f'<p class="sub">各行按编号排序后用固定种子（{self.sp.seed}）打乱，两位评审看到的顺序相同，'
                      '谁都能重建出一样的提示词。</p>')
        for j, groups in r.groups.items():
            s = r.same_type(j)
            body.append(f'<h2 id="groups-{j}">{JUDGE_NAME[j]}分出的 {len(groups)} 种故事类型</h2>'
                        f"<p>同一个参赛者的几次运行，两两落进同一种类型：{s['within']}/{s['within_n']} 对（{pct(s['within'], s['within_n'])}）；"
                        f"不同参赛者之间：{s['between']}/{s['between_n']} 对（{pct(s['between'], s['between_n'])}）。</p>")
            items = []
            for g in sorted(groups, key=lambda g: -len(g["codes"])):
                members = "、".join(f'<a href="#card-{c}">{c}</a>（{self.run_link(r.key[c], self.name(r.key[c].rsplit(".", 1)[0]))}）'
                                   for c in g["codes"])
                items.append(f'<li><b>{e(g["name"])}</b>（{len(g["codes"])} 份）：{e(g["pattern"])}<br><small>{members}</small></li>')
            body.append(f'<ul class="groups">{"".join(items)}</ul>')
        if r.groups:
            heads = "".join(f"<th>{JUDGE_NAME[j]}</th>" for j in r.groups)
            col = {j: r.collisions(j) for j in r.groups}
            trs = "".join(f"<tr><th>{self.name_cell(s)}</th>"
                          + "".join(f"<td>{col[j].get(s, {}).get('shared', 0)}/{col[j].get(s, {}).get('runs', 0)}"
                                    f"<br><small>和对照组撞 {col[j].get(s, {}).get('with_baseline', 0)}</small></td>"
                                    for j in r.groups) + "</tr>"
                          for s in [repo.replace("/", "__") for repo in self.repos])
            body.append('<h2 id="collisions">撞题</h2><p>每个参赛者的几次运行里，有几次和别的参赛者落进同一种故事类型。'
                        '「和对照组撞」是其中和不装 skill 的模型撞的次数：撞得多，说明装了 skill 也没跳出模型自己的默认套路。</p>'
                        f'<table class="tbl"><thead><tr><th>参赛者</th>{heads}</tr></thead><tbody>{trs}</tbody></table>')
        agree = r.cluster_agreement()
        if agree is not None:
            body.append(f"<p>两位评审的分组有多像：调整兰德指数 {agree:.2f}（1 是完全一样，0 是和随机分组一样）。</p>")
        top = "，".join(f"{k} {v} 份" for k, v in r.surnames().most_common(4))
        rows = []
        for n in ("砚", "周砚", "禾"):
            k, who = r.name_count(n)
            base = any(n in x for c in r.cards if r.key[c["code"]].startswith("baseline.") for x in c["names"])
            rows.append(f"「{n}」{k} 份，来自 {who} 个参赛者" + ("，对照组也有" if base else ""))
        body.append('<h2 id="defaults">模型的默认偏好</h2>'
                    f'<p>主角的姓（故事卡「主角」一栏的第一个字）：{top}，共 {len(cards)} 份。'
                    f'人名里带这几个字的：{"；".join(rows)}。这些名字分散在很多参赛者的稿子里，'
                    '更像是写稿的模型自己的偏好，不是某个 skill 带来的。想要独特的人名，要靠人来改。</p>'
                    f'<p>题材上也一样：{len(cards)} 张故事卡里有 {r.mentions("账")[0]} 张提到「账」（讨账、查账、账本），'
                    f'来自 {r.mentions("账")[1]} 个参赛者（含对照组）。</p>')
        body.append(f'<h2 id="cards">{len(cards)} 张故事卡</h2>')
        fields = [("genre", "题材"), ("logline", "梗概"), ("era_place", "时代地点"), ("hook_device", "核心设定"),
                  ("protagonist", "主角"), ("antagonist", "对手"), ("audience", "写给谁看"), ("length", "打算写多长")]
        for code in sorted(cards, key=lambda c: r.key[c]):
            c = cards[code]
            dl = "".join(f"<dt>{lab}</dt><dd>{e(str(c[k]))}</dd>" for k, lab in fields)
            dl += f"<dt>人名</dt><dd>{e('、'.join(c['names']))}</dd>"
            body.append(f'<details class="ev" id="card-{code}"><summary><b>{code}</b> {e(self.story_title(r.key[code]))} '
                        f'<small>{self.name(r.key[code].rsplit(".", 1)[0])} · 第 {r.key[code].rsplit("-", 1)[1]} 次</small></summary>'
                        f'<div><dl class="facts">{dl}</dl><p class="sub">{self.run_link(r.key[code], "这次运行")} · '
                        + " · ".join(f'<a href="{self.raw}blind/{code}.{p}.md">匿名稿·{self.sp.parts[p]}</a>' for p in self.sp.parts)
                        + "</p></div></details>")
        body.append(f'<p class="sub">原始数据：<a href="{self.raw}cards.jsonl">cards.jsonl</a> · '
                    + " · ".join(f'<a href="{self.raw}{f}">{f}</a>' for f in ("clusters.json", "clusters-gpt.json")
                                 if (r.dir / f).exists()) + "</p>")
        self.page(f"{self.base}stories/", f"故事卡、故事类型和撞题 · {self.title}实测记录",
                  f"{self.title}实测 {len(cards)} 份选题的故事卡、故事类型分组和每个参赛者的撞题次数。",
                  "".join(body), [("故事卡", self.base + "stories/")])

    # ── 评审体检里和第一轮不同的几段 ──

    def disputed_items(self) -> list[tuple[str, str]]:
        return [(self.duel_url(t, x, y), f"{self.tracks[t]}：{self.name(x.rsplit('.', 1)[0])} 对 "
                                         f"{self.name(y.rsplit('.', 1)[0])}，第 {x.rsplit('-', 1)[1]} 次")
                for t, x, y in sorted(self.r.disputed())]

    def length_note(self) -> str:
        return ('<p class="sub">提示词写明「篇幅长、格式花哨、附带市场分析或检查清单都不加分」。'
                '这个数字说明不了谁对，只说明篇幅和结论有没有关系，读结果时要记得。</p>')

    def limits(self) -> list[str]:
        return ["主评审和写稿的是同一个模型（claude-opus-5-5）。它可能偏爱自己的写法；对照组也是它写的，"
                "所以这个偏差对所有参赛者大致相同，但不能排除。GPT 复核就是为了看换一个模型结论会不会变。",
                f"每对参赛者只比了 {self.r.runs_per} 次。积分把每个参赛者的 {(len(self.repos) - 1) * self.r.runs_per} 次比较"
                "合在一起算，比只和对照组比稳，但区间重叠的名次先后说明不了太多。",
                "没有请人类编剧盲评。两位评审都是 AI，判的是「AI 认为值得写、值得拍」。选题好不好最终要看读者和观众买不买账，"
                "这一点 AI 评审替代不了。",
                "不能联网。靠联网扫榜找选题的 skill 这一轮没有测，测了的也只能凭已有资料判断市场。"]


class SkeletonRecord(PairRecord):
    """第三轮：所有参赛者按同一张选题卡写全剧骨架，两两比、按积分排名。和第二轮的不同：
    大家写同一个故事，不抽故事卡、不分组；需求限 3000 字，超过的截到 3000 字再评；评委不分维度、只判总体。"""

    deliv_label = "全剧骨架"
    kind = "全剧骨架"
    topic = "全剧骨架类 skill · 同一张选题卡"
    input_step = "同一张选题卡《验尸官的婚礼》：给 60 集竖屏短剧写全剧骨架，全部由 AI 拍，只交骨架，3000 字以内"
    deliv_step = ("找出骨架交付", "每次运行都只交了一份全剧骨架；超过 3000 字的 10 份截到 3000 字，后面注明截掉了")
    entry_note = "仓库里有专门做全剧骨架（总纲、全剧大纲、系列圣经）的 skill，入口就用它；那一步只能从主入口走到的，就用主入口"
    reply_note = ("固定回复和第二轮一样，让它选自己最推荐的方案；只多了半句「骨架之后的分集大纲和剧本不用写」，"
                  "把需求里的「只交骨架」重说一遍，对所有参赛者一样。")
    checks_step = "换序是否一致、偏不偏甲、偏不偏长稿、两位评审合不合"
    site_desc = "AI 短剧全剧骨架 skill"
    extras = ""
    show_quotes = False  # 引文核对的比对方法还在改，这一轮先不放
    length_rule = "需求限 3000 字以内，超过的截到 3000 字再评，这里按原稿字数算。"
    raw_files = "每份骨架的字数（lengths.json）、每一场比较的判决，以及去掉截断说明的对照（duels-nonote.jsonl、duels-nonote-gpt.jsonl、judge-raw-nonote/）"
    fingerprints = "和两位评审调用时记下的提示词指纹比对（去掉截断说明的对照也比）"

    @functools.cached_property
    def lengths(self) -> dict:
        return json.loads((self.r.dir / "lengths.json").read_text(encoding="utf-8"))

    def story_title(self, run: str) -> str:
        return f"{self.lengths[run]['skeleton']:,} 字"

    def run_lead(self, run: str, card: dict | None) -> str:
        n = self.lengths[run]["skeleton"]
        cut = "超过需求的 3000 字，评审只看到前 3000 字。" if n > 3000 else ""
        return f"写了一份全剧骨架，{n:,} 字（去掉空白计）。{cut}"

    def stories(self) -> None:
        """这一轮不抽故事卡。"""

    def length_note(self) -> str:
        return ('<p class="sub">截断以后两位评审仍然更看好超字数的那几份，去掉截断说明重判也一样，'
                f'见<a href="{self.raw}review.md">点评</a>的「截断说明的检查」。'
                '两份都没超 3000 字时，长的那份也赢得多。这些数字说明不了谁对，只说明篇幅和结论有关，读结果时要记得。</p>')

    def limits(self) -> list[str]:
        return ["主评审和写稿的是同一个模型（claude-opus-5-5）。它可能偏爱自己的写法；对照组也是它写的，"
                "所以这个偏差对所有参赛者大致相同，但不能排除。GPT 复核就是为了看换一个模型结论会不会变。",
                f"每对参赛者只比了 {self.r.runs_per} 次。区间重叠的名次先后说明不了太多。",
                "只有一个故事。换一张选题卡、换个题材，名次可能不同。",
                "没有请人类编剧盲评。两位评审都是 AI，判的是纸面上的骨架，没有照着它写出来、拍出来。"]


def build(site, rounds: dict, repo_url: str, repo_path, display_name) -> None:
    for premise, (zh, _, slug) in rounds.items():
        if (ROOT / "evals" / "runs" / premise / "timeline.toml").exists():
            sp = judge.spec(premise)
            cls = Record if sp.pairing != "all" else SkeletonRecord if getattr(sp, "bare", False) else PairRecord
            cls(site, premise, slug, zh, repo_url, repo_path, display_name).build()
