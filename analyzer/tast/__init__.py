"""tast —— tree-sitter 降 IR 后做污点分析的路径穿越原型（topic 12167）。

只依赖 tree-sitter / tree-sitter-rust 解析库，不使用任何现成漏洞规则集。
流水线：parse -> ir -> resolve -> taint -> report。
"""

__all__ = ["ir", "resolve", "taint", "report", "driver"]
