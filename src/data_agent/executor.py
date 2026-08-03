"""执行层：从已路由的问题解析实体，生成参数化只读 SQL 并查 SQLite。"""

from __future__ import annotations

import re
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator, Iterator, Literal

from sqlglot import exp, parse_one

from .catalog import KnowledgeCatalog, ViewKnowledge
from .data_sources import DataSourceConfig, sqlite_source_for_path
from .localization import build_chinese_sql, column_label
from .router import QueryRouter, RouteConfirmationRequired, RouteDecision
from .sql_guard import SQLGuard, SQLValidationError


IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._#-]{1,}")
SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
QUOTED_TEXT_RE = re.compile(r"[\"“‘']([^\"”’']{2,})[\"”’']")
LABELED_TEXT_RE = re.compile(
    r"(?:物料描述|物料名称|供应商名称|供应商|客户名称|客户)"
    r"\s*(?:为|是|包含|含有|叫|：|:)?\s*([^\s，,。；;？?]{2,})"
)
LIKE_PLACEHOLDER_RE = re.compile(
    r"\bLIKE\s+\?(?:\s+ESCAPE\s+(?:'[^']*'|\"[^\"]*\"))?",
    re.IGNORECASE,
)


class ClarificationRequired(ValueError):
    """流程层的可预期中断：路由成功但缺少可唯一过滤的业务值。"""


QueryOperation = Literal[
    "detail",
    "list",
    "count_rows",
    "count_distinct",
    "sum",
    "average",
    "minimum",
    "maximum",
    "text_to_sql",
]


@dataclass(frozen=True)
class QueryPlan:
    """SQL 计划：记录明细或聚合操作，并且只包含白名单表列与绑定参数。"""

    view_name: str
    operation: QueryOperation
    metric_column: str | None
    filter_column: str | None
    filter_value: str | None
    match_mode: str
    sql: str
    sql_chinese: str
    parameters: tuple[Any, ...]
    source_views: tuple[str, ...] = ()
    base_sql: str | None = None


@dataclass(frozen=True)
class QueryResult:
    """端到端输出：区分完整匹配数量与最多 500 行的浏览器预览数据。"""

    question: str
    route: RouteDecision
    plan: QueryPlan
    rows: tuple[dict[str, Any], ...]
    column_labels: dict[str, str]
    notices: tuple[str, ...]
    total_count: int
    has_more: bool


class ReadOnlyQueryService:
    """应用服务：编排路由、实体解析、只读查询与结果校验。"""

    def __init__(
        self,
        database_path: Path | DataSourceConfig,
        catalog: KnowledgeCatalog,
        database_profile: dict[str, Any] | None = None,
        max_execution_seconds: float = 3.0,
        max_export_seconds: float = 30.0,
    ) -> None:
        self.source = (
            database_path
            if isinstance(database_path, DataSourceConfig)
            else sqlite_source_for_path(database_path)
        )
        self.database_path = self.source.database_path
        self.catalog = catalog
        self.router = QueryRouter(catalog)
        self.database_profile = database_profile or {}
        self.max_execution_seconds = max_execution_seconds
        self.max_export_seconds = max_export_seconds

    def _connect(self, *, export: bool = False) -> Any:
        """由活动数据源建立只读连接。"""

        timeout = (
            self.source.export_timeout_seconds
            if export
            else self.source.query_timeout_seconds
        )
        return self.source.connect(timeout_seconds=timeout)

    def _column_labels(
        self,
        plan: QueryPlan,
        rows: tuple[dict[str, Any], ...],
    ) -> dict[str, str]:
        """从已审核视图语义生成结果表头；没有专属语义时使用全局中文字段词典。"""

        if not rows:
            return {}
        semantic_labels: dict[str, str] = {}
        for view_name in plan.source_views or (plan.view_name,):
            try:
                view = self.catalog.by_name(view_name)
            except KeyError:
                continue
            semantic_labels.update(
                {
                    name: detail["label_zh"]
                    for name, detail in view.column_semantics.items()
                    if detail.get("label_zh")
                }
            )
        return {
            name: semantic_labels.get(name, column_label(name))
            for name in rows[0]
        }

    def _quote_identifier(self, identifier: str) -> str:
        """只允许简单 SQL 标识符，再加引号；禁止把用户文本当作表名或列名。"""

        if not SAFE_IDENTIFIER_RE.fullmatch(identifier):
            raise ValueError(f"非法 SQL 标识符: {identifier}")
        return self.source.quote_identifier(identifier)

    def _view_sql(self, view_name: str) -> str:
        if not SAFE_IDENTIFIER_RE.fullmatch(view_name):
            raise ValueError(f"非法 SQL 视图名: {view_name}")
        return self.source.physical_view(view_name)

    @staticmethod
    def _candidate_values(question: str) -> tuple[str, ...]:
        """提取可能的项目号、工单号、物料号或订单号，不直接拼接 SQL。"""

        ignored = {"bom", "ium", "pum", "sql", "erp"}
        values: list[str] = []
        for value in IDENTIFIER_RE.findall(question):
            if value.lower() not in ignored and value not in values:
                values.append(value)
        return tuple(values)

    @staticmethod
    def _text_candidates(question: str) -> tuple[str, ...]:
        """提取引号内文本或“物料描述/供应商/客户”后的文本，用于模糊查询。"""

        ignored = {"查询", "查找", "是否存在", "包含", "含有"}
        values: list[str] = []
        for pattern in (QUOTED_TEXT_RE, LABELED_TEXT_RE):
            for value in pattern.findall(question):
                cleaned = value.strip().rstrip("的")
                if cleaned not in ignored and cleaned not in values:
                    values.append(cleaned)
        return tuple(values)

    @staticmethod
    def _escape_like(value: str) -> str:
        """转义 LIKE 通配符，让用户文本只作为字面量子串。"""

        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    def _value_exists(
        self,
        connection: Any,
        view: ViewKnowledge,
        column: str,
        value: str,
    ) -> bool:
        """在目标视图中验证候选值，避免把日期或普通数字误当业务主键。"""

        base_sql = (
            f"SELECT 1 FROM {self._view_sql(view.name)} "
            f"WHERE {self.source.cast_text(self._quote_identifier(column))} = ?"
        )
        cursor = self.source.execute(
            connection,
            self.source.first_row_sql(base_sql),
            (value,),
        )
        return cursor.fetchone() is not None

    def _find_filter(
        self,
        connection: Any,
        view: ViewKnowledge,
        question: str,
        value_hints: tuple[str, ...],
    ) -> tuple[str, str, str, str] | None:
        """实体层：验证 AI/文本候选是否真实存在，返回字段、原值、模式和绑定值。"""

        candidates = tuple(dict.fromkeys((*value_hints, *self._candidate_values(question))))
        for column in view.filter_columns:
            for value in candidates:
                if self._value_exists(connection, view, column, value):
                    return column, value, "exact", value

        text_candidates = tuple(dict.fromkeys((*value_hints, *self._text_candidates(question))))
        for column in view.filter_columns:
            for value in text_candidates:
                escaped = self._escape_like(value)
                exists_sql = (
                    f"SELECT 1 FROM {self._view_sql(view.name)} "
                    f"WHERE {self.source.cast_text(self._quote_identifier(column))} "
                    "LIKE ? ESCAPE '\\'"
                )
                bound_value = f"%{escaped}%"
                cursor = self.source.execute(
                    connection,
                    self.source.first_row_sql(exists_sql),
                    (bound_value,),
                )
                if cursor.fetchone() is not None:
                    return column, value, "contains", bound_value
        return None

    def _column_type(
        self,
        connection: Any,
        view: ViewKnowledge,
        column: str,
    ) -> str:
        """知识校验层：优先读取画像类型，缺失时只读检查 SQLite 表结构。"""

        for table in self.database_profile.get("tables", []):
            if table.get("name") != view.name:
                continue
            for item in table.get("columns", []):
                if item.get("name") == column:
                    return self.source.profile_type(item).upper()
        if self.source.kind == "sqlite":
            cursor = self.source.execute(
                connection,
                f"PRAGMA table_info({self._quote_identifier(view.name)})",
            )
            for item in cursor:
                if item[1] == column:
                    return str(item[2] or "").upper()
        return ""

    def _aggregate_plan(
        self,
        connection: Any,
        view: ViewKnowledge,
        operation: QueryOperation,
        metric_column: str | None,
        selected_filter: tuple[str, str, str, str] | None,
    ) -> QueryPlan:
        """旧规则兼容层：在无 AI 测试模式中编译固定单值聚合 SQL。"""

        allowed_columns = set(view.output_columns)
        if operation == "count_rows":
            expression = "COUNT(*)"
            alias = "记录数"
            metric_column = None
        else:
            if metric_column is None or metric_column not in allowed_columns:
                raise ClarificationRequired("请明确需要统计的业务指标。")
            quoted_metric = self._quote_identifier(metric_column)
            if operation == "count_distinct":
                expression = f"COUNT(DISTINCT {quoted_metric})"
                alias = f"{metric_column}去重数量"
            else:
                sqlite_type = self._column_type(connection, view, metric_column)
                numeric_markers = ("INT", "REAL", "NUM", "DEC", "FLOAT", "DOUBLE")
                if not any(marker in sqlite_type for marker in numeric_markers):
                    raise ClarificationRequired(f"{metric_column} 不是可计算数值的指标。")
                function, suffix = {
                    "sum": ("SUM", "合计"),
                    "average": ("AVG", "平均值"),
                    "minimum": ("MIN", "最小值"),
                    "maximum": ("MAX", "最大值"),
                }[operation]
                expression = f"{function}({quoted_metric})"
                alias = f"{metric_column}{suffix}"

        where_sql = ""
        parameters: tuple[Any, ...] = ()
        filter_column: str | None = None
        filter_value: str | None = None
        match_mode = "all"
        if selected_filter is not None:
            filter_column, filter_value, match_mode, bound_value = selected_filter
            operator = "= ?" if match_mode == "exact" else "LIKE ? ESCAPE '\\'"
            where_sql = (
                " WHERE "
                f"{self.source.cast_text(self._quote_identifier(filter_column))} "
                f"{operator}"
            )
            parameters = (bound_value,)

        sql = (
            f'SELECT {expression} AS "{alias}" '
            f"FROM {self._view_sql(view.name)}{where_sql}"
        )
        scope_text = "全部记录" if selected_filter is None else f"{filter_column}={filter_value}"
        return QueryPlan(
            view_name=view.name,
            operation=operation,
            metric_column=metric_column,
            filter_column=filter_column,
            filter_value=filter_value,
            match_mode=match_mode,
            sql=sql,
            sql_chinese=f"在【{view.purpose}】中对{scope_text}执行{operation}统计",
            parameters=parameters,
        )

    def plan(
        self,
        question: str,
        route: RouteDecision,
        connection: Any,
        limit: int = 20,
        value_hints: tuple[str, ...] = (),
        operation: QueryOperation = "detail",
        metric_column: str | None = None,
    ) -> QueryPlan:
        """旧规则兼容层：根据已验证意图生成明细、列表或聚合 SELECT。"""

        view = self.catalog.by_name(route.view_name)
        selected_filter = self._find_filter(
            connection,
            view,
            question,
            value_hints,
        )

        if operation not in {"detail", "list"}:
            return self._aggregate_plan(
                connection,
                view,
                operation,
                metric_column,
                selected_filter,
            )

        selected = ", ".join(self._quote_identifier(item) for item in view.output_columns)
        if selected_filter is not None:
            column, value, match_mode, bound_value = selected_filter
            operator = "= ?" if match_mode == "exact" else "LIKE ? ESCAPE '\\'"
            base_sql = (
                f"SELECT {selected} FROM {self._view_sql(view.name)} "
                f"WHERE {self.source.cast_text(self._quote_identifier(column))} {operator}"
            )
            sql = (
                f"{base_sql} LIMIT ?"
                if self.source.kind == "sqlite"
                else self.source.limit_sql(base_sql, limit)
            )
            return QueryPlan(
                view_name=view.name,
                operation=operation,
                metric_column=None,
                filter_column=column,
                filter_value=value,
                match_mode=match_mode,
                sql=sql,
                sql_chinese=build_chinese_sql(view, column, match_mode),
                parameters=(
                    (bound_value, limit)
                    if self.source.kind == "sqlite"
                    else (bound_value,)
                ),
            )

        if operation == "list":
            return QueryPlan(
                view_name=view.name,
                operation=operation,
                metric_column=None,
                filter_column=None,
                filter_value=None,
                match_mode="all",
                sql=(
                    f"SELECT {selected} FROM {self._view_sql(view.name)} LIMIT ?"
                    if self.source.kind == "sqlite"
                    else self.source.limit_sql(
                        f"SELECT {selected} FROM {self._view_sql(view.name)}",
                        limit,
                    )
                ),
                sql_chinese=f"列出【{view.purpose}】的前 {limit} 条记录",
                parameters=(limit,) if self.source.kind == "sqlite" else (),
            )

        raise ClarificationRequired(
            "需要一个具体业务对象才能查询明细，请补充编码、名称或描述。"
        )

    def _validate_result(
        self,
        plan: QueryPlan,
        rows: tuple[dict[str, Any], ...],
    ) -> tuple[str, ...]:
        """对空结果和已知快照缺陷做显式检查，禁止静默输出误导性数字。"""

        database = self.database_profile.get("database", {})
        if self.source.kind == "sqlite":
            fallback_name = self.database_path.name if self.database_path else self.source.database_name
            snapshot_name = database.get("file_name", fallback_name)
            snapshot_time = database.get("snapshot_started_at")
            time_text = f"（源快照时间 {snapshot_time}）" if snapshot_time else ""
            notices: list[str] = [
                f"查询结果来自 {snapshot_name} SQLite 离线快照{time_text}，不是实时 ERP 数据。"
            ]
        else:
            notices = [
                (
                    f"查询结果来自公司数据库 {self.source.database_name}."
                    f"{self.source.schema} 的实时视图；数据可能在查询后继续变化。"
                )
            ]
        if not rows:
            notices.append("未查到符合条件的记录。")
        selected_columns = set(rows[0]) if rows else set()
        for limitation in self.database_profile.get("generated_limitations", []):
            if (
                limitation.get("view") in (plan.source_views or (plan.view_name,))
                and limitation.get("column") in selected_columns
            ):
                notices.append(str(limitation["message"]))
        return tuple(notices)

    @staticmethod
    def _exact_match_variant(
        sql: str,
        parameters: tuple[Any, ...],
    ) -> tuple[str, tuple[Any, ...]] | None:
        """两阶段筛选第一步：把参数化 LIKE 改成等号，并去掉外层通配符。"""

        matches = list(LIKE_PLACEHOLDER_RE.finditer(sql))
        if not matches:
            return None
        exact_parameters = list(parameters)
        replacements: list[tuple[int, int, str]] = []
        for match in matches:
            parameter_index = sql[: match.start()].count("?")
            if parameter_index >= len(exact_parameters):
                return None
            value = exact_parameters[parameter_index]
            if not isinstance(value, str):
                return None
            # 模型/路由层只把两侧 % 当作包含匹配标记；内部 % 不会被悄悄删除。
            exact_parameters[parameter_index] = value.lstrip("%").rstrip("%")
            replacements.append((match.start(), match.end(), "= ?"))
        exact_sql = sql
        for start, end, replacement in reversed(replacements):
            exact_sql = exact_sql[:start] + replacement + exact_sql[end:]
        return exact_sql, tuple(exact_parameters)

    @staticmethod
    def _contains_match_variant(
        sql: str,
        parameters: tuple[Any, ...],
    ) -> tuple[str, tuple[Any, ...]] | None:
        """两阶段筛选第二步：规范为两侧一对 %，内部通配符全部按用户文本转义。"""

        matches = list(LIKE_PLACEHOLDER_RE.finditer(sql))
        if not matches:
            return None
        contains_parameters = list(parameters)
        replacements: list[tuple[int, int, str]] = []
        for match in matches:
            parameter_index = sql[: match.start()].count("?")
            if parameter_index >= len(contains_parameters):
                return None
            value = contains_parameters[parameter_index]
            if not isinstance(value, str):
                return None
            core = value.lstrip("%").rstrip("%")
            escaped_core = (
                core.replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            contains_parameters[parameter_index] = f"%{escaped_core}%"
            replacement = match.group(0)
            if "ESCAPE" not in replacement.upper():
                replacement += " ESCAPE '\\'"
            replacements.append((match.start(), match.end(), replacement))
        contains_sql = sql
        for start, end, replacement in reversed(replacements):
            contains_sql = contains_sql[:start] + replacement + contains_sql[end:]
        return contains_sql, tuple(contains_parameters)

    def _matching_row_sql(self, base_sql: str) -> str | None:
        """两阶段筛选辅助查询：将已通过守卫的 SELECT 降为“是否存在源行”的只读查询。"""

        try:
            tree = parse_one(base_sql, read=self.source.dialect)
        except Exception:
            return None
        if not isinstance(tree, exp.Select):
            return None
        # 保留 FROM/WHERE/JOIN 和 CTE，只去掉聚合、分组及排序，避免聚合空结果被误判为命中。
        tree.set("expressions", [exp.Literal.number("1")])
        for argument in ("distinct", "group", "having", "order", "limit"):
            tree.set(argument, None)
        return tree.limit(1).sql(dialect=self.source.dialect)

    def _execute_generated_query(
        self,
        connection: Any,
        validated: Any,
        deadline: float,
    ) -> tuple[int, tuple[dict[str, Any], ...]]:
        """执行层共享函数：执行计数、预览和 SQLite 进度保护，返回总数与行。"""

        if self.source.kind == "sqlite":
            # SQLite 每执行一批虚拟机指令检查一次截止时间，防止回退查询失控。
            connection.set_progress_handler(
                lambda: 1 if time.monotonic() > deadline else 0,
                1_000,
            )
        try:
            if self.source.kind == "sqlite":
                self.source.execute(
                    connection,
                    f"EXPLAIN QUERY PLAN {validated.sql}",
                    validated.parameters,
                ).fetchall()
            total_cursor = self.source.execute(
                connection,
                validated.count_sql,
                validated.parameters,
            )
            total_raw = total_cursor.fetchone()
            total_row = (
                self.source.row_dict(total_cursor, total_raw)
                if total_raw is not None
                else {}
            )
            result_cursor = self.source.execute(
                connection,
                validated.sql,
                validated.parameters,
            )
            return int(total_row.get("total_count") or 0), self.source.fetchall_dicts(result_cursor)
        except Exception as error:
            lowered = str(error).lower()
            if "interrupted" in lowered or "timeout" in lowered:
                raise SQLValidationError("查询执行时间超过安全限制。") from error
            raise SQLValidationError("查询无法在当前数据源中执行。") from error
        finally:
            if self.source.kind == "sqlite":
                connection.set_progress_handler(None, 0)

    def ask(
        self,
        question: str,
        limit: int = 20,
        confirmed_view: str | None = None,
        route_decision: RouteDecision | None = None,
        value_hints: tuple[str, ...] = (),
        operation: QueryOperation = "detail",
        metric_column: str | None = None,
    ) -> QueryResult:
        """运行完整链路；模糊候选必须带用户确认的视图名才能进入数据库层。"""

        route = route_decision or self.router.route(question, confirmed_view=confirmed_view)
        if route.requires_confirmation:
            raise RouteConfirmationRequired(route)
        with self._connect() as connection:
            plan = self.plan(
                question,
                route,
                connection,
                limit=limit,
                value_hints=value_hints,
                operation=operation,
                metric_column=metric_column,
            )
            cursor = self.source.execute(connection, plan.sql, plan.parameters)
            rows = self.source.fetchall_dicts(cursor)
        return QueryResult(
            question=question,
            route=route,
            plan=plan,
            rows=rows,
            column_labels=self._column_labels(plan, rows),
            notices=self._validate_result(plan, rows),
            total_count=len(rows),
            has_more=False,
        )

    def ask_generated_sql(
        self,
        question: str,
        sql: str,
        parameters: tuple[Any, ...],
        route_decision: RouteDecision,
        limit: int = 500,
    ) -> QueryResult:
        """Text-to-SQL 执行入口：AST 守卫通过后，限时编译并只读执行模型查询。"""

        guard = SQLGuard(
            self.catalog,
            self.database_profile,
            max_rows=500,
            source=self.source,
        )
        contains_variant = self._contains_match_variant(sql, tuple(parameters))
        fallback_sql, fallback_parameters = contains_variant or (sql, tuple(parameters))
        validated = guard.validate(
            fallback_sql,
            fallback_parameters,
            requested_limit=limit,
        )
        deadline = time.monotonic() + self.max_execution_seconds
        with self._connect() as connection:
            # 第一阶段：对模型的文本 LIKE 先执行等值匹配，避免完整描述被无谓扩大。
            exact_variant = self._exact_match_variant(fallback_sql, fallback_parameters)
            selected = validated
            if exact_variant is not None:
                exact_sql, exact_parameters = exact_variant
                exact_validated = guard.validate(
                    exact_sql,
                    exact_parameters,
                    requested_limit=limit,
                )
                exact_total, exact_rows = self._execute_generated_query(
                    connection,
                    exact_validated,
                    deadline,
                )
                exact_tree = parse_one(exact_validated.base_sql, read=self.source.dialect)
                has_aggregate = any(
                    isinstance(node, (exp.Sum, exp.Count, exp.Min, exp.Max, exp.Avg, exp.Group))
                    for node in exact_tree.walk()
                )
                has_exact_source_row = exact_total > 0
                if has_aggregate:
                    matching_sql = self._matching_row_sql(exact_validated.base_sql)
                    if matching_sql is not None:
                        matching_cursor = self.source.execute(
                            connection,
                            matching_sql,
                            exact_validated.parameters,
                        )
                        has_exact_source_row = matching_cursor.fetchone() is not None
                if has_exact_source_row:
                    selected = exact_validated
                    total_count, rows = exact_total, exact_rows
                else:
                    # 第二阶段：精确值没有源行，退回原始 LIKE（参数仍由模型/路由层绑定）。
                    total_count, rows = self._execute_generated_query(
                        connection,
                        validated,
                        deadline,
                    )
            else:
                total_count, rows = self._execute_generated_query(
                    connection,
                    validated,
                    deadline,
                )
        primary_view = selected.source_views[0]
        plan = QueryPlan(
            view_name=primary_view,
            operation="text_to_sql",
            metric_column=None,
            filter_column=None,
            filter_value=None,
            match_mode="generated",
            sql=validated.sql,
            sql_chinese="由 DeepSeek 根据语义层生成，并通过只读 SQL 安全验证",
            parameters=selected.parameters,
            source_views=validated.source_views,
            base_sql=selected.base_sql,
        )
        return QueryResult(
            question=question,
            route=route_decision,
            plan=plan,
            rows=rows,
            column_labels=self._column_labels(plan, rows),
            notices=self._validate_result(plan, rows),
            total_count=total_count,
            has_more=total_count > len(rows),
        )

    @contextmanager
    def open_generated_export(
        self,
        sql: str,
        parameters: tuple[Any, ...],
    ) -> Generator[tuple[tuple[str, ...], Iterator[tuple[Any, ...]]], None, None]:
        """导出边界：重新验证完整 SQL，并以小批次读取，避免把全部记录塞进前端或内存。"""

        guard = SQLGuard(
            self.catalog,
            self.database_profile,
            max_rows=500,
            source=self.source,
        )
        validated = guard.validate(
            sql,
            parameters,
            requested_limit=500,
            preserve_complete=True,
        )
        deadline = time.monotonic() + self.max_export_seconds
        try:
            with self._connect(export=True) as connection:
                if self.source.kind == "sqlite":
                    connection.set_progress_handler(
                        lambda: 1 if time.monotonic() > deadline else 0,
                        1_000,
                    )
                cursor = self.source.execute(
                    connection,
                    validated.sql,
                    validated.parameters,
                )
                columns = self.source.cursor_columns(cursor)

                def row_iterator() -> Iterator[tuple[Any, ...]]:
                    """流式数据层：每次只取 1000 行交给 Excel 写入器。"""

                    while batch := cursor.fetchmany(1_000):
                        for row in batch:
                            yield tuple(row)

                yield columns, row_iterator()
                if self.source.kind == "sqlite":
                    connection.set_progress_handler(None, 0)
        except Exception as error:
            lowered = str(error).lower()
            if "interrupted" in lowered or "timeout" in lowered:
                raise SQLValidationError("完整结果导出时间超过安全限制。") from error
            raise SQLValidationError("完整结果无法从当前数据源导出。") from error
