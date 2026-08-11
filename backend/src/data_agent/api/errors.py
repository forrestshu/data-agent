"""API 错误边界：失败说明脱敏与统一失败响应。"""

from __future__ import annotations

import json
import logging
from uuid import uuid4

from fastapi.responses import JSONResponse

from data_agent.knowledge.prompt import load_prompt
from data_agent.llm import LLMClient


logger = logging.getLogger(__name__)

QUERY_FAILURE_MESSAGES = {
    "ai_unavailable": "当前暂时无法完成问题理解，请稍后重试。",
    "missing_information": "还缺少必要的业务对象、指标或范围，请补充后再查询。",
    "knowledge_unavailable": "本地知识画像不可用，当前暂时不能安全查询。",
    "unsupported_query": "当前语义层中没有足够信息回答这个问题，可以换一种方式说明业务对象和指标。",
    "internal_error": "当前查询没有成功完成，请稍后重试。若持续出现，可将页面上的参考编号提供给管理员。",
}

DASHBOARD_FAILURE_MESSAGES = {
    "ai_unavailable": "当前暂时无法理解 Dashboard 概况问题，请稍后重试。",
    "missing_information": "还缺少可用于概况判断的业务范围，请补充后再试。",
    "knowledge_unavailable": "本地知识画像不可用，当前暂时不能安全查询。",
    "unsupported_query": "当前数据范围暂时无法生成这个概况，可以换一种业务对象或指标描述。",
    "internal_error": "当前 Dashboard 没有成功生成，请稍后重试。",
}


def explain_failure(
    llm_client: LLMClient | None,
    original_question: str,
    category: str,
    fallback_messages: dict[str, str],
    default_category: str = "internal_error",
) -> tuple[str, bool]:
    """生成不泄露内部结构的失败说明；异常时返回确定性文案。"""

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


def failure_response(
    *,
    llm_client: LLMClient | None,
    question: str,
    error: Exception,
    category: str,
    retryable: bool,
    fallback_messages: dict[str, str],
    log_prefix: str,
) -> JSONResponse:
    """记录技术栈，只返回模型整理后的自然语言和追踪号。"""

    reference_id = uuid4().hex[:10]
    logger.exception(
        "%s reference_id=%s category=%s error_type=%s",
        log_prefix,
        reference_id,
        category,
        type(error).__name__,
    )
    answer, generated_by_ai = explain_failure(
        llm_client,
        question,
        category,
        fallback_messages,
    )
    return JSONResponse(
        {
            "status": "query_failed",
            "answer": answer,
            "answer_generated_by_ai": generated_by_ai,
            "reference_id": reference_id,
            "retryable": retryable,
        }
    )
