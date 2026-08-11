"""数据查询 Agent：用语义层约束 Text-to-SQL，并基于真实结果回答。"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from pydantic import BaseModel, Field, field_validator
from sqlglot import exp, parse_one

from data_agent.knowledge.semantic_catalog import SemanticCatalog
from data_agent.database import Database
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


class QueryConstraint(BaseModel):
    """理解层结构：记录用户已经提供的筛选字段、操作符和值，供后端核验追问是否多余。"""

    column: str = Field(min_length=1, max_length=100)
    operator: str = "other"
    value: Any = None

    @field_validator("operator", mode="before")
    @classmethod
    def normalize_operator(cls, value: Any) -> str:
        """协议容错层：辅助操作符允许模型使用 SQL/英文写法，统一后不参与安全决策。"""

        normalized = str(value or "other").strip().casefold()
        aliases = {
            "=": "eq",
            "==": "eq",
            "equals": "eq",
            "equal": "eq",
            "like": "contains",
            "ilike": "contains",
            "fuzzy": "contains",
            ">": "gt",
            ">=": "gte",
            "<": "lt",
            "<=": "lte",
        }
        canonical = aliases.get(normalized, normalized)
        return canonical if canonical in {"eq", "contains", "gt", "gte", "lt", "lte", "in"} else "other"


class IntentAnalysis(PlanningAnalysis):
    """模型输出契约：支持生成 SQL、请求澄清或说明当前知识无法回答。"""

    confidence: float = Field(default=0.8, ge=0, le=1)
    intent_summary: str = "执行数据查询"
    filter_constraints: list[QueryConstraint] = Field(default_factory=list)
    requested_fields: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)

    @field_validator("filter_constraints", mode="before")
    @classmethod
    def normalize_filter_constraints(cls, value: Any) -> list[Any]:
        """协议容错层：筛选元数据只是解释线索；格式不完整时丢弃该项，不阻断正确 SQL。"""

        if isinstance(value, dict):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []
        normalized: list[Any] = []
        for item in value:
            if isinstance(item, QueryConstraint):
                normalized.append(item)
                continue
            if not isinstance(item, dict):
                continue
            column = item.get("column") or item.get("field") or item.get("name")
            if column is None or not str(column).strip():
                continue
            normalized.append(
                {
                    "column": str(column).strip(),
                    "operator": item.get("operator", item.get("op", "other")),
                    "value": item.get("value"),
                }
            )
        return normalized

    @field_validator("intent_summary", mode="before")
    @classmethod
    def normalize_text(cls, value: Any, info: Any) -> str:
        """容错层：说明字段为空不影响 SQL 安全，使用可解释默认文案。"""

        if value is not None and str(value).strip():
            return str(value).strip()
        return "执行数据查询"

    @field_validator(
        "requested_fields",
        "missing_information",
        mode="before",
    )
    @classmethod
    def normalize_string_list(cls, value: Any) -> list[str]:
        """容错层：将 null、单字符串或对象安全归一化为字符串数组。"""

        if value is None:
            return []
        if isinstance(value, dict):
            value = list(value.keys())
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []
        return [str(item) for item in value if str(item).strip()]


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


class DataQueryAgent:
    """查询 Agent：模型负责理解和写 SQL，语义层与 AST 守卫负责事实和安全。"""

    AUTO_ROUTE_THRESHOLD = 0.65

    def __init__(
        self,
        catalog: SemanticCatalog,
        llm_client: LLMClient | None,
        database_profile: dict[str, Any] | None = None,
        source: Database | None = None,
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

        return load_prompt("text_to_sql.md", knowledge_context=self._knowledge_context())

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
            },
            ready_keys={"sql", "parameters", "display_units"},
            clarification_keys={
                "clarification_question",
                "clarification_kind",
                "clarification_options",
                "clarification_unit",
                "filter_constraints",
                "requested_fields",
                "missing_information",
                "source_views",
            },
        )

    def _validate_ready(
        self,
        analysis: IntentAnalysis,
        limit: int,
        effective_question: str,
    ) -> IntentAnalysis:
        """SQL 校验：从 AST 提取真实视图并覆盖模型自报值，形成确定性执行输入。"""

        if analysis.sql is None or not analysis.sql.strip():
            raise SQLValidationError("ready 状态必须提供 SQL。")
        validated = self.sql_guard.validate(
            analysis.sql,
            analysis.parameters,
            requested_limit=limit,
            # 是否限量属于用户语义，不能信任模型自报；只根据原问题中的明确表达判断。
            preserve_query_limit=self._question_requests_limit(effective_question),
        )
        self._validate_result_shape(effective_question, validated.base_sql)
        # 编排层向执行器传递完整安全 SQL；500 行预览只应在执行器最后一跳添加一次。
        analysis.sql = validated.base_sql
        analysis.parameters = list(validated.parameters)
        analysis.source_views = list(validated.source_views)
        return analysis

    @staticmethod
    def _question_requests_grouped_result(question: str) -> bool:
        """意图兜底：识别用户明确要求按对象分别汇总的表达，避免把分组查询误判成单值。"""

        normalized = question.casefold()
        patterns = (
            r"每\s*(?:个|种|类|家|月|年|天)",
            r"各\s*(?:个|种|类|家|月|年|天)",
            r"分别",
            r"按.{1,20}(?:统计|汇总|分组|合计)",
            r"哪些.{0,20}(?:多少|数量|金额|库存)",
        )
        return any(re.search(pattern, normalized) for pattern in patterns)

    @classmethod
    def _question_requests_scalar_aggregate(cls, question: str) -> bool:
        """意图兜底：从原问题识别只应返回一行的总数或合计问题。"""

        if cls._question_requests_grouped_result(question):
            return False
        normalized = question.casefold()
        patterns = (
            r"(?:还有|现有|当前|剩余)?多少(?:库存|数量|金额|余额)",
            r"多少\s*(?:个|种|条|家)?\s*(?:物料|订单|供应商|客户)",
            r"(?:总库存|库存总量|库存合计|总金额|金额合计|数量合计|总数量)",
            r"(?:合计|总计|一共|共计).{0,12}(?:多少|是多少)?",
        )
        return any(re.search(pattern, normalized) for pattern in patterns)

    def _validate_result_shape(self, effective_question: str, sql: str) -> None:
        """粒度守卫：单值汇总只能输出聚合值，不能被普通字段或顶层分组拆成多行。"""

        explicitly_grouped = self._question_requests_grouped_result(effective_question)
        expects_scalar = not explicitly_grouped and self._question_requests_scalar_aggregate(
            effective_question
        )
        if not expects_scalar:
            return

        tree = parse_one(sql, read=self.sql_guard.dialect)
        if not isinstance(tree, exp.Select):
            return
        if tree.args.get("group") is not None:
            raise SQLValidationError(
                "用户要求单个总数或合计值；顶层 GROUP BY 会把答案拆成多行，请移除分组。"
            )

        for projection in tree.expressions:
            expression = projection.this if isinstance(projection, exp.Alias) else projection
            has_aggregate = isinstance(expression, exp.AggFunc) or expression.find(exp.AggFunc) is not None
            if not has_aggregate:
                raise SQLValidationError(
                    "用户要求单个总数或合计值；SELECT 只能保留回答所需的聚合表达式，"
                    "不能附加物料编码、描述等普通字段。"
                )
            for column in expression.find_all(exp.Column):
                if column.find_ancestor(exp.AggFunc) is None:
                    raise SQLValidationError(
                        "用户要求单个总数或合计值；聚合表达式外不能混入普通字段。"
                    )

    @staticmethod
    def _question_requests_limit(question: str) -> bool:
        """语义兜底：用户明确说前几条、Top N 或只要 N 条时才保留模型 LIMIT。"""

        import re

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

    def _single_view_covering_analysis(self, analysis: IntentAnalysis) -> str | None:
        """语义守卫：若一个视图已覆盖全部筛选与输出字段，就证明模型不应因 JOIN 或字段关系而追问。"""

        filter_columns = {
            item.column.casefold() for item in analysis.filter_constraints if item.column
        }
        requested_columns = {
            item.casefold() for item in analysis.requested_fields if item
        }
        # 没有结构化筛选或输出信息时，后端不能臆测用户意图，继续保留模型的真实澄清。
        if not filter_columns or not requested_columns:
            return None
        candidate_names = set(analysis.source_views)
        for view in self.catalog.views:
            if candidate_names and view.name not in candidate_names:
                continue
            allowed_filters = {name.casefold() for name in view.filter_columns}
            allowed_outputs = {name.casefold() for name in view.output_columns}
            if filter_columns <= allowed_filters and requested_columns <= allowed_outputs:
                return view.name
        return None

    def _requested_field_terms(self, analysis: IntentAnalysis) -> set[str]:
        """语义守卫：把请求字段转换成中文标签，识别追问是否正在索要本应由数据库返回的答案。"""

        requested = {name.casefold() for name in analysis.requested_fields}
        terms: set[str] = set()
        for view in self.catalog.views:
            for name, detail in view.column_semantics.items():
                if name.casefold() not in requested:
                    continue
                label = str(detail.get("business_name", "")).strip()
                if label:
                    terms.add(label)
                    # “供应商名称”与自然问法“哪个供应商”应识别为同一输出概念。
                    for suffix in ("名称", "编码", "编号", "数量", "金额"):
                        if label.endswith(suffix) and len(label) > len(suffix):
                            terms.add(label[: -len(suffix)])
        return {term for term in terms if len(term) >= 2}

    def _clarification_issue(self, analysis: IntentAnalysis) -> str | None:
        """编排守卫：验证追问确实在索要缺失输入，而不是重复问题或向用户索要查询结果。"""

        if analysis.status != "clarification_required":
            return None
        if not analysis.clarification_question or not analysis.clarification_question.strip():
            return "clarification_required 必须提供一个具体追问。"
        if not analysis.missing_information:
            return "追问没有声明构造 SQL 真正缺少的 missing_information。"
        covering_view = self._single_view_covering_analysis(analysis)
        if covering_view is not None:
            return (
                f"单个视图 {covering_view} 已同时覆盖全部筛选字段和输出字段；"
                "不得臆测需要跨视图关联或继续追问，应生成单视图 SQL。"
            )
        normalized_question = "".join(
            character for character in analysis.clarification_question if character.isalnum()
        )
        requested_terms = self._requested_field_terms(analysis)
        asked_output_terms = sorted(
            term for term in requested_terms if term in normalized_question
        )
        if asked_output_terms:
            return (
                "追问正在向用户索要本应由数据库返回的字段："
                + "、".join(asked_output_terms)
                + "。应使用这些字段生成 SELECT，而不是继续追问。"
            )
        return None

    def _refine_analysis(
        self,
        analysis: IntentAnalysis,
        repair: RepairFn,
        previous_clarifications: tuple[str, ...],
    ) -> IntentAnalysis:
        """查询专用 refine：拦截重复追问与无效澄清，再进入共享 SQL 校验循环。"""

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

        clarification_issue = self._clarification_issue(analysis)
        if clarification_issue is not None:
            logger.warning("模型提出了无效追问，尝试自动修复：%s", clarification_issue)
            analysis = repair(analysis.model_dump(), clarification_issue)
            repaired_issue = self._clarification_issue(analysis)
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
            return self._refine_analysis(analysis, repair, previous_clarifications)

        return plan_with_ai(
            llm_client=self.llm_client,
            system_prompt=self._system_prompt(),
            question=question,
            parser=self._parse_analysis,
            validate_ready=validate_ready,
            error_factory=SQLGenerationError,
            label="Text-to-SQL",
            max_tokens=2200,
            max_sql_repairs=1,
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
        """理解入口：合并多轮补充，生成并验证 SQL；真正歧义才返回前端追问。"""

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
            raise SQLGenerationError(analysis.route_reason)
        assert analysis.sql is not None
        assert analysis.source_views

        needs_confirmation = analysis.confidence < self.AUTO_ROUTE_THRESHOLD and confirmed_view is None
        primary_view = analysis.source_views[0]
        route = RouteDecision(
            view_name=primary_view,
            confidence=analysis.confidence,
            reason=analysis.route_reason,
            matched_terms=tuple(analysis.matched_concepts),
            alternatives=tuple(analysis.source_views[1:]),
            match_type="ai" if confirmed_view is None else "confirmed",
            requires_confirmation=needs_confirmation,
            confirmation_question=(
                f"我理解你想进行“{analysis.intent_summary}”，是否继续查询？"
                if needs_confirmation
                else None
            ),
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
