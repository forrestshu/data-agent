"""读取随应用发布的 SQLite 静态知识画像。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DatabaseProfileError(RuntimeError):
    """静态知识画像缺失或与已审核语义不兼容。"""


def load_database_profile(path: Path) -> dict[str, Any]:
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DatabaseProfileError("无法读取静态知识画像。") from error
    if not profile.get("tables"):
        raise DatabaseProfileError("静态知识画像不完整。")
    return profile
