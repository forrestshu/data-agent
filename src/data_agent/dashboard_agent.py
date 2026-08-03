"""Dashboard 概况分析链路：理解模糊问题、验证只读 SQL，并交给图表层渲染。"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, replace
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

from .catalog import KnowledgeCatalog, build_query_knowledge
from .data_sources import DataSourceConfig
from .executor import QueryResult
from .llm import LLMClient, LLMUnavailable
from .router import RouteDecision
from .sql_guard import SQLGuard, SQLValidationError


logger = logging.getLogger(__name__)


class DashboardAnalysis(BaseModel):
    """Dashboard 模型输出：描述概况口径、验证 SQL 和可视化偏好。"""

    status: Literal["ready", "clarification_required", "unsupported"]
    confidence: float = Field(default=0.75, ge=0, le=1)
    title: str = "业务数据概况"
    summary: str = "按当前问题从已审核数据中生成概况。"
    route_reason: str = "根据语义层选择概况数据对象"
    clarification_question: str | None = None
    clarification_kind: Literal["choice", "number", "text"] = "text"
    clarification_options: list[str] = Field(default_factory=list)
    clarification_unit: str | None = None
    matched_concepts: list[str] = Field(default_factory=list)
    source_views: list[str] = Field(default_factory=list)
    sql: str | None = None
    parameters: list[Any] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    display_units: dict[str, str] = Field(default_factory=dict)
    visualization: Literal["auto", "ranking", "breakdown", "trend", "metric", "table"] = "auto"
    dimension_columns: list[str] = Field(default_factory=list)
    metric_columns: list[str] = Field(default_factory=list)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: Any) -> Any:
        """协议容错：把模型常见的状态别名归一化为 Dashboard 状态。"""

        if not isinstance(value, str):
            return value
        aliases = {
            "success": "ready",
            "completed": "ready",
            "clarify": "clarification_required",
            "clarification": "clarification_required",
            "not_supported": "unsupported",
        }
        normalized = value.strip().casefold()
        return aliases.get(normalized, normalized)

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value: Any) -> float:
        """协议容错：遗漏置信度时使用保守值，不影响 SQL 安全校验。"""

        return 0.5 if value is None else float(value)

    @field_validator(
        "matched_concepts",
        "source_views",
        "assumptions",
        "clarification_options",
        "dimension_columns",
        "metric_columns",
        mode="before",
    )
    @classmethod
    def normalize_string_list(cls, value: Any) -> list[str]:
        """协议容错：把 null、单字符串或异常对象归一化为字符串数组。"""

        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    @field_validator("parameters", mode="before")
    @classmethod
    def normalize_parameters(cls, value: Any) -> list[Any]:
        """协议容错：把模型参数对象转换为按占位符顺序排列的数组。"""

        if value is None:
            return []
        if isinstance(value, dict):
            return list(value.values())
        if isinstance(value, (list, tuple)):
            return list(value)
        return [value]

    @field_validator("display_units", mode="before")
    @classmethod
    def normalize_display_units(cls, value: Any) -> dict[str, str]:
        """协议容错：只保留短文本单位，异常单位不会进入展示层。"""

        if not isinstance(value, dict):
            return {}
        return {
            str(column): str(unit).strip()
            for column, unit in value.items()
            if unit is not None and str(unit).strip()
        }

    @field_validator("title", "summary", "route_reason", mode="before")
    @classmethod
    def normalize_text(cls, value: Any, info: Any) -> str:
        """协议容错：说明字段为空时使用不会伪造事实的默认文案。"""

        if value is not None and str(value).strip():
            return str(value).strip()
        defaults = {
            "title": "业务数据概况",
            "summary": "按当前问题从已审核数据中生成概况。",
            "route_reason": "根据语义层选择概况数据对象",
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


class DashboardAgent:
    """Dashboard Agent：专注概况探索，不复用精确数据查询的意图与回答提示词。"""

    def __init__(
        self,
        catalog: KnowledgeCatalog,
        llm_client: LLMClient | None,
        database_profile: dict[str, Any] | None = None,
        allow_fallback: bool = True,
        source: DataSourceConfig | None = None,
    ) -> None:
        """装配概况 Agent；安全目录、数据库画像和数据源来自当前活动数据源。"""

        self.catalog = catalog
        self.llm_client = llm_client
        self.database_profile = database_profile or {}
        self.allow_fallback = allow_fallback
        self.source = source
        self.sql_guard = SQLGuard(catalog, self.database_profile, source=source)

    def _knowledge_context(self) -> str:
        """提示构建：只传递已审核语义和机器画像，不把业务行直接交给模型。"""

        knowledge = build_query_knowledge(self.catalog, self.database_profile)
        return json.dumps(knowledge, ensure_ascii=False, separators=(",", ":"))

    def _system_prompt(self) -> str:
        """Dashboard 专用提示：允许概况推断，但要求所有数字经过数据库验证。"""

        is_sqlserver = self.source is not None and self.source.kind == "sqlserver"
        dialect = "SQL Server T-SQL" if is_sqlserver else "SQLite"
        limit_rule = (
            "SQLite 使用固定整数 LIMIT；"
            if not is_sqlserver
            else "SQL Server 使用固定整数 TOP N，不使用 LIMIT；"
        )
        forbidden = (
            "不生成 SQL 注释、PRAGMA、ATTACH、系统表查询或任何写入语句。"
            if not is_sqlserver
            else "不生成 SQL 注释、EXEC、查询提示、跨数据库/Schema、系统表查询或任何写入语句。"
        )
        return f"""
你是 ERP Data Agent 的 Dashboard 概况分析规划器，使用 {dialect} 验证业务概况。
你与“精确数据查询”是两条不同链路：Dashboard 不要求用户先给出精确阈值，
而是先理解用户想观察的趋势、排名、分布或异常，再用数据库结果验证这个概况。

核心目标：
1. 把口语问题解释成一个可观察的概况，例如“什么物料比较少”理解为“按物料汇总现有量，找库存较少的物料”。
2. 选择已审核视图和字段生成一条只读 SELECT；所有图表数值都必须来自这条 SQL 的真实结果。
3. 返回 title、summary、visualization、dimension_columns、metric_columns，帮助后端把结果组织成大数字、图表和数据表。

概况理解规则：
- “比较少、比较多、主要、集中、偏低、偏高、排行、看看情况”等相对表达默认采用排序、分布或趋势展示，不能仅因为没有精确阈值就追问用户。
- “物料比较少/库存少”优先使用库存视图；库存视图一行是物料与库位组合，按物料观察时必须 GROUP BY PartNum、PartDescription 并 SUM(Qty)，再按合计量升序展示前 6～12 项。
- 用户明确问库位时才保留库位粒度；用户问物料时不要把单个库位行误当成物料总量。
- “比较少”不等于凭空创造阈值，不要生成 HAVING Qty < 10 之类的固定标准；优先用 ORDER BY、分位概览或前几项排名。
- 概况问题可以返回 2～4 个字段；优先保留对象名称/编码、核心指标和必要的日期或业务状态。
- 只有没有任何可验证数据对象，或两个业务口径会导致完全不同且无法从问题判断时，才 status=clarification_required；不要为相对词追问阈值。
- summary 只说明本次采用的观察口径，不写模型臆测的数字、结论或数据库外事实。

SQL 安全规则：
- 只能使用当前语义层 JSON 中的逻辑视图和字段，不能猜字段、关系或数据值。
- 只能生成单条 SELECT；允许聚合、GROUP BY、ORDER BY、子查询和语义层批准的 JOIN。
- 禁止 SELECT *；用户输入值必须使用 ? 占位符并按顺序写入 parameters。
- 只有为了概况排名而限制前几项时才使用固定整数 N；{limit_rule}
- 任何 JOIN 必须完整使用语义层批准的关系和 Company 公司键；禁止笛卡尔积。
- {forbidden}

输出 JSON 字段：
- status：ready、clarification_required 或 unsupported。
- title：不超过 20 个中文字符的概况标题。
- summary：一句不带臆测数字的概况口径说明。
- visualization：auto、ranking、breakdown、trend、metric 或 table。
- dimension_columns / metric_columns：必须是 SQL 实际输出的字段名或别名。
- display_units：按输出字段或别名给出可靠短单位；不能判断时为空对象。

必须输出一个 JSON 对象。ready 示例：
{{"status":"ready","title":"库存较少物料","summary":"按物料汇总各库位现有量并按升序展示较少项。","visualization":"ranking","dimension_columns":["PartDescription","PartNum"],"metric_columns":["TotalQty"],"sql":"SELECT PartNum, PartDescription, SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV GROUP BY PartNum, PartDescription ORDER BY TotalQty ASC LIMIT 12","parameters":[],"assumptions":["将‘比较少’理解为当前库存排序靠前的较少项"],"display_units":{{"TotalQty":"件"}}}}

当前语义层 JSON：
{self._knowledge_context()}
""".strip()

    @staticmethod
    def _parse_analysis(payload: dict[str, Any]) -> DashboardAnalysis:
        """协议解析：保留完整概况字段；失败时只保留可修复的核心字段。"""

        try:
            return DashboardAnalysis.model_validate(payload)
        except ValidationError as full_error:
            status = str(payload.get("status", "")).casefold().strip()
            aliases = {
                "success": "ready",
                "completed": "ready",
                "clarify": "clarification_required",
                "clarification": "clarification_required",
                "not_supported": "unsupported",
            }
            normalized_status = aliases.get(status, status)
            common = {
                "status",
                "confidence",
                "title",
                "summary",
                "route_reason",
                "matched_concepts",
                "source_views",
                "assumptions",
            }
            if normalized_status == "ready":
                allowed = common | {
                    "sql",
                    "parameters",
                    "display_units",
                    "visualization",
                    "dimension_columns",
                    "metric_columns",
                }
            elif normalized_status == "clarification_required":
                allowed = common | {
                    "clarification_question",
                    "clarification_kind",
                    "clarification_options",
                    "clarification_unit",
                }
            else:
                allowed = common
            minimal = {key: value for key, value in payload.items() if key in allowed}
            try:
                return DashboardAnalysis.model_validate(minimal)
            except ValidationError:
                raise full_error

    def _repair_analysis(
        self,
        effective_question: str,
        payload: dict[str, Any],
        issue: str,
    ) -> DashboardAnalysis:
        """一次修复：把契约或 SQL Guard 反馈给 Dashboard 模型，不放宽安全边界。"""

        if self.llm_client is None:
            raise LLMUnavailable("DeepSeek 未配置。")
        repair_prompt = f"""
上一次 Dashboard 概况计划没有通过后端验证。请根据同一份语义层修复 JSON 或 SQL，只输出完整 JSON 对象。
验证问题：{issue}
用户问题：{effective_question}
上一次输出：{json.dumps(payload, ensure_ascii=False, default=str)}

{self._system_prompt()}
""".strip()
        repaired = self.llm_client.complete_json(
            "你正在修复一条 ERP Dashboard 概况计划；后端安全规则不可更改。",
            repair_prompt,
            max_tokens=2400,
        )
        try:
            return self._parse_analysis(repaired)
        except ValidationError as error:
            raise DashboardPlanningError("Dashboard 修复后的计划仍不完整。") from error

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

    def _analyze_with_ai(self, effective_question: str, limit: int) -> DashboardAnalysis:
        """模型入口：生成概况计划，契约或 SQL 不通过时自动修复一次。"""

        if self.llm_client is None:
            raise LLMUnavailable("DeepSeek 未配置。")
        payload = self.llm_client.complete_json(
            self._system_prompt(),
            f"用户 Dashboard 问题：{effective_question}",
            max_tokens=2400,
        )
        try:
            analysis = self._parse_analysis(payload)
        except ValidationError as error:
            logger.warning("Dashboard 契约第一次校验失败，尝试自动修复：%s", error)
            analysis = self._repair_analysis(
                effective_question,
                payload,
                "返回 JSON 字段类型不符合 Dashboard 契约",
            )

        if analysis.status == "ready":
            try:
                return self._validate_ready(analysis, limit)
            except SQLValidationError as first_error:
                logger.warning("Dashboard SQL 第一次未通过守卫，尝试自动修复：%s", first_error)
                repaired = self._repair_analysis(
                    effective_question,
                    analysis.model_dump(),
                    str(first_error),
                )
                if repaired.status != "ready":
                    return repaired
                try:
                    return self._validate_ready(repaired, limit)
                except SQLValidationError as second_error:
                    raise DashboardPlanningError(
                        "Dashboard 连续两次未生成可安全执行的概况查询。"
                    ) from second_error
        return analysis

    def _fallback_analysis(self, question: str) -> DashboardAnalysis:
        """测试/诊断降级：无模型时提供一个安全的库存概况，生产模式默认关闭该降级。"""

        normalized = question.casefold()
        scored = []
        for view in self.catalog.views:
            terms = (*view.keywords, *view.aliases, view.domain, view.purpose)
            score = sum(1 for term in terms if term and term.casefold() in normalized)
            if view.domain == "库存" and any(mark in normalized for mark in ("物料", "少", "库存")):
                score += 4
            scored.append((score, view))
        _, view = max(scored, key=lambda item: (item[0], item[1].name))

        if view.domain == "库存" and {"PartNum", "PartDescription", "Qty"} <= set(view.output_columns):
            if self.source is not None and self.source.kind == "sqlserver":
                sql = (
                    f"SELECT TOP 12 PartNum, PartDescription, SUM(Qty) AS DashboardQty "
                    f"FROM {view.name} GROUP BY PartNum, PartDescription ORDER BY DashboardQty ASC"
                )
            else:
                sql = (
                    f"SELECT PartNum, PartDescription, SUM(Qty) AS DashboardQty "
                    f"FROM {view.name} GROUP BY PartNum, PartDescription ORDER BY DashboardQty ASC LIMIT 12"
                )
            return DashboardAnalysis(
                status="ready",
                confidence=0.5,
                title="库存较少物料",
                summary="按物料汇总各库位现有量并按升序展示较少项。",
                route_reason="本地降级选择库存视图进行概况排序",
                source_views=[view.name],
                sql=sql,
                visualization="ranking",
                dimension_columns=["PartDescription", "PartNum"],
                metric_columns=["DashboardQty"],
                display_units={"DashboardQty": "件"},
                assumptions=["将‘比较少’理解为当前库存排序靠前的较少项"],
            )

        selected = [column for column in view.output_columns if column not in view.join_columns][:4]
        if not selected:
            raise DashboardPlanningError("当前语义层没有可用于概况展示的字段。")
        if self.source is not None and self.source.kind == "sqlserver":
            sql = f"SELECT TOP 12 {', '.join(selected)} FROM {view.name}"
        else:
            sql = f"SELECT {', '.join(selected)} FROM {view.name} LIMIT 12"
        return DashboardAnalysis(
            status="ready",
            confidence=0.35,
            title=f"{view.domain}概况",
            summary=f"从{view.purpose}中展示一组概况数据。",
            route_reason="本地降级选择语义目录中最相关的业务视图",
            source_views=[view.name],
            sql=sql,
            visualization="table",
            dimension_columns=selected[:2],
            assumptions=["模型未配置时仅展示已审核视图的有限预览"],
        )

    @staticmethod
    def _effective_question(
        question: str,
        clarification_answer: str | None,
        clarification_history: tuple[tuple[str, str], ...],
        confirmed_view: str | None,
    ) -> str:
        """对话状态层：把已回答信息和用户确认的视图作为本轮概况输入。"""

        effective = question.strip()
        if clarification_history:
            transcript = ["以下信息用户已经回答，禁止重复询问："]
            for index, (asked, answered) in enumerate(clarification_history, start=1):
                transcript.append(f"第 {index} 轮系统追问：{asked}")
                transcript.append(f"第 {index} 轮用户回答：{answered}")
            effective += "\n" + "\n".join(transcript)
        elif clarification_answer and clarification_answer.strip():
            effective += f"\n用户补充：{clarification_answer.strip()}"
        if confirmed_view:
            effective += f"\n用户已确认优先观察数据对象：{confirmed_view}"
        return effective

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
        try:
            analysis = self._analyze_with_ai(effective_question, limit)
        except (LLMUnavailable, DashboardPlanningError):
            if not self.allow_fallback:
                raise
            analysis = self._fallback_analysis(effective_question)

        if analysis.status == "clarification_required":
            provider = self.llm_client.provider if self.llm_client else "local"
            model = self.llm_client.model if self.llm_client else "rule-fallback"
            raise DashboardClarificationRequired(analysis, provider, model)
        if analysis.status == "unsupported":
            raise DashboardPlanningError(analysis.route_reason)
        if not analysis.sql or not analysis.source_views:
            raise DashboardPlanningError("Dashboard 概况计划缺少已验证 SQL 或数据对象。")

        primary_view = analysis.source_views[0]
        route = RouteDecision(
            view_name=primary_view,
            confidence=analysis.confidence,
            reason=analysis.route_reason,
            matched_terms=tuple(analysis.matched_concepts),
            alternatives=tuple(analysis.source_views[1:]),
            # Dashboard 允许模型自动选择最相关视图，不沿用精确查询的低置信度确认停顿。
            match_type="confirmed" if confirmed_view else "ai",
            requires_confirmation=False,
            confirmation_question=None,
        )
        provider = self.llm_client.provider if self.llm_client else "local"
        model = self.llm_client.model if self.llm_client else "rule-fallback"
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

    def localize_result_columns(
        self,
        original_question: str,
        result: QueryResult,
    ) -> QueryResult:
        """展示层：为 Dashboard SQL 生成的未知英文别名补充中文表头，不改变数据值。"""

        if self.llm_client is None or not result.rows:
            return result
        unknown_columns = [
            column
            for column in result.rows[0]
            if result.column_labels.get(column, column) == column
            and re.search(r"[A-Za-z]", column)
        ]
        if not unknown_columns:
            return result
        samples = [
            {column: row.get(column) for column in unknown_columns}
            for row in result.rows[:3]
        ]
        system_prompt = """
你负责把 Dashboard 概况结果中尚未登记语义的英文列名转换为简洁中文表头。
只能翻译输入字段，不得新增、删除或改写字段键；无法判断时省略。
只返回 JSON：{"column_labels":{"英文字段":"中文表头"}}。
""".strip()
        try:
            generated = self.llm_client.complete_json(
                system_prompt,
                json.dumps(
                    {
                        "用户问题": original_question,
                        "来源视图": list(result.plan.source_views or (result.plan.view_name,)),
                        "待处理字段": unknown_columns,
                        "样例值": samples,
                    },
                    ensure_ascii=False,
                    default=str,
                ),
                max_tokens=400,
            )
        except LLMUnavailable:
            return result
        proposed = generated.get("column_labels")
        if not isinstance(proposed, dict):
            return result
        translated = dict(result.column_labels)
        for column in unknown_columns:
            label = proposed.get(column)
            if isinstance(label, str) and 2 <= len(label.strip()) <= 10:
                translated[column] = label.strip()
        return replace(result, column_labels=translated)

    def explain_failure(self, original_question: str, category: str) -> tuple[str, bool]:
        """错误边界：把 Dashboard 计划异常转换为不泄露技术细节的业务提示。"""

        fallback_messages = {
            "ai_unavailable": "当前暂时无法理解 Dashboard 概况问题，请稍后重试。",
            "missing_information": "还缺少可用于概况判断的业务范围，请补充后再试。",
            "unsupported_query": "当前数据范围暂时无法生成这个概况，可以换一种业务对象或指标描述。",
            "internal_error": "当前 Dashboard 没有成功生成，请稍后重试。",
        }
        fallback = fallback_messages.get(category, fallback_messages["internal_error"])
        if self.llm_client is None:
            return fallback, False
        try:
            answer = self.llm_client.complete_text(
                "你是 ERP Dashboard 助手，只用 1 到 2 句中文解释概况生成未完成的原因和下一步；禁止输出 SQL、JSON、表名、字段名或技术异常。",
                f"用户问题：{original_question}\n失败类别：{category}\n底稿：{fallback}",
                max_tokens=300,
            )
            forbidden = ("sql", "json", "api", "exception", "traceback", "sqlite")
            if any(term in answer.casefold() for term in forbidden):
                return fallback, False
            return answer, True
        except Exception:
            logger.exception("生成 Dashboard 错误说明时出现异常")
            return fallback, False
