"""查询运行时：集中装配知识、规划 Agent、只读执行和结果表达。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agents.data_query import DataQueryAgent, QueryUnderstanding
from data_agent.knowledge.catalog import KnowledgeCatalog, load_catalog
from data_agent.knowledge.profile import assert_view_ready
from .dashboard_view import DashboardPayload, build_query_dashboard
from .agents.dashboard import DashboardAgent, DashboardUnderstanding
from data_agent.database import Database
from .execution.executor import QueryResult, ReadOnlyQueryService
from data_agent.llm import LLMClient, LLMUnavailable
from .contracts import RouteConfirmationRequired


@dataclass(frozen=True)
class QueryOutcome:
    understanding: QueryUnderstanding
    result: QueryResult
    answer: str
    answer_generated_by_ai: bool


@dataclass(frozen=True)
class DashboardQueryOutcome:
    understanding: DashboardUnderstanding
    result: QueryResult
    dashboard: DashboardPayload


class QueryRuntime:
    """一个活动数据源的一次查询上下文，隐藏重复装配和就绪检查。"""

    def __init__(
        self,
        source: Database,
        profile: dict[str, Any],
        catalog: KnowledgeCatalog,
        llm: LLMClient,
    ) -> None:
        self.source = source
        self.profile = profile
        self.catalog = catalog
        self.llm = llm
        self.executor = ReadOnlyQueryService(source, catalog, database_profile=profile)

    @classmethod
    def prepare(
        cls,
        source: Database,
        profile: dict[str, Any],
        llm: LLMClient | None,
    ) -> "QueryRuntime":
        if llm is None:
            raise LLMUnavailable("DeepSeek 尚未配置，查询必须使用 AI 规划。")
        return cls(
            source,
            profile,
            load_catalog(),
            llm,
        )

    def _assert_views(self, source_views: tuple[str, ...]) -> None:
        for view in source_views:
            assert_view_ready(self.profile, view)

    def execute_query(
        self,
        question: str,
        *,
        confirmed_view: str | None,
        clarification_answer: str | None,
        clarification_history: tuple[tuple[str, str], ...],
        limit: int,
    ) -> QueryOutcome:
        agent = DataQueryAgent(
            self.catalog,
            self.llm,
            database_profile=self.profile,
            source=self.source,
        )
        understanding = agent.understand(
            question,
            confirmed_view=confirmed_view,
            clarification_answer=clarification_answer,
            clarification_history=clarification_history,
            limit=limit,
        )
        if understanding.route.requires_confirmation:
            raise RouteConfirmationRequired(understanding.route)
        self._assert_views(understanding.source_views)
        result = self.executor.ask_generated_sql(
            understanding.effective_question,
            understanding.generated_sql,
            understanding.sql_parameters,
            route_decision=understanding.route,
            limit=limit,
        )
        result = agent.localize_result_columns(understanding.effective_question, result)
        answer, generated = agent.answer(understanding.effective_question, result)
        return QueryOutcome(understanding, result, answer, generated)

    def execute_dashboard(
        self,
        question: str,
        *,
        confirmed_view: str | None,
        clarification_answer: str | None,
        clarification_history: tuple[tuple[str, str], ...],
        limit: int,
    ) -> DashboardQueryOutcome:
        agent = DashboardAgent(
            self.catalog,
            self.llm,
            database_profile=self.profile,
            source=self.source,
        )
        understanding = agent.understand(
            question,
            confirmed_view=confirmed_view,
            clarification_answer=clarification_answer,
            clarification_history=clarification_history,
            limit=limit,
        )
        self._assert_views(understanding.source_views)
        result = self.executor.ask_generated_sql(
            understanding.effective_question,
            understanding.generated_sql,
            understanding.sql_parameters,
            route_decision=understanding.route,
            limit=limit,
        )
        result = agent.localize_result_columns(understanding.effective_question, result)
        dashboard = build_query_dashboard(
            understanding.effective_question,
            result,
            original_question=question,
            intent_summary=understanding.trace.intent_summary,
            route_reason=understanding.trace.route_reason,
            display_units=understanding.display_units,
            dashboard_title=understanding.title,
            dashboard_summary=understanding.summary,
            visualization_hint=understanding.visualization,
            preferred_dimensions=understanding.dimension_columns,
            preferred_metrics=understanding.metric_columns,
        )
        return DashboardQueryOutcome(understanding, result, dashboard)
