"""查询执行器：只执行已通过安全校验的 SQL，不改写、不再校验。"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator, Iterator

from data_agent.knowledge.semantic_catalog import SemanticCatalog
from data_agent.database import DatabaseSource
from data_agent.query.contracts import RouteDecision
from .column_labels import build_column_labels
from .guard import SQLValidationError, ValidatedSQL
from .prepare import PreparedQuery


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


class QueryExecutor:
    """唯一数据库执行入口：交互查询与完整结果流式导出。"""

    def __init__(
        self,
        source: DatabaseSource,
        catalog: SemanticCatalog,
        database_profile: dict[str, Any] | None = None,
        max_execution_seconds: float = 3.0,
        max_export_seconds: float = 30.0,
    ) -> None:
        self.source = source
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
        output_names = tuple(rows[0].keys()) if rows else ()
        return build_column_labels(
            plan.base_sql or plan.sql,
            self.catalog,
            plan.source_views or (plan.view_name,),
            output_names,
            dialect=self.source.dialect,
        )

    def _build_result_notices(
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

    def _execute_query(
        self,
        connection: Any,
        validated: ValidatedSQL,
        deadline: float,
    ) -> tuple[int, tuple[dict[str, Any], ...]]:
        self.source.install_deadline(connection, deadline)
        try:
            self.source.validate_execution(connection, validated.sql, validated.parameters)
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
            self.source.clear_deadline(connection)

    def execute_validated(
        self,
        question: str,
        prepared: PreparedQuery,
        route_decision: RouteDecision,
    ) -> QueryResult:
        """只跑已校验候选；精确命中时采用等值结果，否则退回包含匹配。"""

        deadline = time.monotonic() + self.max_execution_seconds
        selected = prepared.fallback
        with self._connect() as connection:
            if prepared.exact is None:
                total_count, rows = self._execute_query(connection, prepared.fallback, deadline)
            else:
                exact_total, exact_rows = self._execute_query(
                    connection,
                    prepared.exact,
                    deadline,
                )
                has_exact_source_row = exact_total > 0
                if prepared.exact_needs_probe and prepared.existence_probe is not None:
                    cursor = self.source.execute(
                        connection,
                        prepared.existence_probe.sql,
                        prepared.existence_probe.parameters,
                    )
                    has_exact_source_row = cursor.fetchone() is not None
                if has_exact_source_row:
                    selected = prepared.exact
                    total_count, rows = exact_total, exact_rows
                else:
                    total_count, rows = self._execute_query(
                        connection,
                        prepared.fallback,
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
            notices=self._build_result_notices(plan, rows),
            total_count=total_count,
            has_more=total_count > len(rows),
        )

    @contextmanager
    def open_validated_export(
        self,
        validated: ValidatedSQL,
    ) -> Generator[tuple[tuple[str, ...], Iterator[tuple[Any, ...]]], None, None]:
        deadline = time.monotonic() + self.max_export_seconds
        try:
            with self._connect(export=True) as connection:
                self.source.install_deadline(connection, deadline)
                cursor = self.source.execute(connection, validated.sql, validated.parameters)
                columns = self.source.cursor_columns(cursor)

                def row_iterator() -> Iterator[tuple[Any, ...]]:
                    while batch := cursor.fetchmany(1_000):
                        for row in batch:
                            yield tuple(row)

                yield columns, row_iterator()
                self.source.clear_deadline(connection)
        except Exception as error:
            lowered = str(error).lower()
            if "interrupted" in lowered or "timeout" in lowered:
                raise SQLValidationError("完整结果导出时间超过安全限制。") from error
            raise SQLValidationError("完整结果无法从当前数据源导出。") from error
