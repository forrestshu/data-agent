"""应用路径配置。"""

from pathlib import Path
import os

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_DATABASE_PATH = BACKEND_ROOT / "data_agent_2026_07_15.sqlite"
SEMANTIC_LAYER_ROOT = Path(__file__).resolve().parent / "knowledge" / "semantic_layer"
CATALOG_PATH = SEMANTIC_LAYER_ROOT / "semantic_catalog.json"
DATABASE_PROFILE_PATH = SEMANTIC_LAYER_ROOT / "database_profile.json"
FRONTEND_DIST_PATH = PROJECT_ROOT / "frontend" / "dist"

SQLSERVER_HOST = os.getenv("SQLSERVER_HOST", "192.168.1.107")
SQLSERVER_PORT = int(os.getenv("SQLSERVER_PORT", "1433"))
SQLSERVER_USER = os.getenv("SQLSERVER_USER", "dataagent")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD", "")
SQLSERVER_DATABASE = os.getenv("SQLSERVER_DATABASE", "prod")
SQLSERVER_SCHEMA = os.getenv("SQLSERVER_SCHEMA", "Cux")
DEFAULT_SOURCE_ID = os.getenv("DATA_AGENT_DEFAULT_SOURCE", "sqlserver")
