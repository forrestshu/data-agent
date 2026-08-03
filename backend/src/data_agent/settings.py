"""应用路径配置：集中定义数据库、知识目录和前端产物位置。"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
# 配置层只在后端进程加载本地 .env；该文件已被 gitignore 排除。
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.sqlserver")
DEFAULT_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "sqlite" / "data-agent-2026-7-15.sqlite"
)
SEMANTIC_LAYER_ROOT = Path(__file__).resolve().parent / "semantic_layer"
CATALOG_PATH = SEMANTIC_LAYER_ROOT / "view_catalog.json"
DATABASE_PROFILE_PATH = SEMANTIC_LAYER_ROOT / "database_profile.json"
SYNC_REPORT_PATH = SEMANTIC_LAYER_ROOT / "knowledge_sync_report.json"
SEMANTIC_PROPOSALS_PATH = SEMANTIC_LAYER_ROOT / "semantic_proposals.json"
RUNTIME_ROOT = PROJECT_ROOT / ".data-agent"
ACTIVE_SOURCE_PATH = RUNTIME_ROOT / "active_source.json"
SQLSERVER_KNOWLEDGE_ROOT = RUNTIME_ROOT / "knowledge" / "sqlserver_company"
FRONTEND_DIST_PATH = PROJECT_ROOT / "frontend" / "dist"


def database_path() -> Path:
    """配置层：允许部署时通过环境变量切换快照，默认使用 2026-07-15 更新版。"""

    configured = os.getenv("DATA_AGENT_DATABASE")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DATABASE_PATH
