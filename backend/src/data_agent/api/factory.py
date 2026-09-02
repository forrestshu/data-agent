"""FastAPI 应用工厂。"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from data_agent.api.routes import register_routes
from data_agent.database import Database
from data_agent.knowledge.database_profile import load_database_profile
from data_agent.llm import DeepSeekClient, LLMClient
from data_agent.query.execution.exports import QueryExportRegistry
from data_agent.settings import DATABASE_PROFILE_PATH, DEFAULT_DATABASE_PATH, FRONTEND_DIST_PATH


def create_app(
    llm_client: LLMClient | None = None,
    use_environment_ai: bool = True,
) -> FastAPI:
    """应用工厂：所有自然语言查询都必须使用 AI 规划。"""

    configured_llm = llm_client
    if configured_llm is None and use_environment_ai:
        configured_llm = DeepSeekClient.from_environment()
    app = FastAPI(
        title="Data Agent API",
        version="0.3.0",
        description="DeepSeek 语义理解、自然语言回答与 SQLite 只读查询",
    )
    app.state.database = Database(path=DEFAULT_DATABASE_PATH)
    app.state.profile = load_database_profile(DATABASE_PROFILE_PATH)
    app.state.llm = configured_llm
    app.state.query_exports = QueryExportRegistry()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    register_routes(app)
    if FRONTEND_DIST_PATH.exists():
        # 生产构建存在时由 FastAPI 同源托管；开发阶段仍使用 Vite HMR。
        app.mount("/", StaticFiles(directory=FRONTEND_DIST_PATH, html=True), name="frontend")
    return app
