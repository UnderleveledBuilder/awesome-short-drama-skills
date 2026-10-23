"""根据 data/ 和 web/ 生成网站（shortdramaskills.com）到 web/dist/。只依赖标准库（Python 3.11+）。

中文页在根路径，英文页在 /en/ 下。页面数据与 README 同源：data/*.toml、data/meta.json、
data/skill_index.json（scripts/index_skills.py 抓取的 SKILL.md 列表）。

用法：
  python3 scripts/build_site.py           # 生成 web/dist/
  python3 scripts/build_site.py --serve   # 生成后在 http://localhost:8000 预览
"""

from __future__ import annotations

import argparse
import datetime as dt
import functools
import hashlib
import html
import http.server
import json
import re
import shutil
import tomllib
import urllib.parse

from build import NEW_DAYS, SPECIALIST_MAX, STALE_DAYS, by_stars, display_name, fmt_stars, install_cmd, new_entries, \
    sort_key, tr
from lib import DATA, ROOT, load_meta, load_toml, load_valid, third_party_text
import build_evals

WEB = ROOT / "web"
DIST = WEB / "dist"
SITE = tomllib.loads((WEB / "site.toml").read_text(encoding="utf-8"))
BASE = SITE["base_url"].rstrip("/")
REPO_URL = f"https://github.com/{SITE['repo']}"
SITEMAP_MAX = 300  # 每个 sitemap 文件最多几条（头条站长平台的限制）
# 搜索引擎站长平台的所有权验证标签，写进每页 <head>（site.toml 的 [verify]）
VERIFY_META = "".join(f'<meta name="{k}" content="{html.escape(v)}">\n' for k, v in SITE.get("verify", {}).items())
LANGS = {
    "zh": {"prefix": "", "hreflang": "zh-CN", "locale": "zh_CN"},
    "en": {"prefix": "/en", "hreflang": "en", "locale": "en_US"},
}
KIND = {  # 项目页开头摘要里的说法
    "skill": ("agent skill", "agent skill"),
    "prompts": ("提示词", "prompt-file"),
    "app": ("开源应用", "open-source app"),
}
FORMAT = {
    "skill": ("标准 skill", "Agent skill"),
    "prompts": ("提示词文件（非标准 skill）", "Prompt files (not a standard skill)"),
    "app": ("完整应用", "Full application"),
}
LANG_NAME = {"zh": ("中文", "Chinese"), "en": ("英文", "English"), "multi": ("多语言", "Multilingual")}
NAV = [
    ("/", "首页", "Home"),
    ("/stage/", "按阶段", "By stage"),
    ("/model/", "按视频模型", "By video model"),
    ("/type/", "按类型", "By type"),
    ("/packs/", "推荐组合", "Stacks"),
    ("/guides/", "指南", "Guides"),
    ("/evals/", "实测", "Tests"),
    ("/about/", "关于", "About"),
]
GUIDES = ["what-is-a-short-drama-skill", "install", "how-to-choose", "write-script-with-ai"]


def L(lang: str, zh: str, en: str) -> str:
    return zh if lang == "zh" else en


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


e = functools.partial(html.escape, quote=True)
CJK = re.compile(r"[\u3400-\u9fff]")


# ───────────────────────── 数据 ─────────────────────────

ROUNDS = {"001-open-brief": ("第一轮", "round one", "round-1"), "002-topic": ("第二轮", "round two", "round-2")}


def duel_record(run_dir: Path, name: str = "duels.jsonl") -> dict[tuple[str, str], dict[str, list[int]]]:
    """每个参赛者和对照组盲比的「赢、平、输」次数。两种先后顺序都判它赢才算赢，都判对照组赢才算输。
    name 是判决文件：duels.jsonl 是主评审，duels-gpt.jsonl 是复核。"""
    votes: dict[tuple[str, str, str, str], list[str]] = {}
    for line in (run_dir / name).open(encoding="utf-8"):
        d = json.loads(line)
        mine, side = (d["a_run"], "甲") if not d["a_run"].startswith("baseline.") else (d["b_run"], "乙")
        slug, run = mine.rsplit(".", 1)
        votes.setdefault((run_dir.name, slug, d["track"], run), []).append(
            "W" if d["winner"] == side else "T" if d["winner"] == "平" else "L")
    out: dict[tuple[str, str], dict[str, list[int]]] = {}
    for (rnd, slug, track, _), v in votes.items():
        r = out.setdefault((rnd, slug), {}).setdefault(track, [0, 0, 0])
        r[0 if v.count("W") == len(v) else 2 if v.count("L") == len(v) else 1] += 1
    return out


def standings(premise: str) -> dict[tuple[str, str], dict]:
    """两两全比的轮次：每个参赛者的积分名次（Opus 和 GPT 各一份），和它对对照组三次比较的「赢、平、输」。"""
    r = build_evals.Round(premise)
    track = next(iter(r.sp.tracks))
    out: dict[tuple[str, str], dict] = {}
    for j in r.duels:
        rows = r.standings(j, track)
        place, last = 0, None
        for i, (slug, rec, pts) in enumerate(rows, 1):
            if pts != last:
                place, last = i, pts
            out.setdefault((premise, slug), {})[j] = (place, len(rows), rec, pts)
    h2h = r.head_to_head("opus", track)
    for slug in r.slugs:
        out.setdefault((premise, slug), {})["vs_base"] = h2h.get((slug, "baseline"), [0, 0, 0])
    return out


class Data:
    def __init__(self) -> None:
        self.taxonomy, skills, self.packs, self.ignored = load_valid()
        meta_all = load_meta()
        self.meta = meta_all.get("repos", {})
        self.updated = meta_all.get("fetched_at") or dt.date.today().isoformat()
        self.ref = dt.date.fromisoformat(self.updated)
        index_path = DATA / "skill_index.json"
        self.index = json.loads(index_path.read_text(encoding="utf-8")).get("repos", {}) if index_path.exists() else {}
        self.skills = sorted(skills, key=lambda s: sort_key(s, self.meta))
        self.by_repo = {s["repo"].lower(): s for s in self.skills}
        self.groups = self.taxonomy["groups"]
        self.indexed = [s for s in self.skills if self.groups[s["group"]].get("indexed", True)]
        self.new = new_entries(self.skills, self.meta, self.ref)
        # 编者说明和第三方中文文字的英文译文，只有网站用
        self.overviews = load_toml("overviews.toml") if (DATA / "overviews.toml").exists() else {}
        tr_path = DATA / "translations.json"
        self.translations = json.loads(tr_path.read_text(encoding="utf-8")) if tr_path.exists() else {}
        self.untranslated: set[str] = set()
        # 参加过实测的项目：evals/runs/<轮次>/contestants.toml；有 duels.jsonl 的轮次再算出和对照组盲比的胜负
        self.evaluated: dict[str, list[str]] = {}
        self.duels: dict[tuple[str, str], dict[str, list[int]]] = {}
        self.duels_gpt: dict[tuple[str, str], dict[str, list[int]]] = {}
        # 两两全比的轮次（第二轮起）不算和对照组的胜负，算积分名次
        self.standings: dict[tuple[str, str], dict] = {}
        for roster in sorted((ROOT / "evals" / "runs").glob("*/contestants.toml")):
            for c in tomllib.loads(roster.read_text(encoding="utf-8"))["contestants"]:
                self.evaluated.setdefault(c["repo"].lower(), []).append(roster.parent.name)
            if (roster.parent / "duels.jsonl").exists() and build_evals.judge.spec(roster.parent.name).pairing == "all":
                self.standings.update(standings(roster.parent.name))
                continue
            if (roster.parent / "duels.jsonl").exists():
                self.duels.update(duel_record(roster.parent))
            if (roster.parent / "duels-gpt.jsonl").exists():
                self.duels_gpt.update(duel_record(roster.parent, "duels-gpt.jsonl"))

    def quote(self, text: str, lang: str) -> tuple[str, bool]:
        """第三方文字的展示版本和它是不是译文。英文页遇到中文换成译文，没有译文就先不显示。"""
        text = (text or "").strip()
        if not third_party_text(text):
            return "", False
        if lang == "zh" or not CJK.search(text):
            return third_party_text(text), False
        if text in self.translations:
            return third_party_text(self.translations[text]), True
        self.untranslated.add(text)
        return "", False

    def m(self, s: dict) -> dict:
        return self.meta.get(s["repo"], {})

    def stars(self, s: dict) -> int:
        return self.m(s).get("stars", -1)

    def in_stage(self, key: str) -> list[dict]:
        return by_stars((s for s in self.indexed if key in s["stages"]), self.meta)

    def in_model(self, key: str) -> list[dict]:
        return by_stars((s for s in self.indexed if key in s.get("models", [])), self.meta)

    def in_group(self, key: str) -> list[dict]:
        return [s for s in self.skills if s["group"] == key]


def repo_path(s: dict) -> str:
    return f"/skills/{s['repo'].lower()}/"


def url(lang: str, path: str) -> str:
    return LANGS[lang]["prefix"] + path


def abs_url(lang: str, path: str) -> str:
    return BASE + url(lang, path)


def asset(name: str) -> str:
    digest = hashlib.sha1((WEB / "static" / name).read_bytes()).hexdigest()[:8]
    return f"/static/{name}?v={digest}"


def ld(obj: dict) -> str:
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{text}</script>'


def publisher() -> dict:
    name = SITE["wechat"]["name"] or "Awesome Short Drama Skills"
    return {"@type": "Organization", "name": name, "url": BASE + "/"}


def join(lang: str, items) -> str:
    items = list(items)
    if lang == "zh":
        return "、".join(items)
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 1].rstrip("，,、 ") + "…"


# ───────────────────────── 页面骨架 ─────────────────────────

class Site:
    def __init__(self, data: Data) -> None:
        self.d = data
        self.pages: list[tuple[str, str]] = []  # (path, lastmod)，两种语言都有
        self.zh_pages: list[tuple[str, str]] = []  # 只有中文的页（实测记录）
        self.css = asset("style.css")

    def write(self, lang: str, path: str, page: str) -> None:
        out = DIST / url(lang, path).lstrip("/") / "index.html" if path.endswith("/") else DIST / url(lang, path).lstrip("/")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")

    def page(self, lang: str, path: str, *, title: str, description: str, body: str, crumbs: list[tuple[str, str]],
             jsonld: list[dict] = (), lastmod: str | None = None, og_type: str = "website",
             zh_only: bool = False, wide: bool = False) -> None:
        if lang == "zh":
            (self.zh_pages if zh_only else self.pages).append((path, lastmod or self.d.updated))
        other = "en" if lang == "zh" else "zh"
        # 只有中文的页：不写英文对应页，语言切换去英文的实测页
        alternates = (f'<link rel="alternate" hreflang="zh-CN" href="{abs_url("zh", path)}">' if zh_only else
                      f'<link rel="alternate" hreflang="zh-CN" href="{abs_url("zh", path)}">\n'
                      f'<link rel="alternate" hreflang="en" href="{abs_url("en", path)}">\n'
                      f'<link rel="alternate" hreflang="x-default" href="{abs_url("zh", path)}">')
        switch = url(other, "/evals/" if zh_only else path)
        trail = [(L(lang, "首页", "Home"), "/"), *crumbs]
        crumb_ld = {
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": name, "item": abs_url(lang, p)}
                                for i, (name, p) in enumerate(trail)],
        }
        crumb_html = ""
        if crumbs:
            parts = [f'<a href="{url(lang, p)}">{e(name)}</a>' for name, p in trail[:-1]]
            parts.append(f'<span aria-current="page">{e(trail[-1][0])}</span>')
            crumb_html = f'<nav class="crumbs" aria-label="breadcrumb">{"<span aria-hidden=\"true\">›</span>".join(parts)}</nav>'
        nav = "".join(
            f'<a href="{url(lang, p)}"{" aria-current=\"page\"" if p == path or (p != "/" and path.startswith(p)) else ""}>'
            f'{e(L(lang, zh, en))}</a>' for p, zh, en in NAV)
        head_ld = "".join(ld(x) for x in [*jsonld, crumb_ld] if x)
        og_image = BASE + SITE["og_image"]
        doc = f"""<!doctype html>
<html lang="{LANGS[lang]['hreflang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{abs_url(lang, path)}">
{alternates}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Awesome Short Drama Skills">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{abs_url(lang, path)}">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="{LANGS[lang]['locale']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2a130a">
{VERIFY_META}<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{self.css}">
<link rel="alternate" type="application/json" href="/data.json" title="Awesome Short Drama Skills data">
{head_ld}
</head>
<body>
<header class="site-header"><div class="wrap">
<a class="brand" href="{url(lang, '/')}"><b>Awesome Short Drama Skills</b><span>{e(L(lang, 'AI 短剧 · 漫剧 Skill 精选', 'Curated agent skills for AI short drama'))}</span></a>
<a class="lang-switch" href="{switch}" hreflang="{LANGS[other]['hreflang']}" lang="{LANGS[other]['hreflang']}">{L(lang, 'English', '中文')}</a>
<nav class="site-nav" aria-label="{L(lang, '主导航', 'Main')}">{nav}</nav>
</div></header>
<div class="wrap{' wide' if wide else ''}">
{crumb_html}
<main>
{body}
</main>
</div>
{self.footer(lang)}
</body>
</html>
"""
        self.write(lang, path, doc)

    def footer(self, lang: str) -> str:
        wx = SITE["wechat"]
        follow = ""
        if wx["name"]:
            img = f'<img src="/static/{e(wx["qr"])}" alt="{e(wx["name"])}" loading="lazy">' if wx["qr"] else ""
            follow = (f'<div class="follow">{img}<p>{L(lang, "关注公众号", "Follow us on WeChat:")}'
                      f'「{e(wx["name"])}」{L(lang, "，每周一推送新收录的短剧 skill。", " for new short-drama skills every Monday.")}</p></div>')
        return f"""<footer class="site-footer"><div class="wrap">
{follow}
<p>{L(lang, '数据更新于', 'Data updated')} {self.d.updated} · {L(lang, '每周一自动刷新星数和更新时间', 'Stars and update dates refresh every Monday')} · <a href="{REPO_URL}">GitHub</a> · <a href="{REPO_URL}/issues/new?template=submit-skill.yml">{L(lang, '推荐项目', 'Suggest a skill')}</a> · <a href="/llms.txt">llms.txt</a> · <a href="/data.json">data.json</a></p>
<p>{L(lang, '我们写的简介、点评和分类以 CC0 发布，可自由引用；「仓库自述」和 SKILL.md 说明摘自原仓库，版权归原作者，作者希望撤下可以提 issue。「人工核对」指核对过仓库说明和分类，不代表实测过效果。', 'Our summaries, notes and categories are released under CC0. Repo descriptions and SKILL.md text are quoted from each repo and belong to their authors; authors can ask for removal via an issue. "Checked" means the README and category were reviewed by hand, not that the skill was tested.')}</p>
</div></footer>"""

    # ───────────────────────── 组件 ─────────────────────────

    def status(self, s: dict, lang: str) -> str:
        m = self.d.m(s)
        if m.get("status") == "missing":
            return f'<span class="badge warn">{L(lang, "仓库失效", "Repo missing")}</span>'
        if m.get("archived"):
            return f'<span class="badge warn">{L(lang, "已归档", "Archived")}</span>'
        if m.get("pushed_at") and (self.d.ref - dt.date.fromisoformat(m["pushed_at"])).days > STALE_DAYS:
            return f'<span class="badge">{L(lang, "超过 180 天未更新", "No updates in 180+ days")}</span>'
        return ""

    def stage_names(self, s: dict, lang: str, key: str = "short") -> list[str]:
        return [tr(st, key, lang) for k, st in self.d.taxonomy["stages"].items() if k in s["stages"]]

    def model_names(self, s: dict, lang: str) -> list[str]:
        models = tr(self.d.taxonomy, "models", lang)
        return [models[k] for k in s.get("models", [])]

    def entry(self, s: dict, lang: str) -> str:
        m = self.d.m(s)
        badges = []
        if s.get("tier") == "featured":
            badges.append(f'<span class="badge feat">{L(lang, "精选", "Featured")}</span>')
        if s["format"] != "skill":
            badges.append(f'<span class="badge">{e(L(lang, *FORMAT[s["format"]]).split("（")[0].split(" (")[0])}</span>')
        badges.append(self.status(s, lang))
        bits = [" · ".join(self.stage_names(s, lang))]
        if s.get("models"):
            bits.append(" / ".join(self.model_names(s, lang)))
        bits.append(L(lang, "更新于 ", "updated ") + (m.get("pushed_at") or "—"))
        if m.get("skill_count", 0) > 1:
            bits.append(L(lang, f"{m['skill_count']} 个 skill", f"{m['skill_count']} skills"))
        return (f'<li class="entry"><div class="entry-head"><a class="entry-name" href="{url(lang, repo_path(s))}">'
                f'{e(display_name(s))}</a><span class="stars">★ {fmt_stars(m.get("stars"))}</span>{"".join(badges)}</div>'
                f'<p class="entry-desc">{e(tr(s, "desc", lang))}</p>'
                f'<p class="entry-meta">{e(" · ".join(b for b in bits if b))}</p></li>')

    def entries(self, items, lang: str) -> str:
        return f'<ul class="entries">{"".join(self.entry(s, lang) for s in items)}</ul>'

    def item_list(self, lang: str, name: str, items: list[dict]) -> dict:
        return {"@context": "https://schema.org", "@type": "ItemList", "name": name, "numberOfItems": len(items),
                "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": abs_url(lang, repo_path(s)),
                                     "name": display_name(s)} for i, s in enumerate(items)]}

    def tiles(self, lang: str, rows: list[tuple[str, str, str]]) -> str:
        return '<ul class="tiles">' + "".join(
            f'<li><a href="{url(lang, p)}"><b>{e(t)}</b><span>{e(sub)}</span></a></li>' for p, t, sub in rows) + "</ul>"

    def names(self, items: list[dict], n: int = 3) -> list[str]:
        return [display_name(s) for s in items[:n]]

    # ───────────────────────── 页面 ─────────────────────────

    def home(self, lang: str) -> None:
        d = self.d
        n, platforms = len(d.indexed), len(d.skills) - len(d.indexed)
        stages = [(f"/stage/{k}/", tr(st, "label", lang), L(lang, f"{len(d.in_stage(k))} 个", f"{len(d.in_stage(k))} skills"))
                  for k, st in d.taxonomy["stages"].items() if d.in_stage(k)]
        models = tr(d.taxonomy, "models", lang)
        model_rows = [(f"/model/{k}/", label, L(lang, f"{len(d.in_model(k))} 个", f"{len(d.in_model(k))} skills"))
                      for k, label in models.items() if d.in_model(k)]
        featured = [s for s in d.skills if s.get("tier") == "featured"]
        groups = ""
        for k, g in d.groups.items():
            items = d.in_group(k)
            if not items:
                continue
            groups += (f'<h3 id="type-{k}"><a href="{url(lang, f"/type/{k}/")}">{e(tr(g, "label", lang))}</a>'
                       f'<span class="stars"> {len(items)}</span></h3><p class="sub">{e(tr(g, "intro", lang) or "")}</p>'
                       + self.entries(items[:5], lang)
                       + (f'<p class="section-more"><a href="{url(lang, f"/type/{k}/")}">'
                          f'{L(lang, f"查看全部 {len(items)} 个 →", f"See all {len(items)} →")}</a></p>' if len(items) > 5 else ""))
        new_html = (self.entries(d.new, lang) if d.new else
                    f'<p class="sub">{L(lang, "本周暂无新增。", "Nothing new this week.")}</p>')
        packs = "".join(
            f'<li><a href="{url(lang, "/packs/")}#pack-{i + 1}"><b>{e(tr(p, "name", lang))}</b>'
            f'<span>{e(tr(p, "goal", lang))}</span></a></li>' for i, p in enumerate(d.packs))
        body = f"""
<h1>{L(lang, 'AI 短剧 · 漫剧 Skill 精选', 'AI Short Drama Skills')}</h1>
<p class="lead">{L(lang,
    f'给千问、豆包、龙虾（OpenClaw）、WorkBuddy、Claude Code、Codex 等智能体用的短剧 skill（技能包）目录：从小说改编、分集剧本、钩子和付费卡点，到分镜、角色资产和 Seedance / 可灵 / MiniMax 视频提示词。收录 {n} 个 skill 项目和 {platforms} 个开源平台，按创作阶段和视频模型整理。',
    f'A curated directory of agent skills for AI short drama (micro drama, vertical drama) and AI manju, for Claude Code, Codex, OpenClaw and Chinese agents such as Qwen, Doubao and WorkBuddy: novel adaptation, episode scripts, hooks and paywall points, storyboards, character assets and prompts for Seedance, Kling and MiniMax. {n} skill projects and {platforms} open-source platforms, organized by production stage and video model.')}</p>
<p class="sub">{L(lang, f'每个项目都人工核对过仓库说明和分类；看过但没收的项目有 {len(d.ignored)} 个，都写了原因。数据更新于 {d.updated}。',
    f'Every entry was checked by hand against its README; {len(d.ignored)} more projects were reviewed and declined, each with a reason. Data updated {d.updated}.')}</p>
<div class="note"><p>{L(lang, '「人工核对」不等于实测过效果。安装前请先读一遍 skill 的 SKILL.md，带脚本的 skill 会在你的电脑上执行代码。', '"Checked" does not mean tested. Read a skill\'s SKILL.md before installing; skills that ship scripts run code on your machine.')} <a href="{url(lang, '/guides/install/')}">{L(lang, '怎么安装 →', 'How to install →')}</a></p></div>

<h2 id="by-stage">{L(lang, '按创作阶段找', 'By production stage')}</h2>
{self.tiles(lang, stages)}
<h2 id="by-model">{L(lang, '按视频模型找', 'By video model')}</h2>
{self.tiles(lang, model_rows)}
<h2 id="packs">{L(lang, '推荐组合', 'Suggested stacks')}</h2>
<p class="sub">{L(lang, '按目标搭配好的几个项目。初版依据仓库说明搭配，尚未实测。', 'Projects that work together toward one goal. A first pass based on each README; not yet tested.')}</p>
<ul class="tiles">{packs}</ul>
<h2 id="featured">{L(lang, '精选', 'Featured')}</h2>
{self.entries(featured, lang)}
<h2 id="new">{L(lang, '本周新增', 'New this week')}</h2>
{new_html}
<h2 id="by-type">{L(lang, '按类型', 'By type')}</h2>
{groups}
"""
        title = L(lang, f"AI 短剧 Skill 精选：{n} 个短剧、漫剧技能包（千问、豆包、龙虾、Claude Code 可用）",
                  f"AI Short Drama Skills: {n} curated agent skills for micro drama and manju (Claude Code, Codex, OpenClaw, Qwen, Doubao)")
        desc = L(lang, f"收录 {n} 个 AI 短剧 / 漫剧 skill：小说改编、分集剧本、分镜、角色资产、Seedance / 可灵 / MiniMax 视频提示词，按创作阶段和视频模型整理，千问、豆包、龙虾、Claude Code 等智能体都能装，每周更新。",
                 f"{n} curated agent skills for AI short drama and manju: adaptation, episode scripts, storyboards, character assets and Seedance / Kling / MiniMax prompts, organized by stage and video model, for Claude Code, Codex, OpenClaw and Chinese agents such as Qwen and Doubao, updated weekly.")
        website = {"@context": "https://schema.org", "@type": "WebSite", "name": "Awesome Short Drama Skills",
                   "alternateName": L(lang, "AI 短剧 Skill 精选", "AI Short Drama Skills"), "url": abs_url(lang, "/"),
                   "inLanguage": LANGS[lang]["hreflang"], "description": desc, "publisher": publisher(),
                   "sameAs": [REPO_URL]}
        self.page(lang, "/", title=title, description=desc, body=body, crumbs=[],
                  jsonld=[website, self.item_list(lang, L(lang, "精选", "Featured"), featured)])

    def stage_index(self, lang: str) -> None:
        d = self.d
        rows = [(f"/stage/{k}/", tr(st, "label", lang), L(lang, f"{len(d.in_stage(k))} 个", f"{len(d.in_stage(k))} skills"))
                for k, st in d.taxonomy["stages"].items() if d.in_stage(k)]
        body = (f'<h1>{L(lang, "按创作阶段找短剧 skill", "Short drama skills by production stage")}</h1>'
                f'<p class="lead">{L(lang, "短剧从选题到出片分九个阶段。卡在哪一步，就从哪一步进去找。", "Short drama production runs through nine stages, from topic to finished video. Start from the step you are stuck on.")}</p>'
                + self.tiles(lang, rows))
        self.page(lang, "/stage/", title=L(lang, "按创作阶段找 AI 短剧 Skill", "AI short drama skills by production stage"),
                  description=L(lang, "从选题、改编、人物、集纲、剧本、审稿、分镜、提示词到出片，按阶段查找 AI 短剧 skill。",
                                "Find AI short drama skills by stage: topic, adaptation, characters, episode outlines, script, review, storyboard, prompts and production."),
                  body=body, crumbs=[(L(lang, "按阶段", "By stage"), "/stage/")])

    def stage(self, lang: str, key: str, st: dict) -> None:
        d = self.d
        items = d.in_stage(key)
        if not items:
            return
        focused = [s for s in items if len(s["stages"]) <= SPECIALIST_MAX]
        broad = [s for s in items if len(s["stages"]) > SPECIALIST_MAX]
        label, short = tr(st, "label", lang), tr(st, "short", lang)
        top = join(lang, self.names(items))
        lead = L(lang,
                 f"目前收录 {len(items)} 个能帮你做「{label}」的 skill：专项 {len(focused)} 个（只覆盖 {SPECIALIST_MAX} 个以内的阶段），综合 {len(broad)} 个（全流程或多环节）。星数最高的是 {top}。数据更新于 {d.updated}。",
                 f"{len(items)} skills help with {label}: {len(focused)} focused (covering at most {SPECIALIST_MAX} stages) and {len(broad)} broad (full pipelines or several steps). Most starred: {top}. Data updated {d.updated}.")
        sections = ""
        for name, group in ((L(lang, "专项", "Focused"), focused), (L(lang, "综合", "Broad"), broad)):
            if group:
                sections += f"<h2>{name}（{len(group)}）</h2>" if lang == "zh" else f"<h2>{name} ({len(group)})</h2>"
                sections += self.entries(group, lang)
        body = f"<h1>{e(L(lang, f'短剧{short} Skill：{label}', f'Short drama {short.lower()} skills: {label}'))}</h1><p class=\"lead\">{e(lead)}</p>{sections}"
        title = L(lang, f"短剧{short} Skill 推荐：{len(items)} 个能做{label}的 Claude Code / Codex skill",
                  f"Short drama {short.lower()} skills: {len(items)} agent skills for {label}")
        desc = L(lang, f"{len(items)} 个 AI 短剧 / 漫剧{label} skill，按专项和综合分组、按星数排序，包括 {top}。",
                 f"{len(items)} AI short drama skills for {label}, grouped as focused or broad and sorted by stars, including {top}.")
        self.page(lang, f"/stage/{key}/", title=title, description=desc, body=body,
                  crumbs=[(L(lang, "按阶段", "By stage"), "/stage/"), (label, f"/stage/{key}/")],
                  jsonld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc,
                           "url": abs_url(lang, f"/stage/{key}/"), "inLanguage": LANGS[lang]["hreflang"],
                           "dateModified": d.updated}, self.item_list(lang, title, items)])

    def model_index(self, lang: str) -> None:
        d = self.d
        models = tr(d.taxonomy, "models", lang)
        rows = [(f"/model/{k}/", label, L(lang, f"{len(d.in_model(k))} 个", f"{len(d.in_model(k))} skills"))
                for k, label in models.items() if d.in_model(k)]
        body = (f'<h1>{L(lang, "按视频模型找短剧 skill", "Short drama skills by video model")}</h1>'
                f'<p class="lead">{L(lang, "提示词的写法跟模型绑定：给 Seedance 写的提示词，换到可灵上未必好用。这里只收仓库说明里明确写了适配哪个模型的项目。", "Prompt syntax is tied to the model: a prompt written for Seedance may not work in Kling. Only projects whose README names a model are listed.")}</p>'
                + self.tiles(lang, rows))
        self.page(lang, "/model/", title=L(lang, "按视频模型找 AI 短剧 Skill：Seedance、可灵、MiniMax H3", "AI short drama skills by video model: Seedance, Kling, MiniMax H3"),
                  description=L(lang, "按适配的图像 / 视频模型查找 AI 短剧 skill：Seedance / 即梦、MiniMax H3、可灵、通义万相、ComfyUI、Nano Banana、Veo、Sora。",
                                "Find AI short drama skills by the image or video model they target: Seedance / Jimeng, MiniMax H3, Kling, Wan, ComfyUI, Nano Banana, Veo, Sora."),
                  body=body, crumbs=[(L(lang, "按视频模型", "By video model"), "/model/")])

    def model(self, lang: str, key: str, label: str) -> None:
        d = self.d
        items = d.in_model(key)
        if not items:
            return
        top = join(lang, self.names(items))
        lead = L(lang,
                 f"目前收录 {len(items)} 个在仓库说明里写明适配 {label} 的短剧 skill，覆盖分镜、视频提示词和出片。星数最高的是 {top}。数据更新于 {d.updated}。",
                 f"{len(items)} short drama skills say in their README that they target {label}, covering storyboards, video prompts and production. Most starred: {top}. Data updated {d.updated}.")
        body = f"<h1>{e(L(lang, f'{label} 短剧 Skill', f'{label} skills for AI short drama'))}</h1><p class=\"lead\">{e(lead)}</p>{self.entries(items, lang)}"
        title = L(lang, f"{label} 短剧 Skill：{len(items)} 个适配 {label} 的分镜和提示词 skill",
                  f"{label} skills for AI short drama: {len(items)} storyboard and prompt skills")
        desc = L(lang, f"{len(items)} 个适配 {label} 的 AI 短剧 / 漫剧 skill，包括 {top}，按星数排序。",
                 f"{len(items)} AI short drama and manju skills that target {label}, including {top}, sorted by stars.")
        self.page(lang, f"/model/{key}/", title=title, description=desc, body=body,
                  crumbs=[(L(lang, "按视频模型", "By video model"), "/model/"), (label, f"/model/{key}/")],
                  jsonld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc,
                           "url": abs_url(lang, f"/model/{key}/"), "inLanguage": LANGS[lang]["hreflang"],
                           "dateModified": d.updated}, self.item_list(lang, title, items)])

    def type_index(self, lang: str) -> None:
        d = self.d
        rows = [(f"/type/{k}/", tr(g, "label", lang), L(lang, f"{len(d.in_group(k))} 个", f"{len(d.in_group(k))} projects"))
                for k, g in d.groups.items() if d.in_group(k)]
        body = (f'<h1>{L(lang, "按类型找短剧 skill", "Short drama skills by type")}</h1>'
                f'<p class="lead">{L(lang, "每个项目只归入一个类型：全流程、编剧、分镜和视觉、上游拆解、编剧基本功、去 AI 味，另附可自行部署的开源平台。", "Each project belongs to exactly one type: full pipelines, screenwriting, storyboards and visuals, upstream breakdown, fundamentals, de-AI, plus self-hostable open-source platforms.")}</p>'
                + self.tiles(lang, rows))
        self.page(lang, "/type/", title=L(lang, "按类型找 AI 短剧 Skill", "AI short drama skills by type"),
                  description=L(lang, "全流程、编剧、分镜与视频提示词、IP 评估、编剧基本功、去 AI 味和开源平台，按类型浏览全部 AI 短剧 skill。",
                                "Browse every AI short drama skill by type: full pipelines, screenwriting, storyboards and prompts, IP evaluation, fundamentals, de-AI and open-source platforms."),
                  body=body, crumbs=[(L(lang, "按类型", "By type"), "/type/")])

    def type_page(self, lang: str, key: str, g: dict) -> None:
        d = self.d
        items = d.in_group(key)
        if not items:
            return
        label = tr(g, "label", lang)
        cmds = [(display_name(s), install_cmd(s)) for s in items if install_cmd(s)]
        install = ""
        if cmds:
            lines = [L(lang, "# 默认命令基于 skills CLI，未逐个验证，以各仓库 README 为准",
                       "# Default commands use the skills CLI and were not verified one by one; follow each repo's README")]
            for name, cmd in cmds:
                lines += [f"# {name}", cmd]
            install = f'<h2>{L(lang, "安装命令", "Install commands")}</h2><pre><code>{e(chr(10).join(lines))}</code></pre>'
        top = join(lang, self.names(by_stars(items, d.meta)))
        body = (f'<h1>{e(label)}</h1><p class="lead">{e(tr(g, "intro", lang) or "")}</p>'
                f'<p class="sub">{e(L(lang, f"共 {len(items)} 个，精选在前、其余按星数排序。星数最高的是 {top}。", f"{len(items)} projects, featured first, then by stars. Most starred: {top}."))}</p>'
                + self.entries(items, lang) + install)
        title = L(lang, f"{label}｜AI 短剧 Skill（{len(items)} 个）", f"{label} | AI short drama skills ({len(items)})")
        desc = L(lang, f"{tr(g, 'intro', lang) or label} 共 {len(items)} 个，包括 {top}。",
                 f"{tr(g, 'intro', lang) or label} {len(items)} projects, including {top}.")
        self.page(lang, f"/type/{key}/", title=title, description=desc, body=body,
                  crumbs=[(L(lang, "按类型", "By type"), "/type/"), (label, f"/type/{key}/")],
                  jsonld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc,
                           "url": abs_url(lang, f"/type/{key}/"), "inLanguage": LANGS[lang]["hreflang"],
                           "dateModified": d.updated}, self.item_list(lang, title, items)])

    def packs(self, lang: str) -> None:
        d = self.d
        out = ""
        for i, p in enumerate(d.packs):
            members = [d.by_repo[r.lower()] for r in p["repos"]]
            chain = " → ".join(f'<a href="{url(lang, repo_path(s))}">{e(display_name(s))}</a>' for s in members)
            out += (f'<section class="pack" id="pack-{i + 1}"><h3>{e(tr(p, "name", lang))}</h3>'
                    f'<p class="sub">{e(tr(p, "goal", lang))}</p><p class="chain">{chain}</p>'
                    f'<p>{e(tr(p, "why", lang))}</p></section>')
        body = (f'<h1>{L(lang, "短剧 skill 推荐组合", "Suggested short drama skill stacks")}</h1>'
                f'<p class="lead">{L(lang, "一个 skill 很少能包办全部。这里按目标给出几个可以搭配使用的项目，前一个的产出交给后一个。", "One skill rarely covers everything. Each stack chains a few projects toward one goal, passing one output to the next.")}</p>'
                f'<div class="note"><p>{L(lang, "初版组合依据仓库说明搭配，尚未实测；实测完成后会更新，见", "These stacks are a first pass based on each README and have not been tested yet. They will be updated after testing; see")} <a href="{url(lang, "/evals/")}">{L(lang, "实测", "Tests")}</a>{L(lang, "。", ".")}</p></div>{out}')
        self.page(lang, "/packs/", title=L(lang, "AI 短剧 Skill 推荐组合：小说改编、爆款剧本、Seedance 出片、漫剧连载", "Suggested AI short drama skill stacks: adaptation, hit scripts, Seedance, manju serials"),
                  description=L(lang, "按目标搭配好的 AI 短剧 skill 组合：小说改编短剧、原创红果 / 抖音剧本、用 Seedance 出片、漫剧长线连载。",
                                "AI short drama skill stacks by goal: adapting a novel, original Hongguo / Douyin scripts, rendering with Seedance, long-running manju serials."),
                  body=body, crumbs=[(L(lang, "推荐组合", "Stacks"), "/packs/")])

    def repo(self, lang: str, s: dict) -> None:
        d = self.d
        m = d.m(s)
        name = display_name(s)
        owner = s["repo"].split("/")[0]
        desc = tr(s, "desc", lang)
        group = d.groups[s["group"]]
        stages = self.stage_names(s, lang, "label")
        models = self.model_names(s, lang)
        agents = [d.taxonomy["agents"].get(a, a) for a in s.get("agents", [])]
        fmt = L(lang, *FORMAT[s["format"]])
        stars = fmt_stars(m.get("stars"))

        # 开头一段直接回答「这是什么」，方便搜索和 AI 摘要引用
        short = self.stage_names(s, lang)
        kind = L(lang, *KIND[s["format"]])
        if lang == "zh":
            summary = f"{name} 是 GitHub 上 {owner} 的 {kind} 项目：{desc}。覆盖{join(lang, short)}阶段"
            summary += f"，提示词适配 {join(lang, models)}" if models else ""
            summary += f"，仓库写明支持 {join(lang, agents)}" if agents else ""
            summary += f"。目前 {stars} 星，最近更新于 {m.get('pushed_at') or '—'}"
            summary += f"，许可证 {m['license']}。" if m.get("license") else "，仓库未声明许可证。"
        else:
            article = "an" if kind[0] in "aeio" else "a"
            summary = f"{name} is {article} {kind} project by {owner} on GitHub: {desc.rstrip('.')}. It covers {join(lang, [x.lower() for x in short])}"
            summary += f", with prompts for {join(lang, models)}" if models else ""
            summary += f", and its README says it works with {join(lang, agents)}" if agents else ""
            summary += f". {stars} stars, last updated {m.get('pushed_at') or '—'}"
            summary += f", {m['license']} license." if m.get("license") else ", no license declared."

        facts = [
            (L(lang, "类型", "Type"), f'<a href="{url(lang, f"/type/{s["group"]}/")}">{e(tr(group, "label", lang))}</a>'),
            (L(lang, "创作阶段", "Stages"), " · ".join(
                f'<a href="{url(lang, f"/stage/{k}/")}">{e(tr(st, "short", lang))}</a>'
                for k, st in d.taxonomy["stages"].items() if k in s["stages"])),
        ]
        if models:
            facts.append((L(lang, "视频模型", "Video models"), " · ".join(
                f'<a href="{url(lang, f"/model/{k}/")}">{e(tr(d.taxonomy, "models", lang)[k])}</a>' for k in s["models"])))
        if agents:
            facts.append((L(lang, "支持的 agent", "Agents"), e(" · ".join(agents))))
        facts += [
            (L(lang, "形式", "Format"), e(fmt)),
            (L(lang, "正文语言", "Language"), e(L(lang, *LANG_NAME[s["lang"]]))),
            (L(lang, "GitHub 星数", "GitHub stars"), f"★ {stars}"),
            (L(lang, "最近更新", "Last updated"), e(m.get("pushed_at") or "—") + " " + self.status(s, lang)),
            (L(lang, "许可证", "License"), e(m.get("license") or L(lang, "未声明", "None declared"))),
        ]
        if total := d.index.get(s["repo"], {}).get("total"):  # 应用里和短剧无关的 SKILL.md 不算
            facts.append((L(lang, "SKILL.md 数量", "SKILL.md files"), str(total)))
        if s.get("checked"):
            facts.append((L(lang, "人工核对", "Checked by hand"), e(str(s["checked"]))))
        facts_html = '<dl class="facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts) + "</dl>"

        note = f'<div class="note"><p>{e(tr(s, "note", lang))}</p></div>' if s.get("note") else ""
        ov = d.overviews.get(s["repo"], {})
        overview = f'<h2>{L(lang, "编者说明", "Editor\'s notes")}</h2><p>{e(ov[lang])}</p>' if ov.get(lang) else ""
        gh_desc, translated = d.quote(m.get("description", ""), lang)
        about = (f'<h2>{L(lang, "仓库自述", "In the author\'s words")}</h2><blockquote><p>{e(gh_desc)}</p></blockquote>'
                 + ('<p class="sub">Translated from the Chinese original.</p>' if translated else "")
                 if gh_desc else "")

        idx = d.index.get(s["repo"], {})
        skill_html = ""
        if idx.get("skills"):
            branch = idx.get("branch", "main")
            lis = "".join(
                f'<li><b><a href="https://github.com/{e(s["repo"])}/blob/{e(branch)}/{e(k["path"])}">{e(k["name"])}</a></b>'
                + (f'<p>{e(desc)}</p>' if (desc := d.quote(k["description"], lang)[0]) else "") + "</li>"
                for k in idx["skills"])
            more = idx["total"] - len(idx["skills"])
            more_html = f'<p class="sub">{L(lang, f"另有 {more} 个未列出。", f"{more} more not listed.")}</p>' if more > 0 else ""
            skill_html = (f'<h2>{L(lang, f"仓库里的 skill（{idx['total']} 个）", f"Skills in this repo ({idx['total']})")}</h2>'
                          f'<p class="sub">{L(lang, "名字和说明取自各 SKILL.md 的 frontmatter。", "Names and descriptions come from each SKILL.md frontmatter; Chinese descriptions are shown in our English translation.")}</p>'
                          f'<ul class="skill-list">{lis}</ul>{more_html}')

        cmd = install_cmd(s)
        install = ""
        if cmd:
            lines = [cmd]
            if idx.get("total", 0) > 1 and not s.get("install"):
                first = idx["skills"][0]["name"]
                lines += ["", L(lang, "# 只装其中一个 skill", "# install a single skill"), f"{cmd} --skill {first}"]
            if not s.get("install"):
                lines += ["", L(lang, "# 指定 agent（claude-code / codex / cursor / opencode / gemini-cli / openclaw）",
                                "# pick agents (claude-code / codex / cursor / opencode / gemini-cli / openclaw)"),
                          f"{cmd} -a claude-code -a codex"]
            install = (f'<h2>{L(lang, "安装", "Install")}</h2><pre><code>{e(chr(10).join(lines))}</code></pre>'
                       f'<p class="sub">{L(lang, "默认命令基于", "Default commands use the")} <a href="https://github.com/vercel-labs/skills">skills CLI</a>'
                       f'{L(lang, "，未逐个验证，以仓库 README 为准。安装前先读一遍 SKILL.md。", " and were not verified one by one; follow the repo README. Read SKILL.md before installing.")}'
                       f' <a href="{url(lang, "/guides/install/")}">{L(lang, "安装指南 →", "Install guide →")}</a></p>')
        elif s["format"] == "prompts":
            install = (f'<h2>{L(lang, "怎么用", "How to use")}</h2><p>{L(lang, "这是提示词文件，不是标准 skill，不能用 skills CLI 安装。按仓库 README 把提示词复制进对话或项目使用。", "These are prompt files, not a standard skill, so the skills CLI cannot install them. Copy the prompts into your chat or project as the README describes.")}</p>')

        in_packs = [(i, p) for i, p in enumerate(d.packs) if s["repo"].lower() in {r.lower() for r in p["repos"]}]
        packs_html = ""
        if in_packs:
            packs_html = (f'<h2>{L(lang, "出现在这些推荐组合里", "Part of these stacks")}</h2><ul>'
                          + "".join(f'<li><a href="{url(lang, "/packs/")}#pack-{i + 1}">{e(tr(p, "name", lang))}</a>：{e(tr(p, "goal", lang))}</li>'
                                    if lang == "zh" else
                                    f'<li><a href="{url(lang, "/packs/")}#pack-{i + 1}">{e(tr(p, "name", lang))}</a>: {e(tr(p, "goal", lang))}</li>'
                                    for i, p in in_packs) + "</ul>")

        tested = ""
        rounds = d.evaluated.get(s["repo"].lower(), [])
        if rounds:
            tested = (f'<h2>{L(lang, "实测", "Tested")}</h2>'
                      + "".join(self.tested_round(d, s, run, lang) for run in rounds))
        mine = set(s["stages"])

        peers = [x for x in d.skills if x is not s and x["group"] == s["group"]]
        peers.sort(key=lambda x: (-len(mine & set(x["stages"])) / len(mine | set(x["stages"])), -d.stars(x)))
        alt = (f'<h2>{L(lang, "同类项目", "Similar projects")}</h2>{self.entries(peers[:5], lang)}' if peers else "")

        issue = f"{REPO_URL}/issues/new?title=" + urllib.parse.quote(f"[更正] {s['repo']}")
        body = f"""<h1>{e(name)}</h1>
<p class="sub">{e(s['repo'])}</p>
<p class="lead">{e(summary)}</p>
{note}
{overview}
{facts_html}
<div class="actions"><a class="btn primary" href="https://github.com/{e(s['repo'])}">{L(lang, '在 GitHub 查看', 'View on GitHub')}</a><a class="btn" href="{issue}">{L(lang, '信息有误？提交更正', 'Report an error')}</a></div>
{about}
{tested}
{skill_html}
{install}
{packs_html}
{alt}
"""
        title = L(lang, f"{name}：{clip(desc, 40)}｜AI 短剧 Skill", f"{name}: {clip(desc, 70)} | AI Short Drama Skills")
        meta_desc = clip(summary, 150 if lang == "zh" else 300)
        code_ld = {
            "@context": "https://schema.org", "@type": "SoftwareSourceCode", "name": name, "description": desc,
            "codeRepository": f"https://github.com/{s['repo']}", "url": abs_url(lang, repo_path(s)),
            "keywords": [*stages, *models, L(lang, "AI 短剧", "AI short drama"), "agent skill"],
            "inLanguage": LANGS[lang]["hreflang"],
        }
        if m.get("license"):
            code_ld["license"] = f"https://spdx.org/licenses/{m['license']}"
        if m.get("pushed_at"):
            code_ld["dateModified"] = m["pushed_at"]
        if agents:
            code_ld["runtimePlatform"] = agents
        self.page(lang, repo_path(s), title=title, description=meta_desc, body=body,
                  crumbs=[(tr(group, "label", lang), f"/type/{s['group']}/"), (name, repo_path(s))],
                  jsonld=[code_ld], lastmod=max(d.updated, str(s.get("checked") or "")))

    def tested_round(self, d: Data, s: dict, run: str, lang: str) -> str:
        """项目页「实测」一节里，这个项目参加过的一轮实测的成绩。"""
        zh_n, en_n, anchor = ROUNDS[run]
        slug = s["repo"].replace("/", "__")
        out = f"{REPO_URL}/tree/main/evals/runs/{run}/{slug}"
        links = (f'<a href="{url(lang, "/evals/")}#{anchor}">{L(lang, "看点评", "Read the results")}</a> · '
                 + f'<a href="/evals/{anchor}/">{L(lang, "看每次运行的完整过程", "See every step of each run (Chinese)")}</a> · '
                 + f'<a href="{out}">{L(lang, "看它的原始产出", "See its raw output")}</a></p>')
        if build_evals.judge.spec(run).pairing == "all":
            st, score = d.standings.get((run, slug), {}), ""
            if "opus" in st:
                place, n, _, _ = st["opus"]
                w, ti, lo = st["vs_base"]
                score = L(lang, f"和另外 {n - 1} 个参赛者（含不装 skill 的对照组）两两盲比，积分第 {place} 名（共 {n} 名）；"
                                f"对对照组三次 {w} 赢 {ti} 平 {lo} 输。",
                          f"Compared blind with the other {n - 1} entrants, including a no-skill control, it placed "
                          f"{ordinal(place)} of {n} on points; against the control over three runs it won {w}, tied {ti}, lost {lo}. ")
            if "gpt" in st:
                score += L(lang, f"换 GPT 复核：积分第 {st['gpt'][0]} 名。", f"Re-judged by GPT: placed {ordinal(st['gpt'][0])}. ")
            return "<p>" + L(lang, f"参加了{zh_n}选题实测。", f"Took part in {en_n} of our tests, on story premises. ") + score + links
        rec = d.duels.get((run, slug), {})
        score = ""
        if rec:
            sc, ol = rec.get("script", [0, 0, 0]), rec.get("outline", [0, 0, 0])
            score = L(lang, f"和不装 skill 的对照组盲比三次：剧本 {sc[0]} 赢 {sc[1]} 平 {sc[2]} 输，人物大纲 {ol[0]} 赢 {ol[1]} 平 {ol[2]} 输。",
                      f"Blind comparisons with a no-skill control over three runs: scripts {sc[0]} won, {sc[1]} tied, "
                      f"{sc[2]} lost; characters and outline {ol[0]} won, {ol[1]} tied, {ol[2]} lost. ")
        gpt = d.duels_gpt.get((run, slug), {})
        if gpt:
            gs, go = gpt.get("script", [0, 0, 0]), gpt.get("outline", [0, 0, 0])
            score += L(lang, f"换 GPT 复核：剧本 {gs[0]} 赢 {gs[1]} 平 {gs[2]} 输，人物大纲 {go[0]} 赢 {go[1]} 平 {go[2]} 输。",
                       f"Re-judged by GPT: scripts {gs[0]} won, {gs[1]} tied, {gs[2]} lost; characters and outline "
                       f"{go[0]} won, {go[1]} tied, {go[2]} lost. ")
        return "<p>" + L(lang, f"参加了{zh_n}剧本实测。", f"Took part in {en_n} of our script tests. ") + score + links

    def content(self, lang: str, slug: str, crumbs: list[tuple[str, str]]) -> None:
        raw = (WEB / "content" / lang / f"{slug.replace('/', '__')}.html").read_text(encoding="utf-8")
        m = re.match(r"<!--\s*\n(.*?)\n-->\s*\n", raw, re.S)
        fields = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
        fields = {k.strip(): v.strip() for k, v in fields.items()}
        body = self.fill(raw[m.end():], lang)
        updated = fields.get("updated", self.d.updated)
        path = f"/{slug}/"
        jsonld = [{"@context": "https://schema.org", "@type": "Article", "headline": fields["title"],
                   "description": fields["description"], "inLanguage": LANGS[lang]["hreflang"],
                   "dateModified": updated, "author": publisher(), "publisher": publisher(),
                   "mainEntityOfPage": abs_url(lang, path)}]
        if slug == "glossary":
            terms = re.findall(r'<dt id="([^"]+)">(.*?)</dt>\s*<dd>(.*?)</dd>', body, re.S)
            jsonld.append({"@context": "https://schema.org", "@type": "DefinedTermSet",
                           "name": fields["title"], "url": abs_url(lang, path),
                           "hasDefinedTerm": [{"@type": "DefinedTerm", "name": re.sub("<[^>]+>", "", t),
                                               "description": re.sub(r"\s+", " ", re.sub("<[^>]+>", "", dd)).strip(),
                                               "url": abs_url(lang, path) + "#" + i} for i, t, dd in terms]})
        page = (f'<article class="prose"><h1>{e(fields["title"])}</h1>{body}'
                f'<p class="updated">{L(lang, "更新于", "Updated")} {updated}</p></article>')
        self.page(lang, path, title=fields.get("seo_title", fields["title"]), description=fields["description"],
                  body=page, crumbs=crumbs + [(fields.get("crumb", fields["title"]), path)], jsonld=jsonld,
                  lastmod=updated, og_type="article")

    def fill(self, text: str, lang: str) -> str:
        d = self.d
        wx = SITE["wechat"]["name"]
        langs = [s["lang"] for s in d.skills]
        repl = {
            "count": str(len(d.indexed)), "platforms": str(len(d.skills) - len(d.indexed)),
            "ignored": str(len(d.ignored)), "updated": d.updated, "repo_url": REPO_URL,
            "skill_files": str(sum(len(v.get("skills", [])) for v in d.index.values())),
            "lang_zh": str(langs.count("zh")), "lang_en": str(langs.count("en")), "lang_multi": str(langs.count("multi")),
            "no_license": str(sum(1 for s in d.skills if not d.m(s).get("license"))),
            "maintainer_line": (L(lang, f"由公众号「{wx}」维护。", f"Maintained by the WeChat account 「{wx}」.") if wx else
                                L(lang, "由 GitHub 用户 UnderleveledBuilder 维护。", "Maintained by UnderleveledBuilder on GitHub.")),
        }
        return re.sub(r"\{\{(\w+)\}\}", lambda m: repl[m.group(1)], text)

    def guides_index(self, lang: str) -> None:
        items = ""
        for slug in GUIDES:
            raw = (WEB / "content" / lang / f"guides__{slug}.html").read_text(encoding="utf-8")
            title = re.search(r"title:\s*(.+)", raw).group(1).strip()
            desc = re.search(r"description:\s*(.+)", raw).group(1).strip()
            items += f'<li class="entry"><a class="entry-name" href="{url(lang, f"/guides/{slug}/")}">{e(title)}</a><p class="entry-desc">{e(desc)}</p></li>'
        items += (f'<li class="entry"><a class="entry-name" href="{url(lang, "/glossary/")}">{L(lang, "短剧术语表", "Short drama glossary")}</a>'
                  f'<p class="entry-desc">{L(lang, "漫剧、集纲、钩子、付费卡点、分镜、角色一致性等常用词的解释。", "Plain definitions of manju, episode outlines, hooks, paywall points, storyboards, character consistency and more.")}</p></li>')
        body = (f'<h1>{L(lang, "指南", "Guides")}</h1><p class="lead">{L(lang, "第一次用 agent 做短剧，从这几篇看起。", "New to making short dramas with an agent? Start here.")}</p>'
                f'<ul class="entries">{items}</ul>')
        self.page(lang, "/guides/", title=L(lang, "AI 短剧 Skill 指南：是什么、怎么装、怎么选", "AI short drama skill guides: what they are, how to install, how to choose"),
                  description=L(lang, "AI 短剧 skill 入门：什么是短剧 skill、在千问、豆包、龙虾、Claude Code 等智能体里怎么安装、怎么挑选，以及常用术语。",
                                "Getting started with AI short drama skills: what they are, how to install them in Claude Code, Codex, OpenClaw, Qwen or Doubao, how to choose, and key terms."),
                  body=body, crumbs=[(L(lang, "指南", "Guides"), "/guides/")])

    def not_found(self) -> None:
        body = """<h1>页面不存在 · Page not found</h1>
<p class="lead">这个地址没有内容，可能项目改名或被移除了。<br>This page does not exist; the project may have been renamed or removed.</p>
<p><a class="btn primary" href="/">返回首页</a> <a class="btn" href="/en/">Back to home</a></p>"""
        doc = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>页面不存在 · Page not found | Awesome Short Drama Skills</title><meta name="robots" content="noindex">
<link rel="icon" href="/static/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{self.css}"></head>
<body><div class="wrap"><main>{body}</main></div></body></html>"""
        (DIST / "404.html").write_text(doc, encoding="utf-8")

    # ───────────────────────── 机器可读文件 ─────────────────────────

    def data_json(self) -> None:
        d = self.d
        items = []
        for s in d.skills:
            m = d.m(s)
            idx = d.index.get(s["repo"], {})
            items.append({
                "repo": s["repo"], "name": display_name(s), "github": f"https://github.com/{s['repo']}",
                "page": {"zh": abs_url("zh", repo_path(s)), "en": abs_url("en", repo_path(s))},
                "desc": {"zh": s["desc"], "en": s.get("desc_en") or s["desc"]},
                "note": {"zh": s.get("note"), "en": s.get("note_en") or s.get("note")} if s.get("note") else None,
                "overview": d.overviews.get(s["repo"]) and {k: d.overviews[s["repo"]].get(k) for k in ("zh", "en")},
                "type": s["group"], "stages": s["stages"], "models": s.get("models", []), "agents": s.get("agents", []),
                "format": s["format"], "language": s["lang"], "featured": s.get("tier") == "featured",
                "install": install_cmd(s), "checked": str(s["checked"]) if s.get("checked") else None,
                "stars": m.get("stars"), "pushed_at": m.get("pushed_at"), "license": m.get("license"),
                "archived": m.get("archived", False), "skill_count": m.get("skill_count"),
                "skills": [k["name"] for k in idx.get("skills", [])],
            })
        t = d.taxonomy
        out = {
            "name": "Awesome Short Drama Skills", "url": BASE + "/", "source": REPO_URL, "license": "CC0-1.0",
            "license_note": "CC0 covers our summaries, notes and categories. Linked repos keep their own licenses.",
            "updated": d.updated, "count": len(items),
            "taxonomy": {
                "types": {k: {"zh": g["label"], "en": g.get("label_en")} for k, g in t["groups"].items()},
                "stages": {k: {"zh": st["label"], "en": st.get("label_en")} for k, st in t["stages"].items()},
                "models": {k: {"zh": v, "en": t["models_en"].get(k, v)} for k, v in t["models"].items()},
            },
            "items": items,
        }
        (DIST / "data.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    def llms(self) -> None:
        d = self.d
        n = len(d.indexed)
        lines = [
            "# Awesome Short Drama Skills",
            "",
            f"> A curated, bilingual (Chinese / English) directory of {n} agent skills for AI short drama "
            "(micro drama, vertical drama) and AI manju (AI 漫剧), for Claude Code, Codex, OpenClaw (龙虾) and Chinese agents "
            "such as QwenWork (千问办公), Doubao (豆包) and WorkBuddy: novel "
            "adaptation, episode scripts, hooks and paywall points, script review, storyboards, character assets and "
            f"prompts for Seedance, Kling and MiniMax H3. Plus {len(d.skills) - n} open-source platforms. "
            f"Every entry is checked by hand against its README; data updated {d.updated} and refreshed weekly.",
            "",
            "Chinese pages live at the site root, English pages under /en/. The same data is on GitHub "
            f"({REPO_URL}) and as JSON at {BASE}/data.json (CC0). \"Checked\" means the README and category were "
            "reviewed, not that the skill was tested.",
            "",
            "## Start here",
            f"- [What is an AI short drama skill]({abs_url('en', '/guides/what-is-a-short-drama-skill/')}): definition, how it differs from prompts and apps",
            f"- [How to install]({abs_url('en', '/guides/install/')}): Claude Code, Codex, OpenClaw, QwenWork, Doubao, WorkBuddy, Kimi Code, Trae and other agents",
            f"- [How to choose]({abs_url('en', '/guides/how-to-choose/')}): what to check before installing",
            f"- [How to write a vertical short drama script with AI]({abs_url('en', '/guides/write-script-with-ai/')}): seven steps drawn from the round one test",
            f"- [Glossary]({abs_url('en', '/glossary/')}): manju, episode outlines, hooks, paywall points, storyboards",
            f"- [Suggested stacks]({abs_url('en', '/packs/')}): projects that work together toward one goal",
            f"- [中文首页]({abs_url('zh', '/')}): AI 短剧 · 漫剧 Skill 精选",
            "",
            "## By production stage",
        ]
        for k, st in d.taxonomy["stages"].items():
            items = d.in_stage(k)
            if items:
                lines.append(f"- [{st.get('label_en')}]({abs_url('en', f'/stage/{k}/')}): {len(items)} skills, e.g. {', '.join(self.names(items))}")
        lines += ["", "## By video model"]
        for k, label in d.taxonomy["models_en"].items():
            items = d.in_model(k)
            if items:
                lines.append(f"- [{label}]({abs_url('en', f'/model/{k}/')}): {len(items)} skills, e.g. {', '.join(self.names(items))}")
        lines += ["", "## All projects"]
        for s in d.skills:
            m = d.m(s)
            lines.append(f"- [{display_name(s)}]({abs_url('en', repo_path(s))}) (★{fmt_stars(m.get('stars'))}, "
                         f"{d.groups[s['group']].get('label_en')}): {s.get('desc_en') or s['desc']}")
        lines += ["", "## Tests",
                  f"- [Round two: premise skills for web novels and short dramas]({abs_url('en', '/evals/')}#round-2): 11 web "
                  "novel and short drama premise skills and a no-skill control each chose a premise for a new revenge-fantasy "
                  "story that could become a web novel or a vertical short drama (no genre, length or platform given), three "
                  "runs each with the same model (Claude Code, claude-opus-5-5). Every entry was compared blind with every "
                  "other; reviewers judge as if AI will make the whole drama, so effects and big casts cost no points. Both "
                  "reviewers (Opus and GPT) put the same three skills on top: Tomsawyerhu/Chinese-WebNovel-Skill, "
                  "lingfengQAQ/webnovel-writer and Hao0321/ai-short-drama; the no-skill control placed 9th of 12 with both.",
                  f"- [Round two full record]({abs_url('zh', '/evals/round-2/')}) (Chinese): every run, the anonymous premises, "
                  "the prompt and verdict of every blind comparison (judged by Opus, re-judged by GPT), reviewer health checks "
                  "and the process log.",
                  f"- [Round one: script-writing skills on an open brief]({abs_url('en', '/evals/')}#round-1): a one-line brief "
                  "(a vertical short drama, 60 episodes of 1-2 minutes, no genre or plot) given to 10 script-writing skills and a "
                  "no-skill control, three runs each with the same model (Claude Code, claude-opus-5-5), compared blind with the "
                  "control, judged as if AI will make the whole drama. Both reviewers found four skills beating the control in all "
                  "three runs on both scripts and outlines: zenstory-ai/drama-skills, Shanyin-ai/shanyin-screenwriting-master, "
                  "jtydhr88/screenwriting-skills and adoria111/emma-screenwriting-skills. Skills changed which kind of story got "
                  "written, but the model's default names "
                  "(a character called Xiaoman in 15 of 33 drafts) appeared regardless of skill.",
                  f"- [Round one full record]({abs_url('zh', '/evals/round-1/')}) (Chinese): every input, every step of every run, "
                  "the anonymous drafts, the prompt and verdict of every blind comparison (judged by Opus, re-judged by GPT), "
                  "reviewer health checks and the process log; numbers are recomputed from the raw data at build time.",
                  f"- Raw outputs, logs, story cards and every blind comparison: {REPO_URL}/tree/main/evals/runs"]
        lines += ["", "## Optional", f"- [Full data as JSON]({BASE}/data.json)", f"- [GitHub source]({REPO_URL})", ""]
        (DIST / "llms.txt").write_text("\n".join(lines), encoding="utf-8")

    def sitemap(self) -> None:
        # sitemap.xml 是索引，按语言分文件：GSC 能分开看中英文收录；
        # 头条站长平台写着"不超过 300 条"（说的是条数还是文件数没写清），所以每个文件再按 300 条切
        rows: dict = {lang: [] for lang in LANGS}
        for path, lastmod in self.pages:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{LANGS[x]["hreflang"]}" href="{abs_url(x, path)}"/>'
                           for x in LANGS)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("zh", path)}"/>'
            for lang in LANGS:
                rows[lang].append((lastmod, f"<url><loc>{abs_url(lang, path)}</loc><lastmod>{lastmod}</lastmod>{alts}</url>"))
        for path, lastmod in self.zh_pages:
            rows["zh"].append((lastmod, f"<url><loc>{abs_url('zh', path)}</loc><lastmod>{lastmod}</lastmod></url>"))
        index = []
        for lang, items in rows.items():
            for i in range(0, len(items), SITEMAP_MAX):
                chunk = items[i:i + SITEMAP_MAX]
                name = f"sitemap-{lang}-{i // SITEMAP_MAX + 1}.xml"
                (DIST / name).write_text(
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                    + "\n".join(r for _, r in chunk) + "\n</urlset>\n", encoding="utf-8")
                index.append(f"<sitemap><loc>{BASE}/{name}</loc><lastmod>{max(m for m, _ in chunk)}</lastmod></sitemap>")
        (DIST / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(index) + "\n</sitemapindex>\n", encoding="utf-8")
        if SITE.get("indexnow_key"):
            (DIST / f"{SITE['indexnow_key']}.txt").write_text(SITE["indexnow_key"], encoding="utf-8")
        (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")

    def build(self) -> None:
        if DIST.exists():
            shutil.rmtree(DIST)
        shutil.copytree(WEB / "static", DIST / "static")
        shutil.copy(WEB / "_headers", DIST / "_headers")
        shutil.copy(WEB / "_routes.json", DIST / "_routes.json")  # Functions（访问日志）只跑在页面上
        d = self.d
        for lang in LANGS:
            self.home(lang)
            self.stage_index(lang)
            for k, st in d.taxonomy["stages"].items():
                self.stage(lang, k, st)
            self.model_index(lang)
            for k, label in tr(d.taxonomy, "models", lang).items():
                self.model(lang, k, label)
            self.type_index(lang)
            for k, g in d.groups.items():
                self.type_page(lang, k, g)
            self.packs(lang)
            for s in d.skills:
                self.repo(lang, s)
            self.guides_index(lang)
            for slug in GUIDES:
                self.content(lang, f"guides/{slug}", [(L(lang, "指南", "Guides"), "/guides/")])
            self.content(lang, "glossary", [])
            self.content(lang, "evals", [])
            self.content(lang, "about", [])
        build_evals.build(self, ROUNDS, REPO_URL, repo_path, display_name)
        self.not_found()
        self.data_json()
        self.llms()
        self.sitemap()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true", help="生成后启动本地预览 http://localhost:8000")
    args = ap.parse_args()
    site = Site(Data())
    site.build()
    n = sum(1 for _ in DIST.rglob("index.html"))
    print(f"已生成 {DIST.relative_to(ROOT)}：{n} 个页面（中英各 {len(site.pages)}，另有只出中文的实测记录 {len(site.zh_pages)} 页）。")
    if site.d.untranslated:
        print(f"提示：英文版有 {len(site.d.untranslated)} 段第三方中文说明没有译文，暂不显示；"
              "把「原文: 译文」补进 data/translations.json 即可。")
    if args.serve:
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)
        print("预览：http://localhost:8000")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()


if __name__ == "__main__":
    main()
