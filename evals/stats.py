#!/usr/bin/env python3
"""实测结果的统计：胜负、评审体检（换序一致、位置偏差、篇幅偏差、引文核对）、两位评审的一致度、故事分组的一致度。

网站的实测记录页和 evals/verify.py 都调这里，页面上的数字是生成网站时从 evals/runs/<轮次>/ 现算的。
也可以直接运行，打印一轮的全部数字：
  python evals/stats.py 001-open-brief

只用标准库。
"""
from __future__ import annotations

import json
import math
import re
import sys
import tomllib
from collections import Counter
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge  # noqa: E402

EVALS = Path(__file__).resolve().parent
JUDGES = {"opus": ("duels.jsonl", "clusters.json"), "gpt": ("duels-gpt.jsonl", "clusters-gpt.json")}
QUOTE = re.compile(r"“([^”]+)”|「([^」]+)」|『([^』]+)』|\"([^\"]+)\"")
ELLIPSIS = re.compile(r"……|…|\.\.\.")
SPACE = re.compile(r"\s+")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """二项比例的 95% 置信区间（Wilson 法），样本很少时也不会跑出 0 到 1 之外。"""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    mid = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, mid - half), min(1.0, mid + half)


def kappa(a: list[str], b: list[str]) -> float:
    """Cohen's kappa：两位评审的一致度扣掉碰巧一致的部分。1 是完全一致，0 是和瞎猜一样。"""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in ca) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def ari(x: dict[str, int], y: dict[str, int]) -> float:
    """调整兰德指数：两种分组有多像。1 是完全一样，0 是和随机分组一样。x、y 是「编号 → 组号」。"""
    items = sorted(x)
    pairs = lambda n: n * (n - 1) // 2  # noqa: E731
    table = Counter((x[i], y[i]) for i in items)
    sum_ij = sum(pairs(v) for v in table.values())
    sum_a = sum(pairs(v) for v in Counter(x[i] for i in items).values())
    sum_b = sum(pairs(v) for v in Counter(y[i] for i in items).values())
    expected = sum_a * sum_b / pairs(len(items))
    top = (sum_a + sum_b) / 2
    return 1.0 if top == expected else (sum_ij - expected) / (top - expected)


class Round:
    """一轮实测的全部数据，从 evals/runs/<轮次>/ 读。"""

    def __init__(self, premise: str) -> None:
        self.premise = premise
        self.dir = EVALS / "runs" / premise
        self.key: dict[str, str] = json.loads((self.dir / "blind_key.json").read_text(encoding="utf-8"))
        self.code_of = {v: k for k, v in self.key.items()}
        self.sp = judge.spec(premise)
        self.roster = tomllib.loads((self.dir / "contestants.toml").read_text(encoding="utf-8"))
        self.runs_per = self.roster.get("runs", 1)
        cards = self.dir / "cards.jsonl"  # 第三轮大家写同一个故事，不抽故事卡
        self.cards = [json.loads(l) for l in cards.open(encoding="utf-8")] if cards.exists() else []
        self.duels: dict[str, list[dict]] = {}
        self.groups: dict[str, list[dict]] = {}
        for j, (duels, clusters) in JUDGES.items():
            if (self.dir / duels).exists():
                self.duels[j] = [json.loads(l) for l in (self.dir / duels).open(encoding="utf-8")]
            if (self.dir / clusters).exists():
                self.groups[j] = json.loads((self.dir / clusters).read_text(encoding="utf-8"))["groups"]
        self.slugs = [c["repo"].replace("/", "__") for c in self.roster["contestants"] if c["repo"] != "baseline"]
        self._packets: dict[tuple[str, str], str] = {}

    # ── 稿子 ──

    def packet(self, code: str, track: str) -> str:
        """评审看到的那份匿名稿，和 judge.py 拼给评审的一字不差。"""
        if (code, track) not in self._packets:
            self._packets[code, track] = judge.packet(self.dir, code, self.sp.tracks[track], self.sp.parts,
                                                       getattr(self.sp, "bare", False))
        return self._packets[code, track]

    def prompt(self, track: str, a: str, b: str) -> str:
        return judge.duel_prompt(self.dir, track, a, b, self.sp)

    # ── 胜负 ──

    @property
    def all_pairs(self) -> bool:
        """这一轮是所有参赛者两两全比，还是每个 skill 只和对照组比。"""
        return self.sp.pairing == "all"

    def pairs(self, j: str) -> dict[tuple[str, str, str], list[tuple[dict, str]]]:
        """每一对稿子（项目，前一位的运行，后一位的运行）的两次比较，换算成前一位的「赢 W / 平 T / 输 L」。
        只和对照组比的轮次，前一位是 skill、后一位是对照组；两两全比的轮次，按运行名排先后。"""
        out: dict[tuple[str, str, str], list[tuple[dict, str]]] = {}
        for d in self.duels.get(j, []):
            a, b = d["a_run"], d["b_run"]
            if self.all_pairs:
                x, y = sorted((a, b))
            else:
                x, y = (a, b) if not a.startswith("baseline.") else (b, a)
            side = "甲" if x == a else "乙"
            v = "W" if d["winner"] == side else "T" if d["winner"] == "平" else "L"
            out.setdefault((d["track"], x, y), []).append((d, v))
        return out

    def verdicts(self, j: str) -> dict[tuple[str, str], list[tuple[dict, str]]]:
        """只和对照组比的轮次：每一对（项目，参赛者某次运行）的两次比较，换算成参赛者的「赢 W / 平 T / 输 L」。"""
        return {(t, x): v for (t, x, _), v in self.pairs(j).items()}

    def pair_outcomes(self, j: str) -> dict[tuple[str, str, str], str]:
        """两种顺序都判前一位赢才算赢，都判后一位赢才算输，其余算平。"""
        out = {}
        for k, pair in self.pairs(j).items():
            vs = [v for _, v in pair]
            out[k] = "W" if all(v == "W" for v in vs) else "L" if all(v == "L" for v in vs) else "T"
        return out

    def outcomes(self, j: str) -> dict[tuple[str, str], str]:
        """只和对照组比的轮次：两种顺序都判它赢才算赢，都判对照组赢才算输，其余算平。"""
        return {(t, x): o for (t, x, _), o in self.pair_outcomes(j).items()}

    def record(self, j: str) -> dict[tuple[str, str], list[int]]:
        """每个参赛者每个项目的「赢、平、输」次数。两两全比的轮次，对照组也有一行。"""
        out: dict[tuple[str, str], list[int]] = {}
        flip = {"W": "L", "L": "W", "T": "T"}
        for (track, x, y), o in self.pair_outcomes(j).items():
            for run, res in ((x, o), (y, flip[o])):
                if run.startswith("baseline.") and not self.all_pairs:
                    continue
                r = out.setdefault((run.rsplit(".", 1)[0], track), [0, 0, 0])
                r["WTL".index(res)] += 1
        return out

    def head_to_head(self, j: str, track: str) -> dict[tuple[str, str], list[int]]:
        """两两全比的轮次：每两个参赛者之间几次比较的「赢、平、输」，两个方向都有。"""
        out: dict[tuple[str, str], list[int]] = {}
        flip = {"W": "L", "L": "W", "T": "T"}
        for (t, x, y), o in self.pair_outcomes(j).items():
            if t != track:
                continue
            sx, sy = x.rsplit(".", 1)[0], y.rsplit(".", 1)[0]
            out.setdefault((sx, sy), [0, 0, 0])["WTL".index(o)] += 1
            out.setdefault((sy, sx), [0, 0, 0])["WTL".index(flip[o])] += 1
        return out

    def standings(self, j: str, track: str) -> list[tuple[str, list[int], float]]:
        """两两全比的积分表：赢一次 1 分，平一次 0.5 分。按积分排，同分按赢的次数。"""
        rec = self.record(j)
        rows = [(s, rec.get((s, track), [0, 0, 0])) for s in ["baseline"] + self.slugs]
        rows = [(s, r, r[0] + r[1] / 2) for s, r in rows]
        return sorted(rows, key=lambda x: (-x[2], -x[1][0], x[0]))

    def disputed(self) -> set[tuple]:
        """两位评审给出的最终结果不一样的对子，页面上标「有争议」。"""
        if "gpt" not in self.duels:
            return set()
        f = self.pair_outcomes if self.all_pairs else self.outcomes
        a, b = f("opus"), f("gpt")
        return {k for k in a if k in b and a[k] != b[k]}

    # ── 评审体检 ──

    def consistency(self, j: str, track: str | None = None) -> dict:
        """换序一致：同一对稿子甲乙对调后，评审的结论是否不变。"""
        c = Counter()
        for (t, _, _), pair in self.pairs(j).items():
            if track and t != track:
                continue
            vs = sorted(v for _, v in pair)
            c["same" if vs[0] == vs[1] else "flip" if vs == ["L", "W"] else "half"] += 1
        c["pairs"] = sum(c.values())
        return dict(c)

    def position(self, j: str, track: str | None = None) -> Counter:
        """判甲、判乙、判平各多少次。不偏的评审，甲和乙应该差不多。"""
        return Counter(d["winner"] for d in self.duels.get(j, []) if not track or d["track"] == track)

    def dims(self, j: str, track: str) -> dict[str, dict[str, list[int]]]:
        """分项判断：每个参赛者在每个维度上被判「赢、平、输」的次数，每场的两种顺序各算一次。"""
        out: dict[str, dict[str, list[int]]] = {}
        for d in self.duels.get(j, []):
            if d["track"] != track:
                continue
            for side, run in (("甲", d["a_run"]), ("乙", d["b_run"])):
                for dim, v in d.get("dims", {}).items():
                    r = out.setdefault(run.rsplit(".", 1)[0], {}).setdefault(dim, [0, 0, 0])
                    r[0 if v == side else 1 if v == "平" else 2] += 1
        return out

    def length(self, j: str, track: str | None = None) -> dict:
        """分出胜负的比较里，判篇幅长的那份赢的次数。"""
        longer = total = 0
        for d in self.duels.get(j, []):
            if d["winner"] == "平" or (track and d["track"] != track):
                continue
            la, lb = len(self.packet(d["a"], d["track"])), len(self.packet(d["b"], d["track"]))
            if la == lb:
                continue
            total += 1
            longer += (d["winner"] == "甲") == (la > lb)
        return {"longer": longer, "decided": total}

    def quotes(self, j: str) -> dict:
        """评审理由里加了引号的原文，能不能在两份稿子里找到。省略号两边分开找，空白不计。
        按字面逐字比：引号写法、表格分隔和原稿不同的，也算找不到，所以偏低。"""
        found = total = 0
        misses = []
        for d in self.duels.get(j, []):
            text = SPACE.sub("", self.packet(d["a"], d["track"]) + self.packet(d["b"], d["track"]))
            for m in QUOTE.finditer(d["reason"]):
                q = SPACE.sub("", next(g for g in m.groups() if g))
                bits = [b for b in ELLIPSIS.split(q) if len(b) >= 2]
                if len(q) < 4 or not bits:
                    continue
                total += 1
                if all(b in text for b in bits):
                    found += 1
                else:
                    misses.append((d, q))
        return {"found": found, "total": total, "misses": misses}

    def agreement(self) -> dict:
        """两位评审逐场比较的一致度：每场的胜负、每个维度，以及每对的最终结果。"""
        if "gpt" not in self.duels:
            return {}
        g = {(d["track"], d["a"], d["b"]): d for d in self.duels["gpt"]}
        both = [(d, g[d["track"], d["a"], d["b"]]) for d in self.duels["opus"] if (d["track"], d["a"], d["b"]) in g]
        dims = Counter()
        dims_n = Counter()
        for o, p in both:
            for k, v in o.get("dims", {}).items():
                dims_n[k] += 1
                dims[k] += v == p.get("dims", {}).get(k)
        f = self.pair_outcomes if self.all_pairs else self.outcomes
        oa, ga = f("opus"), f("gpt")
        keys = [k for k in oa if k in ga]
        return {"calls": len(both), "same": sum(o["winner"] == p["winner"] for o, p in both),
                "kappa": kappa([o["winner"] for o, _ in both], [p["winner"] for _, p in both]),
                "dims": {k: (dims[k], dims_n[k]) for k in dims_n},
                "pairs": len(keys), "pairs_same": sum(oa[k] == ga[k] for k in keys),
                "pairs_kappa": kappa([oa[k] for k in keys], [ga[k] for k in keys]) if keys else 0.0}

    # ── 故事分组 ──

    def group_of(self, j: str) -> dict[str, int]:
        return {c: i for i, g in enumerate(self.groups[j]) for c in g["codes"]}

    def same_type(self, j: str) -> dict:
        """同一个参赛者的几次运行落进同一种故事类型的比例，和不同参赛者之间比。"""
        gid = self.group_of(j)
        within = between = within_n = between_n = 0
        for a, b in combinations(sorted(gid), 2):
            same = gid[a] == gid[b]
            if self.key[a].rsplit(".", 1)[0] == self.key[b].rsplit(".", 1)[0]:
                within_n += 1
                within += same
            else:
                between_n += 1
                between += same
        return {"groups": len(self.groups[j]), "within": within, "within_n": within_n,
                "between": between, "between_n": between_n}

    def collisions(self, j: str) -> dict[str, dict]:
        """撞题：每个参赛者有几次运行，和别的参赛者（含对照组）落进同一种故事类型；其中几次和对照组撞。"""
        gid = self.group_of(j)
        members: dict[int, set[str]] = {}
        for code, g in gid.items():
            members.setdefault(g, set()).add(self.key[code].rsplit(".", 1)[0])
        out: dict[str, dict] = {}
        for code, g in gid.items():
            s = self.key[code].rsplit(".", 1)[0]
            r = out.setdefault(s, {"runs": 0, "shared": 0, "with_baseline": 0})
            r["runs"] += 1
            others = members[g] - {s}
            r["shared"] += bool(others)
            r["with_baseline"] += "baseline" in others
        return out

    def cluster_agreement(self) -> float | None:
        if "gpt" not in self.groups:
            return None
        return ari(self.group_of("opus"), self.group_of("gpt"))

    # ── 故事卡里的默认偏好 ──

    def name_count(self, name: str) -> tuple[int, int]:
        """故事卡人名里含某个名字的稿子数，和写过它的参赛者数（含对照组）。"""
        codes = [c["code"] for c in self.cards if any(name in n for n in c["names"])]
        return len(codes), len({self.key[c].rsplit(".", 1)[0] for c in codes})

    def paywalls(self) -> Counter:
        return Counter(c["first_paywall_episode"] for c in self.cards)

    def mentions(self, word: str) -> tuple[int, int]:
        """故事卡（除编号外的各栏和人名）里提到某个词的稿子数，和写过它的参赛者数（含对照组）。"""
        codes = [c["code"] for c in self.cards
                 if any(word in str(v) for k, v in c.items() if k not in ("code", "code_run", "_cost_usd"))]
        return len(codes), len({self.key[c].rsplit(".", 1)[0] for c in codes})

    def surnames(self) -> Counter:
        """主角的姓：故事卡「主角」一栏的第一个字（卡上写的是「姓名，年龄，身份」）。"""
        return Counter(c["protagonist"].strip()[:1] for c in self.cards)


def pct(k: int, n: int) -> str:
    """百分比；不到 10% 的留一位小数。"""
    if not n:
        return "—"
    return f"{k / n:.1%}" if 0 < k / n < 0.1 else f"{k / n:.0%}"


def main() -> None:
    r = Round(sys.argv[1] if len(sys.argv) > 1 else "001-open-brief")
    if r.all_pairs:
        return main_all_pairs(r)
    for j in r.duels:
        print(f"== 评审 {j}")
        rec = r.record(j)
        for s in r.slugs:
            print(f"  {s:55} 剧本 {'-'.join(map(str, rec.get((s, 'script'), [0, 0, 0])))}"
                  f"  人物大纲 {'-'.join(map(str, rec.get((s, 'outline'), [0, 0, 0])))}")
        for t in r.sp.tracks:
            c, p, ln = r.consistency(j, t), r.position(j, t), r.length(j, t)
            print(f"  {t}: 换序一致 {c.get('same', 0)}/{c['pairs']}，判甲 {p['甲']} 判乙 {p['乙']} 判平 {p['平']}，"
                  f"判长的赢 {ln['longer']}/{ln['decided']}")
        q = r.quotes(j)
        print(f"  引文找得到 {q['found']}/{q['total']}（{pct(q['found'], q['total'])}）")
    a = r.agreement()
    if a:
        print(f"== 两位评审：逐场一致 {a['same']}/{a['calls']}，kappa {a['kappa']:.2f}；"
              f"最终结果一致 {a['pairs_same']}/{a['pairs']}，kappa {a['pairs_kappa']:.2f}；有争议 {len(r.disputed())} 对")
    for j in r.groups:
        s = r.same_type(j)
        print(f"== 故事分组 {j}：{s['groups']} 组；同一参赛者 {s['within']}/{s['within_n']}，"
              f"不同参赛者 {s['between']}/{s['between_n']}")
    if r.cluster_agreement() is not None:
        print(f"   两种分组的调整兰德指数 {r.cluster_agreement():.2f}")
    print(f"== 小满 {r.name_count('小满')}，第一个付费卡点 {dict(r.paywalls())}")


def main_all_pairs(r: Round) -> None:
    """两两全比的轮次：积分表、评审体检、两位评审的一致度、故事分组和撞题。"""
    for j in r.duels:
        print(f"== 评审 {j}")
        for t in r.sp.tracks:
            for s, rec, pts in r.standings(j, t):
                print(f"  {s:55} {t} {'-'.join(map(str, rec))}  积分 {pts:g}")
            c, p, ln = r.consistency(j, t), r.position(j, t), r.length(j, t)
            print(f"  {t}: 换序一致 {c.get('same', 0)}/{c['pairs']}，判甲 {p['甲']} 判乙 {p['乙']} 判平 {p['平']}，"
                  f"判长的赢 {ln['longer']}/{ln['decided']}")
        q = r.quotes(j)
        print(f"  引文找得到 {q['found']}/{q['total']}（{pct(q['found'], q['total'])}）")
        for t in r.sp.tracks:
            print(f"  分项（赢-平-输，每场两种顺序各算一次）：")
            for s, row in sorted(r.dims(j, t).items()):
                print(f"   {s:55} " + "  ".join(f"{k} {'-'.join(map(str, v))}" for k, v in row.items()))
    a = r.agreement()
    if a:
        print(f"== 两位评审：逐场一致 {a['same']}/{a['calls']}，kappa {a['kappa']:.2f}；"
              f"最终结果一致 {a['pairs_same']}/{a['pairs']}，kappa {a['pairs_kappa']:.2f}；有争议 {len(r.disputed())} 对")
    for j in r.groups:
        s = r.same_type(j)
        print(f"== 故事分组 {j}：{s['groups']} 组；同一参赛者 {s['within']}/{s['within_n']}，"
              f"不同参赛者 {s['between']}/{s['between_n']}")
        for slug, c in sorted(r.collisions(j).items()):
            print(f"   {slug:55} 撞题 {c['shared']}/{c['runs']}，和对照组撞 {c['with_baseline']}")
    if r.cluster_agreement() is not None:
        print(f"   两种分组的调整兰德指数 {r.cluster_agreement():.2f}")
    if not r.cards:
        return
    print("== 主角的姓：" + "，".join(f"{k} {v}" for k, v in r.surnames().most_common(5)) + f"（共 {len(r.cards)} 份）")
    for n in ("砚", "周砚", "禾"):
        k, who = r.name_count(n)
        print(f"   人名里有「{n}」：{k} 份，{who} 个参赛者（含对照组）")
    k, who = r.mentions("账")
    print(f"== 故事卡里提到「账」的：{k} 份，{who} 个参赛者（含对照组）")


if __name__ == "__main__":
    main()
