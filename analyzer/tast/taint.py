"""taint.py —— 第 3 层：在 IR 上跑污点数据流。

分析策略（全部为显式数据流，不含任何现成规则集）：

* 过程内：按 IR 语句顺序做前向污点传播，状态是「局部变量 -> 污点来源集合」，
  来源记录 source 类别与入口位置，分支做保守合流；
* 过程间：被调函数按实参映射做上下文内联；同一 crate 始终内联，跨 crate
  调用在 ``cross_crate`` 打开时内联（题面要求跨 crate 传播），关闭即消融；
* trait 分派：``obj.method(..)`` 静态看不到实现时，展开该 trait 的全部
  impl 方法，任一实现把污点送到落点都成立；
* 净化：sanitizer 守卫（``if !f(..) { return/continue }``）清除候选变量
  污点；sanitizer 返回值绑定（``enclosed_name`` / ``sanitize_component``）
  的新变量不带污点。开关 ``recognize_sanitizers`` 即消融。

finding 一律记在「调用者上下文的落点行」：共享包装（common::fsx）内部的
fs 调用发生在被内联的子上下文里，其文件/行号仍是真实落点行；同一
(file, line, sink) 去重，保证一条链路只出一条告警。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .ir import IRStmt
from .resolve import (AnalysisConfig, GlobalIndex, SINK_METHODS,
                      arguments_of, call_head_parts, macro_name_and_tt)


@dataclass(frozen=True)
class TaintOrigin:
    source_kind: str          # http_query / http_body / upload_filename / config_file
    entry_line: int
    entry_file: str
    entry_text: str


@dataclass
class Finding:
    rule: str
    file: str
    line: int
    sink: str
    variant_hint: str
    origins: tuple[TaintOrigin, ...]
    trace: tuple[str, ...]

    def key(self) -> tuple:
        return (self.file, self.line, self.sink)


@dataclass
class _Ctx:
    index: GlobalIndex
    cfg: AnalysisConfig
    mod: object                       # 当前函数所属 ModuleIR
    src: bytes                        # 当前文件源码
    findings: list[Finding]
    stack: tuple[str, ...] = ()
    param_origins: dict[str, list[TaintOrigin]] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)
    # 内联场景：调用者所在文件/行号。sink 落点优先记到调用点，使共享包装
    # （common::fsx）内部的 fs 调用不产生「没有链路信息」的实现行告警。
    caller_file: str | None = None
    caller_line: int | None = None


# 由 driver 填充：file -> 源码字节
_MODULE_CACHE: dict[str, bytes] = {}


def set_module_cache(cache: dict[str, bytes]) -> None:
    _MODULE_CACHE.clear()
    _MODULE_CACHE.update(cache)


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

def _text(src: bytes, node) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace")


def _unwrap(node):
    """剥掉 ? （try_expression）与 & （reference_expression）。"""
    cur = node
    while cur is not None and cur.type in ("try_expression", "reference_expression"):
        child = cur.child_by_field_name("expression")
        if child is None:
            named = [c for c in cur.children if c.is_named]
            child = named[0] if named else None
        cur = child
    return cur or node


def _node_name(node) -> str | None:
    if node is None:
        return None
    if isinstance(node.text, bytes):
        return node.text.decode()
    return node.text


def _root_ident(node) -> str | None:
    """表达式最左侧标识符：``a.b.c`` -> a；``x`` -> x。"""
    cur = _unwrap(node)
    while cur is not None:
        if cur.type == "identifier":
            return _node_name(cur)
        if cur.type == "field_expression":
            cur = cur.child_by_field_name("object")
            continue
        if cur.type in ("unary_expression",):
            cur = cur.child_by_field_name("expression")
            continue
        if cur.type == "call_expression":
            cur = cur.child_by_field_name("function")
            continue
        return None
    return None


def _origin_key(o: TaintOrigin):
    return (o.source_kind, o.entry_file, o.entry_line, o.entry_text)


# ---------------------------------------------------------------------------
# 表达式污点求值：返回 (tainted, origins)
# ---------------------------------------------------------------------------

def _eval_expr(node, state: dict, ctx: _Ctx):
    if node is None:
        return False, []
    node = _unwrap(node)
    t = node.type

    if t == "identifier" or t == "self":
        name = _node_name(node)
        if name in state:
            return bool(state[name]), list(state[name])
        if name in ctx.param_origins:
            return True, list(ctx.param_origins[name])
        return False, []

    if t in ("string_literal", "raw_string_literal", "integer_literal",
             "float_literal", "boolean_literal", "char_literal"):
        return False, []

    if t == "macro_invocation":
        _name, tt = macro_name_and_tt(node)
        tainted, origins = False, []
        if tt is not None:
            for ch in tt.children:
                if ch.is_named:
                    sub_t, sub_o = _eval_expr(ch, state, ctx)
                    tainted |= sub_t
                    origins.extend(sub_o)
        return tainted, origins

    if t == "call_expression":
        return _eval_call(node, state, ctx)

    if t == "field_expression":
        # a.b.c：污染取决于接收者表达式（变量/self/另一个调用结果）
        obj = node.child_by_field_name("object")
        if obj is None:
            # 该 grammar 无 object 字段：具名子节点第一个即接收者
            named = [c for c in node.children if c.is_named
                     and c.type != "field_identifier"]
            obj = named[0] if named else None
        if obj is not None:
            return _eval_expr(obj, state, ctx)
        return False, []

    if t == "closure_expression":
        return False, []

    if t == "match_expression":
        tainted, origins = False, []
        for arm in [c for c in node.children if c.type == "match_arm"]:
            value = arm.child_by_field_name("value")
            if value is not None:
                sub_t, sub_o = _eval_expr(value, state, ctx)
                tainted |= sub_t
                origins.extend(sub_o)
        return tainted, origins

    if t == "if_expression":
        tainted, origins = False, []
        for key in ("consequence", "alternative"):
            blk = node.child_by_field_name(key)
            if blk is None:
                continue
            for ch in blk.children:
                if ch.type in ("let_declaration", "call_expression", "macro_invocation"):
                    sub_t, sub_o = _eval_expr(ch, state, ctx)
                    tainted |= sub_t
                    origins.extend(sub_o)
        return tainted, origins

    # 复合表达式：任一具名子表达式污染即污染
    tainted, origins = False, []
    for ch in node.children:
        if ch.is_named:
            sub_t, sub_o = _eval_expr(ch, state, ctx)
            tainted |= sub_t
            origins.extend(sub_o)
    return tainted, origins


def _receiver_node(fn_node):
    """从 field_expression 取接收者节点，兼容无 object 字段的 grammar。"""
    if fn_node is None or fn_node.type != "field_expression":
        return None
    obj = fn_node.child_by_field_name("object")
    if obj is not None:
        return obj
    named = [c for c in fn_node.children if c.is_named
             and c.type != "field_identifier"]
    return named[0] if named else None


def _current_param_names(ctx: _Ctx) -> set[str]:
    fn = ctx.index.funcs.get(ctx.stack[-1]) if ctx.stack else None
    if fn is None:
        return set()
    return {p.name for p in fn.params}


def _receiver_is_param(fn_node, ctx: _Ctx) -> bool:
    """source 调用的接收者是否为当前函数形参（外部输入边界）。

    形参名 = 当前函数 params ∪ 内联注入的 param_origins 键。main 等用
    default() 自建的 req/cfg 是干净局部对象，其内 source 不产生污点。
    """
    param_names = set(ctx.param_origins.keys()) | _current_param_names(ctx)
    if fn_node is not None and fn_node.type == "field_expression":
        recv = _receiver_node(fn_node)
        root = _root_ident(recv) if recv is not None else None
        return root in param_names
    return False


def _source_is_live(fn_node, ctx: _Ctx) -> bool:
    """source 调用是否真的产生污点。

    * 顶层函数（非内联，stack 只有自己）：接收者是形参即外部输入，产生污点；
    * 内联上下文：接收者形参必须在调用点带污染（出现在 param_origins 中）。
      main 里 ``Request::default()`` 构造的干净 req 内联后不触发 source。
    """
    if not _receiver_is_param(fn_node, ctx):
        return False
    if len(ctx.stack) <= 1:
        return True
    recv = _receiver_node(fn_node)
    root = _root_ident(recv) if recv is not None else None
    return root in ctx.param_origins


def _eval_call(node, state: dict, ctx: _Ctx):
    recv, head, fn_node = call_head_parts(node)
    args = arguments_of(node)
    arg_results = [_eval_expr(a, state, ctx) for a in args]
    # 接收者也是数据流的一环：x.trim()/x.join() 等结果随接收者污染
    recv_node = _receiver_node(fn_node)
    recv_result = _eval_expr(recv_node, state, ctx) if recv_node is not None else None
    origins: list[TaintOrigin] = []
    arg_taint = False
    for t, sub_o in arg_results + ([recv_result] if recv_result is not None else []):
        arg_taint |= t
        origins.extend(sub_o)

    # 1) source（配置驱动）。污点产生条件：
    #    - 顶层分析（非内联）：接收者是函数形参即视为外部输入边界；
    #    - 内联上下文：仅当该接收者形参在调用点带污染（在 param_origins 中）。
    #      这样 main 用 default() 自建的干净 req 内联进来后，其 query() 不造污点。
    source_kind = _match_source(head or "", ctx.cfg)
    if source_kind is not None and _source_is_live(fn_node, ctx):
        return True, [TaintOrigin(source_kind, node.start_point[0] + 1,
                                  ctx.mod.file, _text(ctx.src, node))]

    # 2) 仓库内函数：过程间内联，返回值污染取被调函数 return/末值摘要
    fid = _resolve_callee(recv, head or "", ctx)
    # 消融：跨 crate 边界不穿透——不内联、不经返回值传播污染
    if _is_blocked_cross_crate(fid, ctx):
        return False, []
    if fid is not None:
        callee = ctx.index.funcs.get(fid)
        if callee is not None and _enterable(callee.fid, ctx):
            ret_t, ret_o = _inline(node, callee, args, arg_results, ctx,
                                   recv_result)
            return ret_t or arg_taint, (ret_o if ret_t else origins)

    # 3) 未知外部函数/方法：入参或接收者污染则结果污染（保守传播）
    if arg_taint:
        return True, origins
    return False, []


def _enterable(fid: str, ctx: _Ctx) -> bool:
    if fid in ctx.stack:
        return False
    callee_crate = ctx.index.crate_of_fid.get(fid)
    if callee_crate != ctx.mod.crate and not ctx.cfg.cross_crate:
        return False
    return True


def _is_blocked_cross_crate(fid: str | None, ctx: _Ctx) -> bool:
    """cross_crate 关闭时，跨 crate 调用是否构成不穿透边界。"""
    if fid is None or ctx.cfg.cross_crate:
        return False
    callee_crate = ctx.index.crate_of_fid.get(fid)
    return callee_crate is not None and callee_crate != ctx.mod.crate


def _match_source(head_text: str, cfg: AnalysisConfig) -> str | None:
    short = head_text.split("::")[-1]
    for kind, names in cfg.sources.items():
        for nm in names:
            if short == nm.split("::")[-1]:
                return kind
    return None


def _resolve_callee(recv, head_text, ctx: _Ctx) -> str | None:
    if recv is not None:
        cands = ctx.index.func_by_name.get(head_text, [])
        if len(cands) == 1:
            return cands[0].fid
        if cands:
            return cands[0].fid
        return None
    return ctx.index.resolve_fid(head_text, ctx.mod)


# ---------------------------------------------------------------------------
# 过程间内联
# ---------------------------------------------------------------------------

def _inline(call_node, callee, args, arg_results, ctx: _Ctx,
            recv_result=None):
    param_map: dict[str, list[TaintOrigin]] = {}
    # 方法调用：接收者污染映射到 self 形参
    if recv_result is not None and callee.is_method:
        recv_t, recv_origins = recv_result
        if recv_t:
            param_map["self"] = list(recv_origins)
    # 位置形参（跳过 self 本身）
    positional = [p for p in callee.params if p.name != "self"]
    for param, (_t, origins) in zip(positional, arg_results):
        if origins:
            param_map[param.name] = list(origins)
    # 落点行固定在最外层调用者：逐层内联时保留最初的 caller 位置
    caller_file = ctx.caller_file or ctx.mod.file
    caller_line = ctx.caller_line or (call_node.start_point[0] + 1)
    sub_ctx = _Ctx(
        index=ctx.index, cfg=ctx.cfg,
        mod=ctx.index.modules[callee.file],
        src=_MODULE_CACHE.get(callee.file, ctx.src),
        findings=ctx.findings,
        stack=ctx.stack + (callee.fid,),
        param_origins=param_map,
        trace=ctx.trace + [f"{callee.fid}@L{call_node.start_point[0] + 1}"],
        caller_file=caller_file,
        caller_line=caller_line,
    )
    return _run_function(callee, sub_ctx)


def _run_function(fn, ctx: _Ctx):
    """执行一个函数体，返回 (返回值是否污染, 来源)；落点写入 ctx.findings。"""
    state: dict[str, list[TaintOrigin]] = {
        name: list(origins) for name, origins in ctx.param_origins.items()
    }
    ret_t, ret_o = False, []
    stmts = fn.body
    for i, stmt in enumerate(stmts):
        # 最后一条 call 是 Rust 尾表达式：它的值就是函数返回值
        is_tail = (i == len(stmts) - 1) and stmt.kind == "call"
        if is_tail:
            t, o = _eval_tail(stmt, state, ctx)
        else:
            t, o = _analyze_stmt(stmt, state, ctx)
        if t:
            ret_t, ret_o = t, o
    return ret_t, ret_o


def _eval_tail(stmt: IRStmt, state: dict, ctx: _Ctx):
    """尾表达式：既要登记内部落点，又要把它的污点作为返回值。"""
    node = stmt.node
    if node.type == "macro_invocation":
        return _eval_expr(node, state, ctx)
    recv, head, fn_node = call_head_parts(node)
    args = arguments_of(node)
    arg_results = [_eval_expr(a, state, ctx) for a in args]
    recv_node = _receiver_node(fn_node)
    recv_result = _eval_expr(recv_node, state, ctx) if recv_node is not None else None
    origins: list[TaintOrigin] = []
    for _t, sub_o in arg_results + ([recv_result] if recv_result is not None else []):
        origins.extend(sub_o)

    # 尾表达式本身是 sink：在当前（被内联）上下文登记落点
    sink_id = _match_sink(head or "")
    if sink_id is not None:
        fid = _resolve_callee(recv, head or "", ctx)
        if not _is_blocked_cross_crate(fid, ctx):
            _maybe_report(node, arg_results, sink_id, ctx)
        return bool(origins) and not _is_blocked_cross_crate(fid, ctx), origins

    # 尾表达式是普通/trait 调用：内联，返回值取被调函数摘要
    ret_t, ret_o = _dispatch_call(node, recv, head or "", args, arg_results, ctx,
                                  recv_result)
    if ret_t:
        return ret_t, ret_o
    # 未知外部方法（std 的 join/trim 等）：入参/接收者污染则返回值污染
    return bool(origins), origins


# ---------------------------------------------------------------------------
# 语句级分析
# ---------------------------------------------------------------------------

def analyze_function(fn, ctx: _Ctx) -> list[Finding]:
    before = len(ctx.findings)
    _run_function(fn, ctx)
    return ctx.findings[before:]


def _analyze_stmt(stmt: IRStmt, state: dict, ctx: _Ctx):
    if stmt.kind == "let":
        return _analyze_let(stmt, state, ctx)
    if stmt.kind == "call":
        return _analyze_call_stmt(stmt, state, ctx)
    if stmt.kind == "if":
        return _analyze_if(stmt, state, ctx)
    if stmt.kind in ("while", "for"):
        return _analyze_loop(stmt, state, ctx)
    if stmt.kind == "match":
        return _analyze_match(stmt, state, ctx)
    if stmt.kind == "return":
        if stmt.value_node is not None:
            return _eval_expr(stmt.value_node, state, ctx)
        return False, []
    if stmt.kind == "tail":
        # 块内裸尾表达式：它的值就是块/函数返回值
        return _eval_expr(stmt.node, state, ctx)
    return False, []


def _analyze_let(stmt: IRStmt, state: dict, ctx: _Ctx):
    bind = stmt.bind
    value = stmt.value_node
    if value is None:
        if bind:
            state.setdefault(bind, [])
        return False, []

    # sanitizer 返回值绑定：净化结果不带污点
    if ctx.cfg.recognize_sanitizers and _is_sanitizer_call(_unwrap(value), ctx):
        if bind:
            state[bind] = []
        return False, []

    # let 初始化里直接是 sink 调用（File::create / fs::write 等）：先登记落点
    inner = _unwrap(value)
    if inner.type == "call_expression":
        _r, head, fn_node = call_head_parts(inner)
        sink_id = _match_sink(head or "")
        if sink_id is not None:
            fid = _resolve_callee(_r, head or "", ctx)
            if not _is_blocked_cross_crate(fid, ctx):
                args = arguments_of(inner)
                arg_results = [_eval_expr(a, state, ctx) for a in args]
                _maybe_report(inner, arg_results, sink_id, ctx)

    t, origins = _eval_expr(value, state, ctx)
    if bind:
        state[bind] = list(origins) if t else []
    return t, origins


def _analyze_call_stmt(stmt: IRStmt, state: dict, ctx: _Ctx):
    node = stmt.node
    if node.type == "macro_invocation":
        _eval_expr(node, state, ctx)
        return False, []

    recv, head, fn_node = call_head_parts(node)
    args = arguments_of(node)
    arg_results = [_eval_expr(a, state, ctx) for a in args]
    recv_node = _receiver_node(fn_node)
    recv_result = _eval_expr(recv_node, state, ctx) if recv_node is not None else None
    origins: list[TaintOrigin] = []
    for _t, sub_o in arg_results + ([recv_result] if recv_result is not None else []):
        origins.extend(sub_o)

    # source（表达式语句位置，保险处理）
    if _match_source(head or "", ctx.cfg) is not None:
        return True, origins

    # sink
    sink_id = _match_sink(head or "")
    if sink_id is not None:
        fid = _resolve_callee(recv, head or "", ctx)
        if not _is_blocked_cross_crate(fid, ctx):
            _maybe_report(node, arg_results, sink_id, ctx)
        return False, []

    # 普通 / 跨 crate / trait 调用
    _dispatch_call(node, recv, head or "", args, arg_results, ctx, recv_result)
    return bool(origins), origins


def _analyze_if(stmt: IRStmt, state: dict, ctx: _Ctx):
    if ctx.cfg.recognize_sanitizers:
        for name in _guard_cleared_vars(stmt, ctx):
            state.pop(name, None)

    saved = dict(state)
    ret_t, ret_o = False, []
    for sub in stmt.body:
        ret_t, ret_o = _analyze_stmt(sub, state, ctx)
    cons_state = dict(state)

    if stmt.else_body:
        state.clear()
        state.update(saved)
        for sub in stmt.else_body:
            ret_t, ret_o = _analyze_stmt(sub, state, ctx)
        alt_state = dict(state)
        merged = _merge(cons_state, alt_state)
    else:
        merged = _merge(cons_state, saved)
    state.clear()
    state.update(merged)
    return ret_t, ret_o


def _analyze_loop(stmt: IRStmt, state: dict, ctx: _Ctx):
    saved = dict(state)
    ret_t, ret_o = False, []
    for _ in range(2):  # 两遍模拟不动点
        state.clear()
        state.update(saved)
        if stmt.kind == "for" and stmt.loop_var:
            state.setdefault(stmt.loop_var, state.get(stmt.loop_var, []))
        for sub in stmt.body:
            ret_t, ret_o = _analyze_stmt(sub, state, ctx)
    return ret_t, ret_o


def _analyze_match(stmt: IRStmt, state: dict, ctx: _Ctx):
    saved = dict(state)
    branch_states = []
    ret_t, ret_o = False, []
    for _pat, arm_stmts in stmt.match_arms:
        cur = dict(saved)
        for sub in arm_stmts:
            ret_t, ret_o = _analyze_stmt(sub, cur, ctx)
        branch_states.append(cur)
    merged: dict = {}
    for bs in branch_states:
        merged = _merge(merged, bs)
    state.clear()
    state.update(merged)
    return ret_t, ret_o


def _merge(a: dict, b: dict) -> dict:
    out: dict = {}
    for name in set(a) | set(b):
        seen = {}
        for o in a.get(name, []) + b.get(name, []):
            seen[_origin_key(o)] = o
        out[name] = list(seen.values())
    return out


# ---------------------------------------------------------------------------
# 调用分派与落点上报
# ---------------------------------------------------------------------------

def _dispatch_call(node, recv, head_text, args, arg_results, ctx: _Ctx,
                   recv_result=None):
    """内联仓库内调用；返回被调表达式的 (返回值污染, 来源)。"""
    origins: list[TaintOrigin] = []
    for _t, sub_o in arg_results + ([recv_result] if recv_result is not None else []):
        origins.extend(sub_o)
    ret_t, ret_o = False, list(origins)

    # trait 方法：展开全部 impl
    trait_fids = _trait_method_fids(head_text, ctx)
    if trait_fids:
        for mfid in trait_fids:
            callee = ctx.index.funcs.get(mfid)
            if callee is not None and _enterable(callee.fid, ctx):
                t, o = _inline(node, callee, args, arg_results, ctx, recv_result)
                if t:
                    ret_t, ret_o = True, o
        return ret_t, ret_o

    fid = _resolve_callee(recv, head_text, ctx)
    if fid is not None:
        callee = ctx.index.funcs.get(fid)
        if callee is not None and _enterable(callee.fid, ctx):
            return _inline(node, callee, args, arg_results, ctx, recv_result)
    return ret_t, ret_o


def _trait_method_fids(head_text: str, ctx: _Ctx) -> list[str]:
    out = []
    for _trait, fids in ctx.index.trait_impls.items():
        names = {ctx.index.funcs[f].name for f in fids if f in ctx.index.funcs}
        if head_text in names:
            out.extend(fids)
    return out


def _match_sink(head_text: str) -> str | None:
    if head_text in SINK_METHODS:
        return SINK_METHODS[head_text]
    short = head_text.split("::")[-1]
    if short in SINK_METHODS:
        return SINK_METHODS[short]
    return None


def _maybe_report(node, arg_results, sink_id: str, ctx: _Ctx):
    origins: list[TaintOrigin] = []
    for t, sub_o in arg_results:
        if t:
            origins.extend(sub_o)
    if not origins:
        return
    # 内联到共享包装时，落点记最外层调用者的文件/行号
    rep_file = ctx.caller_file or ctx.mod.file
    rep_line = ctx.caller_line or (node.start_point[0] + 1)
    for existing in ctx.findings:
        if existing.file == rep_file and existing.line == rep_line \
                and existing.sink == sink_id:
            seen = {_origin_key(o): o for o in existing.origins}
            for o in origins:
                seen.setdefault(_origin_key(o), o)
            existing.origins = tuple(seen.values())
            return
    ctx.findings.append(Finding(
        rule="path_traversal",
        file=rep_file,
        line=rep_line,
        sink=sink_id,
        variant_hint=_variant_hint(sink_id),
        origins=tuple(origins),
        trace=tuple(ctx.trace),
    ))


def _variant_hint(sink_id: str) -> str:
    return {
        "read_to_string": "read_concat",
        "fs_read": "read_join",
        "fs_write": "unzip_write",
        "file_create": "unzip_entry",
        "named_file_open": "static_dir",
        "add_template_file": "template_include",
        "read_text": "cross_crate",
        "read_bytes": "cross_crate",
        "write_text": "cross_crate",
        "write_bytes": "cross_crate",
    }.get(sink_id, "path_traversal")


# ---------------------------------------------------------------------------
# sanitizer 识别
# ---------------------------------------------------------------------------

def _is_sanitizer_call(node, ctx: _Ctx) -> bool:
    """识别 sanitizer 直接调用，或 sanitizer 结果再经 ok_or_else/expect 等链。

    例如 ``sanitize_component(&raw).ok_or_else(..)?`` 的绑定变量应视为干净。
    """
    cur = _unwrap(node)
    seen = set()
    while cur is not None and cur.id not in seen and cur.type == "call_expression":
        seen.add(cur.id)
        _recv, head, fn_node = call_head_parts(cur)
        if (head or "").split("::")[-1] in ctx.cfg.sanitizer_names:
            return True
        cur = _receiver_node(fn_node)
    return False


def _guard_cleared_vars(stmt: IRStmt, ctx: _Ctx) -> set[str]:
    """``if !sanitizer(..) { return/continue/break/panic }`` -> 净化实参变量。"""
    cond = stmt.cond_node
    if cond is None:
        return set()
    call = cond
    if call.type == "unary_expression":
        inner = call.child_by_field_name("expression")
        if inner is None:
            named = [c for c in call.children if c.is_named]
            inner = named[0] if named else None
        call = inner
    if call is None or call.type != "call_expression":
        return set()
    _recv, head, _ = call_head_parts(call)
    if (head or "").split("::")[-1] not in ctx.cfg.sanitizer_names:
        return set()
    if not _branch_always_exits(stmt.body):
        return set()
    cleared = set()
    for arg in arguments_of(call):
        root = _root_ident(arg)
        if root:
            cleared.add(root)
    return cleared


def _branch_always_exits(stmts: list[IRStmt]) -> bool:
    if not stmts:
        return False
    last = stmts[-1]
    if last.kind == "return":
        return True
    if last.kind == "call" and last.node.type == "macro_invocation":
        name, _ = macro_name_and_tt(last.node)
        return name in ("panic", "unreachable", "todo")
    if last.kind == "if":
        return _branch_always_exits(last.body) and bool(last.else_body) \
            and _branch_always_exits(last.else_body)
    return False
