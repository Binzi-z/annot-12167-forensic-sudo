# 12167 — Rust 路径穿越：跨 crate / 跨 trait 的污点分析原型

组里在复现一篇跨语言污点分析的论文，第一个实验对象是 Rust 的路径穿越。
本仓库是可评测原型的语料与起点：**禁止套用现成规则集，只允许 tree-sitter-rust
一类解析库，先降 IR 再跑数据流**；同一批样本反复跑，结果必须稳定。

## 语料构成

```
crates/
  common/     path_util.rs（canonicalize+前缀校验 / sanitize_component 净化）
              fsx.rs（read_text/read_bytes/write_text/write_bytes 跨 crate 包装）
  rpc/        Request：query / body_field / upload_name（污点入口）
  config/     Config::get + 4 个配置驱动的读文件入口
  ingest/     文件读取拼接（format!）、PathBuf::join、跨 crate read_text
  unpack/     zip 条目名提取 / 整包落地（ZipArchive::by_name、File::create、fs::write）
  serve/      静态目录服务（NamedFile::open）
  render/     模板 include（TemplateEngine::add_template_file、fs::read_to_string）
  app/        trait 对象 AssetSource::resolve → fs::read_to_string
templates/    base/mail/report/selftest 四个模板
config/sanitizers.json   可配置的 source / sanitizer / 静态目录 / 模板白名单
filler/       460 个寄存器表模块（纯计算，无文件系统调用）
```

合计 **470 个 .rs、204,053 行**（`filler/` 就是题面里「20 万行全量 <3 分钟」的那片代码）。

## 标注（labels.json，50 条）

| variant | 条数 | 落点形态 |
|---|---:|---|
| `read_concat` | 10 | `format!("{}/{}", root, name)` → `fs::read_to_string` |
| `read_join` | 8 | `root.join(rel)` / `Path::new(..).join(rel)` → `fs::read` / `fs::read_to_string` |
| `unzip_entry` | 7 | `archive.by_name(&name)` 后 `File::create` 落盘 |
| `unzip_write` | 5 | 请求/配置前缀 + 条目名 → `fs::write` |
| `static_dir` | 7 | `public.join(rel)` → `NamedFile::open` |
| `template_include` | 6 | 模板名拼路径 → `add_template_file` / `fs::read_to_string` |
| `cross_crate` | 4 | 经 `common::path_util::join_under` → `common::fsx::read_text` |
| `trait_dispatch` | 3 | `dyn AssetSource::resolve` 返回值 → `fs::read_to_string` |

| source | 条数 |
|---|---:|
| 请求参数（`Request::query`） | 24 |
| 上传文件名（`Request::upload_name`） | 8 |
| 配置（`Config::get`） | 10 |
| 请求体（`Request::body_field`） | 8 |

每条标注带 `file`/`line`、`variant`、`source`、`entry`（污点入口）、`path`（传播路径）与 `evidence`。
**finding 的 `file`/`line` 指向污点实际到达的文件系统落点行**；共享包装（`common::fsx`）
的实现行不算——那里没有「哪条链路」的信息。

## 良性落点（报了就是误报）

- 常量路径：`fs::read_to_string("/etc/fw/build-id")`、`NamedFile::open(public.join("index.html"))`
- 固定模板：`add_template_file("templates/base.hbs")`、`fs::read_to_string("templates/mail.hbs")`
- 净化后：`canonicalize_prefix_ok`（canonicalize 后必须仍在 root 下）、
  `sanitize_component`（只留单段）、`entry.enclosed_name()`（zip slip 校验）
- 白名单模板：`match name.as_str() { "base" => ..., "mail" => ..., _ => Err }`
- `filler/`：460 个模块没有任何文件系统调用

`config/sanitizers.json` 可增删 source / sanitizer / 静态目录 / 模板白名单（题目要求可配置）。

## 基线（baseline/scan.py）

正则扫「文件系统落点 API」，不看路径是否可控：`File::open` / `File::create` /
`fs::read*` / `fs::write` / `NamedFile::open` / `by_name` / `add_template_file` /
`fsx::read_text` 出现即报。

实测（扫描 crates/ 733 行核心代码，约 0.05 秒；filler 不参与）：

```
labels=50 findings=84 TP=50 FP=34 FN=0
recall=100.0% precision=59.5% false_positive_rate=40.5%
```

## 题面要求的效果指标（本仓库给出的起点）

- 50 条人工标注样本：召回 ≥85%、误报 ≤15%（基线 100% / 40.5%）
- 20 万行全量 <3 分钟、增量 <15 秒，且增量与全量逐条一致（本仓库 204k 行可直接压测）
- 产出 SARIF + 实验报告；报告必须包含消融：去掉跨 crate 传播、去掉净化识别，
  各自的召回/误报变化多少（`config/sanitizers.json` 可以直接当消融开关）

## 跑法

```powershell
python baseline/scan.py | Out-File -Encoding utf8 o.json
python eval.py o.json
python -m pytest tests -q
```

## IR 污点分析原型（analyzer/，本仓库的正式解法）

基线只按 API 名字报；`analyzer/` 是符合题面约束的原型——**不用任何现成规则集**，
只用 tree-sitter-rust 解析，先降自研 IR（`tast/ir.py`），再做名称解析
（`tast/resolve.py`）与显式污点数据流（`tast/taint.py`），最后产出 SARIF
（`tast/report.py`）。source / sink / sanitizer 全部读 `config/sanitizers.json`，
配置即规则，也直接充当消融开关。

```powershell
# 完整实验协议：四组配置 + 20 万行性能 + 增量一致性，产物在 out/
python -I analyzer/experiment.py --root . --out out

# 或分步
python -I analyzer/run.py --root . full --out out                  # 核心语料
python -I analyzer/run.py --root . full --include-filler --out s   # 20 万行压测
python -I analyzer/run.py --root . incremental --changed crates/ingest/src/lib.rs
python -I analyzer/run.py --root . ablations --out out/ablations
python -I eval.py out/findings.sarif
python -I -m pytest tests analyzer/tests -q
```

实测结果（详见 `docs/experiment-report.md`）：

| 配置 | 召回 | 误报率 | 说明 |
|---|---:|---:|---|
| 完整分析 | **100.0%** | **0.0%** | 50/50 命中，0 误报 |
| 去跨 crate 传播 | 92.0% | 0.0% | 丢 4 条 cross_crate，不增误报 |
| 去净化识别 | 100.0% | 5.7% | 召回不变，新增 3 条净化点误报 |
| 两者都去 | 92.0% | 2.1% | 方向自洽 |

性能：204,060 行全量约 21 s（预算 180 s）；增量改 1 文件约 0.3 s（预算 15 s），
469 个文件命中 IR 缓存，增量与全量 finding 逐条一致，重复运行字节级确定。

## 评测口径（eval.py）

- 静态类标注（只有 file/line）：文件相同且行号差 ≤2。
- `needs_review` 不计分；一个标注只算命中一次，同一事件重复上报算误报。
- rule 名称建议用 `path_traversal`（`path_traversal` / `CWE-22` 等别名都认）。
- 分析范围：`crates/`（`baseline/`、`tools/`、`tests/`、`filler/` 不参与基线扫描）。

## 重造语料

```powershell
python tools/make_corpus.py     # 固定生成逻辑，重跑得到同一份代码与 labels.json
```
