"""查询 Agent 共用的对话拼接、字段本地化和安全失败表达。"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import replace

from data_agent.knowledge.prompt import load_prompt
from data_agent.query.execution.executor import QueryResult
from data_agent.llm import LLMClient, LLMUnavailable


logger = logging.getLogger(__name__)


def effective_question(
    question: str,
    clarification_answer: str | None,
    clarification_history: tuple[tuple[str, str], ...],
    confirmed_view: str | None,
) -> str:
    """把用户问题和已确认上下文组织为 JSON 模型输入。"""

    return json.dumps(
        {
            "用户原问题": question.strip(),
            "已回答的澄清记录，禁止重复询问": [
                {"系统追问": asked, "用户回答": answered}
                for asked, answered in clarification_history
            ],
            "用户补充": clarification_answer.strip()
            if clarification_answer and clarification_answer.strip()
            else None,
            "用户已确认的数据对象": confirmed_view,
        },
        ensure_ascii=False,
    )


def localize_result_columns(
    llm_client: LLMClient,
    original_question: str,
    result: QueryResult,
) -> QueryResult:
    """只让模型补充语义目录和本地词典都未知的英文结果列名。"""

    if not result.rows:
        return result
    unknown = [
        column
        for column in result.rows[0]
        if result.column_labels.get(column, column) == column
        and re.search(r"[A-Za-z]", column)
    ]
    if not unknown:
        return result
    evidence = {
        "用户问题": original_question,
        "来源视图": list(result.plan.source_views or (result.plan.view_name,)),
        "待处理字段": unknown,
        "样例值": [
            {column: row.get(column) for column in unknown}
            for row in result.rows[:3]
        ],
    }
    try:
        generated = llm_client.complete_json(
            load_prompt("column_labels.md"),
            json.dumps(evidence, ensure_ascii=False, default=str),
            max_tokens=400,
        )
    except LLMUnavailable:
        return result
    proposed = generated.get("column_labels")
    if not isinstance(proposed, dict):
        return result
    translated = dict(result.column_labels)
    for column in unknown:
        label = proposed.get(column)
        if not isinstance(label, str):
            continue
        label = label.strip()
        if 2 <= len(label) <= 10 and re.search(r"[\u4e00-\u9fff]", label):
            translated[column] = label
    return replace(result, column_labels=translated)


def explain_failure(
    llm_client: LLMClient | None,
    original_question: str,
    category: str,
    fallback_messages: dict[str, str],
    default_category: str = "internal_error",
) -> tuple[str, bool]:
    """记录技术异常的位置不变，只生成不泄露内部结构的用户文案。"""

    fallback = fallback_messages.get(category, fallback_messages[default_category])
    if llm_client is None:
        return fallback, False
    try:
        answer = llm_client.complete_text(
            load_prompt("failure.md"),
            json.dumps(
                {
                    "用户问题": original_question,
                    "失败类别": category,
                    "建议底稿": fallback,
                },
                ensure_ascii=False,
            ),
            max_tokens=300,
        )
        forbidden = (
            "json", "sql", "http", "api", "deepseek", "aiquery", "traceback",
            "exception", "pydantic", "sqlite", "接口契约", "堆栈",
        )
        if any(term in answer.casefold() for term in forbidden):
            return fallback, False
        return answer, True
    except Exception:
        logger.exception("生成查询失败说明时出现异常")
        return fallback, False
