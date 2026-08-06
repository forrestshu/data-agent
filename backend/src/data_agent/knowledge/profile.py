"""读取随应用发布的 SQLite 静态知识画像。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class KnowledgeError(RuntimeError):
    """静态知识画像缺失或与已审核语义不兼容。"""


def load_profile(path: Path) -> dict[str, Any]:
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise KnowledgeError("无法读取静态知识画像。") from error
    if not profile.get("tables"):
        raise KnowledgeError("静态知识画像不完整。")
    return profile


def assert_view_ready(profile: dict[str, Any], view_name: str) -> None:
    actual = {str(table.get("name")) for table in profile.get("tables", [])}
    if view_name not in actual:
        raise KnowledgeError(f"知识画像中不存在视图 {view_name}。")
