"""模型语义投影：把完整治理目录压缩成稳定、有限的提示词卡片。"""

from __future__ import annotations

from pathlib import Path

from .catalog import KnowledgeCatalog


PROMPT_ROOT = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str, **values: str) -> str:
    """读取 Markdown 提示词，并只替换显式的双花括号变量。"""

    template = (PROMPT_ROOT / name).read_text(encoding="utf-8").strip()
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def build_prompt_knowledge(catalog: KnowledgeCatalog) -> str:
    """保留全部已审核视图、字段和可执行关联，同时限制提示词体积。"""

    label_overrides = {
        ("AiQueryBomV", "PartNum"): "上级部件编码",
        ("AiQueryBomV", "PartDescription"): "上级部件描述",
        ("AiQueryPayablesV", "VendorNum"): "供应商内部编号",
        ("AiQueryReceivablesV", "CustNum"): "客户内部编号",
        ("AiQuerySoOverViewV", "PONum"): "客户采购订单号/参考号",
    }
    view_lines: list[str] = []
    for view in catalog.views:
        approved_columns = dict.fromkeys(
            (*view.filter_columns, *view.output_columns, *view.join_columns)
        )
        columns = []
        for name in approved_columns:
            if name == "Company":
                continue
            label = label_overrides.get(
                (view.name, name),
                view.column_semantics.get(name, {}).get("label_zh", name),
            )
            columns.append(f"{name}={label}")
        view_lines.append(
            f"{view.name}|{view.purpose}|{view.grain}|" + ",".join(columns)
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
        relationships.append(
            f"{relationship.left_view}+{relationship.right_view}({keys}){risk}"
        )
    return "\n".join(view_lines) + "\nJOIN:" + ";".join(relationships)
