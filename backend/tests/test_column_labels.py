"""AST 表头：物理列走语义目录，聚合按算子拼接，不调用模型。"""

from __future__ import annotations

import unittest

from data_agent.knowledge.semantic_catalog import load_semantic_catalog
from data_agent.query.execution.column_labels import build_column_labels


class ColumnLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_semantic_catalog()

    def _labels(
        self,
        sql: str,
        source_views: tuple[str, ...],
        output_names: tuple[str, ...] = (),
    ) -> dict[str, str]:
        return build_column_labels(sql, self.catalog, source_views, output_names)

    def test_physical_column_uses_catalog_business_name(self) -> None:
        labels = self._labels(
            "SELECT PartNum, Qty FROM AiQueryPartOnHandV",
            ("AiQueryPartOnHandV",),
            ("PartNum", "Qty"),
        )
        self.assertEqual("物料编码", labels["PartNum"])
        self.assertEqual("现有量", labels["Qty"])

    def test_sum_alias_is_stable_across_english_names(self) -> None:
        views = ("AiQueryPartOnHandV",)
        for alias in ("TotalQty", "total_qty", "qty_sum"):
            sql = f"SELECT SUM(Qty) AS {alias} FROM AiQueryPartOnHandV"
            labels = self._labels(sql, views, (alias,))
            self.assertEqual("现有量合计", labels[alias], alias)

    def test_count_star_and_distinct_count(self) -> None:
        self.assertEqual(
            "行数",
            self._labels(
                "SELECT COUNT(*) AS row_count FROM AiQueryPartOnHandV",
                ("AiQueryPartOnHandV",),
                ("row_count",),
            )["row_count"],
        )
        self.assertEqual(
            "采购订单号去重计数",
            self._labels(
                "SELECT COUNT(DISTINCT PONum) AS OrderCount FROM AiQueryPoOverViewV",
                ("AiQueryPoOverViewV",),
                ("OrderCount",),
            )["OrderCount"],
        )

    def test_plain_count_and_ratio_and_fallback(self) -> None:
        self.assertEqual(
            "现有量计数",
            self._labels(
                "SELECT COUNT(Qty) AS qty_count FROM AiQueryPartOnHandV",
                ("AiQueryPartOnHandV",),
                ("qty_count",),
            )["qty_count"],
        )
        self.assertEqual(
            "现有量/现有量",
            self._labels(
                "SELECT Qty / Qty AS ratio FROM AiQueryPartOnHandV",
                ("AiQueryPartOnHandV",),
                ("ratio",),
            )["ratio"],
        )
        self.assertEqual(
            "weird",
            self._labels(
                "SELECT CASE WHEN Qty > 0 THEN Qty ELSE 0 END AS weird FROM AiQueryPartOnHandV",
                ("AiQueryPartOnHandV",),
                ("weird",),
            )["weird"],
        )

    def test_empty_output_names_use_select_aliases(self) -> None:
        labels = self._labels(
            "SELECT SUM(Qty) AS TotalQty FROM AiQueryPartOnHandV",
            ("AiQueryPartOnHandV",),
        )
        self.assertEqual("现有量合计", labels["TotalQty"])


if __name__ == "__main__":
    unittest.main()
