"""API 公共依赖。"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder

from data_agent.database import DatabaseSource


def json_safe(value: Any) -> Any:
    """把日期等数据库类型转换成标准 JSON 值。"""

    return jsonable_encoder(value)


def active_context(request: Request) -> tuple[DatabaseSource, dict[str, Any]]:
    """返回当前活动数据源和共享结构画像。"""

    source = request.app.state.sources[request.app.state.active_source_id]
    profile = request.app.state.profile
    if source.id == "sqlserver":
        profile = {**profile, "generated_limitations": []}
    return source, profile
