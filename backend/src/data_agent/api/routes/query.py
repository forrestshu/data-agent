"""数据查询路由。"""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from data_agent.api.deps import active_context, json_safe
from data_agent.api.errors import QUERY_FAILURE_MESSAGES, failure_response
from data_agent.api.schemas import QueryRequest
from data_agent.knowledge.database_profile import DatabaseProfileError
from data_agent.llm import LLMClient, LLMUnavailable
from data_agent.query.agents.data_query import AgentClarificationRequired
from data_agent.query.contracts import RouteConfirmationRequired
from data_agent.query.workflow import QueryWorkflow


router = APIRouter()


@router.post("/api/query")
def query_data(payload: QueryRequest, request: Request) -> JSONResponse:
    """查询接口：AI 基于知识生成 SQL，守卫只读执行，再由 AI 基于证据回答。"""

    source, profile = active_context(request)

    def fail(error: Exception, category: str, retryable: bool) -> JSONResponse:
        return failure_response(
            llm_client=request.app.state.llm,
            question=payload.question,
            error=error,
            category=category,
            retryable=retryable,
            fallback_messages=QUERY_FAILURE_MESSAGES,
            log_prefix="客户查询未完成",
        )

    try:
        llm: LLMClient | None = request.app.state.llm
        runtime = QueryWorkflow.prepare(source, profile, llm)
        outcome = runtime.execute_query(
            payload.question,
            confirmed_view=payload.confirmed_view,
            clarification_answer=payload.clarification_answer,
            clarification_history=tuple(
                (turn.question, turn.answer)
                for turn in payload.clarification_history
            ),
            limit=payload.limit,
        )
        result_payload = json_safe(asdict(outcome.result))
        result_payload["download_id"] = None
        if outcome.result.plan.base_sql:
            result_payload["download_id"] = request.app.state.query_exports.register(
                sql=outcome.result.plan.base_sql,
                parameters=outcome.result.plan.parameters,
            )
        return JSONResponse(
            {
                "status": "completed",
                "answer": outcome.answer,
                "answer_generated_by_ai": outcome.answer_generated_by_ai,
                "result": result_payload,
                "ai": asdict(outcome.understanding.trace),
            }
        )
    except AgentClarificationRequired as error:
        return JSONResponse(
            {
                "status": "clarification_required",
                "message": str(error),
                "analysis": error.analysis.model_dump(),
                "ai": {"provider": error.provider, "model": error.model},
            }
        )
    except LLMUnavailable as error:
        return fail(error, "ai_unavailable", retryable=True)
    except RouteConfirmationRequired as error:
        return JSONResponse(
            {
                "status": "confirmation_required",
                "message": str(error),
                "route": asdict(error.decision),
            }
        )
    except DatabaseProfileError as error:
        return fail(error, "knowledge_unavailable", retryable=False)
    except (KeyError, ValueError) as error:
        return fail(error, "unsupported_query", retryable=False)
    except Exception as error:
        # 查询接口是客户边界；未知异常不能把堆栈、内部对象或数据库细节发送到浏览器。
        return fail(error, "internal_error", retryable=True)
