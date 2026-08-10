"""FastAPI 入口：提供 SQLite 查询、Dashboard 和结果导出。"""

from __future__ import annotations

from dataclasses import asdict
import logging
from tempfile import SpooledTemporaryFile
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openpyxl import Workbook
from pydantic import BaseModel, Field

from data_agent.query.agents.support import explain_failure as explain_query_failure
from data_agent.query.agents.data_query import AgentClarificationRequired
from data_agent.knowledge.catalog import load_catalog
from data_agent.database import Database
from data_agent.query.dashboard_view import build_initial_dashboard
from data_agent.query.agents.dashboard import (
    DashboardClarificationRequired,
    DashboardPlanningError,
    DashboardUnsupportedQuery,
)
from data_agent.query.execution.executor import ReadOnlyQueryService
from data_agent.query.execution.exports import QueryExportRegistry
from data_agent.knowledge.profile import KnowledgeError, load_profile
from data_agent.llm import DeepSeekClient, LLMClient, LLMUnavailable
from data_agent.query.contracts import RouteConfirmationRequired
from data_agent.query.workflow import QueryRuntime
from data_agent.settings import DATABASE_PROFILE_PATH, FRONTEND_DIST_PATH


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _json_safe(value: Any) -> Any:
    """把日期等数据库类型转换成标准 JSON 值。"""

    return jsonable_encoder(value)


class ClarificationTurn(BaseModel):
    """对话契约：保存一次系统追问和用户回答，供下一轮完整理解。"""

    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=500)


class QueryRequest(BaseModel):
    """接口模型：接收原问题、500 行预览上限和完整澄清历史。"""

    question: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=500, ge=1, le=500)
    confirmed_view: str | None = Field(default=None, max_length=100)
    clarification_answer: str | None = Field(default=None, max_length=500)
    clarification_history: list[ClarificationTurn] = Field(
        default_factory=list,
        max_length=10,
    )


class DashboardQueryRequest(BaseModel):
    """Dashboard 接口模型：接收概况问题和可选的多轮补充，使用独立查询上限。"""

    question: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=100, ge=1, le=500)
    confirmed_view: str | None = Field(default=None, max_length=100)
    clarification_answer: str | None = Field(default=None, max_length=500)
    clarification_history: list[ClarificationTurn] = Field(
        default_factory=list,
        max_length=10,
    )


def create_app(
    llm_client: LLMClient | None = None,
    use_environment_ai: bool = True,
) -> FastAPI:
    """应用工厂：所有自然语言查询都必须使用 AI 规划。"""

    configured_llm = llm_client
    if configured_llm is None and use_environment_ai:
        configured_llm = DeepSeekClient.from_environment()
    app = FastAPI(
        title="ERP Data Agent API",
        version="0.3.0",
        description="DeepSeek 语义理解、自然语言回答与 SQLite 只读查询",
    )
    app.state.database = Database.from_environment()
    app.state.profile = load_profile(DATABASE_PROFILE_PATH)
    app.state.llm = configured_llm
    app.state.query_exports = QueryExportRegistry()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    def active_context(request: Request) -> tuple[Database, dict[str, Any]]:
        """返回唯一 SQLite 数据库和静态知识画像。"""

        return request.app.state.database, request.app.state.profile

    @app.get("/api/health")
    def health(request: Request) -> dict[str, Any]:
        """健康接口：确认 SQLite 文件和 AI 配置。"""

        source, _ = active_context(request)
        llm: LLMClient | None = request.app.state.llm
        return {
            "service": "ok",
            "database": {
                "type": "sqlite",
                "file": source.path.name,
                "ready": source.path.exists(),
            },
            "ai": {
                "configured": llm is not None,
                "provider": llm.provider if llm else None,
                "model": llm.model if llm else None,
                "required": True,
            },
        }

    @app.get("/api/ai/status")
    def ai_status(request: Request) -> dict[str, Any]:
        """AI 状态接口：只报告是否配置与模型名，绝不返回 Key。"""

        llm: LLMClient | None = request.app.state.llm
        return {
            "configured": llm is not None,
            "provider": llm.provider if llm else None,
            "model": llm.model if llm else None,
            "required": True,
            "role": "数据查询 Text-to-SQL、Dashboard 概况规划、澄清和证据回答",
        }

    @app.get("/api/dashboard")
    def initial_dashboard(request: Request) -> dict[str, Any]:
        """初始 Dashboard：只使用当前知识画像，不擅自执行额外业务查询。"""

        _, profile = active_context(request)
        dashboard = build_initial_dashboard(profile, load_catalog())
        return {
            **_json_safe(dashboard),
        }

    @app.post("/api/dashboard/query")
    def query_dashboard(
        payload: DashboardQueryRequest,
        request: Request,
    ) -> JSONResponse:
        """Dashboard 查询链路：概况理解、只读验证和图表契约彼此独立于数据查询。"""

        source, profile = active_context(request)
        def failure_response(
            error: Exception,
            category: str,
            retryable: bool,
        ) -> JSONResponse:
            """Dashboard 错误边界：记录技术信息，只返回概况生成提示和参考编号。"""

            reference_id = uuid4().hex[:10]
            logger.exception(
                "Dashboard 概况未完成 reference_id=%s category=%s error_type=%s",
                reference_id,
                category,
                type(error).__name__,
            )
            answer, generated_by_ai = explain_query_failure(
                request.app.state.llm,
                payload.question,
                category,
                {
                    "ai_unavailable": "当前暂时无法理解 Dashboard 概况问题，请稍后重试。",
                    "missing_information": "还缺少可用于概况判断的业务范围，请补充后再试。",
                    "knowledge_unavailable": "本地知识画像不可用，当前暂时不能安全查询。",
                    "unsupported_query": "当前数据范围暂时无法生成这个概况，可以换一种业务对象或指标描述。",
                    "internal_error": "当前 Dashboard 没有成功生成，请稍后重试。",
                },
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

        try:
            llm: LLMClient | None = request.app.state.llm
            runtime = QueryRuntime.prepare(source, profile, llm)
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
                    "dashboard": _json_safe(outcome.dashboard),
                    "ai": asdict(outcome.understanding.trace),
                    "evidence": {
                        "source_views": list(outcome.result.plan.source_views or (outcome.result.plan.view_name,)),
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
            return failure_response(error, "ai_unavailable", retryable=True)
        except KnowledgeError as error:
            return failure_response(error, "knowledge_unavailable", retryable=False)
        except DashboardUnsupportedQuery as error:
            return failure_response(error, "unsupported_query", retryable=False)
        except DashboardPlanningError as error:
            return failure_response(error, "internal_error", retryable=True)
        except (KeyError, ValueError) as error:
            return failure_response(error, "unsupported_query", retryable=False)
        except Exception as error:
            return failure_response(error, "internal_error", retryable=True)

    @app.post("/api/query")
    def query_data(payload: QueryRequest, request: Request) -> JSONResponse:
        """查询接口：AI 基于知识生成 SQL，守卫只读执行，再由 AI 基于证据回答。"""

        source, profile = active_context(request)
        def failure_response(
            error: Exception,
            category: str,
            retryable: bool,
        ) -> JSONResponse:
            """客户错误边界：记录完整技术栈，只返回模型整理后的自然语言和追踪号。"""

            reference_id = uuid4().hex[:10]
            logger.exception(
                "客户查询未完成 reference_id=%s category=%s error_type=%s",
                reference_id,
                category,
                type(error).__name__,
            )
            answer, generated_by_ai = explain_query_failure(
                request.app.state.llm,
                payload.question,
                category,
                {
                    "ai_unavailable": "当前暂时无法完成问题理解，请稍后重试。",
                    "missing_information": "还缺少必要的业务对象、指标或范围，请补充后再查询。",
                    "knowledge_unavailable": "本地知识画像不可用，当前暂时不能安全查询。",
                    "unsupported_query": "当前语义层中没有足够信息回答这个问题，可以换一种方式说明业务对象和指标。",
                    "internal_error": "当前查询没有成功完成，请稍后重试。若持续出现，可将页面上的参考编号提供给管理员。",
                },
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

        try:
            llm: LLMClient | None = request.app.state.llm
            runtime = QueryRuntime.prepare(source, profile, llm)
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
            result_payload = _json_safe(asdict(outcome.result))
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
            return failure_response(error, "ai_unavailable", retryable=True)
        except RouteConfirmationRequired as error:
            return JSONResponse(
                {
                    "status": "confirmation_required",
                    "message": str(error),
                    "route": asdict(error.decision),
                }
            )
        except KnowledgeError as error:
            return failure_response(error, "knowledge_unavailable", retryable=False)
        except (KeyError, ValueError) as error:
            return failure_response(error, "unsupported_query", retryable=False)
        except Exception as error:
            # 查询接口是客户边界；未知异常不能把堆栈、内部对象或数据库细节发送到浏览器。
            return failure_response(error, "internal_error", retryable=True)

    @app.get("/api/query/exports/{download_id}")
    def download_query_export(download_id: str, request: Request) -> StreamingResponse:
        """下载接口：凭短期令牌重新执行安全 SQL，并流式生成完整 Excel 文件。"""

        export_store: QueryExportRegistry = request.app.state.query_exports
        plan = export_store.get(download_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="下载已失效，请重新查询。")

        source, profile = active_context(request)

        service = ReadOnlyQueryService(
            source,
            load_catalog(),
            database_profile=profile,
        )
        output = SpooledTemporaryFile(max_size=8 * 1024 * 1024, mode="w+b")
        workbook = Workbook(write_only=True)
        worksheet = workbook.create_sheet("查询结果")

        def safe_excel_value(value: Any) -> Any:
            """Excel 安全层：阻止数据库文本被电子表格解释为公式。"""

            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            if isinstance(value, str):
                value = value[:32_767]
                if value.startswith(("=", "+", "-", "@")):
                    return "'" + value
            return value

        try:
            with service.open_generated_export(plan.sql, plan.parameters) as (columns, rows):
                worksheet.append(columns)
                for row in rows:
                    worksheet.append(tuple(safe_excel_value(value) for value in row))
            workbook.save(output)
            output.seek(0)
        except Exception:
            output.close()
            logger.exception("生成完整查询 Excel 失败 download_id=%s", download_id)
            raise HTTPException(status_code=422, detail="完整结果生成失败，请重新查询后再试。")

        def file_chunks() -> Any:
            """响应流：按 64KB 输出临时文件，并在传输结束后立即释放。"""

            try:
                while chunk := output.read(64 * 1024):
                    yield chunk
            finally:
                output.close()

        return StreamingResponse(
            file_chunks(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="data-agent-query-{download_id[:8]}.xlsx"'
                )
            },
        )

    if FRONTEND_DIST_PATH.exists():
        # 生产构建存在时由 FastAPI 同源托管；开发阶段仍使用 Vite HMR。
        app.mount("/", StaticFiles(directory=FRONTEND_DIST_PATH, html=True), name="frontend")
    return app


app = create_app()
