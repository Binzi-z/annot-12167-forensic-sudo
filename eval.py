#!/usr/bin/env python3
"""eval.py —— 用 labels.json 给检测器/分析器的输出打分。

用法::

    python eval.py findings.json
    python eval.py findings.sarif
    python eval.py findings.json --labels labels.json --root .

支持的输入
===========
1) 题面要求的 findings.json::

       {"findings": [{"rule": "dns_tunnel",
                      "first_seen": "2026-10-01T06:40:07",
                      "last_seen":  "2026-10-01T06:40:59",
                      "entities": {"host": "web01", "src_ip": "10.20.1.51"},
                      "evidence": [{"file": "logs/web01/dns.log", "line": 1, "raw": "..."}]}]}

   也可以直接给一个 finding 列表；静态分析类题目允许
   ``{"findings": [{"file": "src/a.py", "line": 12, "rule": "command_injection"}]}``。
2) SARIF 2.1.0: ``{"runs": [{"results": [{"ruleId": ..., "locations": [...]}]}]}``。
   SARIF 里的时间窗口/实体可选，放在 ``result.properties`` 里即可。

指标
====
- ``recall`` = 命中的标注数 / 标注总数
- ``precision`` = TP / (TP + FP)
- ``false_positive_rate`` = FP / (TP + FP)

匹配规则
========
序列类标注（带 ``first_seen``）：``rule`` 相同 + 时间窗口重叠（默认 ±120s）
+ 实体至少有一个值相同（两侧都有实体时）；finding 的 file/line 正好落在标注
锚点上也算命中。静态类标注（只有 file/line）：文件相同且行号差 ≤ 2。

一个标注只算命中一次；同一个事件重复告警、或命中良性相似流量，都计入 FP——
题面要求「一条序列只产出一条告警」，重复告警就是分析师的噪声。
``needs_review`` 不计入 TP/FP（它是「判不了」的出口，不该被当成告警）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

RULE_ALIASES = {
    "cmd_injection": "command_injection",
    "command-injection": "command_injection",
    "commandinjection": "command_injection",
    "os_command": "command_injection",
    "os_command_injection": "command_injection",
    "cwe-78": "command_injection",
    "cwe_78": "command_injection",
    "privilege-escalation": "privilege_escalation",
    "privesc": "privilege_escalation",
    "lateral-movement": "lateral_movement",
    "bruteforce": "brute_force",
    "brute-force": "brute_force",
    "web_shell": "webshell",
    "web-shell": "webshell",
    "path-scan": "path_scan",
    "web_scan": "path_scan",
    "dns-exfiltration": "dns_tunnel",
    "dns_exfiltration": "dns_tunnel",
}


def norm_rule(value) -> str:
    key = str(value or "").strip().lower().replace(" ", "_").replace("/", "_")
    return RULE_ALIASES.get(key, key)


def norm_path(value) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if text.startswith("file:///"):
        text = text[8:]
    elif text.startswith("file://"):
        text = text[7:]
    while text.startswith("./"):
        text = text[2:]
    return text


def parse_ts(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value))
    text = str(value).strip().replace("Z", "+00:00")
    if text.endswith("+08:00"):
        text = text[:-6]
    parsed = None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S.%f"):
        try:
            parsed = datetime.strptime(text, fmt)
            break
        except ValueError:
            pass
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
    return parsed


def to_int(value) -> int:
    try:
        return int(str(value).strip().lstrip("L").split("-")[0] or 0)
    except (TypeError, ValueError):
        return 0


def flatten_entities(value) -> set[str]:
    out: set[str] = set()

    def walk(node):
        if node is None:
            return
        if isinstance(node, dict):
            for item in node.values():
                walk(item)
        elif isinstance(node, (list, tuple, set)):
            for item in node:
                walk(item)
        else:
            text = str(node).strip().lower()
            if text:
                out.add(text)

    walk(value)
    return out


def read_text(path: str) -> str:
    """容忍 PowerShell 的三种落盘编码：UTF-8 / UTF-8 BOM / UTF-16（``>`` 重定向）。"""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16")
    return data.decode("utf-8-sig")


def load_labels(path: str) -> list[dict]:
    doc = json.loads(read_text(path))
    labels = doc.get("vulns") if isinstance(doc, dict) else doc
    if not isinstance(labels, list):
        raise SystemExit(f"{path}: 找不到 vulns 列表")
    out = []
    for i, raw in enumerate(labels):
        rule = norm_rule(raw.get("sink") or raw.get("rule") or raw.get("kind"))
        out.append({
            "id": raw.get("id") or f"#{i}",
            "rule": rule,
            "file": norm_path(raw.get("file")),
            "line": to_int(raw.get("line") or 0),
            "first": parse_ts(raw.get("first_seen")),
            "last": parse_ts(raw.get("last_seen")),
            "entities": flatten_entities(raw.get("entities")),
        })
    return out


def finding_from_dict(raw: dict) -> dict:
    rule = norm_rule(raw.get("rule") or raw.get("sink") or raw.get("ruleId")
                     or raw.get("check") or raw.get("kind"))
    file = norm_path(raw.get("file") or raw.get("path") or raw.get("uri"))
    line = raw.get("line") or raw.get("start_line") or raw.get("startLine") or 0
    first = parse_ts(raw.get("first_seen") or raw.get("firstSeen") or raw.get("start"))
    last = parse_ts(raw.get("last_seen") or raw.get("lastSeen") or raw.get("end"))
    evidence = raw.get("evidence")
    if isinstance(evidence, list) and evidence:
        if not file:
            for item in evidence:
                if isinstance(item, dict) and item.get("file"):
                    file = norm_path(item.get("file"))
                    line = item.get("line") or line
                    break
        if first is None:
            stamps = [parse_ts(item.get("ts")) for item in evidence
                      if isinstance(item, dict) and item.get("ts")]
            stamps = [s for s in stamps if s]
            if stamps:
                first, last = min(stamps), max(stamps)
    if first is None and raw.get("ts"):
        first = last = parse_ts(raw.get("ts"))
    return {
        "rule": rule,
        "file": file,
        "line": to_int(line or 0),
        "first": first,
        "last": last,
        "entities": flatten_entities(raw.get("entities") or raw.get("entity")),
    }


def findings_from_sarif(doc: dict) -> list[dict]:
    out = []
    for run in doc.get("runs", []):
        for res in run.get("results", []):
            rule = norm_rule(res.get("ruleId") or (res.get("rule") or {}).get("id"))
            file, line = "", 0
            for loc in res.get("locations", []) or []:
                phys = (loc or {}).get("physicalLocation") or {}
                uri = (phys.get("artifactLocation") or {}).get("uri")
                if uri:
                    file = norm_path(uri)
                    region = phys.get("region") or {}
                    line = region.get("startLine") or 0
                    break
            props = res.get("properties") or {}
            first = parse_ts(props.get("first_seen") or props.get("firstSeen"))
            last = parse_ts(props.get("last_seen") or props.get("lastSeen"))
            out.append({
                "rule": rule,
                "file": file,
                "line": to_int(line or 0),
                "first": first,
                "last": last,
                "entities": flatten_entities(props.get("entities")),
                "raw_sarif": True,
            })
    return out


def load_findings(path: str) -> list[dict]:
    doc = json.loads(read_text(path))
    if isinstance(doc, list):
        raw = doc
    elif isinstance(doc, dict) and "findings" in doc:
        raw = doc["findings"]
    elif isinstance(doc, dict) and "runs" in doc:
        return findings_from_sarif(doc)
    else:
        raise SystemExit(f"{path}: 既不是 findings 也不是 SARIF")
    out = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if norm_rule(item.get("rule")) == "needs_review" or item.get("needs_review"):
            continue
        out.append(finding_from_dict(item))
    return out


def windows_overlap(f: dict, lab: dict, tol: int) -> bool:
    if lab["first"] is None:
        return False
    lab_last = lab["last"] or lab["first"]
    f_first = f["first"] or f["last"]
    f_last = f["last"] or f["first"]
    if f_first is None:
        return False
    slack = timedelta(seconds=tol)
    return f_first <= lab_last + slack and f_last >= lab["first"] - slack


def anchor_match(f: dict, lab: dict, line_tol: int) -> bool:
    return bool(lab["file"]) and bool(f["file"]) and lab["file"] == f["file"] \
        and lab["line"] > 0 and abs(int(f["line"]) - lab["line"]) <= line_tol


def best_label(f: dict, labels: list[dict], taken: set[int], tol: int,
               line_tol: int):
    best, best_score = None, -1.0
    for idx, lab in enumerate(labels):
        if idx in taken:
            continue
        sequence = lab["first"] is not None
        if sequence:
            if lab["rule"] != f["rule"]:
                continue
            if not windows_overlap(f, lab, tol):
                continue
            shared = len(lab["entities"] & f["entities"])
            if shared == 0 and not anchor_match(f, lab, line_tol):
                continue
            score = 10.0 + shared
        else:
            if not anchor_match(f, lab, line_tol):
                continue
            score = 5.0
        if score > best_score:
            best, best_score = idx, score
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("findings", help="findings.json 或 findings.sarif")
    ap.add_argument("--labels", default="labels.json")
    ap.add_argument("--root", default=".")
    ap.add_argument("--time-tol", type=int, default=120, help="窗口容差（秒）")
    ap.add_argument("--line-tol", type=int, default=2, help="行号容差")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.findings):
        print(f"找不到 {args.findings}", file=sys.stderr)
        return 2
    labels_path = args.labels if os.path.isabs(args.labels) \
        else os.path.join(args.root, args.labels)
    labels = load_labels(labels_path)
    findings = load_findings(args.findings)

    taken: set[int] = set()
    tp = fp = 0
    fp_samples = []
    for f in findings:
        idx = best_label(f, labels, taken, args.time_tol, args.line_tol)
        if idx is None:
            fp += 1
            if len(fp_samples) < 5:
                fp_samples.append(f)
        else:
            taken.add(idx)
            tp += 1
    fn = len(labels) - len(taken)

    total = tp + fp
    recall = tp / len(labels) if labels else 0.0
    precision = tp / total if total else 0.0
    fpr = fp / total if total else 0.0
    print(f"labels={len(labels)} findings={len(findings)} TP={tp} FP={fp} FN={fn}")
    print(f"recall={recall:.1%} precision={precision:.1%} false_positive_rate={fpr:.1%}")
    if fn:
        missed = [lab["id"] for idx, lab in enumerate(labels) if idx not in taken]
        print("missed=" + ",".join(missed))
    if args.verbose and fp_samples:
        print("--- fp samples ---")
        for f in fp_samples:
            safe = {k: (sorted(v) if isinstance(v, set) else str(v) if isinstance(v, datetime) else v)
                    for k, v in f.items() if k != "raw_sarif"}
            print(json.dumps(safe, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
