"""知识同步验收：用 07-08 画像对比 07-15 快照，验证数据变化可被发现。"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from data_agent.knowledge_sync import KnowledgeSyncService
from data_agent.settings import CATALOG_PATH, PROJECT_ROOT


ORIGINAL_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "sqlite" / "data-agent-2026-07-08.sqlite"
)
UPDATED_DATABASE_PATH = (
    PROJECT_ROOT / "data" / "sqlite" / "data-agent-2026-7-15.sqlite"
)


class KnowledgeSyncTests(unittest.TestCase):
    """同步层测试：保证新快照会更新画像，但不会改写人工业务语义。"""

    def test_updated_snapshot_reports_row_changes_and_keeps_schema_compatible(self) -> None:
        """07-15 行数变化应被记录，同时相同字段结构仍可安全查询。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog_path = root / "view_catalog.json"
            profile_path = root / "database_profile.json"
            report_path = root / "knowledge_sync_report.json"
            shutil.copy2(CATALOG_PATH, catalog_path)

            # 测试状态层：先从 07-08 真实数据库生成独立基线，避免依赖项目当前默认画像。
            baseline_service = KnowledgeSyncService(
                ORIGINAL_DATABASE_PATH,
                catalog_path=catalog_path,
                profile_path=profile_path,
                report_path=report_path,
            )
            baseline_service.sync()

            # 更新验证层：在同一份临时知识文件上切换到 07-15，检查真实漂移结果。
            service = KnowledgeSyncService(
                UPDATED_DATABASE_PATH,
                catalog_path=catalog_path,
                profile_path=profile_path,
                report_path=report_path,
            )

            report = service.sync()
            changes = {
                item["table"]: item
                for item in report["drift"]["row_count_changes"]
            }
            self.assertEqual("ready", report["status"])
            self.assertEqual(2, changes["AiQueryPartOnHandV"]["delta"])
            self.assertEqual({}, report["drift"]["new_columns"])
            self.assertEqual([], report["compatibility"]["invalid_views"])

            updated_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual(
                "查询物料现有量、库位和货位",
                next(
                    view["purpose"]
                    for view in updated_catalog["views"]
                    if view["name"] == "AiQueryPartOnHandV"
                ),
            )


if __name__ == "__main__":
    unittest.main()
