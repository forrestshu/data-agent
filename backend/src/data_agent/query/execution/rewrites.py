"""查询改写：只从已有 SQL 生成候选字符串，不校验、不碰库。"""

from __future__ import annotations

import re
from typing import Any

from sqlglot import exp, parse_one


LIKE_PLACEHOLDER_RE = re.compile(
    r"\bLIKE\s+\?(?:\s+ESCAPE\s+(?:'[^']*'|\"[^\"]*\"))?",
    re.IGNORECASE,
)


def exact_match_variant(
    sql: str,
    parameters: tuple[Any, ...],
) -> tuple[str, tuple[Any, ...]] | None:
    """把 LIKE ? 改成等值比较，并去掉参数两端的 %。"""

    matches = list(LIKE_PLACEHOLDER_RE.finditer(sql))
    if not matches:
        return None
    exact_parameters = list(parameters)
    replacements: list[tuple[int, int, str]] = []
    for match in matches:
        index = sql[: match.start()].count("?")
        if index >= len(exact_parameters) or not isinstance(exact_parameters[index], str):
            return None
        exact_parameters[index] = exact_parameters[index].lstrip("%").rstrip("%")
        replacements.append((match.start(), match.end(), "= ?"))
    exact_sql = sql
    for start, end, replacement in reversed(replacements):
        exact_sql = exact_sql[:start] + replacement + exact_sql[end:]
    return exact_sql, tuple(exact_parameters)


def contains_match_variant(
    sql: str,
    parameters: tuple[Any, ...],
) -> tuple[str, tuple[Any, ...]] | None:
    """把 LIKE 收成带 ESCAPE 的包含匹配，参数按字面量处理。"""

    matches = list(LIKE_PLACEHOLDER_RE.finditer(sql))
    if not matches:
        return None
    contains_parameters = list(parameters)
    replacements: list[tuple[int, int, str]] = []
    for match in matches:
        index = sql[: match.start()].count("?")
        if index >= len(contains_parameters) or not isinstance(contains_parameters[index], str):
            return None
        core = contains_parameters[index].lstrip("%").rstrip("%")
        escaped = core.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        contains_parameters[index] = f"%{escaped}%"
        replacement = match.group(0)
        if "ESCAPE" not in replacement.upper():
            replacement += " ESCAPE '\\'"
        replacements.append((match.start(), match.end(), replacement))
    contains_sql = sql
    for start, end, replacement in reversed(replacements):
        contains_sql = contains_sql[:start] + replacement + contains_sql[end:]
    return contains_sql, tuple(contains_parameters)


def matching_row_sql(base_sql: str, dialect: str) -> str | None:
    """生成只探有无匹配行的 SELECT 1，供精确匹配在聚合查询上使用。"""

    try:
        tree = parse_one(base_sql, read=dialect)
    except Exception:
        return None
    if not isinstance(tree, exp.Select):
        return None
    tree.set("expressions", [exp.Literal.number("1")])
    for argument in ("distinct", "group", "having", "order", "limit"):
        tree.set(argument, None)
    return tree.limit(1).sql(dialect=dialect)


def is_aggregate_sql(sql: str, dialect: str) -> bool:
    """判断 SQL 是否包含会把多行收成汇总结果的聚合或分组。"""

    try:
        tree = parse_one(sql, read=dialect)
    except Exception:
        return False
    return any(
        isinstance(node, (exp.Sum, exp.Count, exp.Min, exp.Max, exp.Avg, exp.Group))
        for node in tree.walk()
    )
