#!/usr/bin/env python3
"""实测评审：把每次运行的三项交付拼成匿名稿，抽故事卡，再让评审两两盲比。

用法（在仓库根目录，按顺序）：
  python evals/judge.py locate 001-open-brief --work /tmp/judge   # 找出每次运行里哪些文件是小传、大纲、剧本
  python evals/judge.py pack   001-open-brief --work /tmp/judge   # 拼成匿名稿，随机编号，对应关系存在 --work 里
  python evals/judge.py cards  001-open-brief --work /tmp/judge   # 每份匿名稿抽一张故事卡
  python evals/judge.py cluster 001-open-brief --work /tmp/judge  # 按故事卡把所有剧分成故事类型，看谁和谁是同一个套路
  python evals/judge.py duel   001-open-brief --work /tmp/judge   # 按这一轮的配对方式两两比，两种顺序各比一次
  python evals/judge.py reveal 001-open-brief --work /tmp/judge   # 评完后揭晓：把故事卡、比较结果和对应关系写进 evals/runs/<premise>/

  python evals/judge.py duel 001-open-brief --work /tmp/judge --judge gpt     # 换 GPT 当评审复核，结果另存 *-gpt
  python evals/judge.py duel 003-skeleton --work /tmp/judge --sample 5        # 先试判 5 对（10 场）看理由
  python evals/judge.py duel 003-skeleton --work /tmp/judge --pairs 123:456   # 只试判指定的几对
  python evals/judge.py cluster 001-open-brief --work /tmp/judge --judge gpt

主评审和故事卡用和参赛者相同的模型（claude-opus-5-5），不给任何工具，只看匿名稿。
复核评审是 GPT（经 Codex CLI），用一字不差的提示词和输出格式；为了不读进本机的个人指令，
它用一个只链接了登录凭据的干净 CODEX_HOME（环境变量 JUDGE_CODEX_HOME）。
每次调用的提示词指纹（sha256）和原始返回存在 --work/raw/<评审>/ 下。
locate 的结果写在 evals/runs/<premise>/deliverables.toml，可以人工改。只用标准库。

每一轮的交付、提示词、比较维度和配对方式不一样，登记在文件末尾的 SPECS 里：
第一轮（001-open-brief）比剧本和人物大纲，每个 skill 只和对照组比；第二轮（002-topic）比选题，所有参赛者两两全比。
两两比较的提示词 10-22 换成了第二版评分标准（不按拍摄成本扣分），两轮都用新提示词重判；
抽故事卡和分组的提示词没变，不要改，verify.py 要靠它们重建当时的提示词。
第三轮（003-skeleton）比全剧骨架，用第三版评分标准：评委提示词只写目标，附上共同的选题卡，只判甲或乙，
不抽故事卡、不分组（大家写的是同一个故事）。超过 3000 字的骨架，评委只看前 3000 字（max_chars，pack 时截断）。
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"
MODEL = "claude-opus-5-5"
EFFORT = "high"
GPT_MODEL = "gpt-6-astra"
GPT_EFFORT = "high"
JUDGE = "opus"                 # 由 --judge 设定
RAW: Path | None = None        # 原始返回存在这里；由 main() 设定
PARTS = {"bios": "人物小传", "outline": "分集大纲", "scripts": "第 1–3 集剧本"}
TEXT = {".md", ".txt", ".markdown", ".fountain", ".json", ".yaml", ".yml", ".csv", ".html"}

LOCATE = """下面是一次短剧创作留下的文件清单，每个文件附了开头。需求要三项交付：人物小传、60 集分集大纲、第 1–3 集完整剧本。
请指出每项交付对应哪些文件（相对路径，按阅读顺序）。只选最终交付的正文；过程文件、检查报告、设定草稿、方案备选、
配置和数据文件都不选。一个文件同时包含几项交付时，几项都写它。某项找不到就给空列表。

{listing}"""

CARD = """下面是一部竖屏短剧的人物小传、分集大纲和前三集剧本。请如实抽出这部剧的基本信息，只写稿子里有的内容，不评价好坏。

{text}"""

CLUSTER = """下面是 {n} 部竖屏短剧的简介，每部有一个编号。请按「故事类型」把它们分组：同一组的剧，核心设定和主线冲突属于同一种套路（比如「全职主妇离婚时拿账本清算婆家」「入殓师从遗体上发现命案」），换个名字和细节就差不多是同一个故事。分组要尽量细，宁可多分几组；每部只进一组；只有一部的也单独成组。给每组起一个短名字，再写一句这一组的共同套路。

{lines}"""

DUEL = """你要把稿子交给 AI 从头拍成竖屏短剧：没有演员和片场，画面、声音、口型都由视频模型生成，场面大小不影响花费。你同时替目标观众判断：拍出来，他们会不会一直看下去。
下面是两份{part}，甲和乙，各自来自一部不同的竖屏短剧（全剧 60 集，每集 1–2 分钟）。
两部剧的题材和故事可能完全不同；你不知道它们出自谁。请只比较写作本身的质量，按下面几个维度逐项判断哪份更好：

{dims}

注意：
- 不扣分：特效、异能、奇幻、大场面、群戏、场景多、角色多、古代和年代布景、水下、天上、动物和怪物。对 AI 来说，这些不额外花钱。
- 也不加分：场面大不等于好看。场面只有落在人物和爽点上，才算数。
- 篇幅长、格式花哨、自带检查清单或说明文字都不加分；夹在正文里的元数据、编号、检查点要拿掉才能交给 AI 出片，算缺点。
- 剧本按每集 1–2 分钟衡量：按画面和台词估，明显装不下的算缺点；情绪和爽点靠心里话和大段旁白推进、没有落在脸上和动作上的，也算缺点。
- 两份差不多就判「平」。理由要引用原文。

=== 甲 ===
{a}

=== 乙 ===
{b}"""

DIMS = {
    "bios": {"人物": "动机清不清楚，有没有缺点和成长，配角是不是工具人",
             "新意": "人物设定和关系有没有新鲜感，是不是常见套路"},
    "outline": {"结构": "冲突升级、反转成不成立，有没有连续塌腰",
                "卡点": "付费卡点卡得准不准，卡点前有没有足够的钩子",
                "新意": "设定和桥段有没有新鲜感，是不是常见套路"},
    "scripts": {"钩子": "开头和每集结尾能不能让人想往下看",
                "对白": "像不像人说的话，角色之间有没有区别",
                "AI 味": "套话、排比、空洞形容词多不多",
                "上屏": "每集 1–2 分钟装不装得下（按画面和台词估，不按场景数、演员数）；情绪和爽点有没有落在脸上和动作上，"
                        "而不是靠心里话和大段旁白；稿子能不能直接交给 AI 出片，夹带编号和自检表算缺点"},
}

TRACKS = {"script": ["scripts"], "outline": ["bios", "outline"]}

CARD_SCHEMA = {"type": "object", "additionalProperties": False,
               "required": ["title", "genre", "logline", "era_place", "hook_device", "protagonist", "names",
                            "opening", "first_paywall_episode", "ending"],
               "properties": {
                   "title": {"type": "string", "description": "剧名"},
                   "genre": {"type": "string", "description": "题材标签，如「女频·重生·复仇」"},
                   "logline": {"type": "string", "description": "一句话梗概，40 字以内"},
                   "era_place": {"type": "string", "description": "时代和地点"},
                   "hook_device": {"type": "string", "description": "核心设定或金手指，一句话"},
                   "protagonist": {"type": "string", "description": "主角姓名和身份"},
                   "names": {"type": "array", "items": {"type": "string"}, "description": "所有有名字的角色姓名"},
                   "opening": {"type": "string", "description": "第 1 集开场画面，一句话"},
                   "first_paywall_episode": {"type": ["integer", "null"], "description": "第一个付费卡点在第几集"},
                   "ending": {"type": "string", "description": "结局，一句话"}}}

CLUSTER_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["groups"],
                  "properties": {"groups": {"type": "array", "items": {
                      "type": "object", "additionalProperties": False, "required": ["name", "pattern", "codes"],
                      "properties": {"name": {"type": "string"}, "pattern": {"type": "string"},
                                     "codes": {"type": "array", "items": {"type": "string"}}}}}}}

DIM_ENUM = {"type": "string", "enum": ["甲", "乙", "平"]}


def track_dims(track: str, sp: "Spec | None" = None) -> dict[str, str]:
    """一个比较项目要看的维度；人物小传和大纲都有「新意」，合并时只留一个。"""
    sp = sp or ROUND1
    return {d: why for part in sp.tracks[track] for d, why in sp.dims[part].items()}


def duel_schema(track: str, sp: "Spec | None" = None) -> dict:
    if getattr(sp, "verdict", None):
        return sp.verdict
    dims = list(track_dims(track, sp))
    return {"type": "object", "additionalProperties": False, "required": ["dims", "winner", "reason"],
            "properties": {"dims": {"type": "object", "additionalProperties": False, "required": dims,
                                    "properties": {d: DIM_ENUM for d in dims}},
                           "winner": DIM_ENUM, "reason": {"type": "string", "description": "三到五句，引用原文"}}}


def locate_schema(parts: dict[str, str]) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(parts),
            "properties": {k: {"type": "array", "items": {"type": "string"}} for k in parts}}


LOCATE_SCHEMA = locate_schema(PARTS)


def ask(prompt: str, schema: dict, system: str, call_id: str = "") -> dict:
    """单次评审调用，返回按 schema 校验过的 JSON。给了 call_id 就把提示词指纹和原始返回存下来。"""
    out = ask_gpt(prompt, schema, system) if JUDGE == "gpt" else ask_opus(prompt, schema, system)
    raw = out.pop("_raw")
    if RAW and call_id:
        RAW.mkdir(parents=True, exist_ok=True)
        meta = {"id": call_id, "judge": JUDGE, "model": GPT_MODEL if JUDGE == "gpt" else MODEL,
                "effort": GPT_EFFORT if JUDGE == "gpt" else EFFORT, "system": system,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "raw": raw}
        (RAW / f"{call_id}.json").write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def ask_gpt(prompt: str, schema: dict, system: str) -> dict:
    """经 Codex CLI 调 GPT：只读沙箱、空目录、不存会话。Codex 没有单独的系统提示参数，system 放在提示词最前面。"""
    home = os.environ.get("JUDGE_CODEX_HOME")
    if not home:
        sys.exit("请设置 JUDGE_CODEX_HOME：一个只放了 auth.json 的干净 Codex 目录")
    with tempfile.TemporaryDirectory() as empty:
        sp, last = Path(empty) / ".schema.json", Path(empty) / ".last.txt"
        sp.write_text(json.dumps(schema), encoding="utf-8")
        cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only", "--color", "never",
               "-m", GPT_MODEL, "-c", f"model_reasoning_effort={GPT_EFFORT}", "--output-schema", str(sp),
               "--json", "-o", str(last), "-"]
        env = os.environ | {"CODEX_HOME": home}
        err = ""
        for attempt in range(3):
            p = subprocess.run(cmd, input=f"{system}\n\n{prompt}", cwd=empty, env=env, capture_output=True,
                               text=True, timeout=3600)
            try:
                data = json.loads(last.read_text(encoding="utf-8"))
                events = [json.loads(l) for l in p.stdout.splitlines() if l.startswith("{")]
                return data | {"_raw": events}
            except (OSError, json.JSONDecodeError):
                err = (p.stdout or p.stderr)[-500:]
        raise RuntimeError(f"调用失败：{err}")


def ask_opus(prompt: str, schema: dict, system: str) -> dict:
    """无工具、无项目设置的单次调用。"""
    with tempfile.TemporaryDirectory() as empty:
        cmd = ["claude", "-p", "--output-format", "json", "--model", MODEL, "--effort", EFFORT, "--tools", "",
               "--setting-sources", "project", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--no-session-persistence", "--system-prompt", system, "--json-schema", json.dumps(schema)]
        env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
        for attempt in range(3):
            p = subprocess.run(cmd, input=prompt, cwd=empty, env=env, capture_output=True, text=True, timeout=1800)
            try:
                out = json.loads(p.stdout)
                data = out.get("structured_output") or json.loads(out["result"])
                return data | {"_cost_usd": out.get("total_cost_usd"), "_raw": out}
            except (json.JSONDecodeError, KeyError, TypeError):
                err = (p.stdout or p.stderr)[-500:]
        raise RuntimeError(f"调用失败：{err}")


def runs_of(premise: str) -> list[tuple[str, int, Path]]:
    base = EVALS / "runs" / premise
    return sorted((d.parent.name, int(d.name.split("-")[1]), d) for d in base.glob("*/run-*") if (d / "output").is_dir())


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def deliv_text(out: Path, ref: str) -> tuple[str, str]:
    """deliverables.toml 里的一项：文件路径，或「路径#L起-止」只取其中几行（交付文件里顺手多写了别的，只取要比的那部分）。
    返回（文件路径，正文）。"""
    path, _, lines = ref.partition("#L")
    text = read_text(out / path)
    if lines:
        a, b = (int(x.lstrip("L")) for x in lines.split("-"))
        text = "\n".join(text.splitlines()[a - 1:b]) + "\n"
    return path, text


def cmd_locate(premise: str, work: Path) -> None:
    sp = spec(premise)
    target = EVALS / "runs" / premise / "deliverables.toml"
    done = tomllib.loads(read_text(target)) if target.exists() else {}
    todo = [(s, n, d) for s, n, d in runs_of(premise) if f"{s}.run-{n}" not in done]

    def one(item):
        s, n, d = item
        files = [p for p in sorted((d / "output").rglob("*")) if p.is_file() and p.suffix.lower() in TEXT]
        listing = "\n\n".join(f"## {p.relative_to(d / 'output')}（{len(read_text(p))} 字）\n{read_text(p)[:400]}"
                              for p in files)
        r = ask(sp.locate.format(listing=listing), locate_schema(sp.parts), "你负责整理文件，只按要求输出。")
        return f"{s}.run-{n}", {k: [f for f in r[k] if (d / "output" / f).is_file()] for k in sp.parts}

    with ThreadPoolExecutor(8) as ex:
        for key, parts in ex.map(one, todo):
            done[key] = parts
            print(key, {k: len(v) for k, v in parts.items()}, flush=True)
    lines = [f"# 每次运行里，哪些文件是{'、'.join(sp.parts.values())}。由 judge.py locate 生成，人工核对过；改了要重新 pack。", ""]
    for key in sorted(done):
        lines.append(f'["{key}"]')
        lines += [f"{k} = {json.dumps(done[key][k], ensure_ascii=False)}" for k in sp.parts]
        lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")


def scrub(text: str, names: list[str]) -> str:
    """去掉能认出 skill 的字样：仓库名、skill 名、作者名。"""
    for n in sorted(set(names), key=len, reverse=True):
        if len(n) >= 3:
            text = re.sub(re.escape(n), "■", text, flags=re.I)
    return text


CLIP_NOTE = "（超过 {} 字，后面截掉了）"


def clip(text: str, limit: int) -> str:
    """超过 limit 字（去掉空白计，不算「<!-- 文件名 -->」那行）就在不超过 limit 的最后一个换行处截断，再注明截掉了。"""
    def count(s):
        return len(re.sub(r"\s", "", re.sub(r"<!-- .*? -->\n", "", s)))
    if count(text) <= limit:
        return text
    cut = max(i for i, ch in enumerate(text) if ch == "\n" and count(text[:i]) <= limit)
    return text[:cut].rstrip() + "\n\n" + CLIP_NOTE.format(limit) + "\n"


def cmd_pack(premise: str, work: Path) -> None:
    sp = spec(premise)
    deliv = tomllib.loads(read_text(EVALS / "runs" / premise / "deliverables.toml"))
    roster = tomllib.loads(read_text(EVALS / "runs" / premise / "contestants.toml"))
    names = ["skills", "skill"]
    for c in roster["contestants"]:
        if c["repo"] != "baseline":
            names += c["repo"].split("/") + [c.get("entry", "")]
    for s, n, d in runs_of(premise):
        names += json.loads(read_text(d / "run.json")).get("installed", [])
    rng = random.Random()
    keys = sorted(deliv)
    codes = rng.sample(range(100, 1000), len(keys))
    blind = work / "blind"
    blind.mkdir(parents=True, exist_ok=True)
    key_map = {}
    for key, code in zip(keys, codes):
        s, run = key.rsplit(".", 1)
        d = EVALS / "runs" / premise / s / run / "output"
        key_map[str(code)] = key
        for part in sp.parts:
            text = scrub("\n\n".join("<!-- {} -->\n{}".format(*deliv_text(d, f)) for f in deliv[key][part]), names)
            if getattr(sp, "max_chars", 0):
                text = clip(text, sp.max_chars)
            (blind / f"{code}.{part}.md").write_text(text, encoding="utf-8")
    (work / "key.json").write_text(json.dumps(key_map, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(keys)} 份匿名稿写到 {blind}")


def packet(work: Path, code: str, parts: list[str], labels: dict[str, str] | None = None, bare: bool = False) -> str:
    """拼给评审的匿名稿。bare 时不加「## 交付名」小标题（第三轮只比一份交付，评委提示词里已经写了是什么）。"""
    if bare:
        return "\n\n".join(read_text(work / "blind" / f"{code}.{p}.md") for p in parts)
    labels = labels or PARTS
    return "\n\n".join(f"## {labels[p]}\n\n{read_text(work / 'blind' / f'{code}.{p}.md')}" for p in parts)


def cmd_cards(premise: str, work: Path) -> None:
    sp = spec(premise)
    key_map = json.loads(read_text(work / "key.json"))
    out = work / "cards.jsonl"
    done = {json.loads(l)["code"] for l in out.open(encoding="utf-8")} if out.exists() else set()

    def one(code):
        r = ask(sp.card.format(text=packet(work, code, list(sp.parts), sp.parts)), sp.card_schema, "你负责如实摘录信息。")
        return {"code": code} | r

    with ThreadPoolExecutor(8) as ex, out.open("a", encoding="utf-8") as f:
        for row in ex.map(one, [c for c in key_map if c not in done]):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(row["code"], row["title"], row["genre"], flush=True)


CLUSTER_SYSTEM = "你是短剧行业编辑，只按要求输出。"
DUEL_SYSTEM = "你是严格、公正的评审，只按要求输出。"
SUFFIX = {"opus": "", "gpt": "-gpt"}


def cluster_rows(work: Path, seed: int = 20261018) -> list[dict]:
    """故事卡按编号排序后用固定种子打乱，谁都能重建出一模一样的提示词。"""
    rows = sorted((json.loads(l) for l in (work / "cards.jsonl").open(encoding="utf-8")), key=lambda r: r["code"])
    random.Random(seed).shuffle(rows)
    return rows


def cluster_prompt(rows: list[dict], sp: "Spec | None" = None) -> str:
    lines = "\n".join(f"- {r['code']}：《{r['title']}》 {r['genre']}。{r['logline']} 主角：{r['protagonist']}。"
                      f"核心设定：{r['hook_device']}" for r in rows)
    return (sp or ROUND1).cluster.format(n=len(rows), lines=lines)


def duel_prompt(work: Path, track: str, a: str, b: str, sp: "Spec | None" = None) -> str:
    sp = sp or ROUND1
    parts = sp.tracks[track]
    dims = "\n".join(f"- {d}：{why}" for d, why in track_dims(track, sp).items())
    bare = getattr(sp, "bare", False)
    return sp.duel.format(part="、".join(sp.parts[p] for p in parts), dims=dims, card=getattr(sp, "brief", ""),
                          a=packet(work, a, parts, sp.parts, bare), b=packet(work, b, parts, sp.parts, bare))


def cmd_cluster(premise: str, work: Path) -> None:
    sp = spec(premise)
    rows = cluster_rows(work, sp.seed)
    r = ask(cluster_prompt(rows, sp), CLUSTER_SCHEMA, sp.cluster_system, "cluster")
    (work / f"clusters{SUFFIX[JUDGE]}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(r['groups'])} 个故事类型")


def pairings(premise: str, slugs: list[str]) -> list[tuple[str, str]]:
    """这一轮谁和谁比。baseline：每个 skill 只和对照组比；all：所有参赛者（含对照组）两两全比。"""
    if spec(premise).pairing == "baseline":
        return [(s, "baseline") for s in slugs if s != "baseline"]
    return list(itertools.combinations(sorted(slugs), 2))


def cmd_duel(premise: str, work: Path, sample: int = 0, pairs: str = "") -> None:
    sp = spec(premise)
    key_map = json.loads(read_text(work / "key.json"))
    code_of = {v: k for k, v in key_map.items()}
    runs = tomllib.loads(read_text(EVALS / "runs" / premise / "contestants.toml")).get("runs", 1)
    slugs = sorted({k.rsplit(".", 1)[0] for k in code_of})
    out = work / f"duels{SUFFIX[JUDGE]}.jsonl"
    done = {(r["track"], r["a"], r["b"]) for r in map(json.loads, out.open(encoding="utf-8"))} if out.exists() else set()
    jobs = []
    for track in sp.tracks:
        for s, o in pairings(premise, slugs):
            for n in range(1, runs + 1):
                x, y = code_of.get(f"{s}.run-{n}"), code_of.get(f"{o}.run-{n}")
                if x and y:
                    for a, b in ((x, y), (y, x)):
                        if (track, a, b) not in done:
                            jobs.append((track, a, b))
    if sample:  # 试判：用固定种子抽 sample 对，每对两种顺序都比
        pairs = sorted({(t, *sorted((a, b))) for t, a, b in jobs})
        keep = set(random.Random(sp.seed).sample(pairs, min(sample, len(pairs))))
        jobs = [j for j in jobs if (j[0], *sorted(j[1:])) in keep]
    if pairs:  # 试判指定的几对（编号对编号），每对两种顺序都比
        keep = {tuple(sorted(p.split(":"))) for p in pairs.split(",")}
        jobs = [j for j in jobs if tuple(sorted(j[1:])) in keep]

    def one(job):
        track, a, b = job
        r = ask(duel_prompt(work, track, a, b, sp), duel_schema(track, sp), sp.duel_system, f"duel.{track}.{a}.{b}")
        return {"track": track, "a": a, "b": b} | r

    print(f"{len(jobs)} 场比较", flush=True)
    with ThreadPoolExecutor(4 if JUDGE == "gpt" else 8) as ex, out.open("a", encoding="utf-8") as f:
        for row in ex.map(one, jobs):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(row["track"], row["a"], row["b"], row["winner"], flush=True)


def cmd_reveal(premise: str, work: Path) -> None:
    key_map = json.loads(read_text(work / "key.json"))
    base = EVALS / "runs" / premise
    (base / "blind_key.json").write_text(json.dumps(key_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name in ("cards.jsonl", "duels.jsonl", "duels-gpt.jsonl"):
        if not (work / name).exists():
            continue
        rows = [json.loads(l) for l in (work / name).open(encoding="utf-8")]
        for r in rows:
            for k in ("code", "a", "b"):
                if k in r:
                    r[k + "_run"] = key_map[r[k]]
        (base / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    deliv = tomllib.loads(read_text(base / "deliverables.toml"))
    sp = spec(premise)
    lengths = {}
    for key in sorted(deliv):
        s, run = key.rsplit(".", 1)
        out = base / s / run / "output"
        lengths[key] = {part: sum(len(re.sub(r"\s", "", deliv_text(out, f)[1])) for f in deliv[key][part])
                        for part in sp.parts}
    (base / "lengths.json").write_text(json.dumps(lengths, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for name in ("clusters.json", "clusters-gpt.json"):
        if not (work / name).exists():
            continue
        groups = json.loads(read_text(work / name))["groups"]
        for g in groups:
            g["runs"] = [key_map[c] for c in g["codes"]]
        (base / name).write_text(json.dumps({"groups": groups}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"写入 {base}")


# ── 第二轮：选题 ──

TOPIC_PARTS = {"topic": "选题"}

TOPIC_LOCATE = """下面是一次给新故事定选题留下的文件清单，每个文件附了开头。需求要的交付是一份选题：一句话卖点，加上选题说明（题材、写给谁看、主角和对手、核心冲突、开篇钩子、爽点从哪来、打算写多长、为什么撑得住）。
请指出哪些文件是最终交付的选题（相对路径，按阅读顺序）。只选最终交付的正文；过程文件、扫榜或分析报告、检查报告、配置和数据文件都不选。最终交付里列了几个备选方案的，照样选它。找不到就给空列表。

{listing}"""

TOPIC_CARD = """下面是一个新故事的选题。请如实抽出它的基本信息，只写稿子里有的内容，不评价好坏。稿子里列了几个方案的，只抽它最终推荐的那一个。

{text}"""

TOPIC_CARD_SCHEMA = {"type": "object", "additionalProperties": False,
                     "required": ["title", "genre", "logline", "era_place", "hook_device", "protagonist", "antagonist",
                                  "names", "audience", "length"],
                     "properties": {
                         "title": {"type": "string", "description": "书名或剧名，没有就写「无」"},
                         "genre": {"type": "string", "description": "题材标签，如「女频·重生·复仇」"},
                         "logline": {"type": "string", "description": "一句话梗概，40 字以内"},
                         "era_place": {"type": "string", "description": "时代和地点"},
                         "hook_device": {"type": "string", "description": "核心设定或金手指，一句话"},
                         "protagonist": {"type": "string", "description": "主角姓名和身份"},
                         "antagonist": {"type": "string", "description": "主要对手的姓名和身份"},
                         "names": {"type": "array", "items": {"type": "string"}, "description": "所有有名字的角色姓名"},
                         "audience": {"type": "string", "description": "写给谁看，照稿子里的说法"},
                         "length": {"type": "string", "description": "打算写多长，照抄稿子里的说法，如「80 集」「120 万字」；没写就写「未写」"}}}

TOPIC_CLUSTER = """下面是 {n} 个新故事的选题，每个有一个编号。请按「故事类型」把它们分组：同一组的选题，核心设定和主线冲突属于同一种套路（比如「全职主妇离婚时拿账本清算婆家」「入殓师从遗体上发现命案」），换个名字和细节就差不多是同一个故事。分组要尽量细，宁可多分几组；每个只进一组；只有一个的也单独成组。给每组起一个短名字，再写一句这一组的共同套路。

{lines}"""

TOPIC_DUEL = """你要把选题交给 AI 从头拍成竖屏短剧：没有演员和片场，画面、声音、口型都由视频模型生成，场面大小不影响花费。你同时替目标观众判断：拍出来，他们会不会一直看下去。
下面是两份新故事的选题，甲和乙，各自来自不同的作者，你不知道它们出自谁。这两个故事以后可以写成网文，也可以拍成竖屏短剧。请只比较选题本身，按下面几个维度逐项判断哪份更好：

{dims}

注意：
- 一份稿子里列了几个方案的，只看它最终推荐的那一个。
- 不扣分：特效、异能、奇幻、大场面、群戏、场景多、角色多、古代和年代布景、水下、天上、动物和怪物。对 AI 来说，这些不额外花钱。
- 也不加分：场面大不等于好看。场面只有落在人物和爽点上，才算进「卖点」和「新意」。
- 篇幅长、格式花哨、附带市场分析或检查清单都不加分；只看这个故事值不值得写、值不值得拍。
- 两份差不多就判「平」。理由要引用原文。

=== 甲 ===
{a}

=== 乙 ===
{b}"""

TOPIC_DIMS = {"topic": {"卖点": "一句话卖点能不能让人立刻想看",
                        "新意": "是不是常见套路换个名字，有没有让人眼前一亮的东西",
                        "冲突和爽点": "主角要什么、谁挡着、爽点从哪来，能不能一直供得上",
                        "续航": "按它自己打算的篇幅，故事撑不撑得住，中段会不会没戏",
                        "上屏": "观众代入谁，这个人有没有一张能演戏的脸；每次爽点落在谁脸上；关键情绪靠不靠心里话撑"}}


# ── 第三轮：全剧骨架 ──

SKELETON_PARTS = {"skeleton": "全剧骨架"}

SKELETON_LOCATE = """下面是一次给竖屏短剧写全剧骨架留下的文件清单，每个文件附了开头。需求要的交付是一份全剧骨架：整部剧怎么走，用来管住后面的分集大纲和剧本。
请指出哪些文件是最终交付的全剧骨架（相对路径，按阅读顺序）。只选最终交付的正文；过程文件、分析报告、检查报告、配置和数据文件都不选。骨架分成几个文件写的，都选上。找不到就给空列表。

{listing}"""

# 评委提示词照 launch/RUBRIC.md 第三版一字不差；{card} 是需求里去掉开头三行要求以后的选题卡。
SKELETON_DUEL = """下面是同一张选题卡写出的两份全剧骨架，甲和乙，出自不同作者。
骨架之后要交给 AI 写成 60 集竖屏短剧，再全部由 AI 拍出来：没有演员和片场，画面和声音都由模型生成。不考虑拍摄成本和难度：场景和人物多少、AI 好不好拍，都不算长处也不算短处。

目标：选出照着它写下去、拍出来以后，观众更可能一集接一集追到最后的那一份。

怎么判由你决定。理由里引用原文。

=== 选题卡 ===
{card}

=== 甲 ===
{a}

=== 乙 ===
{b}"""

# 只判甲或乙，不设平；两种顺序判得不一样就算平。
SKELETON_VERDICT = {"type": "object", "additionalProperties": False, "required": ["reason", "winner"],
                    "properties": {"reason": {"type": "string"}, "winner": {"type": "string", "enum": ["甲", "乙"]}}}


def premise_card(premise: str) -> str:
    """需求全文去掉第一段（交付要求），剩下的就是选题卡。"""
    return read_text(EVALS / "premises" / f"{premise}.md").split("\n\n", 1)[1].strip()


class Spec:
    """一轮评审的设置：交付分几份、各步的提示词、比较维度、配对方式、分组用的随机种子。"""

    def __init__(self, **kw) -> None:
        self.__dict__.update(kw)


ROUND1 = Spec(parts=PARTS, locate=LOCATE, card=CARD, card_schema=CARD_SCHEMA, cluster=CLUSTER, duel=DUEL, dims=DIMS,
              tracks=TRACKS, cluster_system=CLUSTER_SYSTEM, duel_system=DUEL_SYSTEM, seed=20261018, pairing="baseline")

SPECS = {
    "001-open-brief": ROUND1,
    "002-topic": Spec(parts=TOPIC_PARTS, locate=TOPIC_LOCATE, card=TOPIC_CARD, card_schema=TOPIC_CARD_SCHEMA,
                      cluster=TOPIC_CLUSTER, duel=TOPIC_DUEL, dims=TOPIC_DIMS, tracks={"topic": ["topic"]},
                      cluster_system="你是网文和短剧行业编辑，只按要求输出。",
                      duel_system="你是严格、公正的评审，只按要求输出。", seed=20261020, pairing="all"),
    "003-skeleton": Spec(parts=SKELETON_PARTS, locate=SKELETON_LOCATE, card=None, card_schema=None, cluster=None,
                         duel=SKELETON_DUEL, dims={"skeleton": {}}, tracks={"skeleton": ["skeleton"]},
                         cluster_system=None, duel_system="你是严格、公正的评审，只按要求输出。", seed=20261030,
                         pairing="all", verdict=SKELETON_VERDICT, bare=True, brief=premise_card("003-skeleton"),
                         max_chars=3000),
}


def spec(premise: str) -> Spec:
    if premise not in SPECS:
        sys.exit(f"{premise} 没有登记评审设置，见 judge.py 的 SPECS")
    return SPECS[premise]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["locate", "pack", "cards", "cluster", "duel", "reveal"])
    ap.add_argument("premise")
    ap.add_argument("--work", required=True, type=Path, help="放匿名稿和中间结果的目录（仓库之外）")
    ap.add_argument("--judge", choices=["opus", "gpt"], default="opus", help="谁当评审；gpt 用来复核")
    ap.add_argument("--sample", type=int, default=0, help="duel 只试判这么多对（固定种子抽，每对两种顺序）")
    ap.add_argument("--pairs", default="", help="duel 只试判这几对，写成 编号:编号,编号:编号（每对两种顺序）")
    args = ap.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    global JUDGE, RAW
    JUDGE, RAW = args.judge, args.work.resolve() / "raw" / args.judge
    extra = {"sample": args.sample, "pairs": args.pairs} if args.step == "duel" else {}
    globals()[f"cmd_{args.step}"](args.premise, args.work.resolve(), **extra)


if __name__ == "__main__":
    main()
