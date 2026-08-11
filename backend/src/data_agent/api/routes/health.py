"""健康与 AI 状态路由。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from data_agent.api.deps import active_context
from data_agent.llm import LLMClient


router = APIRouter()


@router.get("/api/health")
def health(request: Request) -> dict[str, Any]:
    """健康接口：确认 SQLite 文件和 AI 配置。"""

    source, _ = active_context(request)
    llm: LLMClient | None = request.app.state.llm
    return {
        "service": "ok",
        "database": {
            "type": "sqlite",
            "file": source.path.name,
            "ready": source.path.exists(),
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
