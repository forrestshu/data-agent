"""FastAPI 入口包：对外保持 create_app / app / _json_safe 兼容。"""

from __future__ import annotations

from data_agent.api.deps import json_safe as _json_safe
from data_agent.api.factory import create_app

app = create_app()

__all__ = ["app", "create_app", "_json_safe"]
