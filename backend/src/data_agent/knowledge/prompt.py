"""模型语义投影：把完整治理目录压缩成稳定、有限的提示词卡片。"""

from __future__ import annotations

from pathlib import Path

from .semantic_catalog import SemanticCatalog


PROMPT_ROOT = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str, **values: str) -> str:
    """读取 Markdown 提示词，并只替换显式的双花括号变量。"""

    template = (PROMPT_ROOT / name).read_text(encoding="utf-8").strip()
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def build_semantic_context(catalog: SemanticCatalog) -> str:
    """保留全部已审核视图、字段和可执行关联，同时限制提示词体积。"""

    view_lines: list[str] = []
    for view in catalog.views:
        approved_columns = dict.fromkeys(
            (*view.filter_columns, *view.output_columns, *view.join_columns)
        )
        columns = []
        for name in approved_columns:
            if name == "Company":
                columns.append("Company=公司代码")
                continue
            semantic = view.column_semantics[name]
            business_name = semantic["business_name"]
            description = str(semantic["description"]).removesuffix("。")
            examples = "、".join(semantic["value_examples"])
            example_text = f"；例：{examples}" if examples else ""
            columns.append(
                f"{name}={business_name}（{description}{example_text}）"
            )
        view_lines.append(
            f"{view.name}|{view.business_name}|{view.purpose}|{view.grain}|"
            + ",".join(columns)
        )

    relationships = []
    for relationship in catalog.relationships:
        if not relationship.executable:
            continue
        keys = ",".join(
            left if left == right else f"{left}={right}"
            for left, right in relationship.keys
        )
        risk = "!" if relationship.status == "approved_with_risk" else ""
        guidance = relationship.grain_warning.removesuffix("。")
        relationships.append(
            f"{relationship.left_view}+{relationship.right_view}({keys}){risk}"
            f"[{relationship.cardinality}；{guidance}]"
        )
    return "\n".join(view_lines) + "\nJOIN:" + ";".join(relationships)
