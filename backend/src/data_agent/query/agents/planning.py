"""模型规划公共契约与共享规划骨架（解析降级、修复、ready 校验循环）。"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Literal, TypeVar

from pydantic import BaseModel, Field, ValidationError, field_validator

from data_agent.knowledge.prompt import load_prompt
from data_agent.llm import LLMClient, LLMUnavailable
from data_agent.query.execution.guard import SQLValidationError


logger = logging.getLogger(__name__)

STATUS_FALLBACK_ALIASES = {
    "success": "ready",
    "completed": "ready",
    "supported": "ready",
    "clarify": "clarification_required",
    "clarification": "clarification_required",
    "need_clarification": "clarification_required",
    "not_supported": "unsupported",
}


def effective_question(
    question: str,
    clarification_answer: str | None,
    clarification_history: tuple[tuple[str, str], ...],
    confirmed_view: str | None,
) -> str:
    """把用户问题和已确认上下文组织为 JSON 模型输入。"""

    return json.dumps(
        {
            "用户原问题": question.strip(),
            "已回答的澄清记录，禁止重复询问": [
                {"系统追问": asked, "用户回答": answered}
                for asked, answered in clarification_history
            ],
            "用户补充": clarification_answer.strip()
            if clarification_answer and clarification_answer.strip()
            else None,
            "用户已确认的数据对象": confirmed_view,
        },
        ensure_ascii=False,
    )


class PlanningAnalysis(BaseModel):
    """数据查询与 Dashboard 共享的最小规划协议。"""

    status: Literal["ready", "clarification_required", "unsupported"]
    confidence: float = Field(default=0.75, ge=0, le=1)
    route_reason: str = "根据语义层生成只读查询"
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

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        normalized = value.strip().casefold()
        return STATUS_FALLBACK_ALIASES.get(normalized, normalized)

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value: Any) -> float:
        return 0.5 if value is None else float(value)

    @field_validator("clarification_kind", mode="before")
    @classmethod
    def normalize_clarification_kind(cls, value: Any) -> str:
        return value if value in {"choice", "number", "text"} else "text"

    @field_validator(
        "matched_concepts",
        "source_views",
        "assumptions",
        "clarification_options",
        mode="before",
    )
    @classmethod
    def normalize_string_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, dict):
            value = list(value.keys())
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    @field_validator("parameters", mode="before")
    @classmethod
    def normalize_parameters(cls, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, dict):
            value = [value["value"]] if "value" in value else list(value.values())
        if isinstance(value, (list, tuple)):
            return [
                item["value"]
                if isinstance(item, dict) and "value" in item
                else item
                for item in value
            ]
        return [value]

    @field_validator("display_units", mode="before")
    @classmethod
    def normalize_display_units(cls, value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        return {
            str(column): str(unit).strip()
            for column, unit in value.items()
            if unit is not None and str(unit).strip()
        }

    @field_validator("route_reason", mode="before")
    @classmethod
    def normalize_route_reason(cls, value: Any) -> str:
        return str(value).strip() if value is not None and str(value).strip() else "根据语义层生成只读查询"


AnalysisT = TypeVar("AnalysisT", bound=PlanningAnalysis)
RepairFn = Callable[[dict[str, Any], str], AnalysisT]
RefineFn = Callable[[AnalysisT, RepairFn], AnalysisT]


def parse_planning_payload(
    model: type[AnalysisT],
    payload: dict[str, Any],
    *,
    common_keys: set[str],
    ready_keys: set[str],
    clarification_keys: set[str],
) -> AnalysisT:
    """协议解析：优先完整校验；失败时按状态保留可修复字段再校验。"""

    try:
        return model.model_validate(payload)
    except ValidationError as full_error:
        status = str(payload.get("status", "")).casefold().strip()
        normalized_status = STATUS_FALLBACK_ALIASES.get(status, status)
        if normalized_status == "ready":
            allowed_keys = common_keys | ready_keys
        elif normalized_status == "clarification_required":
            allowed_keys = common_keys | clarification_keys
        else:
            allowed_keys = common_keys
        minimal_payload = {
            key: value for key, value in payload.items() if key in allowed_keys
        }
        try:
            return model.model_validate(minimal_payload)
        except ValidationError:
            raise full_error


def repair_plan(
    llm_client: LLMClient | None,
    *,
    system_prompt: str,
    question: str,
    payload: dict[str, Any],
    issue: str,
    parser: Callable[[dict[str, Any]], AnalysisT],
    error_factory: Callable[[str], Exception],
    label: str,
    max_tokens: int,
) -> AnalysisT:
    """把契约或 SQL Guard 反馈给模型一次，不放宽任何安全规则。"""

    if llm_client is None:
        raise LLMUnavailable("DeepSeek 未配置。")
    repaired = llm_client.complete_json(
        load_prompt("plan_repair.md", label=label),
        json.dumps(
            {
                "验证问题": issue,
                "用户问题": question,
                "上一次输出": payload,
                "原始规划规则": system_prompt,
            },
            ensure_ascii=False,
            default=str,
        ),
        max_tokens=max_tokens,
    )
    try:
        return parser(repaired)
    except Exception as error:
        raise error_factory(f"{label} 修复后的计划仍不完整。") from error


def plan_with_ai(
    *,
    llm_client: LLMClient | None,
    system_prompt: str,
    question: str,
    parser: Callable[[dict[str, Any]], AnalysisT],
    validate_ready: Callable[[AnalysisT], AnalysisT],
    error_factory: Callable[[str], Exception],
    label: str,
    max_tokens: int,
    max_sql_repairs: int = 1,
    contract_issue: str = "INVALID_JSON_CONTRACT",
    refine: RefineFn | None = None,
) -> AnalysisT:
    """共享规划骨架：生成 → 契约解析/修复 → 可选 refine → ready 时 Guard 校验与重试。

    max_sql_repairs 表示 SQL 校验失败后的最大修复次数（总校验次数 = max_sql_repairs + 1）。
    """

    if llm_client is None:
        raise LLMUnavailable("DeepSeek 未配置。")

    def repair(payload: dict[str, Any], issue: str) -> AnalysisT:
        return repair_plan(
            llm_client,
            system_prompt=system_prompt,
            question=question,
            payload=payload,
            issue=issue,
            parser=parser,
            error_factory=error_factory,
            label=label,
            max_tokens=max_tokens,
        )

    payload = llm_client.complete_json(
        system_prompt,
        question,
        max_tokens=max_tokens,
    )
    try:
        analysis = parser(payload)
    except ValidationError as error:
        detail = (
            error.errors(include_input=False)
            if hasattr(error, "errors")
            else error
        )
        logger.warning("%s 契约第一次校验失败，尝试自动修复：%s", label, detail)
        analysis = repair(payload, contract_issue)

    if refine is not None:
        analysis = refine(analysis, repair)

    if analysis.status != "ready":
        return analysis

    attempts = max(1, max_sql_repairs + 1)
    for attempt in range(attempts):
        try:
            return validate_ready(analysis)
        except SQLValidationError as error:
            if attempt >= attempts - 1:
                raise error_factory(
                    f"{label} 连续{attempts}次未生成可安全执行的查询。"
                ) from error
            logger.warning(
                "%s SQL 第 %s 次未通过守卫，尝试自动修复：%s",
                label,
                attempt + 1,
                error,
            )
            analysis = repair(analysis.model_dump(), str(error))
            if refine is not None:
                analysis = refine(analysis, repair)
            if analysis.status != "ready":
                raise error_factory(
                    f"{label} 的 SQL 修复没有返回可继续校验的 ready 计划。"
                )
    return analysis
