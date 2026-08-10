"""应用路径配置。"""

from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_DATABASE_PATH = BACKEND_ROOT / "data_agent_2026_07_15.sqlite"
SEMANTIC_LAYER_ROOT = Path(__file__).resolve().parent / "knowledge" / "semantic_layer"
CATALOG_PATH = SEMANTIC_LAYER_ROOT / "semantic_catalog.json"
DATABASE_PROFILE_PATH = SEMANTIC_LAYER_ROOT / "database_profile.json"
FRONTEND_DIST_PATH = PROJECT_ROOT / "frontend" / "dist"
