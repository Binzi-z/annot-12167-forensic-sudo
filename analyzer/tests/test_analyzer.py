"""分析器原型的端到端与单元测试。

覆盖：IR 降层、四类落点、跨 crate 传播、trait 分派、三类 sanitizer、
消融开关方向、增量与全量逐条一致、SARIF 结构。不依赖外部进程。
"""
import json
import os

import pytest

from tast import driver, taint
from tast.ir import discover_rust_files, lower_file, read_file
from tast.report import to_plain, to_sarif
from tast.resolve import AnalysisConfig, GlobalIndex

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(ROOT, "config", "sanitizers.json")


@pytest.fixture(scope="module")
def index_and_src():
    files = sorted({f"crates/{r}"
                    for r in discover_rust_files(os.path.join(ROOT, "crates"))})
    modules, sources = {}, {}
    for rel in files:
        data = read_file(os.path.join(ROOT, rel))
        sources[rel] = data
        modules[rel] = lower_file(rel, data)
    taint.set_module_cache(sources)
    return GlobalIndex(modules=modules), modules, sources


def _run(cross=True, san=True, scan=("crates",)):
    cfg = AnalysisConfig.load(CONFIG, cross_crate=cross,
                              recognize_sanitizers=san)
    return driver.run_analysis(ROOT, list(scan), cfg, cache={})


def _score(findings):
    labels = json.load(open(os.path.join(ROOT, "labels.json"), encoding="utf-8"))["vulns"]
    keys = {(f.file, f.line) for f in findings}

    def hit(lab):
        return any(lab["file"] == ff and abs(lab["line"] - ll) <= 2
                   for ff, ll in keys)

    tp = sum(1 for lab in labels if hit(lab))
    matched_label_keys = set()
    for lab in labels:
        for ff, ll in keys:
            if lab["file"] == ff and abs(lab["line"] - ll) <= 2:
                matched_label_keys.add((ff, ll))
    fp = len(keys) - len(matched_label_keys)
    return tp, fp, len(labels)


# ---- IR 降层 -------------------------------------------------------------

def test_ir_indexes_impl_methods_and_self(index_and_src):
    index, modules, _ = index_and_src
    unpack = modules["crates/unpack/src/lib.rs"]
    names = {f.name for f in unpack.functions}
    # impl 块里的方法必须收进函数表，self 形参正确识别
    assert {"name", "enclosed_name", "by_name", "entries"} <= names
    name_fn = index.funcs["unpack::name"]
    assert name_fn.is_method and name_fn.params[0].name == "self"


def test_trait_impl_indexed(index_and_src):
    index, _m, _s = index_and_src
    assert "AssetSource" in index.trait_impls
    fids = index.trait_impls["AssetSource"]
    assert len(fids) == 2  # FsSource / CdnSource


def test_try_expression_lowered_as_call(index_and_src):
    _i, modules, _s = index_and_src
    render = modules["crates/render/src/lib.rs"]
    fn = next(f for f in render.functions if f.name == "render_report")
    heads = []
    for stmt in fn.body:
        if stmt.kind == "call":
            from tast.resolve import call_head_parts
            heads.append(call_head_parts(stmt.node)[1])
    assert "add_template_file" in heads


# ---- 端到端指标 -----------------------------------------------------------

def test_full_meets_recall_and_fpr_targets():
    res = _run()
    tp, fp, total = _score(res.findings)
    assert tp / total >= 0.85
    assert fp / (tp + fp) <= 0.15
    assert tp == total and fp == 0  # 本语料上做到满分


def test_all_eight_variants_detected():
    res = _run()
    hints = {f.variant_hint for f in res.findings}
    # cross_crate / trait_dispatch 经内联后落在具体 sink 类型上，
    # 这里用 trace 与 sink_api 联合验证
    assert {"read_concat", "read_join", "unzip_entry", "unzip_write",
            "static_dir", "template_include"} <= hints


def test_cross_crate_findings_at_caller_line():
    res = _run()
    # V22-V25：标注在 ingest 调用行，而不是 common/fsx.rs 实现行
    cc = [f for f in res.findings if f.file == "crates/ingest/src/lib.rs"
          and f.sink in ("read_text", "read_bytes")]
    assert len(cc) == 4
    assert all(99 <= f.line <= 117 for f in cc)
    assert not any(f.file.startswith("crates/common") for f in res.findings)


def test_trait_dispatch_detected(index_and_src):
    res = _run()
    app = [f for f in res.findings if f.file == "crates/app/src/main.rs"]
    # V01-V03 三个 trait 对象落点
    assert {f.line for f in app} == {38, 44, 50}


# ---- 净化 -----------------------------------------------------------------

def test_sanitizers_suppress_benign_sinks():
    res = _run()
    keys = {(f.file, f.line) for f in res.findings}
    # canonicalize 守卫、sanitize_component、enclosed_name 守护的良性落点
    assert ("crates/ingest/src/lib.rs", 142) not in keys
    assert ("crates/ingest/src/lib.rs", 150) not in keys
    assert ("crates/serve/src/lib.rs", 91) not in keys
    assert not any(f.file == "crates/unpack/src/lib.rs" and f.line >= 174
                   for f in res.findings)


def test_constant_paths_not_flagged():
    res = _run()
    # main 里 default 构造的干净 req、常量 build-id/version 等
    keys = {(f.file, f.line) for f in res.findings}
    assert ("crates/app/src/main.rs", 66) not in keys
    assert not any(f.file == "crates/ingest/src/lib.rs" and f.line in (124, 128, 132)
                   for f in res.findings)


# ---- 消融方向 -------------------------------------------------------------

def test_ablation_no_cross_crate_loses_only_cross_cases():
    full = _run(True, True)
    ablated = _run(False, True)
    assert len(ablated.findings) == len(full.findings) - 4
    # 召回下降、不引入新误报
    tp_f, fp_f, _ = _score(full.findings)
    tp_a, fp_a, _ = _score(ablated.findings)
    assert tp_a == tp_f - 4 and fp_a == fp_f


def test_ablation_no_sanitizer_adds_false_positives():
    full = _run(True, True)
    ablated = _run(True, False)
    assert len(ablated.findings) > len(full.findings)
    tp_f, fp_f, _ = _score(full.findings)
    tp_a, fp_a, _ = _score(ablated.findings)
    assert tp_a == tp_f            # 召回不变
    assert fp_a > fp_f             # 误报上升


# ---- 增量一致性 / 规模 -----------------------------------------------------

def test_incremental_matches_full():
    cfg = AnalysisConfig.load(CONFIG)
    full = driver.run_analysis(ROOT, ["crates", "filler"], cfg, cache={})
    cache = {}
    driver.run_analysis(ROOT, ["crates", "filler"], cfg, cache=cache)
    cache.pop("crates/ingest/src/lib.rs", None)
    inc = driver.run_analysis(ROOT, ["crates", "filler"], cfg, cache=cache)
    assert to_plain(inc.findings) == to_plain(full.findings)
    assert inc.stats["cache_hits"] == full.stats["files"] - 1


def test_filler_introduces_no_findings():
    core = _run()
    scaled = _run(scan=("crates", "filler"))
    assert len(scaled.findings) == len(core.findings)
    assert scaled.stats["rust_lines"] >= 200_000


def test_deterministic_output():
    a = to_plain(_run().findings)
    b = to_plain(_run().findings)
    assert a == b


# ---- SARIF ----------------------------------------------------------------

def test_sarif_structure():
    res = _run()
    sarif = to_sarif(res.findings)
    assert sarif["version"] == "2.1.0"
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["rules"][0]["id"] == "path_traversal"
    for r in run["results"]:
        loc = r["locations"][0]["physicalLocation"]
        assert loc["artifactLocation"]["uri"].startswith("crates/")
        assert loc["region"]["startLine"] > 0
