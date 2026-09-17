"""查询运行时：集中装配知识、规划 Agent、安全校验后执行和结果表达。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .agents.data_query import DataQueryAgent, QueryUnderstanding
from data_agent.knowledge.semantic_catalog import SemanticCatalog, load_semantic_catalog
from .dashboard_builder import DashboardPayload, build_query_dashboard
from .agents.dashboard import DashboardAgent, DashboardUnderstanding
from data_agent.database import DatabaseSource
from .execution.executor import QueryResult, QueryExecutor
from .execution.guard import SQLGuard
from .execution.prepare import prepare_executable_query
from data_agent.llm import LLMClient, LLMUnavailable
from .contracts import RouteConfirmationRequired


@dataclass(frozen=True)
class DataQueryOutcome:
    understanding: QueryUnderstanding
    result: QueryResult
    answer: str
    answer_generated_by_ai: bool


@dataclass(frozen=True)
class DashboardQueryOutcome:
    understanding: DashboardUnderstanding
    result: QueryResult
    dashboard: DashboardPayload


class QueryWorkflow:
    """集中编排规划、安全校验后执行、字段表达和最终回答。"""

    def __init__(
        self,
        source: DatabaseSource,
        profile: dict[str, Any],
        catalog: SemanticCatalog,
        llm: LLMClient,
    ) -> None:
        self.source = source
        self.profile = profile
        self.catalog = catalog
        self.llm = llm
        # 规划 repair 与执行前准备共用同一 Guard；执行器只收已校验 SQL。
        self.sql_guard = SQLGuard(
            catalog,
            profile,
            max_rows=500,
            source=source,
        )
        self.executor = QueryExecutor(
            source,
            catalog,
            database_profile=profile,
        )

    @classmethod
    def prepare(
        cls,
        source: DatabaseSource,
        profile: dict[str, Any],
        llm: LLMClient | None,
    ) -> "QueryWorkflow":
        if llm is None:
            raise LLMUnavailable("DeepSeek 尚未配置，查询必须使用 AI 规划。")
        return cls(
            source,
            profile,
            load_semantic_catalog(),
            llm,
        )

    def execute_query(
        self,
        question: str,
        *,
        confirmed_view: str | None,
        clarification_answer: str | None,
        clarification_history: tuple[tuple[str, str], ...],
        limit: int,
    ) -> DataQueryOutcome:
        agent = DataQueryAgent(
            self.catalog,
            self.llm,
            database_profile=self.profile,
            source=self.source,
            sql_guard=self.sql_guard,
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
        result = self.executor.execute_validated(
            understanding.effective_question,
            prepare_executable_query(
                self.sql_guard,
                understanding.generated_sql,
                understanding.sql_parameters,
                limit,
                dialect=self.source.dialect,
            ),
            understanding.route,
        )
        answer, generated = agent.answer(understanding.effective_question, result)
        return DataQueryOutcome(understanding, result, answer, generated)

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
            sql_guard=self.sql_guard,
        )
        understanding = agent.understand(
            question,
            confirmed_view=confirmed_view,
            clarification_answer=clarification_answer,
            clarification_history=clarification_history,
            limit=limit,
        )
        result = self.executor.execute_validated(
            understanding.effective_question,
            prepare_executable_query(
                self.sql_guard,
                understanding.generated_sql,
                understanding.sql_parameters,
                limit,
                dialect=self.source.dialect,
            ),
            understanding.route,
        )
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
