"""查询工作流共享契约。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteDecision:
    view_name: str
    confidence: float
    reason: str
    matched_terms: tuple[str, ...]
    alternatives: tuple[str, ...]
    match_type: str
    requires_confirmation: bool
    confirmation_question: str | None


class RouteConfirmationRequired(ValueError):
    def __init__(self, decision: RouteDecision) -> None:
        super().__init__(decision.confirmation_question or "需要确认查询意图。")
        self.decision = decision
