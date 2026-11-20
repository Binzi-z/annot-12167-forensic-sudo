"""driver.py —— 第 5 层：编排 parse -> IR -> index -> taint -> report。

全量与增量走**同一条分析路径**：增量只是用缓存替换未变更文件的 IR，之后
重新构建全局索引并跑完全一样的函数遍历（顺序固定），因此结果与全量逐条
一致，而不是两套实现各自产出再比对。
"""
from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass

from . import report as report_mod
from . import taint
from .ir import ModuleIR, discover_rust_files, lower_file, read_file
from .report import to_plain, to_sarif, write_json
from .resolve import AnalysisConfig, GlobalIndex
from .taint import Finding, _Ctx, analyze_function, set_module_cache


@dataclass
class AnalysisResult:
    findings: list[Finding]
    modules: dict[str, ModuleIR]
    stats: dict


def _file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_modules(files: list[str], root: str,
                  cache: dict | None = None) -> tuple[dict[str, ModuleIR], dict[str, bytes]]:
    """lower 全部文件；cache 命中（hash 未变）时复用旧 ModuleIR。"""
    modules: dict[str, ModuleIR] = {}
    sources: dict[str, bytes] = {}
    cache = cache if cache is not None else {}
    hits = 0
    for rel in files:
        full = os.path.join(root, rel)
        data = read_file(full)
        sources[rel] = data
        digest = _file_hash(data)
        hit = cache.get(rel)
        if hit is not None and hit["hash"] == digest:
            modules[rel] = hit["module"]
            hits += 1
        else:
            modules[rel] = lower_file(rel, data)
            cache[rel] = {"hash": digest, "module": modules[rel]}
    return modules, sources, hits


def run_analysis(root: str, scan_dirs: list[str], config: AnalysisConfig,
                 cache: dict | None = None) -> AnalysisResult:
    t0 = time.perf_counter()
    files: list[str] = []
    for d in scan_dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for rel in discover_rust_files(base):
            # discover_rust_files 返回相对 base 的路径，补成相对 root
            full_rel = f"{d}/{rel}" if not rel.startswith(d + "/") else rel
            if full_rel not in files:
                files.append(full_rel)
    files.sort()

    t_parse0 = time.perf_counter()
    modules, sources, cache_hits = build_modules(files, root, cache)
    t_parse = time.perf_counter() - t_parse0

    set_module_cache(sources)
    index = GlobalIndex(modules=modules)

    findings: list[Finding] = []
    t_taint0 = time.perf_counter()
    # 固定函数遍历顺序：先按文件、再按 IR 内顺序，保证输出确定性
    for rel in sorted(modules):
        mod = modules[rel]
        ctx = _Ctx(index=index, cfg=config, mod=mod, src=sources[rel],
                   findings=findings, stack=(), trace=[])
        for fn in mod.functions:
            ctx.stack = (fn.fid,)
            ctx.trace = [fn.fid]
            analyze_function(fn, ctx)
    t_taint = time.perf_counter() - t_taint0

    # 去重 + 稳定排序
    uniq: dict[tuple, Finding] = {}
    for f in findings:
        uniq.setdefault(f.key(), f)
    findings = report_mod.sorted_findings(list(uniq.values()))

    total_lines = sum(s.count(b"\n") for s in sources.values())
    stats = {
        "files": len(files),
        "rust_lines": total_lines,
        "functions": sum(len(m.functions) for m in modules.values()),
        "parse_sec": round(t_parse, 4),
        "taint_sec": round(t_taint, 4),
        "total_sec": round(time.perf_counter() - t0, 4),
        "findings": len(findings),
        "cache_hits": cache_hits,
    }
    return AnalysisResult(findings=findings, modules=modules, stats=stats)


def emit(result: AnalysisResult, out_dir: str) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "findings.json")
    sarif_path = os.path.join(out_dir, "findings.sarif")
    write_json(to_plain(result.findings), json_path)
    write_json(to_sarif(result.findings), sarif_path)
    return {"json": json_path, "sarif": sarif_path}
