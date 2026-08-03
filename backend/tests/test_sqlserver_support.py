"""SQL Server 双数据源、T-SQL 守卫与安全 API 验收。"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock

from fastapi.testclient import TestClient

from data_agent.ai_agent import AIQueryAgent
from data_agent.api import create_app
from data_agent.catalog import load_catalog
from data_agent.data_sources import (
    DataSourceRegistry,
    SQLITE_SOURCE_ID,
    SQLSERVER_SOURCE_ID,
    build_source_configs,
)
from data_agent.knowledge_sync import KnowledgeSyncService
from data_agent.settings import DEFAULT_DATABASE_PATH
from data_agent.sql_guard import SQLGuard, SQLValidationError
from data_agent.sqlserver_knowledge_sync import SQLServerKnowledgeSyncService


class SQLServerSupportTests(unittest.TestCase):
    """不访问网络即可证明方言映射、越权阻断和切换状态契约。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.profile = KnowledgeSyncService(DEFAULT_DATABASE_PATH).ensure_current(
            auto_sync=True
        )
        cls.source = build_source_configs()[SQLSERVER_SOURCE_ID]
        cls.guard = SQLGuard(
            cls.catalog,
            cls.profile,
            source=cls.source,
        )

    def test_tsql_preview_uses_top_and_fixed_cux_schema(self) -> None:
        validated = self.guard.validate(
            "SELECT PartNum, PartDescription FROM AiQueryPartV "
            "WHERE PartDescription LIKE ? ORDER BY PartNum",
            ("%螺栓%",),
            requested_limit=100,
        )
        self.assertIn("SELECT TOP 100", validated.sql)
        self.assertIn("FROM Cux.AiQueryPartV", validated.sql)
        self.assertNotIn("LIMIT", validated.sql)
        self.assertIn("ORDER BY PartNum", validated.base_sql)
        self.assertNotIn("ORDER BY", validated.count_sql)
        self.assertIn("COUNT_BIG(*)", validated.count_sql)

    def test_tsql_guard_accepts_only_complete_approved_join_keys(self) -> None:
        approved = self.guard.validate(
            "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
            "JOIN AiQueryPartOnHandV o "
            "ON p.Company = o.Company AND p.PartNum = o.PartNum",
            (),
            requested_limit=100,
        )
        self.assertIn("JOIN Cux.AiQueryPartOnHandV", approved.sql)
        with self.assertRaises(SQLValidationError):
            self.guard.validate(
                "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
                "JOIN AiQueryPartOnHandV o ON p.PartNum = o.PartNum",
                (),
                requested_limit=100,
            )

    def test_tsql_cte_count_hoists_with_clause(self) -> None:
        validated = self.guard.validate(
            "WITH materials AS ("
            "SELECT PartNum FROM AiQueryPartV"
            ") SELECT PartNum FROM materials ORDER BY PartNum",
            (),
            requested_limit=100,
        )
        self.assertTrue(validated.count_sql.startswith("WITH materials AS"))
        self.assertIn("SELECT COUNT_BIG(*)", validated.count_sql)
        self.assertNotIn("FROM (WITH ", validated.count_sql)

    def test_tsql_guard_rejects_write_external_and_cross_schema_paths(self) -> None:
        invalid_sql = (
            "DELETE FROM AiQueryPartV",
            "SELECT PartNum INTO copied FROM AiQueryPartV",
            "SELECT PartNum FROM dbo.AiQueryPartV",
            "SELECT PartNum FROM other.prod.AiQueryPartV",
            "SELECT PartNum FROM AiQueryPartV WITH (NOLOCK)",
            "SELECT PartNum FROM AiQueryPartV OPTION (MAXDOP 1)",
            "SELECT * FROM AiQueryPartV",
            "SELECT PartNum FROM sys.tables",
        )
        for sql in invalid_sql:
            with self.subTest(sql=sql):
                with self.assertRaises(SQLValidationError):
                    self.guard.validate(sql, (), requested_limit=100)

    def test_sqlserver_prompt_uses_tsql_not_sqlite_limit(self) -> None:
        agent = AIQueryAgent(
            self.catalog,
            None,
            database_profile=self.profile,
            source=self.source,
        )
        prompt = agent._system_prompt()
        self.assertIn("SQL Server T-SQL", prompt)
        self.assertIn("TOP N", prompt)
        self.assertIn("不要使用 LIMIT", prompt)
        self.assertIn("SELECT INTO", prompt)

    def test_active_source_persists_only_source_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "active_source.json"
            registry = DataSourceRegistry(
                active_source_id=SQLITE_SOURCE_ID,
                state_path=state_path,
            )
            registry.activate(SQLSERVER_SOURCE_ID)
            stored = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual({"active_source_id": SQLSERVER_SOURCE_ID}, stored)
            restored = DataSourceRegistry(state_path=state_path)
            self.assertEqual(SQLSERVER_SOURCE_ID, restored.active_source_id)

    def test_data_source_api_never_exposes_credentials(self) -> None:
        app = create_app(
            use_environment_ai=False,
            require_ai=False,
            source_id=SQLITE_SOURCE_ID,
            persist_source=False,
        )
        with TestClient(app) as client:
            response = client.get("/api/data-sources")
        self.assertEqual(200, response.status_code)
        payload_text = response.text.casefold()
        self.assertNotIn("password", payload_text)
        self.assertNotIn("username", payload_text)
        self.assertNotIn("dataagent", payload_text)
        self.assertEqual(SQLITE_SOURCE_ID, response.json()["active_source_id"])

    def test_sqlserver_statistics_use_bounded_parallel_workers(self) -> None:
        service = SQLServerKnowledgeSyncService(self.source)
        tables = [
            {
                "name": f"AiQueryTest{index}V",
                "row_count": 0,
                "statistics_status": "not_scanned",
                "columns": [{"name": "Value", "quality": "unknown"}],
            }
            for index in range(4)
        ]
        lock = threading.Lock()
        active = 0
        maximum_active = 0

        def fake_scan(table: dict[str, object]) -> str:
            nonlocal active, maximum_active
            with lock:
                active += 1
                maximum_active = max(maximum_active, active)
            time.sleep(0.02)
            table["statistics_status"] = "ready"
            with lock:
                active -= 1
            return "ready"

        service._scan_table_statistics = fake_scan  # type: ignore[method-assign]
        service._add_statistics(tables, schema_fingerprint="current")
        self.assertEqual(2, maximum_active)
        self.assertTrue(
            all(table["statistics_status"] == "ready" for table in tables)
        )

    def test_sqlserver_known_failure_obeys_retry_cooldown(self) -> None:
        service = SQLServerKnowledgeSyncService(self.source)
        table = {
            "name": "AiQueryProjRevCstV",
            "row_count": 0,
            "statistics_status": "not_scanned",
            "columns": [{"name": "ProjectID", "quality": "unknown"}],
        }
        failed_at = time.time()
        previous = {
            "database": {"schema_fingerprint": "same-schema"},
            "tables": [
                {
                    **table,
                    "statistics_status": "unknown",
                    "statistics_error": "OperationalError",
                    "statistics_failed_at": failed_at,
                }
            ],
        }
        scanner = Mock(return_value="ready")
        service._scan_table_statistics = scanner
        service._add_statistics(
            [table],
            previous=previous,
            schema_fingerprint="same-schema",
        )
        scanner.assert_not_called()
        self.assertEqual("unknown", table["statistics_status"])
        self.assertGreater(table["statistics_retry_after"], failed_at)

    def test_sqlserver_switch_uses_fast_preflight_instead_of_full_sync(self) -> None:
        app = create_app(
            use_environment_ai=False,
            require_ai=False,
            source_id=SQLITE_SOURCE_ID,
            persist_source=False,
        )
        manager = app.state.knowledge_by_source[SQLSERVER_SOURCE_ID]
        sqlite_profile = KnowledgeSyncService(DEFAULT_DATABASE_PATH).ensure_current(
            auto_sync=True
        )
        manager.prepare_for_activation = Mock(return_value=sqlite_profile)
        manager.ensure_current = Mock(return_value=sqlite_profile)
        manager.status = Mock(
            return_value={
                "status": "ready",
                "generated_at": sqlite_profile.get("generated_at"),
            }
        )
        manager.sync = Mock()
        with TestClient(app) as client:
            response = client.put(
                "/api/data-sources/active",
                json={"source_id": SQLSERVER_SOURCE_ID},
            )
        self.assertEqual(200, response.status_code)
        manager.prepare_for_activation.assert_called_once_with()
        manager.sync.assert_not_called()


if __name__ == "__main__":
    unittest.main()
