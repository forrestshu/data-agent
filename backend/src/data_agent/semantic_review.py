"""语义审核层：让 AI 为新表/字段生成建议，但只有人工批准后才能修改查询知识。"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from .llm import LLMClient, LLMUnavailable
from .settings import CATALOG_PATH, SEMANTIC_PROPOSALS_PATH


class SemanticReviewError(ValueError):
    """审核边界异常：提案不存在、已处理或建议超出当前数据库结构。"""


class SemanticReviewService:
    """语义治理服务：数据库负责事实、AI 负责候选语义、人负责最终授权。"""

    def __init__(
        self,
        llm_client: LLMClient | None,
        catalog_path: Path = CATALOG_PATH,
        proposals_path: Path = SEMANTIC_PROPOSALS_PATH,
    ) -> None:
        self.llm_client = llm_client
        self.catalog_path = catalog_path.resolve()
        self.proposals_path = proposals_path.resolve()
        self._lock = threading.Lock()

    @staticmethod
    def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
        """持久化层：用原子替换保护审核状态和知识目录。"""

        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f"{path.suffix}.tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)

    def load(self) -> dict[str, Any]:
        """状态层：读取当前语义提案；不存在时返回可直接展示的空状态。"""

        if not self.proposals_path.exists():
            return {
                "status": "not_generated",
                "database_fingerprint": None,
                "generated_at": None,
                "proposals": [],
            }
        try:
            return json.loads(self.proposals_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SemanticReviewError("语义提案文件损坏。") from error

    @staticmethod
    def _schema_changes(profile: dict[str, Any]) -> list[dict[str, Any]]:
        """输入裁剪：只提取新增表和新增字段，不把普通行数据变化发送给大模型。"""

        drift = profile.get("drift", {})
        table_map = {table["name"]: table for table in profile.get("tables", [])}
        changes: list[dict[str, Any]] = []
        for table_name in drift.get("new_tables", []):
            table = table_map.get(table_name)
            if table:
                changes.append(
                    {
                        "kind": "new_table",
                        "target_view": table_name,
                        "target_column": None,
                        "columns": [
                            {
                                "name": column["name"],
                                "type": column.get("data_type") or column.get("sqlite_type", ""),
                                "quality": column["quality"],
                            }
                            for column in table["columns"]
                        ],
                    }
                )
        for table_name, column_names in drift.get("new_columns", {}).items():
            table = table_map.get(table_name)
            if not table:
                continue
            columns = {column["name"]: column for column in table["columns"]}
            for column_name in column_names:
                column = columns.get(column_name)
                if column:
                    changes.append(
                        {
                            "kind": "new_column",
                            "target_view": table_name,
                            "target_column": column_name,
                            "column": {
                                "name": column_name,
                                "type": column.get("data_type") or column.get("sqlite_type", ""),
                                "quality": column["quality"],
                            },
                        }
                    )
        return changes

    @staticmethod
    def _proposal_id(fingerprint: str, kind: str, view: str, column: str | None) -> str:
        """标识层：以数据库版本和目标生成稳定 ID，避免重复同步产生重复提案。"""

        source = f"{fingerprint}:{kind}:{view}:{column or ''}".encode("utf-8")
        return hashlib.sha256(source).hexdigest()[:16]

    def ensure_for_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        """生成入口：结构无变化时不调用 AI；有变化时为人工审核生成语义候选。"""

        fingerprint = str(profile.get("database", {}).get("content_fingerprint", ""))
        existing = self.load()
        if existing.get("database_fingerprint") == fingerprint:
            return existing
        changes = self._schema_changes(profile)
        generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        if not changes:
            payload = {
                "status": "no_schema_changes",
                "database_fingerprint": fingerprint,
                "generated_at": generated_at,
                "proposals": [],
            }
            self._atomic_write(self.proposals_path, payload)
            return payload
        if self.llm_client is None:
            return {
                "status": "ai_not_configured",
                "database_fingerprint": fingerprint,
                "generated_at": generated_at,
                "proposals": [],
                "pending_changes": changes,
            }

        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        system_prompt = """
你是 ERP 数据知识架构师。根据新增数据库视图/字段及现有业务知识，为每个变化生成待人工审核的语义提案。
你只能提出建议，不能声称建议已确认。字段名含义不清时降低 confidence 并在 review_question 中说明需要业务人员确认什么。
不要编造数据样本、关联关系或计算公式。必须输出 JSON：顶层为 proposals 数组，每项包含 kind、target_view、target_column、confidence、reason、review_question、suggestion。
new_column 的 suggestion 包含 label_zh、description、add_to_filter_columns、add_to_output_columns、keywords。
new_table 的 suggestion 包含 domain、purpose、grain、keywords、aliases、filter_columns、output_columns；列只能来自输入结构。
""".strip()
        user_prompt = (
            "现有业务目录 JSON：\n"
            f"{json.dumps(catalog.get('views', []), ensure_ascii=False)}\n\n"
            "数据库结构变化 JSON：\n"
            f"{json.dumps(changes, ensure_ascii=False)}"
        )
        try:
            generated = self.llm_client.complete_json(system_prompt, user_prompt, max_tokens=2400)
        except LLMUnavailable:
            return {
                "status": "ai_unavailable",
                "database_fingerprint": fingerprint,
                "generated_at": generated_at,
                "proposals": [],
                "pending_changes": changes,
            }

        allowed_targets = {
            (change["kind"], change["target_view"], change.get("target_column"))
            for change in changes
        }
        proposals: list[dict[str, Any]] = []
        for raw in generated.get("proposals", []):
            target = (raw.get("kind"), raw.get("target_view"), raw.get("target_column"))
            if target not in allowed_targets or not isinstance(raw.get("suggestion"), dict):
                continue
            proposals.append(
                {
                    "id": self._proposal_id(fingerprint, *target),
                    "kind": target[0],
                    "target_view": target[1],
                    "target_column": target[2],
                    "confidence": max(0.0, min(1.0, float(raw.get("confidence", 0)))),
                    "reason": str(raw.get("reason", "")),
                    "review_question": str(raw.get("review_question", "")),
                    "suggestion": raw["suggestion"],
                    "status": "pending",
                    "reviewed_at": None,
                    "reviewer_note": None,
                }
            )
        payload = {
            "status": "pending_review" if proposals else "ai_output_invalid",
            "database_fingerprint": fingerprint,
            "generated_at": generated_at,
            "provider": self.llm_client.provider,
            "model": self.llm_client.model,
            "proposals": proposals,
        }
        self._atomic_write(self.proposals_path, payload)
        return payload

    @staticmethod
    def _actual_columns(profile: dict[str, Any], view_name: str) -> set[str]:
        """审核校验：从机器画像读取真实字段，拒绝把 AI 幻觉字段写入白名单。"""

        for table in profile.get("tables", []):
            if table["name"] == view_name:
                return {column["name"] for column in table["columns"]}
        return set()

    def _apply_approved(self, proposal: dict[str, Any], profile: dict[str, Any]) -> None:
        """知识写入：只应用当前画像中真实存在的目标，并保留 AI 建议的审核记录。"""

        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        view_name = proposal["target_view"]
        actual_columns = self._actual_columns(profile, view_name)
        if not actual_columns:
            raise SemanticReviewError(f"当前数据库中不存在 {view_name}。")
        suggestion = proposal["suggestion"]
        if proposal["kind"] == "new_column":
            column = proposal["target_column"]
            if column not in actual_columns:
                raise SemanticReviewError(f"当前数据库中不存在字段 {view_name}.{column}。")
            view = next((item for item in catalog["views"] if item["name"] == view_name), None)
            if view is None:
                raise SemanticReviewError(f"知识目录中不存在视图 {view_name}。")
            view.setdefault("column_semantics", {})[column] = {
                "label_zh": str(suggestion.get("label_zh", column)),
                "description": str(suggestion.get("description", "")),
                "approved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            if suggestion.get("add_to_filter_columns") and column not in view["filter_columns"]:
                view["filter_columns"].append(column)
            if suggestion.get("add_to_output_columns") and column not in view["output_columns"]:
                view["output_columns"].append(column)
            for keyword in suggestion.get("keywords", []):
                if isinstance(keyword, str) and keyword and keyword not in view["keywords"]:
                    view["keywords"].append(keyword)
        elif proposal["kind"] == "new_table":
            if any(item["name"] == view_name for item in catalog["views"]):
                raise SemanticReviewError(f"视图 {view_name} 已在知识目录中。")
            filters = [item for item in suggestion.get("filter_columns", []) if item in actual_columns]
            outputs = [item for item in suggestion.get("output_columns", []) if item in actual_columns]
            if not filters or not outputs:
                raise SemanticReviewError("新视图提案必须包含真实的筛选字段和输出字段。")
            catalog["views"].append(
                {
                    "name": view_name,
                    "source_view": f"Cux.{view_name}",
                    "domain": str(suggestion.get("domain", "待确认")),
                    "purpose": str(suggestion.get("purpose", "待确认业务用途")),
                    "grain": str(suggestion.get("grain", "待确认数据粒度")),
                    "keywords": [str(item) for item in suggestion.get("keywords", [])],
                    "aliases": [str(item) for item in suggestion.get("aliases", [])],
                    "filter_columns": filters,
                    "output_columns": outputs,
                    "join_columns": [],
                    "semantic_review": {
                        "approved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                        "proposal_id": proposal["id"],
                    },
                }
            )
        else:
            raise SemanticReviewError("不支持的语义提案类型。")
        self._atomic_write(self.catalog_path, catalog)

    def review(
        self,
        proposal_id: str,
        decision: str,
        reviewer_note: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """审核入口：批准时更新正式语义目录，拒绝时只保存决策；两者都保留可追溯状态。"""

        if decision not in {"approve", "reject"}:
            raise SemanticReviewError("decision 必须是 approve 或 reject。")
        with self._lock:
            payload = self.load()
            proposal = next(
                (item for item in payload.get("proposals", []) if item["id"] == proposal_id),
                None,
            )
            if proposal is None:
                raise SemanticReviewError("未找到语义提案。")
            if proposal["status"] != "pending":
                raise SemanticReviewError("该语义提案已经审核。")
            if decision == "approve":
                self._apply_approved(proposal, profile)
            proposal["status"] = "approved" if decision == "approve" else "rejected"
            proposal["reviewed_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
            proposal["reviewer_note"] = reviewer_note.strip()
            pending = [item for item in payload["proposals"] if item["status"] == "pending"]
            payload["status"] = "pending_review" if pending else "review_complete"
            self._atomic_write(self.proposals_path, payload)
            return payload
