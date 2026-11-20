"""ir.py —— 第 1 层：tree-sitter-rust 解析后降为轻量 IR。

IR 不追求可执行，只保留污点分析需要的信息：

* :class:`ModuleIR` —— 一个 .rs 文件：函数表、trait/impl、use 别名；
* :class:`FunctionIR` —— 一个函数：形参、按源码顺序排列的语句记录；
* 语句记录（:class:`IRStmt`）覆盖 let / 表达式调用 / if / while / for /
  match / return，嵌套块递归降下来，``order`` 全局单调保证输出稳定。

表达式侧不单独建树，而是在 :mod:`tast.taint` 里对 tree-sitter 表达式节点
做一次递归求值（变量 -> 污点标记），避免维护第二棵表达式树。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import tree_sitter_rust as tsr
from tree_sitter import Language, Parser

_RUST = Language(tsr.language())


def new_parser() -> Parser:
    return Parser(_RUST)


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class Param:
    name: str
    type_text: str


@dataclass
class IRStmt:
    """一条有序语句。kind 决定其余字段如何解释。"""
    order: int
    kind: str                       # let | call | if | while | for | match | return
    node: object                    # 对应的 tree-sitter 节点
    line: int
    # let
    bind: str | None = None
    value_node: object | None = None
    # 块类语句的子语句
    body: list["IRStmt"] = field(default_factory=list)
    else_body: list["IRStmt"] = field(default_factory=list)
    # for: 迭代变量名; match: 被 match 的表达式节点
    loop_var: str | None = None
    match_node: object | None = None
    match_arms: list[tuple[object, list[IRStmt]]] = field(default_factory=list)
    # if 的条件表达式（用于识别 sanitizer 守卫）
    cond_node: object | None = None


@dataclass
class FunctionIR:
    fid: str                        # crate::module::...::name（含参数个数消歧后缀在外部加）
    name: str
    file: str                       # 相对仓库根的路径，正斜杠
    node: object
    params: list[Param]
    body: list[IRStmt]
    line: int
    trait_name: str | None = None   # 在 impl X for Y 块里时，trait 名
    self_ty: str | None = None
    is_method: bool = False


@dataclass
class TraitImpl:
    trait_name: str
    self_ty: str
    file: str
    methods: list[str]              # 函数 fid


@dataclass
class ModuleIR:
    file: str
    crate: str
    mod_path: str                   # 如 common::path_util
    functions: list[FunctionIR]
    impls: list[TraitImpl]
    use_aliases: dict[str, str]     # 本地别名 -> 规范名前缀（fw_common -> common 等）
    parse_error: bool = False


# ---------------------------------------------------------------------------
# crate / 模块路径推断
# ---------------------------------------------------------------------------

def crate_of_file(rel: str) -> str:
    parts = rel.split("/")
    return parts[1] if parts and parts[0] == "crates" and len(parts) > 1 else parts[0]


def mod_path_of(rel: str, crate: str) -> str:
    """crates/common/src/path_util.rs -> common::path_util。"""
    parts = rel.split("/")
    idx = parts.index("src") if "src" in parts else -1
    segs = parts[idx + 1:] if idx >= 0 else parts[1:]
    if segs and segs[-1] == "lib.rs":
        segs = segs[:-1]
    elif segs and segs[-1] == "main.rs":
        segs = segs[:-1]
    elif segs and segs[-1].endswith(".rs"):
        segs[-1] = segs[-1][:-3]
    return "::".join([crate] + segs) if segs else crate


# ---------------------------------------------------------------------------
#  lowering
# ---------------------------------------------------------------------------

class _Lower:
    def __init__(self, src: bytes):
        self.src = src
        self.order = 0

    def text(self, node) -> str:
        return self.src[node.start_byte:node.end_byte].decode("utf-8", "replace")

    def next_order(self) -> int:
        self.order += 1
        return self.order

    def lower_block(self, block) -> list[IRStmt]:
        out: list[IRStmt] = []
        for ch in block.children:
            # call / macro / let / if 等走标准语句降层
            if ch.type in ("call_expression", "macro_invocation", "let_declaration",
                           "expression_statement", "if_expression", "while_expression",
                           "loop_expression", "for_expression", "match_expression",
                           "return_expression", "try_expression"):
                out.extend(self.lower_stmt(ch))
                continue
            # 其余裸尾表达式（&self.name、字段访问、字面量等）作为 tail 语句
            if ch.is_named:
                out.append(IRStmt(order=self.next_order(), kind="tail", node=ch,
                                  line=ch.start_point[0] + 1))
        return out

    def lower_stmt(self, node) -> list[IRStmt]:
        t = node.type
        if t == "let_declaration":
            pattern = node.child_by_field_name("pattern")
            value = node.child_by_field_name("value")
            bind = None
            if pattern is not None:
                if pattern.type == "identifier":
                    bind = self.text(pattern)
                else:
                    # tuple_struct_pattern / tuple_pattern：取其中第一个 identifier
                    bind = self._first_ident(pattern)
            return [IRStmt(order=self.next_order(), kind="let", node=node,
                           line=node.start_point[0] + 1, bind=bind, value_node=value)]
        if t == "expression_statement":
            inner = node.children[0]
            return self.lower_stmt(inner)
        if t == "try_expression":
            # foo(..)?; —— 把内部调用/macro 提为语句，保留原节点行号
            inner = node.child_by_field_name("expression")
            if inner is None:
                named = [c for c in node.children if c.is_named]
                inner = named[0] if named else None
            if inner is not None and inner.type in ("call_expression", "macro_invocation"):
                return [IRStmt(order=self.next_order(), kind="call", node=inner,
                               line=inner.start_point[0] + 1)]
            return self.lower_stmt(inner) if inner is not None else []
        if t == "call_expression" or t == "macro_invocation":
            return [IRStmt(order=self.next_order(), kind="call", node=node,
                           line=node.start_point[0] + 1)]
        if t == "if_expression":
            cond = node.child_by_field_name("condition")
            cons = node.child_by_field_name("consequence")
            alt = node.child_by_field_name("alternative")
            stmt = IRStmt(order=self.next_order(), kind="if", node=node,
                          line=node.start_point[0] + 1, cond_node=cond,
                          body=self.lower_block(cons) if cons else [])
            if alt is not None:
                # alt 节点本身是 if_expression（else if）或 block
                if alt.type == "block":
                    stmt.else_body = self.lower_block(alt)
                else:
                    stmt.else_body = self.lower_stmt(alt)
            return [stmt]
        if t in ("while_expression", "loop_expression"):
            body = node.child_by_field_name("body")
            cond = node.child_by_field_name("condition")
            return [IRStmt(order=self.next_order(), kind="while", node=node,
                           line=node.start_point[0] + 1, cond_node=cond,
                           body=self.lower_block(body) if body else [])]
        if t == "for_expression":
            body = node.child_by_field_name("body")
            pat = node.child_by_field_name("pattern")
            loop_var = self._first_ident(pat) if pat is not None else None
            return [IRStmt(order=self.next_order(), kind="for", node=node,
                           line=node.start_point[0] + 1, loop_var=loop_var,
                           body=self.lower_block(body) if body else [])]
        if t == "match_expression":
            scrut = node.child_by_field_name("value")
            arms: list[tuple[object, list[IRStmt]]] = []
            for arm in [c for c in node.children if c.type == "match_arm"]:
                value = arm.child_by_field_name("value")
                pat = arm.child_by_field_name("pattern")
                if value is not None and value.type == "block":
                    arm_stmts = self.lower_block(value)
                elif value is not None:
                    arm_stmts = self.lower_stmt(value)
                else:
                    arm_stmts = []
                arms.append((pat, arm_stmts))
            return [IRStmt(order=self.next_order(), kind="match", node=node,
                           line=node.start_point[0] + 1, match_node=scrut,
                           match_arms=arms)]
        if t == "return_expression":
            return [IRStmt(order=self.next_order(), kind="return", node=node,
                           line=node.start_point[0] + 1,
                           value_node=node.child_by_field_name("value"))]
        # 其余节点（分号、宏的裸 token 等）不产生 IR 语句
        return []

    @staticmethod
    def _first_ident(pattern) -> str | None:
        if pattern is None:
            return None
        stack = [pattern]
        while stack:
            cur = stack.pop()
            if cur.type == "identifier":
                return cur.text.decode("utf-8") if isinstance(cur.text, bytes) \
                    else cur.text
            stack.extend(cur.children)
        return None


def _collect_use_aliases(root, src: bytes) -> dict[str, str]:
    """只收集 ``use ... as alias`` 与首段别名，供调用名归一化使用。"""
    aliases: dict[str, str] = {}
    for node in _walk(root):
        if node.type != "use_declaration":
            continue
        text = src[node.start_byte:node.end_byte].decode("utf-8", "replace")
        if " as " in text:
            # use fw_common as common;
            left = text.split(" as ")[0].replace("use ", "").strip()
            right = text.split(" as ")[1].split(";")[0].strip().split("{")[0].strip()
            aliases[right] = left
    return aliases


def _walk(node):
    stack = [node]
    while stack:
        cur = stack.pop()
        yield cur
        stack.extend(cur.children)


def lower_file(rel: str, src_bytes: bytes) -> ModuleIR:
    parser = new_parser()
    tree = parser.parse(src_bytes)
    root = tree.root_node
    crate = crate_of_file(rel)
    mod = mod_path_of(rel, crate)
    lower = _Lower(src_bytes)

    functions: list[FunctionIR] = []
    impls: list[TraitImpl] = []

    def lower_fn(fn_node, trait_name: str | None, self_ty: str | None) -> FunctionIR:
        name_node = fn_node.child_by_field_name("name")
        name = lower.text(name_node)
        params_node = fn_node.child_by_field_name("parameters")
        params: list[Param] = []
        is_method = False
        if params_node is not None:
            for pn in params_node.children:
                if pn.type == "self_parameter":
                    is_method = True
                    params.append(Param("self", lower.text(pn)))
                    continue
                if pn.type != "parameter":
                    continue
                # 该 grammar 无 pattern/type 字段：parameter = pattern ':' type
                ptype = pn.child_by_field_name("type")
                pname = pn.child_by_field_name("pattern")
                if pname is None or ptype is None:
                    named = [c for c in pn.children if c.is_named]
                    pname = named[0] if named else None
                    ptype = named[1] if len(named) > 1 else None
                pname_text = lower.text(pname) if pname is not None else ""
                ptype_text = lower.text(ptype) if ptype is not None else ""
                params.append(Param(pname_text, ptype_text))
        body_node = fn_node.child_by_field_name("body")
        body = lower.lower_block(body_node) if body_node is not None else []
        fid = f"{mod}::{name}"
        return FunctionIR(fid=fid, name=name, file=rel, node=fn_node, params=params,
                          body=body, line=fn_node.start_point[0] + 1,
                          trait_name=trait_name, self_ty=self_ty, is_method=is_method)

    # 先展开 impl 块，再收顶层函数
    for node in _walk(root):
        if node.type != "impl_item":
            continue
        # 该 grammar 版本 impl_item 无 trait/type 字段，按子节点结构解析：
        # impl Type { .. }  或  impl Trait for Type { .. }
        type_idents = [c for c in node.children if c.type in
                       ("type_identifier", "scoped_type_identifier", "generic_type")]
        has_for = any(c.type == "for" for c in node.children)
        if has_for and len(type_idents) >= 2:
            trait_name = lower.text(type_idents[0])
            self_ty = lower.text(type_idents[1])
        else:
            trait_name = None
            self_ty = lower.text(type_idents[0]) if type_idents else None
        method_fids: list[str] = []
        # 方法在 declaration_list 内，不一定是 impl_item 的直接子节点
        fn_nodes = [c for c in node.children if c.type == "function_item"]
        if not fn_nodes:
            fn_nodes = [c for c in _walk(node) if c.type == "function_item"]
        for fn_node in fn_nodes:
            fir = lower_fn(fn_node, trait_name, self_ty)
            functions.append(fir)
            method_fids.append(fir.fid)
        if trait_name is not None:
            impls.append(TraitImpl(trait_name=trait_name, self_ty=self_ty or "",
                                   file=rel, methods=method_fids))

    for node in root.children:
        if node.type == "function_item":
            functions.append(lower_fn(node, None, None))

    aliases = _collect_use_aliases(root, src_bytes)
    return ModuleIR(file=rel, crate=crate, mod_path=mod, functions=functions,
                    impls=impls, use_aliases=aliases, parse_error=root.has_error)


def read_file(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def discover_rust_files(root: str) -> list[str]:
    """确定性顺序收集 .rs 文件；默认只看 crates/，filler 等由调用方决定。"""
    out: list[str]
    out = []
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in {".git", "__pycache__"})
        for name in sorted(names):
            if name.endswith(".rs"):
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, os.path.dirname(root) if os.path.basename(root) == "" else root)
                out.append(rel.replace(os.sep, "/"))
    return sorted(out)
