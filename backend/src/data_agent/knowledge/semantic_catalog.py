"""语义层：加载 16 张已批准视图、字段含义和已审核跨视图关系。

该模块只读取后端内置的结构化语义资产，不访问业务数据。运行时查询 Agent、
路由器和 SQL Guard 共用同一份目录，避免“文档说一套、代码用另一套”。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data_agent.settings import CATALOG_PATH

DEFAULT_CATALOG_PATH = CATALOG_PATH


@dataclass(frozen=True)
class SemanticView:
    """知识层的单视图对象：提供路由语义与 SQL 白名单。"""

    name: str
    business_name: str
    domain: str
    purpose: str
    grain: str
    filter_columns: tuple[str, ...]
    output_columns: tuple[str, ...]
    join_columns: tuple[str, ...]
    column_semantics: dict[str, dict[str, Any]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticView":
        """将 JSON 记录转成不可变对象，供路由与执行层共用。"""

        return cls(
            name=data["name"],
            business_name=data["business_name"],
            domain=data["domain"],
            purpose=data["purpose"],
            grain=data["grain"],
            filter_columns=tuple(data["filter_columns"]),
            output_columns=tuple(data["output_columns"]),
            join_columns=tuple(data.get("join_columns", [])),
            column_semantics={
                str(name): {
                    "business_name": str(detail["business_name"]),
                    "description": str(detail["description"]),
                    "value_examples": tuple(
                        str(item)
                        for item in detail.get("value_examples", [])
                        if item is not None and str(item).strip()
                    ),
                }
                for name, detail in data.get("column_semantics", {}).items()
                if isinstance(detail, dict)
            },
        )


@dataclass(frozen=True)
class SemanticRelationship:
    """一条经过治理的跨视图关系；键方向以 left_view 到 right_view 表示。"""

    id: str
    left_view: str
    right_view: str
    keys: tuple[tuple[str, str], ...]
    status: str
    cardinality: str
    grain_warning: str

    @property
    def executable(self) -> bool:
        return self.status in {"approved", "approved_with_risk"}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticRelationship":
        return cls(
            id=str(data["id"]),
            left_view=str(data["left_view"]),
            right_view=str(data["right_view"]),
            keys=tuple(
                (str(item["left"]), str(item["right"]))
                for item in data.get("keys", [])
                if isinstance(item, dict) and item.get("left") and item.get("right")
            ),
            status=str(data.get("status", "advisory_not_enforceable")),
            cardinality=str(data.get("cardinality", "unknown")),
            grain_warning=str(data.get("grain_warning", "")),
        )


@dataclass(frozen=True)
class SemanticCatalog:
    """运行时语义目录：只暴露查询规划与 SQL Guard 使用的知识。"""

    views: tuple[SemanticView, ...]
    relationships: tuple[SemanticRelationship, ...]

    def by_name(self, name: str) -> SemanticView:
        """按白名单名称查找视图；未找到时显式失败。"""

        for view in self.views:
            if view.name == name:
                return view
        raise KeyError(f"未收录的视图: {name}")


def load_semantic_catalog(path: Path | None = None) -> SemanticCatalog:
    """从后端语义资产加载单一事实源，输出类型化知识目录。"""

    catalog_path = path or DEFAULT_CATALOG_PATH
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    return SemanticCatalog(
        views=tuple(SemanticView.from_dict(item) for item in raw["views"]),
        relationships=tuple(
            SemanticRelationship.from_dict(item)
            for item in raw.get("relationships", [])
            if isinstance(item, dict)
        ),
    )
