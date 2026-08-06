"""短期查询导出注册表。"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class QueryExportPlan:
    created_at: float
    sql: str
    parameters: tuple[Any, ...]


class QueryExportRegistry:
    def __init__(self, ttl_seconds: float = 900, capacity: int = 20) -> None:
        self.ttl_seconds = ttl_seconds
        self.capacity = capacity
        self._plans: dict[str, QueryExportPlan] = {}

    def _purge(self, now: float) -> None:
        for key in [
            key for key, plan in self._plans.items()
            if now - plan.created_at > self.ttl_seconds
        ]:
            self._plans.pop(key, None)

    def register(self, *, sql: str, parameters: tuple[Any, ...]) -> str:
        now = time.monotonic()
        self._purge(now)
        while len(self._plans) >= self.capacity:
            oldest = min(self._plans, key=lambda key: self._plans[key].created_at)
            self._plans.pop(oldest, None)
        download_id = uuid4().hex
        self._plans[download_id] = QueryExportPlan(now, sql, parameters)
        return download_id

    def get(self, download_id: str) -> QueryExportPlan | None:
        self._purge(time.monotonic())
        return self._plans.get(download_id)

    def consume(self, download_id: str) -> QueryExportPlan | None:
        plan = self.get(download_id)
        if plan is not None:
            self._plans.pop(download_id, None)
        return plan
