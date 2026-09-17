"""Text-to-SQL 验收：验证 Knowledge grounding、AST 安全和真实 SQLite 执行。"""

from __future__ import annotations

import unittest
from typing import Any

from data_agent.query.agents.data_query import (
    AgentUnsupportedQuery,
    DataQueryAgent,
    IntentAnalysis,
)
from data_agent.knowledge.semantic_catalog import load_semantic_catalog
from data_agent.query.agents.dashboard import DashboardAgent
from data_agent.query.execution.executor import QueryExecutor, QueryResult
from data_agent.query.execution.prepare import prepare_executable_query
from data_agent.database import Database, SQLServerDatabase
from data_agent.knowledge.database_profile import load_database_profile
from data_agent.knowledge.prompt import build_semantic_context
from data_agent.query.contracts import RouteDecision
from data_agent.settings import DATABASE_PROFILE_PATH, DEFAULT_DATABASE_PATH
from data_agent.query.execution.guard import SQLGuard, SQLValidationError


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


class RankingWithoutLimitLLMClient:
    """测试替身：排名 SQL 已排序但未写 LIMIT，规划层不应再改写。"""

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
        self.json_calls += 1
        return {
            "status": "ready",
            "confidence": 0.96,
            "intent_summary": "查询库存总量最高的前5个物料",
            "route_reason": "库存视图可按物料汇总和排序",
            "source_views": ["AiQueryPartOnHandV"],
            "sql": (
                "SELECT PartNum, SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV "
                "GROUP BY PartNum ORDER BY TotalQty DESC"
            ),
            "parameters": [],
        }

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        return "排名查询已完成。"


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
        """返回 `=` 和无效辅助项，但 SQL 本身满足安全与业务粒度要求。"""

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
            "requested_fields": ["Qty"],
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

        return "库存总量查询已完成。"


class UnsupportedRepairingLLMClient:
    """测试替身：第一次误报不支持，第二次按现有单视图事实生成 SQL。"""

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
        self.json_calls += 1
        common = {
            "confidence": 0.95,
            "intent_summary": "查询项目公司名称",
            "route_reason": "项目财务视图包含所需字段",
            "source_views": ["AiQueryProjRevCstV"],
            "filter_constraints": [
                {"column": "ProjectID", "operator": "eq", "value": "22149-2"}
            ],
            "requested_fields": ["CompanyName"],
        }
        if self.json_calls == 1:
            return {**common, "status": "unsupported"}
        return {
            **common,
            "status": "ready",
            "sql": "SELECT CompanyName FROM AiQueryProjRevCstV WHERE ProjectID = ?",
            "parameters": ["22149-2"],
        }

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        return "公司名称查询已完成。"


class TrulyUnsupportedLLMClient:
    """测试替身：请求字段不存在，后端应保留真正的不支持结论。"""

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
        self.json_calls += 1
        return {
            "status": "unsupported",
            "route_reason": "语义层没有员工身份证号字段",
            "source_views": [],
            "filter_constraints": [],
            "requested_fields": ["EmployeeIdCard"],
        }

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> str:
        return "当前数据不包含该字段。"


class GuardRetreatingLLMClient(UnsupportedRepairingLLMClient):
    """测试替身：Guard 拒绝后模型改口不支持，第三次才生成安全 SQL。"""

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1200,
    ) -> dict[str, Any]:
        self.json_calls += 1
        common = {
            "confidence": 0.95,
            "intent_summary": "查询项目公司名称",
            "route_reason": "项目财务视图包含所需字段",
            "source_views": ["AiQueryProjRevCstV"],
            "filter_constraints": [
                {"column": "ProjectID", "operator": "eq", "value": "22149-2"}
            ],
            "requested_fields": ["CompanyName"],
            "parameters": ["22149-2"],
        }
        if self.json_calls == 1:
            return {**common, "status": "ready", "sql": "SELECT * FROM AiQueryProjRevCstV"}
        if self.json_calls == 2:
            return {**common, "status": "unsupported", "sql": None}
        return {
            **common,
            "status": "ready",
            "sql": "SELECT CompanyName FROM AiQueryProjRevCstV WHERE ProjectID = ?",
        }


class TextToSQLTests(unittest.TestCase):
    """安全链路测试：模型可组合 SELECT，但权限、资源和执行均由后端决定。"""

    @classmethod
    def setUpClass(cls) -> None:
        """加载当前语义层与真实数据库画像。"""

        cls.catalog = load_semantic_catalog()
        cls.profile = load_database_profile(DATABASE_PROFILE_PATH)
        cls.guard = SQLGuard(cls.catalog, cls.profile)
        cls.executor = QueryExecutor(
            Database(path=DEFAULT_DATABASE_PATH),
            cls.catalog,
            database_profile=cls.profile,
        )

    def _execute_sql(
        self,
        question: str,
        sql: str,
        parameters: tuple[Any, ...],
        route: RouteDecision,
        limit: int = 500,
    ) -> QueryResult:
        prepared = prepare_executable_query(
            self.guard,
            sql,
            parameters,
            limit,
            dialect=self.executor.source.dialect,
        )
        return self.executor.execute_validated(question, prepared, route)

    def test_sqlserver_guard_uses_tsql_and_cux_schema(self) -> None:
        source = SQLServerDatabase("127.0.0.1", 1433, "user", "password", "prod")
        guard = SQLGuard(self.catalog, self.profile, source=source)
        validated = guard.validate(
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartNum = ?",
            ["110000012"],
            requested_limit=10,
        )
        self.assertIn("SELECT TOP 10", validated.sql)
        self.assertIn("FROM Cux.AiQueryPartV", validated.sql)

    def test_prompt_prefers_precomputed_business_fields_and_preserves_parameters(self) -> None:
        """提示词必须阻止二次聚合、参数截断、错误编码字段和应收应付串域。"""

        agent = DataQueryAgent(
            self.catalog,
            llm_client=None,
            database_profile=self.profile,
        )
        prompt = agent._system_prompt()

        self.assertLess(len(prompt), 12_000)
        self.assertIn("AvgPrice直接查询", prompt)
        self.assertIn("不用AVG(AvgPrice)", prompt)
        self.assertIn("默认不二次SUM", prompt)
        self.assertIn("参数必须完整原样保留", prompt)
        self.assertIn("才分别用ProjectID、JobNum、PartNum", prompt)
        self.assertIn("PONum、PartNum、OrderQty、ReceivedQty、InvoiceQty、RemainQty", prompt)
        self.assertIn("应付只用Payables", prompt)
        self.assertIn("JobNum 是工单号，不是数量字段", prompt)
        self.assertIn("JobQty 是工单计划生产数量", prompt)
        self.assertIn("多少张工单/工单张数", prompt)
        self.assertIn("工单末道完成量用JobOprCompQty", prompt)
        self.assertIn("威图悬臂箱底座，A250063", prompt)
        self.assertIn("必须返回完整、可执行的参数化 SQLite `SELECT`", prompt)
        self.assertIn("每行粒度", prompt)
        self.assertIn("COUNT(DISTINCT 对象键)", prompt)
        self.assertIn("唯一对象集合", prompt)
        self.assertIn("assumptions", prompt)
        self.assertNotIn("entity_keys", prompt)
        self.assertNotIn("result_shape", prompt)
        self.assertNotIn("requested_fields", prompt)
        self.assertEqual(16, prompt.count("Company=公司代码"))
        self.assertIn("项目“已验收”表示Checkdate非空", prompt)
        self.assertIn("SELECT覆盖用户要求的全部字段", prompt)

    def test_planning_does_not_rewrite_missing_top_n_limit(self) -> None:
        """规划只做 Guard，不再把问题里的前 N 补进 SQL。"""

        fake = RankingWithoutLimitLLMClient()
        agent = DataQueryAgent(self.catalog, fake, database_profile=self.profile)

        understanding = agent.understand("查询库存总量最高的前5个物料")

        self.assertEqual(1, fake.json_calls)
        self.assertIn("ORDER BY TotalQty DESC", understanding.generated_sql)
        self.assertNotIn("LIMIT", understanding.generated_sql)

    def test_compact_prompt_knowledge_keeps_all_views_and_fields(self) -> None:
        """紧凑语义卡片必须保留全部视图、业务名称、字段描述和精选示例。"""

        knowledge = build_semantic_context(self.catalog)
        self.assertLess(len(knowledge), 9000)
        for view in self.catalog.views:
            self.assertIn(view.name, knowledge)
            self.assertIn(view.business_name, knowledge)
            for column, semantic in view.column_semantics.items():
                self.assertIn(column, knowledge)
                if column != "Company":
                    self.assertIn(semantic["business_name"], knowledge)
                    self.assertIn(semantic["description"].removesuffix("。"), knowledge)
        self.assertIn("例：Approved、Draft、Rejected", knowledge)
        self.assertEqual(16, knowledge.count("Company=公司代码"))

    def test_dashboard_prompt_uses_same_compact_semantic_projection(self) -> None:
        """Dashboard 复用同一份紧凑语义投影，不发送完整治理 JSON。"""

        prompt = DashboardAgent(
            self.catalog,
            None,
            database_profile=self.profile,
        )._system_prompt()
        self.assertLess(len(prompt), 9500)
        for view in self.catalog.views:
            self.assertIn(view.name, prompt)

    def test_semantic_catalog_covers_every_documented_column(self) -> None:
        """权威文档中的 16 张视图和 154 个字段必须完整进入正式语义层。"""

        self.assertEqual(16, len(self.catalog.views))
        self.assertEqual(
            154,
            sum(len(view.column_semantics) for view in self.catalog.views),
        )
        self.assertTrue(all("Company" in view.join_columns for view in self.catalog.views))
        self.assertTrue(all("Company" in view.output_columns for view in self.catalog.views))
        self.assertEqual(17, len({item.id for item in self.catalog.relationships}))

    def test_guard_allows_company_code_output(self) -> None:
        """公司代码是已确认允许展示的字段，仍可同时作为 JOIN 必要键。"""

        validated = self.guard.validate(
            "SELECT Company FROM AiQueryPartV WHERE PartDescription = ?",
            ["16Mn钢板30"],
            requested_limit=20,
        )
        self.assertEqual(("AiQueryPartV",), validated.source_views)

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

    def test_guard_accepts_new_verified_direct_relationships(self) -> None:
        """已核验唯一性和覆盖率的三条直接关系应复用现有 JOIN 守卫。"""

        cases = (
            (
                "SELECT j.JobNum, p.CustName FROM AiQueryJobV j "
                "JOIN AiQueryProjectV p ON j.Company = p.Company "
                "AND j.ProjectID = p.ProjectID"
            ),
            (
                "SELECT t.JobNum, j.ProjectID FROM AiQueryJobTrackingV t "
                "JOIN AiQueryJobV j ON t.Company = j.Company "
                "AND t.JobNum = j.JobNum"
            ),
            (
                "SELECT s.OrderNum, p.PartDescription FROM AiQuerySoOverViewV s "
                "JOIN AiQueryPartV p ON s.Company = p.Company "
                "AND s.PartNum = p.PartNum"
            ),
            (
                "SELECT j.JobNum, p.PartDescription FROM AiQueryJobProgressV j "
                "LEFT JOIN AiQueryPartV p ON j.Company = p.Company "
                "AND j.PartNum = p.PartNum"
            ),
            (
                "SELECT DISTINCT s.OrderNum, r.CustName, r.RemainAmount "
                "FROM AiQuerySoOverViewV s JOIN AiQueryReceivablesV r "
                "ON s.Company = r.Company AND s.Customer_Name = r.CustName"
            ),
        )
        for sql in cases:
            with self.subTest(sql=sql):
                self.guard.validate(sql, [], requested_limit=20)

    def test_grouped_distinct_entity_count_passes_guard_without_declared_contract(self) -> None:
        """按业务键去重的分组计数只走 Guard，不再核对形态声明。"""

        agent = DataQueryAgent(self.catalog, None, database_profile=self.profile)
        analysis = IntentAnalysis(
            status="ready",
            source_views=["AiQueryPoOverViewV"],
            sql=(
                "SELECT ApproveStatus_c, COUNT(DISTINCT PONum) AS OrderCount "
                "FROM AiQueryPoOverViewV GROUP BY ApproveStatus_c "
                "ORDER BY OrderCount DESC"
            ),
        )
        validated = agent._validate_ready(
            analysis,
            500,
            "查询各个审批状态的采购订单数量分布",
        )
        self.assertIn("COUNT(DISTINCT PONum)", validated.sql or "")

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
        result = self._execute_sql(
            "有没有螺栓之类的",
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ? LIMIT 20",
            ("%螺栓%",),
            route,
            limit=20,
        )
        self.assertGreater(len(result.rows), 0)
        self.assertLessEqual(len(result.rows), 20)
        self.assertTrue(all("螺栓" in str(row["PartDescription"]) for row in result.rows))
        self.assertEqual((), result.notices)

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
        result = self._execute_sql(
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
        result = self._execute_sql(
            "查询GCr15圆钢Φ45还有多少库存",
            (
                "SELECT SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV "
                "WHERE PartDescription LIKE ?"
            ),
            ("%GCr15圆钢Φ45%",),
            route,
        )

        self.assertEqual(1, len(result.rows))
        self.assertIsNotNone(result.rows[0]["TotalQty"])
        self.assertGreaterEqual(float(result.rows[0]["TotalQty"]), 0.0)
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
        result = self._execute_sql(
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
        result = self._execute_sql(
            "查询描述为GCr15圆钢Φ45的物料编码",
            "SELECT PartNum, PartDescription FROM AiQueryPartV WHERE PartDescription LIKE ?",
            ("%GCr15%Φ45%",),
            route,
            limit=20,
        )
        self.assertEqual((r"%GCr15\%Φ45%",), result.plan.parameters)
        self.assertEqual(0, result.total_count)
        self.assertEqual(("未查到符合条件的记录。",), result.notices)

    def test_guard_rejects_writes_unknown_objects_and_unapproved_columns(self) -> None:
        """用一组负例覆盖连接、开放对象和字段权限边界。"""

        invalid_cases = [
            (
                "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
                "JOIN AiQueryPartOnHandV o ON p.PartNum = o.PartNum",
                [],
            ),
            (
                "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
                "JOIN AiQueryPartOnHandV o ON 1 = 1",
                [],
            ),
            (
                "SELECT p.PartNum, o.Qty FROM AiQueryPartV p "
                "JOIN AiQueryPartOnHandV o",
                [],
            ),
            (
                "SELECT s.PartNum, o.Qty FROM AiQuerySoOverViewV s "
                "JOIN AiQueryPartOnHandV o "
                "ON s.Company = o.Company AND s.PartNum = o.PartNum",
                [],
            ),
            ("DELETE FROM AiQueryPartV", []),
            ("SELECT name FROM sqlite_master", []),
            ("SELECT * FROM AiQueryPartV", []),
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
        agent = DataQueryAgent(
            self.catalog,
            fake,
            database_profile=self.profile,
        )
        understanding = agent.understand("有没有螺栓之类的", limit=20)
        self.assertEqual(2, fake.json_calls)
        self.assertIn("PartDescription LIKE ?", understanding.generated_sql)
        self.assertEqual(("%螺栓%",), understanding.sql_parameters)

    def test_agent_repairs_false_unsupported_when_single_view_covers(self) -> None:
        """模型误报不支持时，现有语义事实应触发一次修复并得到安全 SQL。"""

        fake = UnsupportedRepairingLLMClient()
        agent = DataQueryAgent(self.catalog, fake, database_profile=self.profile)

        understanding = agent.understand("查询项目22149-2在项目财务视图中的公司名称")

        self.assertEqual(2, fake.json_calls)
        self.assertEqual(("AiQueryProjRevCstV",), understanding.source_views)
        self.assertIn("SELECT CompanyName", understanding.generated_sql)

    def test_agent_preserves_true_unsupported_result(self) -> None:
        """语义层没有所需字段时，不得强迫模型生成 SQL。"""

        fake = TrulyUnsupportedLLMClient()
        agent = DataQueryAgent(self.catalog, fake, database_profile=self.profile)

        with self.assertRaises(AgentUnsupportedQuery):
            agent.understand("查询员工身份证号")

        self.assertEqual(1, fake.json_calls)

    def test_guard_repair_cannot_retreat_to_false_unsupported(self) -> None:
        """Guard 拒绝 SQL 后，模型不得用误报 unsupported 绕过 refine。"""

        fake = GuardRetreatingLLMClient()
        agent = DataQueryAgent(self.catalog, fake, database_profile=self.profile)

        understanding = agent.understand("查询项目22149-2在项目财务视图中的公司名称")

        self.assertEqual(3, fake.json_calls)
        self.assertIn("WHERE ProjectID = ?", understanding.generated_sql)

    def test_correct_sql_ignores_nonstandard_auxiliary_metadata(self) -> None:
        """正确 SQL 不应因 `=` 或无效辅助筛选项触发 query_failed。"""

        fake = TolerantMetadataLLMClient()
        agent = DataQueryAgent(
            self.catalog,
            fake,
            database_profile=self.profile,
        )

        understanding = agent.understand("查询GCr15圆钢Φ45还有多少库存")

        self.assertEqual(1, fake.json_calls)
        self.assertEqual(("AiQueryPartOnHandV",), understanding.source_views)
        self.assertIn("SUM(Qty) AS TotalQty", understanding.generated_sql or "")

if __name__ == "__main__":
    unittest.main()
