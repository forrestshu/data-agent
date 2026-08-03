"""语义层：加载 16 张 ERP 视图、字段含义和已审核跨视图关系。

该模块只读取后端内置的结构化语义资产，不访问业务数据。运行时查询 Agent、
路由器和 SQL Guard 共用同一份目录，避免“文档说一套、代码用另一套”。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .settings import CATALOG_PATH

DEFAULT_CATALOG_PATH = CATALOG_PATH


@dataclass(frozen=True)
class ViewKnowledge:
    """知识层的单视图对象：提供路由语义与 SQL 白名单。"""

    name: str
    source_view: str
    chinese_name: str
    domain: str
    purpose: str
    description: str
    grain: str
    keywords: tuple[str, ...]
    aliases: tuple[str, ...]
    filter_columns: tuple[str, ...]
    output_columns: tuple[str, ...]
    join_columns: tuple[str, ...]
    column_semantics: dict[str, dict[str, str]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ViewKnowledge":
        """将 JSON 记录转成不可变对象，供路由与执行层共用。"""

        return cls(
            name=data["name"],
            source_view=data["source_view"],
            chinese_name=str(data.get("chinese_name", data["name"])),
            domain=data["domain"],
            purpose=data["purpose"],
            description=str(data.get("description", data["purpose"])),
            grain=data["grain"],
            keywords=tuple(data["keywords"]),
            aliases=tuple(data.get("aliases", [])),
            filter_columns=tuple(data["filter_columns"]),
            output_columns=tuple(data["output_columns"]),
            join_columns=tuple(data.get("join_columns", [])),
            column_semantics={
                str(name): {
                    "label_zh": str(detail.get("label_zh", name)),
                    "description": str(detail.get("description", "")),
                }
                for name, detail in data.get("column_semantics", {}).items()
                if isinstance(detail, dict)
            },
        )


@dataclass(frozen=True)
class RelationshipKnowledge:
    """一条经过治理的跨视图关系；键方向以 left_view 到 right_view 表示。"""

    id: str
    topic: str
    left_view: str
    right_view: str
    keys: tuple[tuple[str, str], ...]
    cardinality: str
    status: str
    required_all_keys: bool
    description: str
    coverage_evidence: str
    grain_warning: str

    @property
    def executable(self) -> bool:
        return self.status in {"approved", "approved_with_risk"}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelationshipKnowledge":
        return cls(
            id=str(data["id"]),
            topic=str(data.get("topic", data["id"])),
            left_view=str(data["left_view"]),
            right_view=str(data["right_view"]),
            keys=tuple(
                (str(item["left"]), str(item["right"]))
                for item in data.get("keys", [])
                if isinstance(item, dict) and item.get("left") and item.get("right")
            ),
            cardinality=str(data.get("cardinality", "unknown")),
            status=str(data.get("status", "advisory_not_enforceable")),
            required_all_keys=bool(data.get("required_all_keys", True)),
            description=str(data.get("description", "")),
            coverage_evidence=str(data.get("coverage_evidence", "")),
            grain_warning=str(data.get("grain_warning", "")),
        )


@dataclass(frozen=True)
class KnowledgeCatalog:
    """知识目录根对象：包含所有视图和已知数据限制。"""

    version: str
    views: tuple[ViewKnowledge, ...]
    known_limitations: tuple[str, ...]
    business_rules: tuple[dict[str, Any], ...]
    relationships: tuple[RelationshipKnowledge, ...]
    join_policies: tuple[dict[str, Any], ...]
    semantic_equivalences: tuple[dict[str, Any], ...]
    semantic_conflicts: tuple[dict[str, Any], ...]
    semantic_source: dict[str, Any]

    def by_name(self, name: str) -> ViewKnowledge:
        """按白名单名称查找视图；未找到时显式失败。"""

        for view in self.views:
            if view.name == name:
                return view
        raise KeyError(f"未收录的视图: {name}")


def load_catalog(path: Path | None = None) -> KnowledgeCatalog:
    """从后端语义资产加载单一事实源，输出类型化知识目录。"""

    catalog_path = path or DEFAULT_CATALOG_PATH
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    return KnowledgeCatalog(
        version=raw["catalog_version"],
        views=tuple(ViewKnowledge.from_dict(item) for item in raw["views"]),
        known_limitations=tuple(raw.get("known_limitations", [])),
        business_rules=tuple(
            item for item in raw.get("business_rules", []) if isinstance(item, dict)
        ),
        relationships=tuple(
            RelationshipKnowledge.from_dict(item)
            for item in raw.get("relationships", [])
            if isinstance(item, dict)
        ),
        join_policies=tuple(
            item for item in raw.get("join_policies", []) if isinstance(item, dict)
        ),
        semantic_equivalences=tuple(
            item for item in raw.get("semantic_equivalences", []) if isinstance(item, dict)
        ),
        semantic_conflicts=tuple(
            item for item in raw.get("semantic_conflicts", []) if isinstance(item, dict)
        ),
        semantic_source=dict(raw.get("semantic_source", {})),
    )


def build_query_knowledge(
    catalog: KnowledgeCatalog,
    database_profile: dict[str, Any],
) -> dict[str, Any]:
    """知识提示层：合并人工语义和实时机器画像，不发送任何业务数据行。"""

    profile_tables = {
        str(table["name"]): table
        for table in database_profile.get("tables", [])
        if isinstance(table, dict) and table.get("name")
    }
    limitation_map: dict[str, list[str]] = {}
    for item in database_profile.get("generated_limitations", []):
        if not isinstance(item, dict):
            continue
        limitation_map.setdefault(str(item.get("view", "")), []).append(
            str(item.get("message", ""))
        )

    views: list[dict[str, Any]] = []
    for view in catalog.views:
        table = profile_tables.get(view.name, {})
        actual_columns = {
            str(column["name"]): column
            for column in table.get("columns", [])
            if isinstance(column, dict) and column.get("name")
        }
        approved_columns = tuple(
            dict.fromkeys(
                (*view.filter_columns, *view.output_columns, *view.join_columns)
            )
        )
        columns = []
        for name in approved_columns:
            actual = actual_columns.get(name, {})
            semantics = view.column_semantics.get(name, {})
            roles = []
            if name in view.filter_columns:
                roles.append("filter")
            if name in view.output_columns:
                roles.append("output")
            if name in view.join_columns:
                roles.append("join")
            columns.append(
                {
                    "name": name,
                    "type": str(
                        actual.get("data_type")
                        or actual.get("sqlite_type", "")
                    ),
                    "quality": str(actual.get("quality", "unknown")),
                    "roles": roles,
                    "label_zh": semantics.get("label_zh", name),
                    "description": semantics.get("description", ""),
                }
            )
        views.append(
            {
                "name": view.name,
                "chinese_name": view.chinese_name,
                "domain": view.domain,
                "purpose": view.purpose,
                "description": view.description,
                "grain": view.grain,
                "keywords": list(view.keywords),
                "aliases": list(view.aliases),
                "row_count": int(table.get("row_count", 0)),
                "columns": columns,
                "limitations": limitation_map.get(view.name, []),
            }
        )
    return {
        "catalog_version": catalog.version,
        "snapshot": database_profile.get("database", {}).get("file_name"),
        "data_source": {
            key: database_profile.get("database", {}).get(key)
            for key in ("source_id", "source_kind", "dataset_label", "database_name", "schema")
            if database_profile.get("database", {}).get(key) is not None
        },
        "views": views,
        "business_rules": list(catalog.business_rules),
        "relationships": [
            {
                "id": item.id,
                "topic": item.topic,
                "left_view": item.left_view,
                "right_view": item.right_view,
                "keys": [
                    {"left": left, "right": right} for left, right in item.keys
                ],
                "cardinality": item.cardinality,
                "status": item.status,
                "required_all_keys": item.required_all_keys,
                "description": item.description,
                "coverage_evidence": item.coverage_evidence,
                "grain_warning": item.grain_warning,
            }
            for item in catalog.relationships
        ],
        "join_policies": list(catalog.join_policies),
        "semantic_equivalences": list(catalog.semantic_equivalences),
        "semantic_conflicts": list(catalog.semantic_conflicts),
        "semantic_source": catalog.semantic_source,
        "known_limitations": list(catalog.known_limitations),
    }
