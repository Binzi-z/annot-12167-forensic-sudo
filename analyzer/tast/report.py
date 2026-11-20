"""report.py —— 第 4 层：把 Finding 落成 findings.json 与 SARIF 2.1.0。

两种输出走同一份 finding 数据，顺序固定为 (file, line, sink)，保证同一批
样本反复跑字节级稳定、增量与全量逐条一致。
"""
from __future__ import annotations

import json

from .taint import Finding

RULE_ID = "path_traversal"
SINK_CWE = "CWE-22"


def sorted_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: (f.file, f.line, f.sink))


def to_plain(findings: list[Finding]) -> dict:
    out = []
    for f in sorted_findings(findings):
        kinds = sorted({o.source_kind for o in f.origins})
        out.append({
            "rule": RULE_ID,
            "sink": RULE_ID,
            "file": f.file,
            "line": f.line,
            "sink_api": f.sink,
            "variant": f.variant_hint,
            "source_kinds": kinds,
            "entry_points": [
                {"file": o.entry_file, "line": o.entry_line,
                 "source": o.source_kind, "text": o.entry_text}
                for o in f.origins
            ],
            "trace": list(f.trace),
            "evidence": f"{f.sink} at {f.file}:{f.line} reached by taint "
                        f"from {','.join(kinds)}",
        })
    return {"findings": out}


def to_sarif(findings: list[Finding], tool_name: str = "tast-12167",
             tool_version: str = "0.1.0") -> dict:
    results = []
    for f in sorted_findings(findings):
        kinds = sorted({o.source_kind for o in f.origins})
        results.append({
            "ruleId": RULE_ID,
            "level": "error",
            "message": {
                "text": (f"不可信路径（来源: {', '.join(kinds)}）到达文件系统落点 "
                         f"{f.sink}；缺少 canonicalize+前缀校验或单段化净化。"),
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.file.replace("\\", "/")},
                    "region": {"startLine": f.line},
                }
            }],
            "properties": {
                "sink_api": f.sink,
                "variant": f.variant_hint,
                "source_kinds": kinds,
                "trace": list(f.trace),
                "cwe": SINK_CWE,
            },
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": tool_name,
                    "version": tool_version,
                    "informationUri": "https://example.invalid/tast-12167",
                    "rules": [{
                        "id": RULE_ID,
                        "name": "PathTraversal",
                        "shortDescription": {"text": "不可信路径到达文件系统落点"},
                        "fullDescription": {
                            "text": ("请求参数、上传文件名或配置值未经 "
                                     "canonicalize+前缀校验等净化，经拼接/join/"
                                     "跨 crate/trait 分派到达文件读取、解压落盘、"
                                     "静态目录服务或模板 include 落点。"),
                        },
                        "helpUri": "https://cwe.mitre.org/data/definitions/22.html",
                        "properties": {"tags": ["security", "cwe-22",
                                                "path-traversal", "taint"]},
                    }],
                }
            },
            "results": results,
        }],
    }


def write_json(doc: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
