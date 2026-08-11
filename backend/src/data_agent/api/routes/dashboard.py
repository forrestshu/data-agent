"""Dashboard 相关路由。"""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from data_agent.api.deps import active_context, json_safe
from data_agent.api.errors import DASHBOARD_FAILURE_MESSAGES, failure_response
from data_agent.api.schemas import DashboardQueryRequest
from data_agent.knowledge.database_profile import DatabaseProfileError
from data_agent.knowledge.semantic_catalog import load_semantic_catalog
from data_agent.llm import LLMClient, LLMUnavailable
from data_agent.query.agents.dashboard import (
    DashboardClarificationRequired,
    DashboardPlanningError,
    DashboardUnsupportedQuery,
)
from data_agent.query.dashboard_builder import build_initial_dashboard
from data_agent.query.workflow import QueryWorkflow


router = APIRouter()


@router.get("/api/dashboard")
def initial_dashboard(request: Request) -> dict:
    """初始 Dashboard：只使用当前知识画像，不擅自执行额外业务查询。"""

    _, profile = active_context(request)
    dashboard = build_initial_dashboard(profile, load_semantic_catalog())
    return {
        **json_safe(dashboard),
    }


@router.post("/api/dashboard/query")
def query_dashboard(
    payload: DashboardQueryRequest,
    request: Request,
) -> JSONResponse:
    """Dashboard 查询链路：概况理解、只读验证和图表契约彼此独立于数据查询。"""

    source, profile = active_context(request)

    def fail(error: Exception, category: str, retryable: bool) -> JSONResponse:
        return failure_response(
            llm_client=request.app.state.llm,
            question=payload.question,
            error=error,
            category=category,
            retryable=retryable,
            fallback_messages=DASHBOARD_FAILURE_MESSAGES,
            log_prefix="Dashboard 概况未完成",
        )

    try:
        llm: LLMClient | None = request.app.state.llm
        runtime = QueryWorkflow.prepare(source, profile, llm)
        outcome = runtime.execute_dashboard(
            payload.question,
            confirmed_view=payload.confirmed_view,
            clarification_answer=payload.clarification_answer,
            clarification_history=tuple(
                (turn.question, turn.answer)
                for turn in payload.clarification_history
            ),
            limit=payload.limit,
        )
        return JSONResponse(
            {
                "status": "completed",
                "dashboard": json_safe(outcome.dashboard),
                "ai": asdict(outcome.understanding.trace),
                "evidence": {
                    "source_views": list(
                        outcome.result.plan.source_views or (outcome.result.plan.view_name,)
                    ),
                    "total_count": outcome.result.total_count,
                    "displayed_count": len(outcome.result.rows),
                    "has_more": outcome.result.has_more,
                    "notices": list(outcome.result.notices),
                },
            }
        )
    except DashboardClarificationRequired as error:
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
    except DatabaseProfileError as error:
        return fail(error, "knowledge_unavailable", retryable=False)
    except DashboardUnsupportedQuery as error:
        return fail(error, "unsupported_query", retryable=False)
    except DashboardPlanningError as error:
        return fail(error, "internal_error", retryable=True)
    except (KeyError, ValueError) as error:
        return fail(error, "unsupported_query", retryable=False)
    except Exception as error:
        return fail(error, "internal_error", retryable=True)
