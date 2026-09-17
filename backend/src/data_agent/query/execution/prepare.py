"""执行前准备：改写候选 SQL，并让每一条都先过同一套安全校验。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .guard import SQLGuard, SQLValidationError, ValidatedSQL
from .rewrites import (
    contains_match_variant,
    exact_match_variant,
    is_aggregate_sql,
    matching_row_sql,
)


@dataclass(frozen=True)
class PreparedQuery:
    """已通过安全校验、可供执行器直接使用的查询候选。"""

    fallback: ValidatedSQL
    exact: ValidatedSQL | None = None
    existence_probe: ValidatedSQL | None = None
    exact_needs_probe: bool = False


def prepare_executable_query(
    guard: SQLGuard,
    sql: str,
    parameters: tuple[Any, ...],
    requested_limit: int,
    dialect: str = "sqlite",
) -> PreparedQuery:
    """改写匹配变体后逐条校验；过不了的变体直接丢掉，不找模型修复。"""

    contains = contains_match_variant(sql, parameters)
    fallback_sql, fallback_parameters = contains or (sql, parameters)
    fallback = guard.validate(
        fallback_sql,
        fallback_parameters,
        requested_limit=requested_limit,
    )
    exact_raw = exact_match_variant(fallback_sql, fallback_parameters)
    if exact_raw is None:
        return PreparedQuery(fallback=fallback)

    try:
        exact = guard.validate(
            *exact_raw,
            requested_limit=requested_limit,
        )
    except SQLValidationError:
        return PreparedQuery(fallback=fallback)

    needs_probe = is_aggregate_sql(exact.base_sql, dialect)
    probe: ValidatedSQL | None = None
    if needs_probe:
        probe_sql = matching_row_sql(exact.base_sql, dialect)
        if probe_sql is not None:
            try:
                probe = guard.validate(
                    probe_sql,
                    exact.parameters,
                    requested_limit=1,
                    preserve_query_limit=True,
                )
            except SQLValidationError:
                probe = None
    return PreparedQuery(
        fallback=fallback,
        exact=exact,
        existence_probe=probe,
        exact_needs_probe=needs_probe,
    )
