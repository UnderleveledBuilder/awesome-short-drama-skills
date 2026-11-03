#!/usr/bin/env python3
"""核对一轮实测的公开数据：文件有没有被改过，评审提示词能不能重建，页面上的数字能不能重算出来。

用法（在仓库根目录）：
  python evals/verify.py 001-open-brief           # 核对
  python evals/verify.py 001-open-brief --write   # 数据定稿后重写指纹清单 MANIFEST.sha256

做三件事：
  1. 逐个核对 evals/runs/<轮次>/MANIFEST.sha256 里的 sha256 指纹，也报出清单里没有的新文件。
     清单和 sha256sum 的格式相同，在轮次目录里运行 shasum -a 256 -c MANIFEST.sha256 也能核对。
  2. 用 judge.py 的同一段代码，从匿名稿重建每一次评审调用的提示词，和调用时记下的指纹比对。
     两两盲比两位评审的都存了；第一轮的故事分组只存了 GPT 的。
     第三轮去掉截断说明的对照（judge-raw-nonote/）也核：把被截稿子结尾那行说明和它前面的空行删掉再重建。
  3. 用 stats.py 把实测记录页上的数字重算一遍，打印出来，可以和网站对照。
只用标准库。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge  # noqa: E402
import stats  # noqa: E402

MANIFEST = "MANIFEST.sha256"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def files(base: Path) -> list[Path]:
    return sorted(p for p in base.rglob("*") if p.is_file() and p.name != MANIFEST and p.name != ".DS_Store")


def check_manifest(base: Path) -> int:
    listed = {}
    for line in (base / MANIFEST).read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        listed[rel] = digest
    bad = 0
    for rel, digest in listed.items():
        p = base / rel
        if not p.exists():
            print(f"  缺文件：{rel}")
            bad += 1
        elif sha(p) != digest:
            print(f"  指纹不符：{rel}")
            bad += 1
    extra = [str(p.relative_to(base)) for p in files(base) if str(p.relative_to(base)) not in listed]
    for rel in extra:
        print(f"  清单里没有：{rel}")
    print(f"1. 指纹清单：{len(listed)} 个文件，{bad} 个不符，{len(extra)} 个不在清单里")
    return bad + len(extra)


def nonote_view(base: Path, sp) -> Path:
    """去掉截断说明的匿名稿：被截的稿子只删掉结尾那行说明和它前面的空行，截法不变。"""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "blind").mkdir()
    note = "\n\n" + judge.CLIP_NOTE.format(sp.max_chars) + "\n"
    for p in (base / "blind").glob("*.md"):
        t = p.read_text(encoding="utf-8")
        (tmp / "blind" / p.name).write_text(t[: -len(note)] + "\n" if t.endswith(note) else t, encoding="utf-8")
    return tmp


def check_prompts(base: Path) -> int:
    sp = judge.spec(base.name)
    problems = 0
    for raw_dir, work, what in (("judge-raw", base, ""), ("judge-raw-nonote", None, "（去掉截断说明的对照）")):
        if not (base / raw_dir).is_dir():
            continue
        work = work or nonote_view(base, sp)
        for j, label in (("opus", "Opus"), ("gpt", "GPT")):
            if not (base / raw_dir / j).is_dir():
                continue
            raw = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (base / raw_dir / j).glob("*.json")}
            ok = bad = 0
            for cid, rec in sorted(raw.items()):
                if cid == "cluster":
                    prompt = judge.cluster_prompt(judge.cluster_rows(base, sp.seed), sp)
                else:
                    _, track, a, b = cid.split(".")
                    prompt = judge.duel_prompt(work, track, a, b, sp)
                if hashlib.sha256(prompt.encode("utf-8")).hexdigest() == rec["prompt_sha256"]:
                    ok += 1
                else:
                    bad += 1
                    print(f"  重建的提示词和记录不符：{raw_dir} {j} {cid}")
            print(f"2. 评审提示词{what}：重建 {ok + bad} 次 {label} 调用，{ok} 次和记录一致")
            problems += bad
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("premise")
    ap.add_argument("--write", action="store_true", help="重写指纹清单")
    args = ap.parse_args()
    base = Path(__file__).resolve().parent / "runs" / args.premise
    if args.write:
        lines = [f"{sha(p)}  {p.relative_to(base)}" for p in files(base)]
        (base / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"写入 {base / MANIFEST}：{len(lines)} 个文件")
        return
    problems = check_manifest(base) + check_prompts(base)
    print("3. 重算的数字：")
    sys.argv = [sys.argv[0], args.premise]
    stats.main()
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
