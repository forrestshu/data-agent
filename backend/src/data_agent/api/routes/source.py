"""活动数据源的读取与显式切换。"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


router = APIRouter()


class SourceSelection(BaseModel):
    source_id: Literal["sqlite", "sqlserver"]


def _payload(request: Request) -> dict:
    active_id = request.app.state.active_source_id
    return {
        "active_source_id": active_id,
        "sources": [
            {
                "id": source.id,
                "label": source.label,
                "active": source.id == active_id,
            }
            for source in request.app.state.sources.values()
        ],
    }


@router.get("/api/source")
def get_source(request: Request) -> dict:
    return _payload(request)


@router.put("/api/source")
def select_source(payload: SourceSelection, request: Request) -> dict:
    if payload.source_id not in request.app.state.sources:
        raise HTTPException(status_code=404, detail="数据源不存在。")
    request.app.state.active_source_id = payload.source_id
    return _payload(request)
