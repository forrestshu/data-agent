"""决策层：支持标准关键词直达和模糊问法确认的 ERP 查询路由器。"""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from .catalog import KnowledgeCatalog, ViewKnowledge


# 决定性指标比通用对象词更能区分视图。例如“物料编码”可能出现在多张表中，
# 但“现有量”可以确定用户需要库存视图。
DECISIVE_TERMS: dict[str, tuple[str, ...]] = {
    "AiQueryPartOnHandV": ("库存", "现有量", "库位", "货位"),
}


@dataclass(frozen=True)
class RouteCandidate:
    """单个路由候选：保留得分、命中词和匹配类型，供排序与解释。"""

    view: ViewKnowledge
    score: float
    matched_terms: tuple[str, ...]
    match_type: str


@dataclass(frozen=True)
class RouteDecision:
    """路由输出：除视图外，明确说明是否必须先得到用户确认。"""

    view_name: str
    confidence: float
    reason: str
    matched_terms: tuple[str, ...]
    alternatives: tuple[str, ...]
    match_type: str
    requires_confirmation: bool
    confirmation_question: str | None


class RouteConfirmationRequired(ValueError):
    """流程中断：系统只有模糊候选，在用户确认前不得执行数据库查询。"""

    def __init__(self, decision: RouteDecision) -> None:
        super().__init__(decision.confirmation_question or "需要确认查询意图。")
        self.decision = decision


class QueryRouter:
    """查询路由器：标准词直接路由；口语或近似词只建议候选并要求确认。"""

    def __init__(self, catalog: KnowledgeCatalog) -> None:
        self.catalog = catalog

    @staticmethod
    def _normalize(text: str) -> str:
        """统一大小写、标点和空白，保留中文与业务编号。"""

        ignored = " ，,。；;：:？?！!、的了呢吗帮我请查查询一下看看"
        normalized = text.lower()
        for character in ignored:
            normalized = normalized.replace(character, "")
        return normalized

    def _score_exact(self, normalized_question: str, view: ViewKnowledge) -> RouteCandidate:
        """计算知识目录标准关键词得分；只有真正命中关键词才算精确路由。"""

        matched: list[str] = []
        score = 0.0
        for keyword in view.keywords:
            normalized_keyword = self._normalize(keyword)
            if normalized_keyword and normalized_keyword in normalized_question:
                matched.append(keyword)
                score += 2.0 + min(len(normalized_keyword), 8) / 2

        if matched and self._normalize(view.domain) in normalized_question:
            score += 0.5

        for term in DECISIVE_TERMS.get(view.name, ()):
            if self._normalize(term) in normalized_question:
                score += 6.0

        return RouteCandidate(
            view=view,
            score=score,
            matched_terms=tuple(matched),
            match_type="exact",
        )

    @staticmethod
    def _best_window_similarity(alias: str, question: str) -> float:
        """比较口语别名与问题中的同长度窗口，用于容忍少量错字和前后赘词。"""

        if not alias or not question:
            return 0.0
        if alias in question:
            return 1.0
        if len(question) <= len(alias):
            return SequenceMatcher(None, alias, question).ratio()
        window_size = len(alias)
        return max(
            SequenceMatcher(None, alias, question[index : index + window_size]).ratio()
            for index in range(len(question) - window_size + 1)
        )

    def _score_fuzzy(self, normalized_question: str, view: ViewKnowledge) -> RouteCandidate:
        """在标准词未命中时，用口语别名和字符相似度产生待确认候选。"""

        matches: list[tuple[float, str]] = []
        for alias in view.aliases:
            normalized_alias = self._normalize(alias)
            similarity = self._best_window_similarity(normalized_alias, normalized_question)
            # 短语至少三字，阈值 0.72；常见两字错别字应直接作为 alias 收录。
            if similarity >= 0.72:
                matches.append((similarity, alias))

        matches.sort(key=lambda item: (-item[0], -len(item[1])))
        if not matches:
            return RouteCandidate(view, 0.0, (), "fuzzy")
        best_similarity, best_alias = matches[0]
        return RouteCandidate(
            view=view,
            score=best_similarity * 10 + min(len(best_alias), 8) / 10,
            matched_terms=(best_alias,),
            match_type="fuzzy",
        )

    def _confirmed_decision(self, confirmed_view: str) -> RouteDecision:
        """将用户明确确认的白名单视图转换成可执行路由决策。"""

        view = self.catalog.by_name(confirmed_view)
        return RouteDecision(
            view_name=view.name,
            confidence=1.0,
            reason=f"用户已确认；{view.purpose}",
            matched_terms=(),
            alternatives=(),
            match_type="confirmed",
            requires_confirmation=False,
            confirmation_question=None,
        )

    def route(self, question: str, confirmed_view: str | None = None) -> RouteDecision:
        """先尝试标准词；仅在无标准命中时进行模糊建议，并阻止自动执行。"""

        if confirmed_view is not None:
            return self._confirmed_decision(confirmed_view)

        normalized = self._normalize(question)
        exact_candidates = sorted(
            (self._score_exact(normalized, view) for view in self.catalog.views),
            key=lambda item: (-item.score, item.view.name),
        )
        best = exact_candidates[0]
        if best.score > 0 and best.matched_terms:
            second_score = exact_candidates[1].score if len(exact_candidates) > 1 else 0.0
            confidence = min(
                0.99,
                0.55 + best.score / 30 + max(best.score - second_score, 0) / 40,
            )
            alternatives = tuple(
                item.view.name for item in exact_candidates[1:3] if item.score > 0
            )
            return RouteDecision(
                view_name=best.view.name,
                confidence=round(confidence, 3),
                reason=f"命中标准词 {', '.join(best.matched_terms)}；{best.view.purpose}",
                matched_terms=best.matched_terms,
                alternatives=alternatives,
                match_type="exact",
                requires_confirmation=False,
                confirmation_question=None,
            )

        fuzzy_candidates = sorted(
            (self._score_fuzzy(normalized, view) for view in self.catalog.views),
            key=lambda item: (-item.score, item.view.name),
        )
        fuzzy_best = fuzzy_candidates[0]
        if fuzzy_best.score <= 0:
            raise ValueError("无法判断查询意图，请补充要查的业务对象和指标。")

        alternatives = tuple(
            item.view.name for item in fuzzy_candidates[1:3] if item.score > 0
        )
        suggested_term = fuzzy_best.matched_terms[0]
        confirmation = (
            f"我理解你可能想进行以下查询：“{fuzzy_best.view.purpose}”"
            f"（识别到口语表达“{suggested_term}”）。"
            f"是否确认选择 {fuzzy_best.view.name}？"
        )
        return RouteDecision(
            view_name=fuzzy_best.view.name,
            confidence=round(min(0.89, fuzzy_best.score / 12), 3),
            reason=f"模糊匹配口语表达 {suggested_term}；尚未执行查询",
            matched_terms=fuzzy_best.matched_terms,
            alternatives=alternatives,
            match_type="fuzzy",
            requires_confirmation=True,
            confirmation_question=confirmation,
        )
