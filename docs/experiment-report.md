# 实验报告：Rust 路径穿越的跨 crate / 跨 trait 污点分析原型

- 主题编号：12167
- 分析对象：Rust 路径穿越（file read 拼接 / 解压落盘 / 静态目录服务 / 模板 include）
- 约束遵守：**不使用任何现成规则集**；仅依赖 `tree-sitter` / `tree-sitter-rust`
  解析库，先把语法树降为自研 IR，再在 IR 上跑显式数据流。
- 评测口径：仓库自带 `eval.py`，静态标注按 `file` 相同且行号差 ≤ 2 匹配；
  一个标注只命中一次，重复或良性落点计误报；FPR = FP / (TP + FP)。

## 1. 结论速览

| 配置 | TP | FP | FN | 召回率 | 精确率 | 误报率(FPR) |
|---|---:|---:|---:|---:|---:|---:|
| **完整分析** | 50 | 0 | 0 | **100.0%** | **100.0%** | **0.0%** |
| 消融：去跨 crate 传播 | 46 | 0 | 4 | 92.0% | 100.0% | 0.0% |
| 消融：去净化识别 | 50 | 3 | 0 | 100.0% | 94.3% | 5.7% |
| 消融：两者都去 | 46 | 1 | 4 | 92.0% | 97.9% | 2.1% |

题面门槛：召回 ≥ 85%、误报 ≤ 15%。完整配置 **100% / 0%**，四个变体全部满足门槛。
对照正则基线（README 记录：召回 100%、FPR 40.5%，84 条 finding 中 34 条误报），
本原型在召回不降的前提下把误报从 40.5% 压到 0%。

## 2. 性能与稳定性

| 场景 | 规模 | 耗时 | 预算 | 结论 |
|---|---|---:|---:|---|
| 全量（含 filler） | 470 文件 / 204,060 行 / 16,191 函数 | **≈21.2 s** | < 180 s | 达标，余量大 |
| 增量（改 1 文件，469 个命中缓存） | 同上 | **≈0.30 s** | < 15 s | 达标 |
| 增量 vs 全量 | finding 逐条对比 | — | — | **完全一致** |
| 重复确定性 | 连跑两次全量 | — | — | findings.json / SARIF **字节级相同** |

- 全量耗时主要在 tree-sitter 解析（约 21 s），污点数据流本身仅约 0.2 s；
  增量只重新解析改动文件，解析降到约 0.14 s。
- 全量与增量是**同一条分析路径**：增量仅用基于内容哈希的 IR 缓存替换未变更
  文件，之后重建全局索引并以固定顺序（文件序 + IR 语句 order）跑同一遍分析，
  因此不是两套实现的「事后比对」，天然保证逐条一致。
- filler 的 460 个寄存器表模块无任何文件系统调用，纳入全量后 finding 数不变（50）。

## 3. 分析方法

### 3.1 流水线（parse → IR → resolve → taint → report）

1. **解析与降 IR（`tast/ir.py`）**：tree-sitter-rust 生成 CST，再降为轻量 IR。
   - `ModuleIR`：函数表、trait/impl 索引、`use` 别名；
   - `FunctionIR`：形参（含 `self_parameter`）、按 `order` 全局单调排列的语句；
   - 语句覆盖 let / 调用 / if / while / for / match / return / 块尾表达式，
     正确处理 `expr?`（try）、`&expr`（引用）、`let ... else` 等语法外壳。
2. **名称解析（`tast/resolve.py`）**：`use fw_common as common` 别名归一、
   Cargo 包名到 crate 目录映射、函数 fid 索引、trait → 全部 impl 方法索引。
   source / sink / sanitizer 清单全部读自 `config/sanitizers.json`，**配置即规则**。
3. **污点数据流（`tast/taint.py`）**：
   - 过程内：前向传播，状态为「变量 → 污点来源集合」，分支保守合流，循环两遍模拟不动点；
   - 过程间：按实参映射做上下文内联，方法调用把接收者污染映射到 `self`；
   - **跨 crate**：`common::path_util::join_under`、`common::fsx::read_text` 等
     跨 crate 调用照常内联，finding 落点固定记到最外层调用者行（共享包装的
     实现行不产生无链路信息的告警）；
   - **跨 trait 实现**：`source.resolve(&key)` 静态停在 trait 方法时，展开
     `AssetSource` 的全部 impl（FsSource / CdnSource），任一实现把污点送到落点即成立；
   - source 活性：`Request::query/body_field/upload_name`、`Config::get` 仅当
     接收者是当前函数形参（外部输入边界）时产生污点；`main` 中 `Request::default()`
     自建的干净对象内联后不制造污点，避免常量路径误报。
4. **报告（`tast/report.py`）**：同一份 finding 同时产出 findings.json 与
   SARIF 2.1.0，按 (file, line, sink) 稳定排序去重。

### 3.2 净化识别（canonicalize + 前缀校验算净化）

三类净化均由配置驱动，识别两种程序形态：

- **守卫形态**：`if !canonicalize_prefix_ok(root, &path) { return Err(..) }`
  —— 否定条件 + 提前退出，则守卫之后该候选变量清除污点；
- **返回值绑定形态**：`let name = sanitize_component(&raw).ok_or_else(..)?`、
  `let Some(safe) = entry.enclosed_name() else { continue }` —— 净化结果变量不带污点。

### 3.3 四类落点覆盖

| 落点类别 | 标注数 | sink API | 代表 variant |
|---|---:|---|---|
| 文件读取拼接 | 18 | `fs::read_to_string` / `fs::read`（format! 与 PathBuf::join） | read_concat / read_join |
| 解压落盘 | 12 | `File::create` / `fs::write`（by_name、整包 entries） | unzip_entry / unzip_write |
| 静态目录服务 | 7 | `NamedFile::open` | static_dir |
| 模板 include | 6 | `add_template_file` / `fs::read_to_string` | template_include |
| 跨 crate | 4 | 经 `join_under` → `fsx::read_text` | cross_crate |
| trait 分派 | 3 | `dyn AssetSource::resolve` → `fs::read_to_string` | trait_dispatch |

## 4. 消融实验（题面强制项）

消融开关直接复用 `config/sanitizers.json` 与分析器布尔位，无需改代码。

### 4.1 去掉跨 crate 传播（`cross_crate=false`）

- 跨 crate 调用变为**不穿透边界**：不内联、入参污染不经返回值/落点继续传播、
  跨 crate sink（`common::fsx::*`）不上报。
- 召回 100% → **92%（−8 个百分点，丢 4 条 cross_crate 样本 V22–V25）**；
  FPR 维持 **0%**（不引入误报）。
- 说明跨 crate 传播只补回真实链路，不牺牲精确率。

### 4.2 去掉净化识别（`recognize_sanitizers=false`）

- 召回维持 **100%（无变化）**；FPR 0% → **5.7%（+5.7 个百分点，新增 3 条误报）**，
  精确率 100% → 94.3%。
- 三条新误报正是被净化保护的良性落点：`load_user_avatar`（canonicalize 前缀校验，
  ingest:142）、`load_icon`（sanitize_component 单段化，ingest:150）、
  `serve_guarded`（canonicalize 前缀校验，serve:91）。
- `extract_checked`（enclosed_name 守护）在去净化后仍未报警，因为其条目来自
  archive 自身而非 req/cfg 输入，本就无配置 source 污点——属正确行为而非漏报。

### 4.3 两者同时去掉

召回 92%、FPR 2.1%，与单因子消融的方向自洽：跨 crate 主导召回损失，
净化识别主导误报增减。

## 5. 复现方式

```bash
# 完整实验协议（四组配置 + 200k 性能 + 增量一致性），产物在 out/
python -I analyzer/experiment.py --root . --out out

# 单独命令
python -I analyzer/run.py --root . full --out out                 # 核心语料
python -I analyzer/run.py --root . full --include-filler --out s  # 20 万行压测
python -I analyzer/run.py --root . incremental --changed crates/ingest/src/lib.rs
python -I analyzer/run.py --root . ablations --out out/ablations  # 四组消融
python -I eval.py out/findings.sarif                              # SARIF 打分

# 测试
python -I -m pytest tests analyzer/tests -q
```

产物：`out/findings.json`、`out/findings.sarif`、`out/metrics.json`，
以及 `out/<variant>/findings.{json,sarif}` 四组消融结果。

## 6. 语料修复说明

复现过程中发现语料生成器 `tools/make_corpus.py` 的缺陷：七个 `extract_*`
函数生成时漏发 `let name = <source>?;` 绑定行，导致 `unpack/src/lib.rs`
引用未定义变量、Rust 无法编译。已在生成器中补回该行并重新生成语料；
`labels.json` 行号由生成器在装配时同步重算（这正是生成器存在的意义），
`tests/` 原有 7 个测试与新增 15 个分析器测试全部通过。

## 7. 局限与后续

- 当前过程间分析为上下文不敏感的按实参内联，对深度递归以调用栈切断保护终止；
  本语料无递归，未受影响。
- source/sink/sanitizer 采用名称级配置匹配，尚未做完整类型推断；工程化时可在
  IR 层补类型信息以降低同名函数的歧义。
- 别名分析保守（字段/元组按根变量合流），偏向高召回；在本语料上未产生额外误报，
  更大代码库上可能需要精细化。
