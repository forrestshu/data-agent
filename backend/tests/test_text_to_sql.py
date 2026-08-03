"""Text-to-SQL 验收：验证 Knowledge grounding、AST 安全和真实 SQLite 执行。"""

from __future__ import annotations

import unittest
from typing import Any

from data_agent.ai_agent import AIQueryAgent, IntentAnalysis
from data_agent.catalog import build_query_knowledge, load_catalog
from data_agent.executor import ReadOnlyQueryService
from data_agent.knowledge_sync import KnowledgeSyncService
from data_agent.router import RouteDecision
from data_agent.settings import DEFAULT_DATABASE_PATH
from data_agent.sql_guard import SQLGuard, SQLValidationError


class RepairingLLMClient:
    """测试替身：第一次生成危险 SQL，第二次根据守卫反馈修复为安全查询。"""

    provider = "deepseek"
    model = "deepseek-v4-flash"

    def __init__(self) -> None:
        self.json_calls = 0

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> dict[str, Any]:
        """按调用次数返回危险计划和修复后的参数化查询。"""

        self.json_calls += 1
        common = {
            "status": "ready",
            "confidence": 0.95,
            "intent_summary": "查询螺栓类物料",
            "route_reason": "物料描述支持包含匹配",
            "clarification_question": None,
            "matched_concepts": ["螺栓", "物料"],
            "source_views": ["AiQueryPartV"],
            "assumptions": [],
        }
        if self.json_calls == 1:
            return {**common, "sql": "SELECT * FROM AiQueryPartV", "parameters": []}
        return {
            **common,
            "sql": "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ? LIMIT 20",
            "parameters": ["%螺栓%"],
        }

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        """回答能力不属于本测试重点，返回固定文本。"""

        return "找到螺栓类物料。"


class ScalarAggregateRepairingLLMClient:
    """测试替身：模拟模型先把单值库存总量错误拆成分组结果，再按粒度守卫修复。"""

    provider = "deepseek"
    model = "deepseek-v4-flash"

    def __init__(self) -> None:
        """记录模型调用与修复提示，验证错误 SQL 不会直接进入执行层。"""

        self.json_calls = 0
        self.user_prompts: list[str] = []

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> dict[str, Any]:
        """第一次附加普通字段和分组，第二次只保留单个 SUM 输出。"""

        self.json_calls += 1
        self.user_prompts.append(user_prompt)
        common = {
            "status": "ready",
            "confidence": 0.98,
            "intent_summary": "查询指定物料库存总量",
            "route_reason": "库存视图包含物料描述和库存数量",
            "clarification_question": None,
            "matched_concepts": ["GCr15圆钢Φ45", "库存"],
            "source_views": ["AiQueryPartOnHandV"],
            "filter_constraints": [
                {
                    "column": "PartDescription",
                    "operator": "contains",
                    "value": "GCr15圆钢Φ45",
                }
            ],
            "requested_fields": ["Qty"],
            "parameters": ["%GCr15圆钢Φ45%"],
            "assumptions": [],
        }
        if self.json_calls == 1:
            return {
                **common,
                # 故意省略 result_shape，证明原问题语义兜底也能拦住旧模型输出。
                "sql": (
                    "SELECT PartNum, PartDescription, SUM(Qty) AS TotalQty "
                    "FROM AiQueryPartOnHandV WHERE PartDescription LIKE ? "
                    "GROUP BY PartNum, PartDescription"
                ),
            }
        return {
            **common,
            "result_shape": "scalar",
            "sql": (
                "SELECT SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV "
                "WHERE PartDescription LIKE ?"
            ),
        }

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        """本测试只覆盖查询规划，回答层返回固定文本。"""

        return "当前库存总量为 21373.997。"


class TolerantMetadataLLMClient:
    """测试替身：SQL 正确但辅助元数据使用模型自然产生的非标准别名。"""

    provider = "deepseek"
    model = "deepseek-v4-flash"

    def __init__(self) -> None:
        """记录调用次数，证明元数据别名不会浪费一次模型修复。"""

        self.json_calls = 0

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> dict[str, Any]:
        """返回 `=` 和 single_value，但 SQL 本身满足安全与业务粒度要求。"""

        self.json_calls += 1
        return {
            "status": "success",
            "confidence": "very high",
            "intent_summary": "查询指定物料库存总量",
            "filter_constraints": [
                {
                    "field": "PartDescription",
                    "operator": "=",
                    "value": "GCr15圆钢Φ45",
                },
                "模型偶发生成的无效辅助项",
            ],
            "requested_fields": ["PartNum", "PartDescription", "Qty"],
            "result_shape": "single_value",
            "operation": "模型自由描述的未知操作",
            "source_views": ["模型自报值不作为事实"],
            "sql": (
                "SELECT SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV "
                "WHERE PartDescription = ?"
            ),
            "parameters": ["GCr15圆钢Φ45"],
        }

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        """本测试只覆盖理解层，回答层返回固定文本。"""

        return "当前库存总量为 21373.997。"


class TextToSQLTests(unittest.TestCase):
    """安全链路测试：模型可组合 SELECT，但权限、资源和执行均由后端决定。"""

    @classmethod
    def setUpClass(cls) -> None:
        """加载当前语义层与真实数据库画像，所有测试保持只读。"""

        cls.catalog = load_catalog()
        cls.profile = KnowledgeSyncService(DEFAULT_DATABASE_PATH).ensure_current(auto_sync=True)
        cls.guard = SQLGuard(cls.catalog, cls.profile)
        cls.service = ReadOnlyQueryService(
            DEFAULT_DATABASE_PATH,
            cls.catalog,
            database_profile=cls.profile,
        )

    def test_knowledge_context_contains_semantics_but_no_business_rows(self) -> None:
        """模型提示应包含用途、粒度、字段类型与质量，但不包含业务数据样本。"""

        knowledge = build_query_knowledge(self.catalog, self.profile)
        part_view = next(item for item in knowledge["views"] if item["name"] == "AiQueryPartV")
        self.assertIn("物料", part_view["domain"])
        self.assertTrue(any(item["name"] == "PartDescription" for item in part_view["columns"]))
        self.assertNotIn("null_count", part_view["columns"][0])
        self.assertNotIn("path", knowledge)
        self.assertEqual([], knowledge["business_rules"])
        self.assertEqual(12, len(knowledge["relationships"]))
        company = next(item for item in part_view["columns"] if item["name"] == "Company")
        self.assertEqual(["join"], company["roles"])
        self.assertIn("公司", company["description"])
        purchase_progress = next(
            item for item in knowledge["views"] if item["name"] == "AiQueryPoProgressV"
        )
        self.assertIn("查询供应商", purchase_progress["purpose"])
        purchase_columns = {
            item["name"]: item["roles"] for item in purchase_progress["columns"]
        }
        self.assertIn("filter", purchase_columns["LineDesc"])
        self.assertIn("output", purchase_columns["VendorName"])

    def test_prompt_prefers_precomputed_business_fields_and_preserves_parameters(self) -> None:
        """提示词必须阻止二次聚合、参数截断、错误编码字段和应收应付串域。"""

        agent = AIQueryAgent(
            self.catalog,
            llm_client=None,
            database_profile=self.profile,
            allow_fallback=False,
        )
        prompt = agent._system_prompt()

        self.assertIn("直接查询 AiQueryPoPriceV.AvgPrice", prompt)
        self.assertIn("不生成 AVG(AvgPrice)", prompt)
        self.assertIn("汇总字段擅自 SUM", prompt)
        self.assertIn("“钢板30”不能缩短为“钢板”", prompt)
        self.assertIn("分别筛选 ProjectID、JobNum、PartNum", prompt)
        self.assertIn("PONum、OrderQty、ReceivedQty、InvoiceQty、RemainQty", prompt)
        self.assertIn("不得只因公司名称相似就在应付与应收之间切换", prompt)
        self.assertIn("优先匹配 JobOprCompQty", prompt)

    def test_semantic_catalog_covers_every_documented_column(self) -> None:
        """权威文档中的 16 张视图和 154 个字段必须完整进入正式语义层。"""

        self.assertEqual(16, len(self.catalog.views))
        self.assertEqual(
            154,
            sum(len(view.column_semantics) for view in self.catalog.views),
        )
        self.assertTrue(all("Company" in view.join_columns for view in self.catalog.views))
        self.assertEqual(12, len({item.id for item in self.catalog.relationships}))

    def test_guard_accepts_complete_approved_join(self) -> None:
        """物料与库存必须使用 Company + PartNum 完整双键关联。"""

        validated = self.guard.validate(
            "SELECT p.PartNum, p.PartDescription, o.BinNum, o.Qty "
            "FROM AiQueryPartV AS p "
            "JOIN AiQueryPartOnHandV AS o "
            "ON p.Company = o.Company AND p.PartNum = o.PartNum",
            [],
            requested_limit=20,
        )
        self.assertEqual(("AiQueryPartV", "AiQueryPartOnHandV"), validated.source_views)

    def test_guard_rejects_partial_cross_and_unapproved_joins(self) -> None:
        """缺公司键、恒真条件和未批准视图组合都不能进入执行器。"""

        invalid_sql = (
            "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
            "JOIN AiQueryPartOnHandV o ON p.PartNum = o.PartNum",
            "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
            "JOIN AiQueryPartOnHandV o ON 1 = 1",
            "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
            "JOIN AiQueryPartOnHandV o",
            "SELECT s.PartNum, o.Qty FROM AiQuerySoOverViewV s "
            "JOIN AiQueryPartOnHandV o "
            "ON s.Company = o.Company AND s.PartNum = o.PartNum",
        )
        for sql in invalid_sql:
            with self.subTest(sql=sql):
                with self.assertRaises(SQLValidationError):
                    self.guard.validate(sql, [], requested_limit=20)

    def test_guard_accepts_both_bom_material_roles(self) -> None:
        """BOM 上级件和子物料是两个不同但都已批准的关系。"""

        for bom_column in ("PartNum", "ECOMtl_MtlPartNum"):
            sql = (
                "SELECT p.PartNum, b.MtlPartDescription FROM AiQueryPartV p "
                "JOIN AiQueryBomV b ON p.Company = b.Company "
                f"AND p.PartNum = b.{bom_column}"
            )
            with self.subTest(bom_column=bom_column):
                self.guard.validate(sql, [], requested_limit=20)

    def test_guard_blocks_direct_aggregation_on_risky_relationship(self) -> None:
        """采购明细与应付汇总粒度不同，直接 JOIN 后汇总必须被阻止。"""

        sql = (
            "SELECT p.VendorID, SUM(a.RemainAmount) AS total_remain "
            "FROM AiQueryPoProgressV p JOIN AiQueryPayablesV a "
            "ON p.Company = a.Company AND p.VendorID = a.VendorID "
            "GROUP BY p.VendorID"
        )
        with self.assertRaisesRegex(SQLValidationError, "粒度放大"):
            self.guard.validate(sql, [], requested_limit=20)

    def test_safe_parameterized_fuzzy_sql_is_limited(self) -> None:
        """描述包含查询允许执行，并由守卫把返回条数限制到请求上限。"""

        validated = self.guard.validate(
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ? LIMIT 99",
            ["%螺栓%"],
            requested_limit=20,
        )
        self.assertEqual(("AiQueryPartV",), validated.source_views)
        self.assertTrue(validated.sql.endswith("LIMIT 20"))
        self.assertEqual(("%螺栓%",), validated.parameters)

    def test_preview_limit_is_removed_from_complete_query_when_user_did_not_ask(self) -> None:
        """模型擅自添加的 500 行预览不能污染完整结果计数与 Excel 导出。"""

        validated = self.guard.validate(
            "SELECT PartNum, PartDescription FROM AiQueryPartV LIMIT 500",
            [],
            requested_limit=500,
            preserve_query_limit=False,
        )
        self.assertNotIn("LIMIT", validated.base_sql)
        self.assertTrue(validated.sql.endswith("LIMIT 500"))

    def test_generated_fuzzy_sql_returns_real_bolt_materials(self) -> None:
        """Text-to-SQL 通过后应从真实快照返回描述包含螺栓的物料。"""

        route = RouteDecision(
            view_name="AiQueryPartV",
            confidence=0.95,
            reason="物料描述包含匹配",
            matched_terms=("螺栓",),
            alternatives=(),
            match_type="ai",
            requires_confirmation=False,
            confirmation_question=None,
        )
        result = self.service.ask_generated_sql(
            "有没有螺栓之类的",
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ? LIMIT 20",
            ("%螺栓%",),
            route,
            limit=20,
        )
        self.assertEqual("text_to_sql", result.plan.operation)
        self.assertGreater(len(result.rows), 0)
        self.assertLessEqual(len(result.rows), 20)
        self.assertTrue(all("螺栓" in str(row["PartDescription"]) for row in result.rows))

    def test_generated_like_prefers_exact_match_when_full_description_exists(self) -> None:
        """两阶段筛选第一步命中完整描述时，结果计划应保留等值筛选而不扩大范围。"""

        route = RouteDecision(
            view_name="AiQueryPartV",
            confidence=0.95,
            reason="物料描述包含匹配",
            matched_terms=("GCr15圆钢Φ45",),
            alternatives=(),
            match_type="ai",
            requires_confirmation=False,
            confirmation_question=None,
        )
        result = self.service.ask_generated_sql(
            "查询描述为GCr15圆钢Φ45的物料编码",
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ?",
            ("%GCr15圆钢Φ45%",),
            route,
            limit=20,
        )
        self.assertIn("=", result.plan.base_sql or "")
        self.assertNotIn(" LIKE ", (result.plan.base_sql or "").upper())
        self.assertEqual(("GCr15圆钢Φ45",), result.plan.parameters)
        self.assertTrue(all(row["PartDescription"] == "GCr15圆钢Φ45" for row in result.rows))

    def test_scalar_inventory_sum_keeps_one_row_during_exact_match(self) -> None:
        """单值库存汇总进入精确阶段时只能替换筛选条件，不能增加字段或分组。"""

        route = RouteDecision(
            view_name="AiQueryPartOnHandV",
            confidence=0.98,
            reason="按完整物料描述汇总库存",
            matched_terms=("GCr15圆钢Φ45",),
            alternatives=(),
            match_type="ai",
            requires_confirmation=False,
            confirmation_question=None,
        )
        result = self.service.ask_generated_sql(
            "查询GCr15圆钢Φ45还有多少库存",
            (
                "SELECT SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV "
                "WHERE PartDescription LIKE ?"
            ),
            ("%GCr15圆钢Φ45%",),
            route,
        )

        self.assertEqual(1, len(result.rows))
        self.assertAlmostEqual(21373.997, result.rows[0]["TotalQty"])
        self.assertIn(" = ?", result.plan.base_sql or "")
        self.assertNotIn("GROUP BY", (result.plan.base_sql or "").upper())
        self.assertEqual(("GCr15圆钢Φ45",), result.plan.parameters)

    def test_generated_like_falls_back_to_contains_when_exact_has_no_row(self) -> None:
        """两阶段筛选第一步无精确结果时，第二步才使用两侧百分号的包含匹配。"""

        route = RouteDecision(
            view_name="AiQueryPartV",
            confidence=0.95,
            reason="物料描述包含匹配",
            matched_terms=("钢板",),
            alternatives=(),
            match_type="ai",
            requires_confirmation=False,
            confirmation_question=None,
        )
        result = self.service.ask_generated_sql(
            "查询描述包含钢板的物料编码",
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ?",
            ("%钢板%",),
            route,
            limit=20,
        )
        self.assertIn(" LIKE ", (result.plan.base_sql or "").upper())
        self.assertEqual(("%钢板%",), result.plan.parameters)
        self.assertGreater(result.total_count, 0)

    def test_internal_like_wildcards_are_not_allowed_to_expand_fallback(self) -> None:
        """模型误把描述拆成内部通配符时，回退阶段按字面量处理，避免扩大到错误物料集合。"""

        route = RouteDecision(
            view_name="AiQueryPartV",
            confidence=0.95,
            reason="物料描述包含匹配",
            matched_terms=("GCr15", "Φ45"),
            alternatives=(),
            match_type="ai",
            requires_confirmation=False,
            confirmation_question=None,
        )
        result = self.service.ask_generated_sql(
            "查询描述为GCr15圆钢Φ45的物料编码",
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ?",
            ("%GCr15%Φ45%",),
            route,
            limit=20,
        )
        self.assertEqual((r"%GCr15\%Φ45%",), result.plan.parameters)
        self.assertEqual(0, result.total_count)

    def test_guard_rejects_writes_unknown_objects_and_unapproved_columns(self) -> None:
        """只读连接之外再用 AST 和语义层同时阻断越权 SQL。"""

        invalid_cases = [
            ("DELETE FROM AiQueryPartV", []),
            ("SELECT name FROM sqlite_master", []),
            ("SELECT * FROM AiQueryPartV", []),
            ("SELECT Company FROM AiQueryPartV", []),
            ("SELECT Company AS Company FROM AiQueryPartV", []),
            ("SELECT PartNum FROM AiQueryPartV WHERE PartDescription LIKE ?", []),
        ]
        for sql, parameters in invalid_cases:
            with self.subTest(sql=sql):
                with self.assertRaises(SQLValidationError):
                    self.guard.validate(sql, parameters, requested_limit=20)

    def test_guard_allows_approved_columns_through_cte_aliases(self) -> None:
        """严格列校验仍应支持 CTE 和派生字段，避免安全收紧破坏组合查询能力。"""

        validated = self.guard.validate(
            "WITH materials AS ("
            "SELECT PartNum AS material_code FROM AiQueryPartV"
            ") SELECT material_code FROM materials ORDER BY material_code LIMIT 10",
            [],
            requested_limit=20,
        )
        self.assertEqual(("AiQueryPartV",), validated.source_views)
        self.assertTrue(validated.sql.endswith("LIMIT 10"))

    def test_agent_repairs_unsafe_sql_once(self) -> None:
        """模型第一次使用 SELECT 星号时，守卫反馈应触发一次安全修复。"""

        fake = RepairingLLMClient()
        agent = AIQueryAgent(
            self.catalog,
            fake,
            database_profile=self.profile,
            allow_fallback=False,
        )
        understanding = agent.understand("有没有螺栓之类的", limit=20)
        self.assertEqual(2, fake.json_calls)
        self.assertEqual("text_to_sql", understanding.operation)
        self.assertIn("PartDescription LIKE ?", understanding.generated_sql or "")
        self.assertEqual(("%螺栓%",), understanding.sql_parameters)

    def test_agent_repairs_grouped_sql_for_scalar_inventory_total(self) -> None:
        """“还有多少库存”必须修复为单行 SUM，不能携带普通字段或 GROUP BY。"""

        fake = ScalarAggregateRepairingLLMClient()
        agent = AIQueryAgent(
            self.catalog,
            fake,
            database_profile=self.profile,
            allow_fallback=False,
        )

        understanding = agent.understand("查询GCr15圆钢Φ45还有多少库存")

        self.assertEqual(2, fake.json_calls)
        self.assertIn("GROUP BY 会把答案拆成多行", fake.user_prompts[1])
        self.assertIn("SUM(Qty) AS TotalQty", understanding.generated_sql or "")
        self.assertNotIn("GROUP BY", (understanding.generated_sql or "").upper())
        self.assertNotIn("PartNum", understanding.generated_sql or "")
        self.assertNotIn("PartDescription,", understanding.generated_sql or "")

    def test_correct_sql_ignores_nonstandard_auxiliary_metadata(self) -> None:
        """正确 SQL 不应因 `=`、single_value 或无效辅助筛选项触发 query_failed。"""

        fake = TolerantMetadataLLMClient()
        agent = AIQueryAgent(
            self.catalog,
            fake,
            database_profile=self.profile,
            allow_fallback=False,
        )

        understanding = agent.understand("查询GCr15圆钢Φ45还有多少库存")

        self.assertEqual(1, fake.json_calls)
        self.assertEqual(("AiQueryPartOnHandV",), understanding.source_views)
        self.assertIn("SUM(Qty) AS TotalQty", understanding.generated_sql or "")

    def test_ready_metadata_is_rebuilt_from_validated_sql_ast(self) -> None:
        """模型自报字段和粒度不可信，ready 计划必须由 AST 覆盖为真实值。"""

        agent = AIQueryAgent(
            self.catalog,
            llm_client=None,
            database_profile=self.profile,
            allow_fallback=False,
        )
        analysis = IntentAnalysis.model_validate(
            {
                "status": "ready",
                "source_views": ["AiQueryPartV"],
                "requested_fields": ["PartNum", "PartDescription"],
                "filter_constraints": [
                    {"column": "PartNum", "operator": "LIKE", "value": "错误线索"}
                ],
                "result_shape": "grouped",
                "sql": (
                    "SELECT SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV "
                    "WHERE PartDescription = ?"
                ),
                "parameters": ["GCr15圆钢Φ45"],
            }
        )

        validated = agent._validate_ready(
            analysis,
            limit=500,
            effective_question="查询GCr15圆钢Φ45还有多少库存",
        )

        self.assertEqual(["AiQueryPartOnHandV"], validated.source_views)
        self.assertEqual(["Qty"], validated.requested_fields)
        self.assertEqual("scalar", validated.result_shape)
        self.assertEqual("PartDescription", validated.filter_constraints[0].column)
        self.assertEqual("eq", validated.filter_constraints[0].operator)


if __name__ == "__main__":
    unittest.main()
