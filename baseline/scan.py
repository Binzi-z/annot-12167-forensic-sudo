#!/usr/bin/env python3
"""baseline/scan.py —— 12167 的现有基线：正则扫「文件系统落点 API」。

现状：只按 API 名字报，不看路径是不是用户可控的。于是常量模板、
public/index.html、canonicalize+前缀校验之后的读取、enclosed_name
校验过的解压条目全被报成漏洞（误报）；而真正跨 crate、经 trait 对象
传播的路径也只是「报在调用行」，没有任何污点证据。

用法::

    python baseline/scan.py > findings.json
    python eval.py findings.json

只依赖标准库；扫描 crates/（baseline/、tools/、tests/、filler/ 不参与）。
"""
from __future__ import annotations

import json
import os
import re
import sys

SCAN_ROOT = "crates"
SKIP_DIRS = {"__pycache__", ".git", "baseline", "tools", "tests", "filler"}

SINK = re.compile(
    r"(?:"
    r"File::open|File::create"
    r"|fs::read_to_string|fs::read_dir|fs::read|fs::write|fs::copy"
    r"|NamedFile::open|add_template_file|by_name"
    r"|read_text|read_bytes"
    r")\s*\("
)


def scan_file(rel: str) -> list[dict]:
    out = []
    with open(rel, encoding="utf-8", errors="ignore") as fh:
        for no, line in enumerate(fh, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if SINK.search(line):
                out.append({
                    "rule": "path_traversal",
                    "sink": "path_traversal",
                    "file": rel.replace("\\", "/"),
                    "line": no,
                    "evidence": stripped[:200],
                })
    return out


def main() -> int:
    findings: list[dict] = []
    for dirpath, dirnames, names in os.walk(SCAN_ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(names):
            if name.endswith(".rs"):
                findings.extend(scan_file(os.path.join(dirpath, name)))
    json.dump({"findings": findings}, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")
    print(f"[baseline] {len(findings)} path hits (regex on fs APIs, no taint)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
