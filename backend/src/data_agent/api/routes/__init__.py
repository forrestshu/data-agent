"""注册全部 API 路由。"""

from __future__ import annotations

from fastapi import FastAPI

from data_agent.api.routes import dashboard, exports, health, query


def register_routes(app: FastAPI) -> None:
    """把各路由模块挂到应用上。"""

    app.include_router(health.router)
    app.include_router(dashboard.router)
    app.include_router(query.router)
    app.include_router(exports.router)
