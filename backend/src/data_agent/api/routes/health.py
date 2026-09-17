"""健康与 AI 状态路由。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from data_agent.api.deps import active_context
from data_agent.llm import LLMClient


router = APIRouter()


@router.get("/api/health")
def health(request: Request) -> dict[str, Any]:
    """健康接口：确认当前数据源和 AI 配置。"""

    source, _ = active_context(request)
    llm: LLMClient | None = request.app.state.llm
    ready = False
    detail = None
    try:
        if source.id == "sqlite":
            ready = source.path.exists()
        else:
            with source.connect(timeout_seconds=3) as connection:
                cursor = source.execute(connection, "SELECT 1 AS ready")
                ready = bool(cursor.fetchone())
    except Exception:
        detail = "当前数据源暂时无法连接。"
    return {
        "service": "ok",
        "database": {
            "id": source.id,
            "type": source.dialect,
            "label": source.label,
            "ready": ready,
            "detail": detail,
            "file": source.path.name if source.id == "sqlite" else None,
        },
        "ai": {
            "configured": llm is not None,
            "provider": llm.provider if llm else None,
            "model": llm.model if llm else None,
            "required": True,
        },
    }


@router.get("/api/ai/status")
def ai_status(request: Request) -> dict[str, Any]:
    """AI 状态接口：只报告是否配置与模型名，绝不返回 Key。"""

    llm: LLMClient | None = request.app.state.llm
    return {
        "configured": llm is not None,
        "provider": llm.provider if llm else None,
        "model": llm.model if llm else None,
        "required": True,
        "role": "数据查询 Text-to-SQL、Dashboard 概况规划、澄清和证据回答",
    }
