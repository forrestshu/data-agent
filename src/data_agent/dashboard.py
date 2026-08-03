"""把知识画像与安全查询结果转换为前端可渲染的动态 Dashboard 契约。"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from numbers import Real
import re
from typing import Any

from .catalog import KnowledgeCatalog
from .executor import QueryResult


DashboardPayload = dict[str, Any]

_DATE_MARKERS = (
    "date",
    "time",
    "day",
    "month",
    "year",
    "日期",
    "时间",
    "月份",
    "年度",
)
_AGGREGATE_MARKERS = ("合计", "总量", "总额", "总数", "一共", "多少")
_FILTER_MARKERS = (
    "低于",
    "少于",
    "小于",
    "高于",
    "多于",
    "大于",
    "不超过",
    "不少于",
    "至少",
    "哪些",
    "列出",
    "明细",
)
_LIST_MARKERS = ("哪些", "列出", "明细", "分别", "哪几")
_BOLD_NUMBER_RE = re.compile(
    r"\*\*\s*([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*\*\*"
)


def _number(value: Any) -> float | int | None:
    """只接受可安全绘图的有限实数，并保留整数显示。"""

    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        return None
    numeric = float(value)
    if numeric != numeric or numeric in {float("inf"), float("-inf")}:
        return None
    return int(numeric) if numeric.is_integer() else numeric


def _widget(
    widget_id: str,
    kind: str,
    title: str,
    *,
    relevance: float,
    size: str,
    subtitle: str = "",
    value: Any = None,
    data: list[dict[str, Any]] | None = None,
    columns: list[str] | None = None,
    rows: list[dict[str, Any]] | None = None,
    source: str = "",
    unit: str = "",
    column_units: dict[str, str] | None = None,
) -> DashboardPayload:
    return {
        "id": widget_id,
        "kind": kind,
        "title": title,
        "subtitle": subtitle,
        "relevance": relevance,
        "size": size,
        "value": value,
        "data": data or [],
        "columns": columns or [],
        "rows": rows or [],
        "source": source,
        "unit": unit,
        "column_units": column_units or {},
    }


def build_initial_dashboard(
    profile: dict[str, Any],
    catalog: KnowledgeCatalog,
) -> DashboardPayload:
    """构建无需额外业务查询的初始概览，所有数字均来自当前知识画像。"""

    summary = profile.get("summary", {})
    tables = {
        str(table.get("name")): int(table.get("row_count") or 0)
        for table in profile.get("tables", [])
        if isinstance(table, dict) and table.get("name")
    }
    view_map = {view.name: view for view in catalog.views}
    ranked_views = sorted(tables.items(), key=lambda item: item[1], reverse=True)
    top_views = [
        {
            "label": (
                f"{view_map[name].domain} · {view_map[name].purpose[:6]}"
                if name in view_map
                else name
            ),
            "detail": view_map[name].purpose if name in view_map else name,
            "value": row_count,
        }
        for name, row_count in ranked_views[:6]
    ]

    domain_rows: dict[str, int] = defaultdict(int)
    for name, row_count in tables.items():
        view = view_map.get(name)
        domain_rows[view.domain if view else "其他"] += row_count
    domains = [
        {"label": domain, "value": row_count}
        for domain, row_count in sorted(
            domain_rows.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    generated_at = str(profile.get("generated_at") or "")
    snapshot = str(
        profile.get("database", {}).get("file_name")
        or profile.get("database", {}).get("database_name")
        or "当前数据源"
    )
    return {
        "mode": "initial",
        "title": "业务数据概览",
        "question": None,
        "summary": "先从当前数据源的整体覆盖开始；提出问题后，图表会围绕你的核心关注点重新排布。",
        "layout_reason": "初始布局按数据覆盖面与业务领域组织。",
        "generated_at": generated_at,
        "widgets": [
            _widget(
                "dataset-volume",
                "metric",
                "当前数据记录",
                relevance=0.92,
                size="hero",
                subtitle=f"来自 {snapshot} 的已画像业务记录",
                value=int(summary.get("total_row_count") or sum(tables.values())),
                source="知识画像",
                unit="条",
            ),
            _widget(
                "view-coverage",
                "metric",
                "已审核业务视图",
                relevance=0.72,
                size="compact",
                subtitle="可用于自然语言查询",
                value=int(summary.get("business_table_count") or len(tables)),
                source="语义层",
                unit="个",
            ),
            _widget(
                "largest-views",
                "bar",
                "主要数据覆盖",
                relevance=0.68,
                size="standard",
                subtitle="按业务视图记录量展示前 6 项",
                data=top_views,
                source="知识画像",
            ),
            _widget(
                "domain-mix",
                "bar",
                "业务领域分布",
                relevance=0.6,
                size="standard",
                subtitle="各业务领域已纳入画像的记录量",
                data=domains,
                source="知识目录",
            ),
        ],
    }


def _column_relevance(question: str, column: str, label: str) -> int:
    normalized = question.casefold().replace(" ", "")
    score = 0
    for candidate in (column, label):
        cleaned = candidate.casefold().replace(" ", "")
        if cleaned and cleaned in normalized:
            score += len(cleaned) * 2
    return score


def _is_date_column(column: str, label: str) -> bool:
    lowered = f"{column} {label}".casefold()
    return any(marker in lowered for marker in _DATE_MARKERS)


def _select_columns(
    result: QueryResult,
) -> tuple[list[str], list[str]]:
    if not result.rows:
        return [], []
    numeric: list[str] = []
    categorical: list[str] = []
    for column in result.rows[0]:
        values = [row.get(column) for row in result.rows if row.get(column) is not None]
        if values and sum(_number(value) is not None for value in values) >= max(
            1,
            len(values) // 2,
        ):
            numeric.append(column)
        else:
            categorical.append(column)
    return numeric, categorical


def _prioritize_columns(
    columns: list[str],
    preferred: tuple[str, ...] | list[str],
) -> list[str]:
    """展示层列排序：优先使用 Dashboard Agent 指定的维度或指标，再保留其余可用列。"""

    if not preferred:
        return columns
    available = {column.casefold(): column for column in columns}
    selected: list[str] = []
    for item in preferred:
        column = available.get(item.casefold())
        if column is not None and column not in selected:
            selected.append(column)
    selected.extend(column for column in columns if column not in selected)
    return selected


def _answer_metric(question: str, answer: str) -> float | int | None:
    """只提取纯聚合结论；筛选阈值和列表条件绝不能充当回答指标。"""

    if not any(marker in question for marker in _AGGREGATE_MARKERS):
        return None
    if any(marker in question for marker in _FILTER_MARKERS):
        return None
    match = _BOLD_NUMBER_RE.search(answer)
    if match is None:
        return None
    try:
        value = float(match.group(1).replace(",", ""))
    except ValueError:
        return None
    return int(value) if value.is_integer() else value


def _unit_for(
    column: str | None,
    labels: dict[str, str],
    display_units: dict[str, str],
) -> str:
    """读取模型为 SQL 输出列判断的展示单位，并兼容本地化列名。"""

    if column is None:
        return ""
    label = labels.get(column, column)
    return str(display_units.get(column) or display_units.get(label) or "").strip()


def build_query_dashboard(
    question: str,
    result: QueryResult,
    *,
    original_question: str | None = None,
    answer: str = "",
    intent_summary: str,
    route_reason: str,
    display_units: dict[str, str] | None = None,
    dashboard_title: str | None = None,
    dashboard_summary: str | None = None,
    visualization_hint: str = "auto",
    preferred_dimensions: tuple[str, ...] = (),
    preferred_metrics: tuple[str, ...] = (),
) -> DashboardPayload:
    """根据已验证结果生成 Dashboard；概况链路可额外传入模型选择的展示维度。"""

    numeric_columns, categorical_columns = _select_columns(result)
    labels = result.column_labels
    units = display_units or {}
    asks_for_list = any(marker in question for marker in _LIST_MARKERS)
    asks_for_count = any(
        marker in question
        for marker in ("有多少", "共有多少", "多少个", "多少条", "几条", "几种")
    )
    numeric_columns.sort(
        key=lambda column: _column_relevance(
            question,
            column,
            labels.get(column, column),
        ),
        reverse=True,
    )
    numeric_columns = _prioritize_columns(numeric_columns, preferred_metrics)
    categorical_columns.sort(
        key=lambda column: (
            _is_date_column(column, labels.get(column, column)),
            _column_relevance(question, column, labels.get(column, column)),
        ),
        reverse=True,
    )
    categorical_columns = _prioritize_columns(categorical_columns, preferred_dimensions)
    primary_numeric = numeric_columns[0] if numeric_columns else None
    primary_category = categorical_columns[0] if categorical_columns else None
    answer_metric = _answer_metric(question, answer)
    source_views = result.plan.source_views or (result.plan.view_name,)
    source_label = "、".join(source_views)
    widgets: list[DashboardPayload] = []

    if answer_metric is not None:
        primary_label = (
            labels.get(primary_numeric, primary_numeric)
            if primary_numeric
            else "核心结果"
        )
        widgets.append(
            _widget(
                "primary-answer",
                "metric",
                primary_label,
                relevance=1.0,
                size="hero",
                subtitle=intent_summary or "当前问题的核心结果",
                value=answer_metric,
                source=source_label,
                unit=_unit_for(primary_numeric, labels, units),
            )
        )
        if primary_numeric and primary_category and len(result.rows) > 1:
            widgets.append(
                _widget(
                    "related-distribution",
                    "bar",
                    f"{labels.get(primary_numeric, primary_numeric)}明细分布",
                    relevance=0.74,
                    size="standard",
                    subtitle="核心结论对应的前 12 条预览明细",
                    data=[
                        {
                            "label": str(
                                row.get(primary_category)
                                if row.get(primary_category) is not None
                                else "—"
                            ),
                            "value": value,
                            "unit": _unit_for(primary_numeric, labels, units),
                        }
                        for row in result.rows[:12]
                        if (value := _number(row.get(primary_numeric))) is not None
                    ],
                    source=source_label,
                    unit=_unit_for(primary_numeric, labels, units),
                )
            )
    elif len(result.rows) == 1 and primary_numeric:
        primary_label = labels.get(primary_numeric, primary_numeric)
        widgets.append(
            _widget(
                "primary-answer",
                "metric",
                primary_label,
                relevance=1.0,
                size="hero",
                subtitle=intent_summary or "当前问题的核心结果",
                value=_number(result.rows[0].get(primary_numeric)),
                source=source_label,
                unit=_unit_for(primary_numeric, labels, units),
            )
        )
        remaining_metrics = [
            column for column in numeric_columns[1:4]
            if _number(result.rows[0].get(column)) is not None
        ]
        if remaining_metrics:
            widgets.append(
                _widget(
                    "related-metrics",
                    "bar",
                    "关联指标",
                    relevance=0.74,
                    size="standard",
                    subtitle="同一查询结果中的其他数值指标",
                    data=[
                        {
                            "label": labels.get(column, column),
                            "value": _number(result.rows[0].get(column)),
                            "unit": _unit_for(column, labels, units),
                        }
                        for column in remaining_metrics
                    ],
                    source=source_label,
                )
            )
    elif primary_numeric and result.rows:
        numeric_label = labels.get(primary_numeric, primary_numeric)
        category = primary_category
        if category is None:
            category = next(
                (column for column in result.rows[0] if column != primary_numeric),
                primary_numeric,
            )
        category_label = labels.get(category, category)
        points = [
            {
                "label": str(row.get(category) if row.get(category) is not None else "—"),
                "value": _number(row.get(primary_numeric)),
                "unit": _unit_for(primary_numeric, labels, units),
            }
            for row in result.rows[:12]
            if _number(row.get(primary_numeric)) is not None
        ]
        chart_kind = "line" if _is_date_column(category, category_label) else "bar"
        if visualization_hint == "trend":
            chart_kind = "line"
        elif visualization_hint in {"ranking", "breakdown"}:
            chart_kind = "bar"
        widgets.append(
            _widget(
                "primary-answer",
                chart_kind,
                f"{numeric_label} · {category_label}",
                relevance=1.0,
                size="hero",
                subtitle=intent_summary or "当前问题的核心结果",
                data=points,
                source=source_label,
                unit=_unit_for(primary_numeric, labels, units),
            )
        )

        numeric_values = [
            value
            for row in result.rows
            if (value := _number(row.get(primary_numeric))) is not None
        ]
        if numeric_values:
            widgets.append(
                _widget(
                    "numeric-range",
                    "bar",
                    f"{numeric_label}概览",
                    relevance=0.38 if asks_for_list else 0.7,
                    size="standard",
                    subtitle="当前预览数据的均值、最大值与最小值",
                    data=[
                        {
                            "label": "平均",
                            "value": sum(numeric_values) / len(numeric_values),
                            "unit": _unit_for(primary_numeric, labels, units),
                        },
                        {
                            "label": "最大",
                            "value": max(numeric_values),
                            "unit": _unit_for(primary_numeric, labels, units),
                        },
                        {
                            "label": "最小",
                            "value": min(numeric_values),
                            "unit": _unit_for(primary_numeric, labels, units),
                        },
                    ],
                    source=source_label,
                    unit=_unit_for(primary_numeric, labels, units),
                )
            )
    else:
        widgets.append(
            _widget(
                "primary-answer",
                "metric",
                "符合条件的记录",
                relevance=1.0,
                size="hero",
                subtitle=intent_summary or "当前问题的核心结果",
                value=result.total_count,
                source=source_label,
                unit="条",
            )
        )

    primary_is_total = (
        widgets
        and widgets[0]["kind"] == "metric"
        and widgets[0]["value"] == result.total_count
        and widgets[0]["title"] == "符合条件的记录"
    )
    if not primary_is_total:
        widgets.append(
            _widget(
                "matching-records",
                "metric",
                "完整匹配记录",
                relevance=0.82 if asks_for_count else 0.58,
                size="compact",
                subtitle=f"Dashboard 当前使用前 {len(result.rows)} 条预览数据",
                value=result.total_count,
                source=source_label,
                unit="条",
            )
        )

    if result.rows:
        preview_columns = list(result.rows[0])[:4]
        display_columns = [labels.get(column, column) for column in preview_columns]
        widgets.append(
            _widget(
                "evidence-preview",
                "table",
                "数据依据",
                relevance=0.92 if asks_for_list else 0.52,
                size="wide",
                subtitle="与主图表使用同一份安全查询结果",
                columns=display_columns,
                rows=[
                    {
                        labels.get(column, column): row.get(column)
                        for column in preview_columns
                    }
                    for row in result.rows[:3]
                ],
                source=source_label,
                column_units={
                    labels.get(column, column): _unit_for(column, labels, units)
                    for column in preview_columns
                    if _unit_for(column, labels, units)
                },
            )
        )

    return {
        "mode": "query",
        "title": dashboard_title or intent_summary or "查询 Dashboard",
        # 展示契约只保留用户首轮问题，不把内部拼接的多轮记录暴露给标题层。
        "question": (original_question or question).strip(),
        "summary": dashboard_summary or route_reason or "图表已按当前问题与结果相关度重新排布。",
        "layout_reason": (
            f"概况展示模式为 {visualization_hint}；核心结果占据最大面积，"
            "其他面板按其对当前概况的贡献度递减。"
        ),
        "generated_at": "",
        "widgets": widgets,
    }
