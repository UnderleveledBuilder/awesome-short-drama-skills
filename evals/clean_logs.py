#!/usr/bin/env python3
"""把实测运行的原始日志清理成可以公开的版本。公开的日志全部由这个脚本生成，删了什么、改了什么都写在下面。

用法：
  python evals/clean_logs.py <原始 jsonl> <输出 jsonl>

原始日志有两种格式：run.py 存下的 stream-json（正式运行），以及 Claude Code 自己留的会话记录（试点和沙箱自检）。
两种都是一行一个 JSON，按同样的规则处理：

只留对话本身：user、assistant、system、result 四类事件。其他的整类删掉：
  - stream-json 里的 rate_limit_event：运行者订阅账号的额度用量，和实测无关。
  - 会话记录里 Claude Code 自己用的内部记录：发给接口的请求副本、系统提示词快照、账号所属组织、额度和费用状态、
    界面状态等。只留下 sandbox_instructions 这一条，它记下了沙箱实际生效的读写范围。

不是 JSON 的行也删掉：命令行工具把自己的提示（例如「no stdin data received」）和日志打到了同一个文件里，不是对话内容。

在留下的事件里，删掉的（没有内容，或者是重复）：
  - thinking_tokens 事件：只有「已思考多少 token」的计数，占原始日志一大半行数。
  - 思考块的 signature：加密签名，不可读。思考正文本来就是空的，保留空的思考块，能看出模型在哪里思考过。
  - tool_use_result / toolUseResult / wire_tool_inputs：工具输入和返回的重复副本，正文在 message 里原样保留。

改掉的（本机路径和用户名）：
  - 运行时的临时目录换成 /scratch（第二轮起的运行目录 /tmp/sd-evals 也换成 /scratch；其他临时目录去掉用户编号，
    写成 /tmp/claude），用户主目录换成 /Users/user，
    ls -l 里的属主换成 user。
  - 工作目录里的轮次编号统一成公开的编号（001-open-brief）。

其余内容，包括 agent 读到的第三方 skill 原文、命令输出、每一轮的费用和耗时，都原样保留。只用标准库。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KEEP_TYPES = {"user", "assistant", "system", "result"}
KEEP_ATTACHMENTS = {"sandbox_instructions"}
DROP_EVENTS = {("system", "thinking_tokens")}
DROP_KEYS = {"tool_use_result", "toolUseResult", "wire_tool_inputs"}

SCRUB = [
    # 临时目录，绝对路径形式和 Claude Code 把路径压成目录名的形式
    (re.compile(r"(?:/private)?/tmp/claude-\d+/-Users-[\w.-]+?/[0-9a-f-]{36}/scratchpad"), "/scratch"),
    (re.compile(r"-private-tmp-claude-\d+--Users-[\w.-]+?-[0-9a-f-]{36}-scratchpad"), "-scratch"),
    (re.compile(r"(?:/private)?/tmp/claude-\d+(?=/)"), "/tmp/claude"),
    # 第二轮起，运行目录放在 /tmp/sd-evals/<轮次>/ 下
    (re.compile(r"(?:/private)?/tmp/sd-evals(?![\w-])"), "/scratch"),
    (re.compile(r"-private-tmp-sd-evals-"), "-scratch-"),
    (re.compile(r"(ws[/-])\d{3}-open-brief"), r"\g<1>001-open-brief"),
    (re.compile(r"/Users/[A-Za-z0-9_.-]+"), "/Users/user"),
    (re.compile(r"-Users-(?!user\b)[A-Za-z0-9_.]+"), "-Users-user"),
    (re.compile(r"(\s\d+ )[a-z][a-z0-9_]*(  ?(?:wheel|staff)\b)"), r"\g<1>user\g<2>"),
    (re.compile(r"# \d{3} · 开放题"), "# 001 · 开放题"),
]


def scrub(value):
    if isinstance(value, str):
        for pat, rep in SCRUB:
            value = pat.sub(rep, value)
        return value
    if isinstance(value, list):
        return [scrub(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k in DROP_KEYS:
                continue
            if k == "signature" and value.get("type") == "thinking":
                continue
            out[k] = scrub(v)
        return out
    return value


def clean(src: Path, dest: Path) -> tuple[int, int]:
    kept = dropped = 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    with src.open(encoding="utf-8") as f, dest.open("w", encoding="utf-8") as out:
        for line in f:
            if not line.strip():
                continue
            if not line.startswith("{"):  # 命令行工具自己的提示，不是事件
                dropped += 1
                continue
            ev = json.loads(line)
            kind = ev.get("type")
            keep = kind in KEEP_TYPES or (kind == "attachment" and ev["attachment"].get("type") in KEEP_ATTACHMENTS)
            if not keep or (kind, ev.get("subtype")) in DROP_EVENTS:
                dropped += 1
                continue
            out.write(json.dumps(scrub(ev), ensure_ascii=False) + "\n")
            kept += 1
    return kept, dropped


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    k, d = clean(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"{sys.argv[2]}：保留 {k} 行，删掉 {d} 行")
