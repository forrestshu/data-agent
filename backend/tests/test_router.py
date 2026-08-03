"""查询路由验收：覆盖 Excel 中的 21 个业务场景。"""

from __future__ import annotations

import unittest

from data_agent.catalog import load_catalog
from data_agent.router import QueryRouter


class QueryRouterTests(unittest.TestCase):
    """决策层测试：确保自然语言意图会进入正确的 ERP 视图。"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试组共享只读知识目录和路由器，不改变任何数据。"""

        cls.catalog = load_catalog()
        cls.router = QueryRouter(cls.catalog)

    def test_catalog_contains_all_16_views(self) -> None:
        """知识库必须完整覆盖快照中的 16 个业务视图。"""

        self.assertEqual(16, len(self.catalog.views))
        self.assertEqual(16, len({view.name for view in self.catalog.views}))

    def test_routes_all_business_scenarios(self) -> None:
        """将 21 个业务需求逐一与期望视图对比。"""

        cases = [
            ("查物料最新采购价、平均单价和采购提前期", "AiQueryPoPriceV"),
            ("查询物料现有量和库位是否可发货", "AiQueryPartOnHandV"),
            ("按项目查询项目工单数量和要求交期", "AiQueryJobV"),
            ("通过物料描述查询物料编码", "AiQueryPartV"),
            ("查询采购进度、到货时间、在检数量和收货净值", "AiQueryPoProgressV"),
            ("通过物料描述查询库存、合格区和货位", "AiQueryPartOnHandV"),
            ("检查物料名称规格，根据图号查物料描述", "AiQueryPartV"),
            ("通过物料编码查询现有量", "AiQueryPartOnHandV"),
            ("查询BOM结构中物料的上级部件", "AiQueryBomV"),
            ("根据工单查询报工数量和末道工序", "AiQueryJobProgressV"),
            ("采购追踪中查订单、收货、开票数量和未结DMR", "AiQueryPoOverViewV"),
            ("查询采购订单进度和审批状态", "AiQueryPoOverViewV"),
            ("查询项目工单追踪和完工入库数量", "AiQueryProjectJobV"),
            ("物料一览中查询物料是否存在", "AiQueryPartV"),
            ("查询销售订单的订单金额、发货和退货数量", "AiQuerySoOverViewV"),
            ("项目追踪一览：项目机型、项目状态、发货日期和验收日期", "AiQueryProjectV"),
            ("生产追踪中查询工单执行和工单完工数量", "AiQueryJobTrackingV"),
            ("查询零件时间轴上的库存计量单位和采购计量单位", "AiQueryPartTimeTrackingV"),
            ("项目收入成本中查询项目发生成本和已确认收入", "AiQueryProjRevCstV"),
            ("查询供应商应付发票、供应商付款和应付余额", "AiQueryPayablesV"),
            ("客户对账：查询应收发票、客户收款和应收余额", "AiQueryReceivablesV"),
        ]
        for question, expected_view in cases:
            with self.subTest(question=question):
                decision = self.router.route(question)
                self.assertEqual(expected_view, decision.view_name)
                self.assertTrue(decision.matched_terms)
                self.assertGreaterEqual(decision.confidence, 0.55)
                self.assertFalse(decision.requires_confirmation)
                self.assertEqual("exact", decision.match_type)

    def test_colloquial_question_returns_candidate_for_confirmation(self) -> None:
        """口语问法只给出模糊候选和确认问题，不能直接当成精确路由。"""

        decision = self.router.route("帮我看看物料 110000012 仓里还剩多少")
        self.assertEqual("AiQueryPartOnHandV", decision.view_name)
        self.assertEqual("fuzzy", decision.match_type)
        self.assertTrue(decision.requires_confirmation)
        self.assertIn("是否确认", decision.confirmation_question or "")
        self.assertIn("仓里还剩多少", decision.matched_terms)

    def test_common_typo_returns_candidate_for_confirmation(self) -> None:
        """知识目录收录的常见错别字会提出候选，但仍需用户确认。"""

        decision = self.router.route("物料 110000012 的库寸在哪")
        self.assertEqual("AiQueryPartOnHandV", decision.view_name)
        self.assertTrue(decision.requires_confirmation)
        self.assertIn("库寸", decision.matched_terms)

    def test_unknown_question_requests_clarification(self) -> None:
        """不含业务意图的问题必须拒绝猜测视图。"""

        with self.assertRaisesRegex(ValueError, "补充"):
            self.router.route("帮我查一下")


if __name__ == "__main__":
    unittest.main()
