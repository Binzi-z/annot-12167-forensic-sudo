#!/usr/bin/env python3
"""experiment.py —— 按题面固定协议跑完整实验并产出可对照指标。

协议
====
1. 50 条人工标注样本（labels.json），统计 recall / precision / FPR；
2. 四组配置：full / no_cross_crate / no_sanitizer / no_cross_no_sanitizer；
3. 性能：20 万行全量（含 filler）与增量（改 1 文件），并校验逐条一致；
4. 结果落 out/ ：findings.json、findings.sarif、metrics.json、ablation 表。

用法::

    python analyzer/experiment.py --root . --out out
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tast import driver
from tast.report import to_plain, to_sarif, write_json
from tast.resolve import AnalysisConfig

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from eval import load_labels, load_findings, best_label  # noqa: E402

VARIANTS = [
    ("full", True, True, "完整分析（跨crate传播 + 净化识别）"),
    ("no_cross_crate", False, True, "消融：去掉跨 crate 传播"),
    ("no_sanitizer", True, False, "消融：去掉净化识别"),
    ("no_cross_no_sanitizer", False, False, "消融：两者都去掉"),
]


def score(findings_path: str, labels_path: str) -> dict:
    labels = load_labels(labels_path)
    findings = load_findings(findings_path)
    taken: set[int] = set()
    tp = fp = 0
    for f in findings:
        idx = best_label(f, labels, taken, tol=120, line_tol=2)
        if idx is None:
            fp += 1
        else:
            taken.add(idx)
            tp += 1
    fn = len(labels) - len(taken)
    total = tp + fp
    return {
        "labels": len(labels), "findings": len(findings),
        "TP": tp, "FP": fp, "FN": fn,
        "recall": round(tp / len(labels), 4) if labels else 0.0,
        "precision": round(tp / total, 4) if total else 0.0,
        "false_positive_rate": round(fp / total, 4) if total else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="out")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    out = os.path.join(root, args.out)
    os.makedirs(out, exist_ok=True)
    labels_path = os.path.join(root, "labels.json")

    results = {"variants": [], "performance": {}}

    # ---- 1) 四组配置（核心语料 crates/）----
    for name, cross, san, desc in VARIANTS:
        cfg = AnalysisConfig.load(os.path.join(root, "config", "sanitizers.json"),
                                  cross_crate=cross, recognize_sanitizers=san)
        t0 = time.perf_counter()
        res = driver.run_analysis(root, ["crates"], cfg, cache={})
        elapsed = time.perf_counter() - t0
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        jpath = os.path.join(d, "findings.json")
        spath = os.path.join(d, "findings.sarif")
        write_json(to_plain(res.findings), jpath)
        write_json(to_sarif(res.findings), spath)
        metrics = score(jpath, labels_path)
        metrics.update({"name": name, "description": desc,
                        "cross_crate": cross, "sanitizers": san,
                        "elapsed_sec": round(elapsed, 4)})
        results["variants"].append(metrics)

    # 主输出固定指向 full 组，方便 eval.py 直接消费
    write_json(to_plain(driver.run_analysis(
        root, ["crates"],
        AnalysisConfig.load(os.path.join(root, "config", "sanitizers.json")),
        cache={}).findings), os.path.join(out, "findings.json"))

    # ---- 2) 性能：20 万行全量 ----
    cfg = AnalysisConfig.load(os.path.join(root, "config", "sanitizers.json"))
    t0 = time.perf_counter()
    full_scale = driver.run_analysis(root, ["crates", "filler"], cfg, cache={})
    full_sec = time.perf_counter() - t0

    # ---- 3) 增量：改 1 个文件，其余走缓存 ----
    cache: dict = {}
    driver.run_analysis(root, ["crates", "filler"], cfg, cache=cache)
    changed = "crates/ingest/src/lib.rs"
    cache.pop(changed, None)
    t0 = time.perf_counter()
    inc_scale = driver.run_analysis(root, ["crates", "filler"], cfg, cache=cache)
    inc_sec = time.perf_counter() - t0
    identical = to_plain(full_scale.findings) == to_plain(inc_scale.findings)

    results["performance"] = {
        "full_200k": {
            "files": full_scale.stats["files"],
            "rust_lines": full_scale.stats["rust_lines"],
            "functions": full_scale.stats["functions"],
            "elapsed_sec": round(full_sec, 4),
            "budget_sec": 180,
            "within_budget": full_sec < 180,
            "findings": full_scale.stats["findings"],
        },
        "incremental": {
            "changed_files": [changed],
            "elapsed_sec": round(inc_sec, 4),
            "budget_sec": 15,
            "within_budget": inc_sec < 15,
            "cache_hits": inc_scale.stats["cache_hits"],
            "findings": inc_scale.stats["findings"],
            "identical_to_full": identical,
        },
    }
    write_json(results, os.path.join(out, "metrics.json"))
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
