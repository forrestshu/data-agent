"""数据查询 Agent：用语义层约束 Text-to-SQL，并基于真实结果回答。"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from pydantic import ConfigDict, Field, field_validator

from data_agent.knowledge.semantic_catalog import SemanticCatalog
from data_agent.database import DatabaseSource
from data_agent.query.execution.executor import QueryResult
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


logger = logging.getLogger(__name__)


class IntentAnalysis(PlanningAnalysis):
    """模型输出契约：ready 时写 SQL，否则追问或说明语义层无法回答。"""

    model_config = ConfigDict(extra="ignore")
    confidence: float = Field(default=0.8, ge=0, le=1)
    intent_summary: str = "执行数据查询"

    @field_validator("intent_summary", mode="before")
    @classmethod
    def normalize_text(cls, value: Any, info: Any) -> str:
        """容错层：说明字段为空不影响 SQL 安全，使用可解释默认文案。"""

        if value is not None and str(value).strip():
            return str(value).strip()
        return "执行数据查询"


@dataclass(frozen=True)
class AITrace:
    """可解释状态：公开查询结论摘要，不暴露或伪造模型隐藏思维链。"""

    provider: str
    model: str
    mode: str
    intent_summary: str
    confidence: float
    route_reason: str


@dataclass(frozen=True)
class QueryUnderstanding:
    """理解层输出：只携带已通过 SQL Guard 的模型查询计划。"""

    effective_question: str
    route: RouteDecision
    generated_sql: str
    sql_parameters: tuple[Any, ...]
    source_views: tuple[str, ...]
    assumptions: tuple[str, ...]
    display_units: dict[str, str]
    trace: AITrace


class AgentClarificationRequired(ValueError):
    """对话中断：模型判断业务含义不足时，把一个具体问题交给前端。"""

    def __init__(self, analysis: IntentAnalysis, provider: str, model: str) -> None:
        self.analysis = analysis
        self.provider = provider
        self.model = model
        super().__init__(analysis.clarification_question or "请补充要查询的业务对象、指标或范围。")


class SQLGenerationError(ValueError):
    """生成边界异常：模型连续两次不能产生可安全执行的语义层约束 SQL。"""


class AgentUnsupportedQuery(SQLGenerationError):
    """能力边界：现有语义层确实缺少回答问题所需的字段或安全关系。"""


class DataQueryAgent:
    """查询 Agent：模型负责理解和写 SQL，语义层与 AST 守卫负责事实和安全。"""

    def __init__(
        self,
        catalog: SemanticCatalog,
        llm_client: LLMClient | None,
        database_profile: dict[str, Any] | None = None,
        source: DatabaseSource | None = None,
        sql_guard: SQLGuard | None = None,
    ) -> None:
        """装配 Agent；知识画像约束 SQLite 查询范围。

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
        """提示构建：只发送视图用途、粒度、字段含义和极简关联，不发送业务行。"""

        return build_semantic_context(self.catalog)

    def _system_prompt(self) -> str:
        """返回 Text-to-SQL 指令与包含字段描述的紧凑语义卡片。"""

        dialect = "SQL Server T-SQL" if self.source and self.source.dialect == "tsql" else "SQLite"
        limit_rule = "TOP (N)" if dialect.startswith("SQL Server") else "LIMIT N"
        return load_prompt(
            "text_to_sql.md",
            knowledge_context=self._knowledge_context(),
            database_dialect=dialect,
            limit_rule=limit_rule,
        )

    @staticmethod
    def _parse_analysis(payload: dict[str, Any]) -> IntentAnalysis:
        """协议解析：优先保留完整解释；辅助字段异常时退回最小可执行 JSON 外壳。"""

        return parse_planning_payload(
            IntentAnalysis,
            payload,
            common_keys={
                "status",
                "intent_summary",
                "route_reason",
                "matched_concepts",
                "assumptions",
                "source_views",
            },
            ready_keys={
                "sql",
                "parameters",
                "display_units",
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
        analysis: IntentAnalysis,
        limit: int,
        effective_question: str,
    ) -> IntentAnalysis:
        """安全校验：只走 Guard，并从 AST 回填真实视图，不改写模型 SQL。"""

        if analysis.sql is None or not analysis.sql.strip():
            raise SQLValidationError("ready 状态必须提供 SQL。")
        validated = self.sql_guard.validate(
            analysis.sql,
            analysis.parameters,
            requested_limit=limit,
            # 是否限量属于用户语义，不能信任模型自报；只根据原问题中的明确表达判断。
            preserve_query_limit=self._question_requests_limit(effective_question),
        )
        # 只信任 Guard 从 AST 提取的真实视图，不信任模型自报。
        analysis.source_views = list(validated.source_views)
        # 编排层向执行器传递完整安全 SQL；500 行预览只应在执行器最后一跳添加一次。
        analysis.sql = validated.base_sql
        analysis.parameters = list(validated.parameters)
        return analysis

    @staticmethod
    def _question_requests_limit(question: str) -> bool:
        """语义兜底：用户明确说前几条、Top N 或只要 N 条时才保留模型 LIMIT。"""

        patterns = (
            r"前\s*[一二三四五六七八九十百千\d]+\s*(?:条|个|名)",
            r"top\s*\d+",
            r"(?:只要|最多|返回)\s*[一二三四五六七八九十百千\d]+\s*(?:条|个|名)",
            r"(?:最高|最低|最新|最早|第一|最后)\s*(?:的)?\s*(?:一条|一个|一名)?",
        )
        normalized = question.casefold()
        return any(re.search(pattern, normalized) for pattern in patterns)

    @staticmethod
    def _repeats_clarification(candidate: str | None, previous: tuple[str, ...]) -> bool:
        """对话守卫：阻止模型再次询问用户已经回答过的同一信息。"""

        if not candidate:
            return False
        normalized = "".join(character for character in candidate if character.isalnum())
        for item in previous:
            old = "".join(character for character in item if character.isalnum())
            if normalized == old or SequenceMatcher(None, normalized, old).ratio() >= 0.78:
                return True
        return False

    @staticmethod
    def _label_terms(label: str) -> set[str]:
        """把字段中文名展开成可与用户问法对齐的短词，例如供应商名称 → 供应商。"""

        terms = {label}
        for suffix in ("名称", "编码", "编号", "数量", "金额"):
            if label.endswith(suffix) and len(label) > len(suffix):
                terms.add(label[: -len(suffix)])
        return {term for term in terms if len(term) >= 2}

    def _single_view_covering_question(
        self,
        analysis: IntentAnalysis,
        question: str,
    ) -> str | None:
        """模型已点名视图时，若其中恰好一张能覆盖问题中的输出和筛选线索，就不应再追问。"""

        named = [name for name in analysis.source_views if name]
        if not named or not question.strip():
            return None
        catalog_names = {view.name for view in self.catalog.views}
        candidates: list[str] = []
        for view in self.catalog.views:
            if view.name not in named or view.name not in catalog_names:
                continue
            output_terms = {
                term
                for name in view.output_columns
                for term in self._label_terms(
                    str(view.column_semantics.get(name, {}).get("business_name", "")).strip()
                )
            }
            filter_labels = [
                str(view.column_semantics.get(name, {}).get("business_name", "")).strip()
                for name in view.filter_columns
            ]
            wants_output = any(term in question for term in output_terms)
            has_filter_cue = any(
                label and (label in question or any(token in question for token in ("描述", "名称", "编码", "号")))
                for label in filter_labels
            )
            if wants_output and has_filter_cue:
                candidates.append(view.name)
        if len(candidates) == 1:
            return candidates[0]
        return None

    def _clarification_issue(
        self,
        analysis: IntentAnalysis,
        question: str,
    ) -> str | None:
        """编排守卫：只允许“不补一句就无法选视图”的追问，其它应直接写 SQL。"""

        if analysis.status != "clarification_required":
            return None
        asked = (analysis.clarification_question or "").strip()
        if not asked:
            return "clarification_required 必须提供一个具体追问。"
        if re.search(r"(描述|编码|料号).{0,12}(还是|或).{0,12}(描述|编码|料号)", asked):
            return "用户未明确说编码或料号时，文本应按描述筛选并生成 SQL，不得追问是描述还是编码。"
        if re.search(
            r"DISTINCT|是否聚合|要不要分组|是否分组|公司代码|按公司区分|阈值",
            asked,
            re.IGNORECASE,
        ):
            return "不要为 DISTINCT、聚合、分组、公司范围或阈值追问；把默认口径写入 assumptions 并生成 SQL。"
        covering_view = self._single_view_covering_question(analysis, question)
        if covering_view is not None:
            return (
                f"单个视图 {covering_view} 已能覆盖当前问题；"
                "不得继续追问，应生成单视图 SQL。"
            )
        answer_ask = re.search(r"哪个([^？?，,。]{1,12})", asked)
        if answer_ask:
            target = answer_ask.group(1).strip()
            if target and target in question:
                return (
                    f"追问正在向用户索要本应由数据库返回的结果：{target}。"
                    "应生成 SELECT，而不是继续追问。"
                )
        return None

    def _unsupported_issue(self, analysis: IntentAnalysis) -> str | None:
        """能力守卫：模型点名了已收录视图时，不得把问题报成语义层不支持。"""

        if analysis.status != "unsupported":
            return None
        known = [
            name
            for name in analysis.source_views
            if any(view.name == name for view in self.catalog.views)
        ]
        if not known:
            return None
        return (
            f"语义层已包含 {known[0]} 等可用视图；"
            "当前语义层能够回答，不得返回 unsupported，应生成 SQL。"
        )

    def _refine_analysis(
        self,
        analysis: IntentAnalysis,
        repair: RepairFn,
        previous_clarifications: tuple[str, ...],
        question: str,
    ) -> IntentAnalysis:
        """查询专用 refine：复核误报不支持、重复追问和无效澄清。"""

        unsupported_issue = self._unsupported_issue(analysis)
        if unsupported_issue is not None:
            logger.warning("模型误报语义层不支持，尝试自动修复：%s", unsupported_issue)
            analysis = repair(analysis.model_dump(), unsupported_issue)
            if analysis.status == "unsupported":
                raise SQLGenerationError("模型连续两次误报当前语义层不支持该查询。")

        if analysis.status == "clarification_required" and self._repeats_clarification(
            analysis.clarification_question,
            previous_clarifications,
        ):
            logger.warning("模型重复询问已回答信息，尝试自动修复一次")
            analysis = repair(analysis.model_dump(), "REPEATED_CLARIFICATION")
            if analysis.status == "clarification_required" and self._repeats_clarification(
                analysis.clarification_question,
                previous_clarifications,
            ):
                raise SQLGenerationError("模型连续重复询问用户已经回答的信息。")

        clarification_issue = self._clarification_issue(analysis, question)
        if clarification_issue is not None:
            logger.warning("模型提出了无效追问，尝试自动修复：%s", clarification_issue)
            analysis = repair(analysis.model_dump(), clarification_issue)
            repaired_issue = self._clarification_issue(analysis, question)
            if repaired_issue is not None:
                raise SQLGenerationError("模型连续两次提出无法由语义层支持的追问。")
        return analysis

    def _analyze_with_ai(
        self,
        question: str,
        limit: int,
        previous_clarifications: tuple[str, ...] = (),
    ) -> IntentAnalysis:
        """生成入口：走共享规划骨架，澄清策略由 refine 钩子保留。"""

        def validate_ready(analysis: IntentAnalysis) -> IntentAnalysis:
            return self._validate_ready(analysis, limit, question)

        def refine(analysis: IntentAnalysis, repair: RepairFn) -> IntentAnalysis:
            return self._refine_analysis(analysis, repair, previous_clarifications, question)

        return plan_with_ai(
            llm_client=self.llm_client,
            system_prompt=self._system_prompt(),
            question=question,
            parser=self._parse_analysis,
            validate_ready=validate_ready,
            error_factory=SQLGenerationError,
            label="Text-to-SQL",
            max_tokens=2200,
            # ERP100 实测已证明：第一次 Guard 反馈后模型仍可能保留同一语义错误。
            # 第二次仍走同一验证 Seam，不放宽安全规则。
            max_sql_repairs=2,
            contract_issue="INVALID_JSON_CONTRACT",
            refine=refine,
        )

    def understand(
        self,
        question: str,
        confirmed_view: str | None = None,
        clarification_answer: str | None = None,
        clarification_history: tuple[tuple[str, str], ...] = (),
        limit: int = 500,
    ) -> QueryUnderstanding:
        """理解入口：合并多轮补充，生成并验证 SQL；只有无法选择视图时才追问。"""

        merged_question = effective_question(
            question,
            clarification_answer,
            clarification_history,
            confirmed_view,
        )
        analysis = self._analyze_with_ai(
            merged_question,
            limit,
            previous_clarifications=tuple(item[0] for item in clarification_history),
        )

        assert self.llm_client is not None
        if analysis.status == "clarification_required":
            raise AgentClarificationRequired(
                analysis,
                provider=self.llm_client.provider,
                model=self.llm_client.model,
            )
        if analysis.status == "unsupported":
            raise AgentUnsupportedQuery(analysis.route_reason)
        assert analysis.sql is not None
        assert analysis.source_views

        primary_view = analysis.source_views[0]
        route = RouteDecision(
            view_name=primary_view,
            confidence=analysis.confidence,
            reason=analysis.route_reason,
            matched_terms=tuple(analysis.matched_concepts),
            alternatives=tuple(analysis.source_views[1:]),
            match_type="ai" if confirmed_view is None else "confirmed",
            requires_confirmation=False,
            confirmation_question=None,
        )
        return QueryUnderstanding(
            effective_question=merged_question,
            route=route,
            generated_sql=analysis.sql,
            sql_parameters=tuple(analysis.parameters),
            source_views=tuple(analysis.source_views),
            assumptions=tuple(analysis.assumptions),
            display_units=dict(analysis.display_units),
            trace=AITrace(
                provider=self.llm_client.provider,
                model=self.llm_client.model,
                mode="text_to_sql",
                intent_summary=analysis.intent_summary,
                confidence=analysis.confidence,
                route_reason=analysis.route_reason,
            ),
        )

    def answer(self, original_question: str, result: QueryResult) -> tuple[str, bool]:
        """回答层：只把有限查询结果和质量提示交给模型，不让 SQL 文本改变回答事实。"""

        if self.llm_client is None:
            raise LLMUnavailable("DeepSeek 未配置，无法生成客户回答。")
        evidence = {
            "source_views": list(result.plan.source_views or (result.plan.view_name,)),
            "rows": list(result.rows),
            "notices": list(result.notices),
            "total_count": result.total_count,
            "displayed_count": len(result.rows),
            "has_more": result.has_more,
        }
        system_prompt = load_prompt("answer.md")
        user_prompt = json.dumps(
            {"用户问题": original_question, "数据依据": evidence},
            ensure_ascii=False,
            default=str,
        )
        try:
            answer = self.llm_client.complete_text(
                system_prompt,
                user_prompt,
                max_tokens=1000,
            )
            return answer, True
        except LLMUnavailable:
            raise
