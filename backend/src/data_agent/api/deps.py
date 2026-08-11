"""API 公共依赖。"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder

from data_agent.database import Database


def json_safe(value: Any) -> Any:
    """把日期等数据库类型转换成标准 JSON 值。"""

    return jsonable_encoder(value)


def active_context(request: Request) -> tuple[Database, dict[str, Any]]:
    """返回唯一 SQLite 数据库和静态知识画像。"""

    return request.app.state.database, request.app.state.profile
