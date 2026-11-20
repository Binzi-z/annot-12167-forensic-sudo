"""resolve.py —— 第 2 层：名称解析与全局索引。

tree-sitter 只给语法结构，名字到定义的映射在这里自己建：

* use 别名归一化（``use fw_common as common`` -> ``common::fsx::read_text``
  还原成 ``fw_common::...``，再按 Cargo 包名映射到 ``common`` crate）；
* 函数 fid 索引、trait -> impl 方法索引（跨 trait 实现分派用）；
* source / sink / sanitizer 的判定全部来自 ``config/sanitizers.json``，
  规则本身不内置，配置即规则，也直接充当消融开关。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .ir import ModuleIR

# Cargo 包名 -> 目录/crate 名（fw_common -> common）。
_PACKAGE_TO_CRATE = {
    "fw_common": "common",
    "fw_rpc": "rpc",
    "fw_config": "config",
    "fw_ingest": "ingest",
    "fw_unpack": "unpack",
    "fw_serve": "serve",
    "fw_render": "render",
    "fw_app": "app",
}

# 文件系统落点 API：方法名（receiver 形态）或全路径末段名。
# 这是「落点形态」清单而非漏洞规则——是否报警取决于污点是否到达。
SINK_METHODS = {
    "File::open": "file_open",
    "File::create": "file_create",
    "fs::read_to_string": "read_to_string",
    "fs::read": "fs_read",
    "fs::write": "fs_write",
    "fs::read_dir": "read_dir",
    "fs::copy": "fs_copy",
    "NamedFile::open": "named_file_open",
    "add_template_file": "add_template_file",
    "read_text": "read_text",
    "read_bytes": "read_bytes",
    "write_text": "write_text",
    "write_bytes": "write_bytes",
}


@dataclass
class AnalysisConfig:
    sources: dict[str, list[str]]              # source 类别 -> 调用名列表
    sanitizer_names: set[str]                  # 净化函数短名
    sanitizer_kinds: dict[str, str]            # 短名 -> kind
    static_dirs: set[str]
    template_dirs: set[str]
    safe_templates: set[str]
    cross_crate: bool = True                   # 消融开关：跨 crate 传播
    recognize_sanitizers: bool = True          # 消融开关：净化识别

    @classmethod
    def load(cls, path: str, cross_crate: bool = True,
             recognize_sanitizers: bool = True) -> "AnalysisConfig":
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        sans = doc.get("sanitizers", [])
        return cls(
            sources=doc.get("sources", {}),
            sanitizer_names={s["name"] for s in sans},
            sanitizer_kinds={s["name"]: s.get("kind", "") for s in sans},
            static_dirs=set(doc.get("static_dirs", [])),
            template_dirs=set(doc.get("template_dirs", [])),
            safe_templates=set(doc.get("safe_templates", [])),
            cross_crate=cross_crate,
            recognize_sanitizers=recognize_sanitizers,
        )

    def source_call_names(self) -> set[str]:
        out: set[str] = set()
        for names in self.sources.values():
            out.update(names)
        return out
@dataclass
class GlobalIndex:
    modules: dict[str, ModuleIR]
    funcs: dict[str, object] = field(default_factory=dict)              # fid -> FunctionIR
    func_by_name: dict[str, list[object]] = field(default_factory=dict)  # 短名 -> FunctionIR
    trait_impls: dict[str, list[str]] = field(default_factory=dict)      # trait 名 -> 方法 fid
    crate_of_fid: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        for mod in self.modules.values():
            for fn in mod.functions:
                self.funcs[fn.fid] = fn
                self.func_by_name.setdefault(fn.name, []).append(fn)
                self.crate_of_fid[fn.fid] = mod.crate
                if fn.trait_name:
                    self.trait_impls.setdefault(fn.trait_name, []).append(fn.fid)

    def resolve_fid(self, callee_text: str, current_mod: ModuleIR) -> str | None:
        """把调用表达式的文本路径尽量归一到某个函数 fid。"""
        name = normalize_path(callee_text, current_mod)
        if name is None:
            return None
        # 直接全路径命中
        if name in self.funcs:
            return name
        # 末段名唯一命中
        short = name.split("::")[-1]
        cands = self.func_by_name.get(short, [])
        if len(cands) == 1:
            return cands[0].fid
        # 多候选时用路径前缀匹配
        tail = name.split("::")
        for cand in cands:
            fid_parts = cand.fid.split("::")
            if len(fid_parts) >= len(tail) and fid_parts[-len(tail):] == tail:
                return cand.fid
        return None


def normalize_path(text: str, mod: ModuleIR) -> str | None:
    """归一化调用/路径文本：去泛型、处理 use 别名与 Cargo 包名。"""
    text = text.strip()
    # 去掉可能的 turbofish / 泛型
    if "<" in text:
        text = text.split("<", 1)[0]
    parts = [p for p in text.split("::") if p]
    if not parts:
        return None
    if parts[0] in mod.use_aliases:
        parts[0] = mod.use_aliases[parts[0]]
    if parts[0] in _PACKAGE_TO_CRATE:
        parts[0] = _PACKAGE_TO_CRATE[parts[0]]
    # crate 根段名（common/rpc/...）直接保留
    return "::".join(parts)


def call_head_parts(call_node) -> tuple[str | None, str | None, object | None]:
    """拆 call_expression 的函数位。

    返回 (receiver 文本或 None, 方法/函数短名, 函数位子节点)。
    形如 ``req.query(..)`` -> ("req", "query", field_expression)；
    ``fs::read_to_string(..)`` -> (None, "fs::read_to_string", scoped_identifier)；
    ``common::fsx::read_text(..)`` -> (None, "common::fsx::read_text", ...)。
    """
    fn_node = call_node.child_by_field_name("function")
    if fn_node is None:
        return None, None, None
    if fn_node.type == "field_expression":
        recv = fn_node.child_by_field_name("object")
        field = fn_node.child_by_field_name("field")
        recv_text = recv.text.decode() if recv is not None and isinstance(recv.text, bytes) \
            else (recv.text if recv is not None else None)
        name = field.text.decode() if field is not None and isinstance(field.text, bytes) \
            else (field.text if field is not None else None)
        return recv_text, name, fn_node
    if fn_node.type == "scoped_identifier":
        return None, fn_node.text.decode() if isinstance(fn_node.text, bytes) else fn_node.text, fn_node
    if fn_node.type == "identifier":
        return None, fn_node.text.decode() if isinstance(fn_node.text, bytes) else fn_node.text, fn_node
    return None, fn_node.text.decode() if isinstance(fn_node.text, bytes) else fn_node.text, fn_node


def arguments_of(call_node):
    args = call_node.child_by_field_name("arguments")
    if args is None:
        return []
    return [c for c in args.children if c.is_named and c.type not in (",",)]


def macro_name_and_tt(macro_node):
    name_node = macro_node.child_by_field_name("macro") or macro_node.children[0]
    name = name_node.text.decode() if isinstance(name_node.text, bytes) else name_node.text
    tt = None
    for ch in macro_node.children:
        if ch.type == "token_tree":
            tt = ch
            break
    return name, tt
