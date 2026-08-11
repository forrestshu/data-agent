"""查询运行时：集中装配知识、规划 Agent、只读执行和结果表达。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from typing import Any

from .agents.data_query import DataQueryAgent, QueryUnderstanding
from data_agent.knowledge.semantic_catalog import SemanticCatalog, load_semantic_catalog
from data_agent.knowledge.prompt import load_prompt
from .dashboard_builder import DashboardPayload, build_query_dashboard
from .agents.dashboard import DashboardAgent, DashboardUnderstanding
from data_agent.database import Database
from .execution.executor import QueryResult, ReadOnlyQueryExecutor
from .execution.guard import SQLGuard
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
    """集中编排规划、只读执行、字段表达和最终回答。"""

    def __init__(
        self,
        source: Database,
        profile: dict[str, Any],
        catalog: SemanticCatalog,
        llm: LLMClient,
    ) -> None:
        self.source = source
        self.profile = profile
        self.catalog = catalog
        self.llm = llm
        # 单一安全入口：规划/repair 与执行前强制校验共用同一 Guard。
        self.sql_guard = SQLGuard(
            catalog,
            profile,
            max_rows=500,
            source=source,
        )
        self.executor = ReadOnlyQueryExecutor(
            source,
            catalog,
            database_profile=profile,
            guard=self.sql_guard,
        )

    @classmethod
    def prepare(
        cls,
        source: Database,
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

    def _localize_result_columns(
        self,
        original_question: str,
        result: QueryResult,
    ) -> QueryResult:
        """让模型只补充语义目录未覆盖的英文查询别名。"""

        if not result.rows:
            return result
        unknown = [
            column
            for column in result.rows[0]
            if result.column_labels.get(column, column) == column
            and re.search(r"[A-Za-z]", column)
        ]
        if not unknown:
            return result
        evidence = {
            "用户问题": original_question,
            "来源视图": list(result.plan.source_views or (result.plan.view_name,)),
            "待处理字段": unknown,
            "样例值": [
                {column: row.get(column) for column in unknown}
                for row in result.rows[:3]
            ],
        }
        try:
            generated = self.llm.complete_json(
                load_prompt("column_labels.md"),
                json.dumps(evidence, ensure_ascii=False, default=str),
                max_tokens=400,
            )
        except LLMUnavailable:
            return result
        proposed = generated.get("column_labels")
        if not isinstance(proposed, dict):
            return result
        translated = dict(result.column_labels)
        for column in unknown:
            label = proposed.get(column)
            if not isinstance(label, str):
                continue
            label = label.strip()
            if 2 <= len(label) <= 10 and re.search(r"[\u4e00-\u9fff]", label):
                translated[column] = label
        return replace(result, column_labels=translated)

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
        result = self.executor.execute_generated_sql(
            understanding.effective_question,
            understanding.generated_sql,
            understanding.sql_parameters,
            route_decision=understanding.route,
            limit=limit,
        )
        result = self._localize_result_columns(understanding.effective_question, result)
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
        result = self.executor.execute_generated_sql(
            understanding.effective_question,
            understanding.generated_sql,
            understanding.sql_parameters,
            route_decision=understanding.route,
            limit=limit,
        )
        result = self._localize_result_columns(understanding.effective_question, result)
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
