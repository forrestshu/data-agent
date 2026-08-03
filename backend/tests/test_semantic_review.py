"""新增结构语义治理验收：AI 只提议，人工批准后才能修改知识目录。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from data_agent.semantic_review import SemanticReviewService


class FakeSemanticLLM:
    """测试替身：为真实存在的新字段返回一项语义建议。"""

    provider = "deepseek"
    model = "deepseek-v4-flash"

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> dict[str, Any]:
        """返回可审核建议，避免单元测试依赖外部网络。"""

        return {
            "proposals": [
                {
                    "kind": "new_column",
                    "target_view": "AiQueryPartOnHandV",
                    "target_column": "SafetyStock",
                    "confidence": 0.9,
                    "reason": "字段名表示安全库存",
                    "review_question": "是否允许作为输出字段？",
                    "suggestion": {
                        "label_zh": "安全库存",
                        "description": "物料安全库存阈值",
                        "add_to_filter_columns": False,
                        "add_to_output_columns": True,
                        "keywords": ["安全库存"],
                    },
                }
            ]
        }

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        """满足统一协议；语义提案流程不会调用文本回答。"""

        return ""


class SemanticReviewTests(unittest.TestCase):
    """审核闭环：验证新增字段不会在 AI 生成建议时自动进入白名单。"""

    def test_new_column_requires_human_approval_before_catalog_update(self) -> None:
        """生成建议不改目录，人工批准后才添加字段语义和输出白名单。"""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog_path = root / "catalog.json"
            proposals_path = root / "semantic-proposals.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "views": [
                            {
                                "name": "AiQueryPartOnHandV",
                                "source_view": "Cux.AiQueryPartOnHandV",
                                "domain": "库存",
                                "purpose": "查询库存",
                                "grain": "物料库位",
                                "keywords": ["库存"],
                                "aliases": [],
                                "filter_columns": ["PartNum"],
                                "output_columns": ["PartNum", "Qty"],
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            profile = {
                "database": {"content_fingerprint": "new-fingerprint"},
                "drift": {
                    "new_tables": [],
                    "new_columns": {"AiQueryPartOnHandV": ["SafetyStock"]},
                },
                "tables": [
                    {
                        "name": "AiQueryPartOnHandV",
                        "columns": [
                            {"name": "PartNum", "sqlite_type": "TEXT", "quality": {}},
                            {"name": "Qty", "sqlite_type": "REAL", "quality": {}},
                            {"name": "SafetyStock", "sqlite_type": "REAL", "quality": {}},
                        ],
                    }
                ],
            }
            service = SemanticReviewService(
                FakeSemanticLLM(),
                catalog_path=catalog_path,
                proposals_path=proposals_path,
            )

            state = service.ensure_for_profile(profile)
            before = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual("pending_review", state["status"])
            self.assertNotIn("SafetyStock", before["views"][0]["output_columns"])

            reviewed = service.review(
                state["proposals"][0]["id"],
                decision="approve",
                reviewer_note="业务确认",
                profile=profile,
            )
            after = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual("review_complete", reviewed["status"])
            self.assertIn("SafetyStock", after["views"][0]["output_columns"])
            self.assertEqual(
                "安全库存",
                after["views"][0]["column_semantics"]["SafetyStock"]["label_zh"],
            )


if __name__ == "__main__":
    unittest.main()
