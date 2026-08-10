"""只读执行器：仅执行经过语义和 AST 守卫验证的模型 SQL。"""

from __future__ import annotations

import re
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator, Iterator

from sqlglot import exp, parse_one

from data_agent.knowledge.catalog import KnowledgeCatalog
from data_agent.database import Database
from .localization import column_label
from data_agent.query.contracts import RouteDecision
from .guard import SQLGuard, SQLValidationError


LIKE_PLACEHOLDER_RE = re.compile(
    r"\bLIKE\s+\?(?:\s+ESCAPE\s+(?:'[^']*'|\"[^\"]*\"))?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class QueryPlan:
    view_name: str
    sql: str
    parameters: tuple[Any, ...]
    source_views: tuple[str, ...] = ()
    base_sql: str | None = None


@dataclass(frozen=True)
class QueryResult:
    question: str
    route: RouteDecision
    plan: QueryPlan
    rows: tuple[dict[str, Any], ...]
    column_labels: dict[str, str]
    notices: tuple[str, ...]
    total_count: int
    has_more: bool


class ReadOnlyQueryService:
    """生成 SQL 的唯一数据库执行 Interface，并支持完整结果流式导出。"""

    def __init__(
        self,
        source: Database,
        catalog: KnowledgeCatalog,
        database_profile: dict[str, Any] | None = None,
        max_execution_seconds: float = 3.0,
        max_export_seconds: float = 30.0,
    ) -> None:
        self.source = source
        self.database_path = self.source.database_path
        self.catalog = catalog
        self.database_profile = database_profile or {}
        self.max_execution_seconds = max_execution_seconds
        self.max_export_seconds = max_export_seconds

    def _connect(self, *, export: bool = False) -> Any:
        timeout = self.source.export_timeout_seconds if export else self.source.query_timeout_seconds
        return self.source.connect(timeout_seconds=timeout)

    def _column_labels(
        self,
        plan: QueryPlan,
        rows: tuple[dict[str, Any], ...],
    ) -> dict[str, str]:
        if not rows:
            return {}
        semantics: dict[str, str] = {}
        for view_name in plan.source_views or (plan.view_name,):
            try:
                view = self.catalog.by_name(view_name)
            except KeyError:
                continue
            semantics.update(
                {
                    name: detail["label_zh"]
                    for name, detail in view.column_semantics.items()
                    if detail.get("label_zh")
                }
            )
        return {name: semantics.get(name, column_label(name)) for name in rows[0]}

    def _validate_result(
        self,
        plan: QueryPlan,
        rows: tuple[dict[str, Any], ...],
    ) -> tuple[str, ...]:
        notices: list[str] = []
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

    @staticmethod
    def _contains_match_variant(
        sql: str,
        parameters: tuple[Any, ...],
    ) -> tuple[str, tuple[Any, ...]] | None:
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

    def _matching_row_sql(self, base_sql: str) -> str | None:
        try:
            tree = parse_one(base_sql, read=self.source.dialect)
        except Exception:
            return None
        if not isinstance(tree, exp.Select):
            return None
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
        connection.set_progress_handler(
            lambda: 1 if time.monotonic() > deadline else 0,
            1_000,
        )
        try:
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
            total_row = self.source.row_dict(total_cursor, total_raw) if total_raw is not None else {}
            result_cursor = self.source.execute(connection, validated.sql, validated.parameters)
            return (
                int(total_row.get("total_count") or 0),
                self.source.fetchall_dicts(result_cursor),
            )
        except Exception as error:
            lowered = str(error).lower()
            if "interrupted" in lowered or "timeout" in lowered:
                raise SQLValidationError("查询执行时间超过安全限制。") from error
            raise SQLValidationError("查询无法在当前数据源中执行。") from error
        finally:
            connection.set_progress_handler(None, 0)

    def ask_generated_sql(
        self,
        question: str,
        sql: str,
        parameters: tuple[Any, ...],
        route_decision: RouteDecision,
        limit: int = 500,
    ) -> QueryResult:
        guard = SQLGuard(
            self.catalog,
            self.database_profile,
            max_rows=500,
            source=self.source,
        )
        contains_variant = self._contains_match_variant(sql, tuple(parameters))
        fallback_sql, fallback_parameters = contains_variant or (sql, tuple(parameters))
        validated = guard.validate(fallback_sql, fallback_parameters, requested_limit=limit)
        deadline = time.monotonic() + self.max_execution_seconds
        selected = validated
        with self._connect() as connection:
            exact_variant = self._exact_match_variant(fallback_sql, fallback_parameters)
            if exact_variant is None:
                total_count, rows = self._execute_generated_query(connection, validated, deadline)
            else:
                exact_validated = guard.validate(*exact_variant, requested_limit=limit)
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
                        cursor = self.source.execute(
                            connection,
                            matching_sql,
                            exact_validated.parameters,
                        )
                        has_exact_source_row = cursor.fetchone() is not None
                if has_exact_source_row:
                    selected = exact_validated
                    total_count, rows = exact_total, exact_rows
                else:
                    total_count, rows = self._execute_generated_query(
                        connection,
                        validated,
                        deadline,
                    )
        plan = QueryPlan(
            view_name=selected.source_views[0],
            sql=selected.sql,
            parameters=selected.parameters,
            source_views=selected.source_views,
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
                connection.set_progress_handler(
                    lambda: 1 if time.monotonic() > deadline else 0,
                    1_000,
                )
                cursor = self.source.execute(connection, validated.sql, validated.parameters)
                columns = self.source.cursor_columns(cursor)

                def row_iterator() -> Iterator[tuple[Any, ...]]:
                    while batch := cursor.fetchmany(1_000):
                        for row in batch:
                            yield tuple(row)

                yield columns, row_iterator()
                connection.set_progress_handler(None, 0)
        except Exception as error:
            lowered = str(error).lower()
            if "interrupted" in lowered or "timeout" in lowered:
                raise SQLValidationError("完整结果导出时间超过安全限制。") from error
            raise SQLValidationError("完整结果无法从当前数据源导出。") from error
