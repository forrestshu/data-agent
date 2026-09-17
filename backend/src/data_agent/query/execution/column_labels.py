"""用已校验 SQL 的 AST 和语义目录拼中文表头，不调用模型。"""

from __future__ import annotations

from sqlglot import exp, parse_one
from sqlglot.errors import ParseError

from data_agent.knowledge.semantic_catalog import SemanticCatalog


def build_column_labels(
    sql: str,
    catalog: SemanticCatalog,
    source_views: tuple[str, ...],
    output_names: tuple[str, ...] = (),
    dialect: str = "sqlite",
) -> dict[str, str]:
    """按顶层 SELECT 投影生成 column_labels；对不上模板时保留输出列名。"""

    semantics = _column_semantics(catalog, source_views)
    try:
        tree = parse_one(sql, read=dialect)
    except ParseError:
        return {name: _lookup(semantics, name, name) for name in output_names}
    select = tree if isinstance(tree, exp.Select) else tree.find(exp.Select)
    if select is None:
        return {name: _lookup(semantics, name, name) for name in output_names}
    projections = list(select.expressions)
    names = output_names or tuple(_output_name(projection) for projection in projections)
    if len(names) == len(projections):
        return {
            name: _label_projection(projection, semantics, name)
            for name, projection in zip(names, projections)
        }
    by_alias = {_output_name(projection).casefold(): projection for projection in projections}
    labels: dict[str, str] = {}
    for name in names:
        projection = by_alias.get(name.casefold())
        if projection is None:
            labels[name] = _lookup(semantics, name, name)
        else:
            labels[name] = _label_projection(projection, semantics, name)
    return labels


def _column_semantics(
    catalog: SemanticCatalog,
    source_views: tuple[str, ...],
) -> dict[str, str]:
    semantics: dict[str, str] = {}
    for view_name in source_views:
        try:
            view = catalog.by_name(view_name)
        except KeyError:
            continue
        semantics.update(
            {
                name: str(detail["business_name"])
                for name, detail in view.column_semantics.items()
                if detail.get("business_name")
            }
        )
    return semantics


def _lookup(semantics: dict[str, str], physical_name: str, fallback: str) -> str:
    if physical_name in semantics:
        return semantics[physical_name]
    folded = {name.casefold(): label for name, label in semantics.items()}
    return folded.get(physical_name.casefold(), fallback)


def _output_name(projection: exp.Expression) -> str:
    if isinstance(projection, exp.Alias) and projection.alias:
        return projection.alias
    return projection.alias_or_name or projection.sql()


def _label_projection(
    projection: exp.Expression,
    semantics: dict[str, str],
    fallback: str,
) -> str:
    rendered = _render(_unwrap(projection), semantics)
    return rendered if rendered else fallback


def _unwrap(expression: exp.Expression) -> exp.Expression:
    current: exp.Expression = expression
    while True:
        if isinstance(current, (exp.Alias, exp.Paren, exp.Cast)):
            inner = current.this
            if not isinstance(inner, exp.Expression):
                return current
            current = inner
            continue
        return current


def _render(expression: exp.Expression, semantics: dict[str, str]) -> str | None:
    node = _unwrap(expression)
    if isinstance(node, exp.Column):
        return _lookup(semantics, node.name, node.name)
    if isinstance(node, exp.Sum):
        return _with_suffix(node.this, semantics, "合计")
    if isinstance(node, exp.Avg):
        return _with_suffix(node.this, semantics, "平均")
    if isinstance(node, exp.Min):
        return _with_suffix(node.this, semantics, "最小")
    if isinstance(node, exp.Max):
        return _with_suffix(node.this, semantics, "最大")
    if isinstance(node, exp.Count):
        return _render_count(node, semantics)
    if isinstance(node, exp.Div):
        left = _column_operand_label(node.this, semantics)
        right = _column_operand_label(node.expression, semantics)
        if left and right:
            return f"{left}/{right}"
        return None
    return None


def _render_count(node: exp.Count, semantics: dict[str, str]) -> str | None:
    target = node.this
    if target is None or isinstance(target, exp.Star):
        return "行数"
    if isinstance(target, exp.Distinct):
        operand = _distinct_operand(target)
        label = _column_operand_label(operand, semantics)
        return f"{label}去重计数" if label else None
    label = _column_operand_label(target, semantics)
    return f"{label}计数" if label else None


def _distinct_operand(distinct: exp.Distinct) -> exp.Expression | None:
    expressions = distinct.expressions
    if expressions:
        first = expressions[0]
        return first if isinstance(first, exp.Expression) else None
    inner = distinct.this
    return inner if isinstance(inner, exp.Expression) else None


def _with_suffix(
    operand: exp.Expression | None,
    semantics: dict[str, str],
    suffix: str,
) -> str | None:
    label = _column_operand_label(operand, semantics)
    return f"{label}{suffix}" if label else None


def _column_operand_label(
    operand: exp.Expression | None,
    semantics: dict[str, str],
) -> str | None:
    if operand is None:
        return None
    node = _unwrap(operand)
    if isinstance(node, exp.Column):
        return _lookup(semantics, node.name, node.name)
    return None
