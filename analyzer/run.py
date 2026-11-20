#!/usr/bin/env python3
"""run.py —— taint-style 路径穿越分析原型的命令行入口。

子命令
======
* ``full``        全量分析（默认 crates/，可加 --include-filler 压测 20 万行）
* ``incremental`` 增量分析：--changed 给出改动文件，复用其余文件的 IR 缓存
* ``ablations``   一次性跑 全量 / 去跨crate / 去净化 / 两者都去 四组配置

示例
====
::

    python analyzer/run.py full --root . --out out
    python analyzer/run.py full --root . --include-filler --out out-scale
    python analyzer/run.py incremental --root . --changed crates/ingest/src/lib.rs
    python analyzer/run.py ablations --root . --out out/ablations
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tast import driver
from tast.report import to_plain, to_sarif, write_json
from tast.resolve import AnalysisConfig

DEFAULT_SCAN = ["crates"]
FILLER_SCAN = ["crates", "filler"]


def _config(root: str, cross: bool, san: bool) -> AnalysisConfig:
    return AnalysisConfig.load(os.path.join(root, "config", "sanitizers.json"),
                               cross_crate=cross, recognize_sanitizers=san)


def _do_full(root: str, out: str, include_filler: bool,
             cross: bool = True, san: bool = True, cache: dict | None = None,
             emit_files: bool = True):
    cfg = _config(root, cross, san)
    dirs = FILLER_SCAN if include_filler else DEFAULT_SCAN
    result = driver.run_analysis(root, dirs, cfg, cache=cache)
    paths = {}
    if emit_files and out:
        paths = driver.emit(result, out)
    return result, paths


def cmd_full(args) -> int:
    result, paths = _do_full(args.root, args.out, args.include_filler)
    print(json.dumps(result.stats, ensure_ascii=False, indent=2))
    if paths:
        print("wrote:", paths["json"], paths["sarif"])
    return 0


def cmd_incremental(args) -> int:
    # 1) 全量打底，建立缓存
    full_result, _ = _do_full(args.root, args.out, args.include_filler,
                              cache={}, emit_files=False)
    full_doc = to_plain(full_result.findings)

    # 2) 模拟改动：只把 --changed 文件踢出缓存，其余全部复用
    cache = {}
    # 重新构建一次缓存（与全量相同的 cache 对象内容）
    _do_full(args.root, args.out, args.include_filler, cache=cache,
             emit_files=False)
    changed = [c.replace("\\", "/").lstrip("./") for c in args.changed]
    for rel in changed:
        cache.pop(rel, None)

    inc_result, paths = _do_full(args.root, args.out, args.include_filler,
                                 cache=cache, emit_files=bool(args.out))
    inc_doc = to_plain(inc_result.findings)

    same = full_doc["findings"] == inc_doc["findings"]
    print(json.dumps({
        "changed": changed,
        "full": full_result.stats,
        "incremental": inc_result.stats,
        "findings_identical": same,
        "full_findings": len(full_doc["findings"]),
        "incremental_findings": len(inc_doc["findings"]),
    }, ensure_ascii=False, indent=2))
    if not same:
        print("ERROR: 增量与全量结果不一致", file=sys.stderr)
        return 3
    return 0


def cmd_ablations(args) -> int:
    variants = [
        ("full", True, True),
        ("no_cross_crate", False, True),
        ("no_sanitizer", True, False),
        ("no_cross_no_sanitizer", False, False),
    ]
    summary = []
    for name, cross, san in variants:
        result, _ = _do_full(args.root, "", args.include_filler,
                             cross=cross, san=san, cache={}, emit_files=False)
        if args.out:
            d = os.path.join(args.out, name)
            os.makedirs(d, exist_ok=True)
            write_json(to_plain(result.findings), os.path.join(d, "findings.json"))
            write_json(to_sarif(result.findings), os.path.join(d, "findings.sarif"))
        summary.append({"variant": name, "cross_crate": cross,
                        "sanitizers": san, **result.stats})
    if args.out:
        write_json({"ablations": summary},
                   os.path.join(args.out, "ablation_stats.json"))
    print(json.dumps({"ablations": summary}, ensure_ascii=False, indent=2))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="tree-sitter IR 污点分析原型 (12167)")
    ap.add_argument("--root", default=".", help="仓库根目录")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_full = sub.add_parser("full", help="全量分析")
    p_full.add_argument("--out", default="out")
    p_full.add_argument("--include-filler", action="store_true",
                        help="把 filler/ 20 万行一起纳入，做性能压测")
    p_full.set_defaults(func=cmd_full)

    p_inc = sub.add_parser("incremental", help="增量分析并校验与全量逐条一致")
    p_inc.add_argument("--out", default="out-inc")
    p_inc.add_argument("--changed", nargs="+", required=True,
                       help="发生改动的文件（相对 root）")
    p_inc.add_argument("--include-filler", action="store_true")
    p_inc.set_defaults(func=cmd_incremental)

    p_abl = sub.add_parser("ablations", help="消融实验四组配置")
    p_abl.add_argument("--out", default="out/ablations")
    p_abl.add_argument("--include-filler", action="store_true")
    p_abl.set_defaults(func=cmd_ablations)

    args = ap.parse_args(argv)
    args.root = os.path.abspath(args.root)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
