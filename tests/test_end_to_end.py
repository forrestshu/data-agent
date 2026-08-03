"""端到端验收：使用真实 SQLite 快照验证路由、SQL 和结果。"""

from __future__ import annotations

import sqlite3
import unittest

from data_agent.catalog import load_catalog
from data_agent.executor import ClarificationRequired, ReadOnlyQueryService
from data_agent.knowledge_sync import KnowledgeSyncService
from data_agent.router import RouteConfirmationRequired
from data_agent.settings import DEFAULT_DATABASE_PATH


DATABASE_PATH = DEFAULT_DATABASE_PATH


class EndToEndTests(unittest.TestCase):
    """系统链路测试：每条问题从自然语言一直到真实数据行。"""

    @classmethod
    def setUpClass(cls) -> None:
        """创建一个只读服务实例，所有测试共用同一知识版本。"""

        profile = KnowledgeSyncService(DATABASE_PATH).ensure_current(auto_sync=True)
        cls.service = ReadOnlyQueryService(
            DATABASE_PATH,
            load_catalog(),
            database_profile=profile,
        )

    def test_catalog_tables_and_columns_exist_in_snapshot(self) -> None:
        """知识目录中的 16 张表及所有过滤/输出列必须与 SQLite 快照一致。"""

        uri = f"file:{DATABASE_PATH.resolve()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            table_names = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            for view in self.service.catalog.views:
                with self.subTest(view=view.name):
                    self.assertIn(view.name, table_names)
                    columns = {
                        row[1]
                        for row in connection.execute(
                            f'PRAGMA table_info("{view.name}")'
                        )
                    }
                    self.assertTrue(set(view.filter_columns).issubset(columns))
                    self.assertTrue(set(view.output_columns).issubset(columns))
                    self.assertTrue(set(view.join_columns).issubset(columns))

    def test_inventory_question_returns_real_quantity_and_bin(self) -> None:
        """库存问题应路由到现有量表并返回真实库位。"""

        result = self.service.ask("查询物料 110000012 的库存和库位")
        self.assertEqual("AiQueryPartOnHandV", result.route.view_name)
        self.assertEqual("PartNum", result.plan.filter_column)
        self.assertTrue(result.plan.sql.startswith("SELECT "))
        self.assertIn("?", result.plan.sql)
        self.assertIn('"PartNum" AS "物料编码"', result.plan.sql_chinese)
        self.assertEqual("物料编码", result.column_labels["PartNum"])
        self.assertEqual("现有量", result.column_labels["Qty"])
        self.assertIn(":查询值", result.plan.sql_chinese)
        self.assertTrue(any(row["Qty"] == 8290 and row["BinName"] == "原材料货位" for row in result.rows))
        self.assertTrue(any("离线快照" in notice for notice in result.notices))

    def test_fuzzy_route_cannot_query_before_confirmation(self) -> None:
        """模糊候选没有用户确认时必须中断，不能访问后续 SQL 执行流程。"""

        question = "帮我看看物料 110000012 仓里还剩多少"
        with self.assertRaises(RouteConfirmationRequired) as caught:
            self.service.ask(question)
        self.assertEqual("AiQueryPartOnHandV", caught.exception.decision.view_name)
        self.assertTrue(caught.exception.decision.requires_confirmation)

    def test_confirmed_fuzzy_route_returns_real_inventory(self) -> None:
        """用户确认候选视图后，系统才允许继续解析编号并查询真实库存。"""

        question = "帮我看看物料 110000012 仓里还剩多少"
        result = self.service.ask(
            question,
            confirmed_view="AiQueryPartOnHandV",
        )
        self.assertEqual("confirmed", result.route.match_type)
        self.assertFalse(result.route.requires_confirmation)
        self.assertTrue(any(row["Qty"] == 8290 for row in result.rows))

    def test_purchase_price_reports_known_avg_price_gap(self) -> None:
        """采购价问题可返回最新价，但必须显式报告 AvgPrice 快照缺失。"""

        result = self.service.ask("查询物料 6100001876 的最新采购价和平均价")
        self.assertEqual("AiQueryPoPriceV", result.route.view_name)
        self.assertTrue(any(abs(row["NewPrice"] - 3796.09658) < 0.00001 for row in result.rows))
        self.assertTrue(any("AvgPrice" in notice for notice in result.notices))

    def test_project_question_returns_customer_machine_and_status(self) -> None:
        """项目问题应返回客户、机型、状态和日期字段。"""

        result = self.service.ask("查询项目 24M148-B 的项目客户、项目机型和项目状态")
        self.assertEqual("AiQueryProjectV", result.route.view_name)
        self.assertEqual("三辊行星轧机", result.rows[0]["MachineType"])
        self.assertEqual("有效", result.rows[0]["ProjectStatus"])

    def test_job_progress_question_returns_reported_quantities(self) -> None:
        """工单进度问题应区分报工数量和末道工序完成数量。"""

        result = self.service.ask("查询工单 000022 的报工数量和末道工序")
        self.assertEqual("AiQueryJobProgressV", result.route.view_name)
        self.assertEqual(10, result.rows[0]["LaborQty"])
        self.assertEqual(10, result.rows[0]["JobOprCompQty"])

    def test_material_identity_question_returns_description(self) -> None:
        """物料身份问题应进入基础物料表，而不是库存或采购表。"""

        result = self.service.ask("查询物料 110000001 的物料描述")
        self.assertEqual("AiQueryPartV", result.route.view_name)
        self.assertEqual("16Mn钢板30", result.rows[0]["PartDescription"])

    def test_fuzzy_material_description_runs_full_query(self) -> None:
        """物料描述支持字面量子串模糊查询，并保持 SQL 参数化。"""

        result = self.service.ask("通过物料描述 TS机柜 查询最新采购价")
        self.assertEqual("AiQueryPoPriceV", result.route.view_name)
        self.assertEqual("LineDesc", result.plan.filter_column)
        self.assertEqual("contains", result.plan.match_mode)
        self.assertEqual("%TS机柜%", result.plan.parameters[0])
        self.assertIn("包含匹配", result.plan.sql_chinese)
        self.assertTrue(any("TS机柜" in row["LineDesc"] for row in result.rows))

    def test_missing_identifier_requests_clarification(self) -> None:
        """只有意图没有业务编码时，流程必须停止并请用户补充。"""

        with self.assertRaisesRegex(ClarificationRequired, "具体业务对象"):
            self.service.ask("查询某个物料的库存和库位")

    def test_global_inventory_sum_uses_safe_aggregate_plan(self) -> None:
        """全局合计允许没有物料号，但统计函数和字段必须来自受控操作。"""

        result = self.service.ask(
            "所有物料的库存数量合计",
            operation="sum",
            metric_column="Qty",
        )
        self.assertEqual("sum", result.plan.operation)
        self.assertIsNone(result.plan.filter_column)
        self.assertEqual((), result.plan.parameters)
        self.assertAlmostEqual(3728843.4834, result.rows[0]["Qty合计"])

    def test_material_kind_count_uses_distinct_whitelisted_column(self) -> None:
        """物料种类数通过白名单字段去重计数，不依赖用户提供 SQL。"""

        route = self.service.router.route("物料一览")
        result = self.service.ask(
            "物料一览共有多少种物料",
            route_decision=route,
            operation="count_distinct",
            metric_column="PartNum",
        )
        self.assertEqual("count_distinct", result.plan.operation)
        self.assertGreater(result.rows[0]["PartNum去重数量"], 0)

    def test_aggregate_rejects_non_whitelisted_metric(self) -> None:
        """统计字段仍受知识目录白名单保护，不能把用户文本当作 SQL 标识符。"""

        with self.assertRaisesRegex(ClarificationRequired, "统计"):
            self.service.ask(
                "所有物料的库存数量合计",
                operation="sum",
                metric_column="Qty) FROM sqlite_master --",
            )


if __name__ == "__main__":
    unittest.main()
