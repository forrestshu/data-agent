"""模型规划公共契约与一次安全修复流程。"""

from __future__ import annotations

import json
from typing import Any, Callable, Literal, TypeVar

from pydantic import BaseModel, Field, field_validator

from data_agent.knowledge.prompt import load_prompt
from data_agent.llm import LLMClient, LLMUnavailable


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
        return {
            "success": "ready",
            "completed": "ready",
            "clarify": "clarification_required",
            "clarification": "clarification_required",
            "need_clarification": "clarification_required",
            "not_supported": "unsupported",
        }.get(normalized, normalized)

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
            return list(value.values())
        if isinstance(value, (list, tuple)):
            return list(value)
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
