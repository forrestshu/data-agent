"""Dashboard Agent：理解概况问题、验证只读 SQL，并交给图表层渲染。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import Field, field_validator

from data_agent.knowledge.semantic_catalog import SemanticCatalog
from data_agent.database import Database
from data_agent.llm import LLMClient, LLMUnavailable
from data_agent.knowledge.prompt import build_semantic_context, load_prompt
from .planning import (
    PlanningAnalysis,
    RepairFn,
    effective_question,
    parse_planning_payload,
    plan_with_ai,
)
from data_agent.query.contracts import RouteDecision
from data_agent.query.execution.guard import SQLGuard, SQLValidationError

class DashboardAnalysis(PlanningAnalysis):
    """Dashboard 模型输出：描述概况口径、验证 SQL 和可视化偏好。"""

    title: str = "业务数据概况"
    summary: str = "按当前问题从已审核数据中生成概况。"
    visualization: Literal["auto", "ranking", "breakdown", "trend", "metric", "table"] = "auto"
    dimension_columns: list[str] = Field(default_factory=list)
    metric_columns: list[str] = Field(default_factory=list)

    @field_validator("dimension_columns", "metric_columns", mode="before")
    @classmethod
    def normalize_dashboard_string_list(cls, value: Any) -> list[str]:
        """协议容错：把 null、单字符串或异常对象归一化为字符串数组。"""

        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    @field_validator("title", "summary", mode="before")
    @classmethod
    def normalize_text(cls, value: Any, info: Any) -> str:
        """协议容错：说明字段为空时使用不会伪造事实的默认文案。"""

        if value is not None and str(value).strip():
            return str(value).strip()
        defaults = {
            "title": "业务数据概况",
            "summary": "按当前问题从已审核数据中生成概况。",
        }
        return defaults[info.field_name]


@dataclass(frozen=True)
class DashboardTrace:
    """可解释状态：记录 Dashboard 使用的模型模式和概况口径。"""

    provider: str
    model: str
    mode: str
    intent_summary: str
    confidence: float
    route_reason: str


@dataclass(frozen=True)
class DashboardUnderstanding:
    """Dashboard 理解结果：携带已通过 SQL Guard 的完整只读 SQL。"""

    effective_question: str
    route: RouteDecision
    generated_sql: str
    sql_parameters: tuple[Any, ...]
    source_views: tuple[str, ...]
    assumptions: tuple[str, ...]
    display_units: dict[str, str]
    title: str
    summary: str
    visualization: str
    dimension_columns: tuple[str, ...]
    metric_columns: tuple[str, ...]
    trace: DashboardTrace


class DashboardClarificationRequired(ValueError):
    """Dashboard 只有在无法选择安全数据对象时才把问题交给前端补充。"""

    def __init__(self, analysis: DashboardAnalysis, provider: str, model: str) -> None:
        self.analysis = analysis
        self.provider = provider
        self.model = model
        super().__init__(analysis.clarification_question or "请补充希望观察的业务范围。")


class DashboardPlanningError(ValueError):
    """Dashboard 计划异常：模型没有形成可验证的概况查询。"""


class DashboardUnsupportedQuery(DashboardPlanningError):
    """语义层确实没有可验证的数据对象，而不是模型计划或 SQL 校验失败。"""


class DashboardAgent:
    """Dashboard Agent：专注概况探索，不复用数据查询的意图与回答提示词。"""

    def __init__(
        self,
        catalog: SemanticCatalog,
        llm_client: LLMClient | None,
        database_profile: dict[str, Any] | None = None,
        source: Database | None = None,
        sql_guard: SQLGuard | None = None,
    ) -> None:
        """装配概况 Agent；安全目录和数据库画像约束 SQLite 查询。

        sql_guard 应与执行器共用同一实例；未注入时仅便于单测自行构造。
        """

        self.catalog = catalog
        self.llm_client = llm_client
        self.database_profile = database_profile or {}
        self.source = source
        self.sql_guard = sql_guard or SQLGuard(
            catalog,
            self.database_profile,
            source=source,
        )

    def _knowledge_context(self) -> str:
        """提示构建：只传递已审核语义的紧凑投影，不把完整治理资产重复发送。"""

        return build_semantic_context(self.catalog)

    def _system_prompt(self) -> str:
        """Dashboard 专用提示：允许概况推断，但要求所有数字经过数据库验证。"""

        return load_prompt("dashboard.md", knowledge_context=self._knowledge_context())

    @staticmethod
    def _parse_analysis(payload: dict[str, Any]) -> DashboardAnalysis:
        """协议解析：保留完整概况字段；失败时只保留可修复的核心字段。"""

        return parse_planning_payload(
            DashboardAnalysis,
            payload,
            common_keys={
                "status",
                "confidence",
                "title",
                "summary",
                "route_reason",
                "matched_concepts",
                "source_views",
                "assumptions",
            },
            ready_keys={
                "sql",
                "parameters",
                "display_units",
                "visualization",
                "dimension_columns",
                "metric_columns",
            },
            clarification_keys={
                "clarification_question",
                "clarification_kind",
                "clarification_options",
                "clarification_unit",
            },
        )

    def _validate_ready(
        self,
        analysis: DashboardAnalysis,
        limit: int,
    ) -> DashboardAnalysis:
        """SQL 校验：把模型逻辑 SQL 转成固定物理范围，并回填真实视图。"""

        if analysis.sql is None or not analysis.sql.strip():
            raise SQLValidationError("Dashboard ready 状态必须提供 SQL。")
        validated = self.sql_guard.validate(
            analysis.sql,
            analysis.parameters,
            requested_limit=limit,
            # Dashboard 规划器可以主动选择前几项，保留其概况语义上的 LIMIT/TOP。
            preserve_query_limit=True,
        )
        analysis.sql = validated.base_sql
        analysis.parameters = list(validated.parameters)
        analysis.source_views = list(validated.source_views)
        return analysis

    @staticmethod
    def _refine_analysis(analysis: DashboardAnalysis, repair: RepairFn) -> DashboardAnalysis:
        """Dashboard 专用 refine：业务可查时不把 unsupported 当真终态。"""

        if analysis.status == "unsupported":
            return repair(
                analysis.model_dump(),
                "UNSUPPORTED_WITH_AVAILABLE_SEMANTICS",
            )
        return analysis

    def _analyze_with_ai(self, question: str, limit: int) -> DashboardAnalysis:
        """模型入口：走共享规划骨架，概况差异由 refine 与修复次数保留。"""

        def validate_ready(analysis: DashboardAnalysis) -> DashboardAnalysis:
            return self._validate_ready(analysis, limit)

        return plan_with_ai(
            llm_client=self.llm_client,
            system_prompt=self._system_prompt(),
            question=question,
            parser=self._parse_analysis,
            validate_ready=validate_ready,
            error_factory=DashboardPlanningError,
            label="Dashboard",
            max_tokens=2400,
            max_sql_repairs=2,
            contract_issue="INVALID_DASHBOARD_JSON_CONTRACT",
            refine=self._refine_analysis,
        )
    @staticmethod
    def _known_business_ambiguity(question: str) -> DashboardAnalysis | None:
        """在调用模型前拦截已知的跨业务对象歧义，避免模型猜测或误报不支持。"""

        normalized = re.sub(r"\s+", "", question.casefold())
        if "订单" not in normalized or "工单" in normalized:
            return None

        sales_markers = ("销售订单", "销售单", "订单金额", "发货", "退货", "红票", "客户采购订单")
        purchase_markers = ("采购订单", "采购单", "供应商", "收货", "在检", "采购进度")
        has_sales_scope = any(marker in normalized for marker in sales_markers)
        # “客户采购订单”是销售订单视图里的客户侧 PO 号，不能因包含“采购订单”四字
        # 被同时误判为公司采购订单。
        purchase_context = normalized.replace("客户采购订单", "")
        has_purchase_scope = any(marker in purchase_context for marker in purchase_markers)
        if has_sales_scope != has_purchase_scope:
            return None
        if has_sales_scope and has_purchase_scope:
            reason = "问题同时包含销售订单和采购订单语义，需要确认统计范围"
        else:
            reason = "当前语义层同时包含销售订单和采购订单，单独说订单无法确定统计口径"
        return DashboardAnalysis(
            status="clarification_required",
            confidence=0.98,
            title="订单范围确认",
            summary="确认订单业务类型后再从对应视图统计并展示。",
            route_reason=reason,
            clarification_question="你想统计销售订单还是采购订单？",
            clarification_kind="choice",
            clarification_options=["销售订单", "采购订单"],
            matched_concepts=["订单", "订单数量"],
        )

    @staticmethod
    def _effective_question(
        question: str,
        clarification_answer: str | None,
        clarification_history: tuple[tuple[str, str], ...],
        confirmed_view: str | None,
    ) -> str:
        """对话状态层：把已回答信息和用户确认的视图作为本轮概况输入。"""

        return effective_question(
            question,
            clarification_answer,
            clarification_history,
            confirmed_view,
        )

    def understand(
        self,
        question: str,
        confirmed_view: str | None = None,
        clarification_answer: str | None = None,
        clarification_history: tuple[tuple[str, str], ...] = (),
        limit: int = 100,
    ) -> DashboardUnderstanding:
        """理解入口：概况不按置信度弹确认，只有真正无法安全规划时才追问。"""

        effective_question = self._effective_question(
            question,
            clarification_answer,
            clarification_history,
            confirmed_view,
        )
        known_ambiguity = self._known_business_ambiguity(effective_question)
        if known_ambiguity is not None:
            if self.llm_client is None:
                raise LLMUnavailable("DeepSeek 未配置。")
            provider = self.llm_client.provider
            model = self.llm_client.model
            raise DashboardClarificationRequired(known_ambiguity, provider, model)
        analysis = self._analyze_with_ai(effective_question, limit)

        if analysis.status == "clarification_required":
            assert self.llm_client is not None
            provider = self.llm_client.provider
            model = self.llm_client.model
            raise DashboardClarificationRequired(analysis, provider, model)
        if analysis.status == "unsupported":
            raise DashboardUnsupportedQuery(analysis.route_reason)
        if not analysis.sql or not analysis.source_views:
            raise DashboardPlanningError("Dashboard 概况计划缺少已验证 SQL 或数据对象。")

        primary_view = analysis.source_views[0]
        route = RouteDecision(
            view_name=primary_view,
            confidence=analysis.confidence,
            reason=analysis.route_reason,
            matched_terms=tuple(analysis.matched_concepts),
            alternatives=tuple(analysis.source_views[1:]),
            # Dashboard 允许模型自动选择最相关视图，不沿用数据查询的低置信度确认停顿。
            match_type="confirmed" if confirmed_view else "ai",
            requires_confirmation=False,
            confirmation_question=None,
        )
        assert self.llm_client is not None
        provider = self.llm_client.provider
        model = self.llm_client.model
        return DashboardUnderstanding(
            effective_question=effective_question,
            route=route,
            generated_sql=analysis.sql,
            sql_parameters=tuple(analysis.parameters),
            source_views=tuple(analysis.source_views),
            assumptions=tuple(analysis.assumptions),
            display_units=dict(analysis.display_units),
            title=analysis.title,
            summary=analysis.summary,
            visualization=analysis.visualization,
            dimension_columns=tuple(analysis.dimension_columns),
            metric_columns=tuple(analysis.metric_columns),
            trace=DashboardTrace(
                provider=provider,
                model=model,
                mode="dashboard_overview",
                intent_summary=analysis.title,
                confidence=analysis.confidence,
                route_reason=analysis.route_reason,
            ),
        )
