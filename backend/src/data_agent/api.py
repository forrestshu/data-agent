"""FastAPI 接口层：向 React 提供查询、确认和知识同步边界。"""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
import logging
from logging.handlers import RotatingFileHandler
from tempfile import SpooledTemporaryFile
import threading
import time
from typing import Annotated, Any, AsyncIterator
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openpyxl import Workbook
from pydantic import BaseModel, Field

from .ai_agent import AIQueryAgent, AgentClarificationRequired
from .catalog import load_catalog
from .data_sources import (
    DataSourceConfig,
    DataSourceRegistry,
    SQLITE_SOURCE_ID,
)
from .dashboard import build_initial_dashboard, build_query_dashboard
from .dashboard_agent import (
    DashboardAgent,
    DashboardClarificationRequired,
    DashboardPlanningError,
)
from .executor import ClarificationRequired, ReadOnlyQueryService
from .knowledge_sync import KnowledgeReviewRequired, KnowledgeSyncService
from .llm import DeepSeekClient, LLMClient, LLMUnavailable
from .router import RouteConfirmationRequired
from .semantic_review import SemanticReviewError, SemanticReviewService
from .settings import CATALOG_PATH, FRONTEND_DIST_PATH, RUNTIME_ROOT
from .sqlserver_knowledge_sync import SQLServerKnowledgeSyncService


logger = logging.getLogger(__name__)
QUERY_ERROR_LOG_PATH = RUNTIME_ROOT / "query-errors.log"


def _configure_query_error_log() -> None:
    """把客户边界异常保存在本机运行目录，便于凭参考编号排查。"""

    QUERY_ERROR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    resolved = str(QUERY_ERROR_LOG_PATH.resolve())
    if any(
        isinstance(handler, RotatingFileHandler)
        and getattr(handler, "baseFilename", None) == resolved
        for handler in logger.handlers
    ):
        return
    handler = RotatingFileHandler(
        QUERY_ERROR_LOG_PATH,
        maxBytes=2 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    handler.setLevel(logging.ERROR)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


_configure_query_error_log()


def _json_safe(value: Any) -> Any:
    """把 SQL Server Decimal、日期等驱动类型转换成标准 JSON 值。"""

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


@dataclass(frozen=True)
class QueryExportPlan:
    """临时导出凭证：只保存已验证 SQL，不缓存完整业务数据，15 分钟后失效。"""

    created_at: float
    source_id: str
    database_fingerprint: str
    schema_fingerprint: str
    sql: str
    parameters: tuple[Any, ...]


@dataclass
class KnowledgeSyncJob:
    """后台画像任务状态；旧画像在任务完成前继续服务查询。"""

    job_id: str
    source_id: str
    source_kind: str
    dataset_label: str
    status: str
    created_at: float
    completed_views: int = 0
    total_views: int = 0
    current_view: str | None = None
    finished_at: float | None = None
    message: str | None = None

    def public_dict(self) -> dict[str, Any]:
        return asdict(self)


class SyncRequest(BaseModel):
    """接口模型：保留显式同步原因，便于后续接入审计日志。"""

    reason: str = Field(default="manual", min_length=2, max_length=200)


class SemanticReviewRequest(BaseModel):
    """接口模型：人工明确批准或拒绝 AI 语义建议，并可留下审核说明。"""

    decision: str = Field(pattern="^(approve|reject)$")
    reviewer_note: str = Field(default="", max_length=500)


class DataSourceSwitchRequest(BaseModel):
    """切换契约：只接受后端预先登记的固定数据源 ID。"""

    source_id: str = Field(pattern="^(sqlite_internal|sqlserver_company)$")


def _knowledge_service(source: DataSourceConfig) -> Any:
    if source.kind == "sqlite":
        assert source.database_path is not None
        return KnowledgeSyncService(
            source.database_path,
            catalog_path=CATALOG_PATH,
            profile_path=source.profile_path,
            report_path=source.report_path,
        )
    return SQLServerKnowledgeSyncService(source)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """启动时确保活动数据源已连接并有独立机器画像。"""

    source: DataSourceConfig = app.state.source_registry.active()
    manager = app.state.knowledge_by_source[source.source_id]
    if source.kind == "sqlserver":
        # 首次启动或结构发生变化时完成限时完整画像；已有兼容画像可直接复用。
        existing = manager.load_profile()
        status = manager.status() if existing is not None else {"status": "update_required"}
        if existing is None or status.get("status") == "update_required":
            manager.sync()
    profile = manager.ensure_current(auto_sync=True)
    semantic: SemanticReviewService = app.state.semantic_by_source[source.source_id]
    semantic.ensure_for_profile(profile)
    yield


def create_app(
    llm_client: LLMClient | None = None,
    use_environment_ai: bool = True,
    require_ai: bool = True,
    source_id: str | None = None,
    persist_source: bool = True,
) -> FastAPI:
    """应用工厂：客户模式强制 AI；测试或诊断可显式允许本地规则能力。"""

    configured_llm = llm_client
    if configured_llm is None and use_environment_ai:
        configured_llm = DeepSeekClient.from_environment()
    app = FastAPI(
        title="ERP Data Agent API",
        version="0.3.0",
        description="DeepSeek 语义理解、自然语言回答与 SQLite/SQL Server 双数据源服务",
        lifespan=lifespan,
    )
    app.state.source_registry = DataSourceRegistry(
        active_source_id=source_id,
        persist=persist_source,
    )
    app.state.knowledge_by_source = {
        source.source_id: _knowledge_service(source)
        for source in app.state.source_registry.sources.values()
    }
    app.state.llm = configured_llm
    app.state.require_ai = require_ai
    app.state.semantic_by_source = {
        source.source_id: SemanticReviewService(
            configured_llm,
            proposals_path=source.proposals_path,
        )
        for source in app.state.source_registry.sources.values()
    }
    app.state.query_exports: dict[str, QueryExportPlan] = {}
    app.state.knowledge_sync_jobs: dict[str, KnowledgeSyncJob] = {}
    app.state.knowledge_sync_jobs_lock = threading.RLock()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type"],
    )

    def active_context(request: Request) -> tuple[DataSourceConfig, Any, SemanticReviewService]:
        """每次请求只读取一次活动源，确保并发切换时上下文不混用。"""

        registry: DataSourceRegistry = request.app.state.source_registry
        source = registry.active()
        return (
            source,
            request.app.state.knowledge_by_source[source.source_id],
            request.app.state.semantic_by_source[source.source_id],
        )

    def source_envelope(source: DataSourceConfig) -> dict[str, Any]:
        return source.source_metadata()

    def data_sources_payload(request: Request) -> dict[str, Any]:
        registry: DataSourceRegistry = request.app.state.source_registry
        sources = []
        for public in registry.list_public():
            manager = request.app.state.knowledge_by_source[public["source_id"]]
            if public["source_id"] == registry.active_source_id:
                status = manager.status()
            elif public["source_kind"] == "sqlserver":
                status = manager.status(check_remote=False)
            else:
                status = manager.status()
            sources.append(
                {
                    **public,
                    "status": status.get("status", "unknown"),
                    "reason": status.get("reason"),
                    "generated_at": status.get("generated_at"),
                }
            )
        return {
            "active_source_id": registry.active_source_id,
            "sources": sources,
        }

    @app.get("/api/health")
    def health(request: Request) -> dict[str, Any]:
        """健康接口：同时返回服务状态和知识画像是否可查询。"""

        source, manager, _ = active_context(request)
        llm: LLMClient | None = request.app.state.llm
        return {
            "service": "ok",
            "knowledge": {**manager.status(), **source_envelope(source)},
            "data_source": source.public_dict(),
            "ai": {
                "configured": llm is not None,
                "provider": llm.provider if llm else None,
                "model": llm.model if llm else None,
                "required": request.app.state.require_ai,
            },
        }

    @app.get("/api/data-sources")
    def data_sources(request: Request) -> dict[str, Any]:
        """列出固定数据源及安全状态，不返回账号、密码或连接串。"""

        return data_sources_payload(request)

    @app.put("/api/data-sources/active")
    def switch_data_source(
        payload: DataSourceSwitchRequest,
        request: Request,
    ) -> dict[str, Any]:
        """先验证目标连接与画像，成功后才原子切换并清理旧导出令牌。"""

        registry: DataSourceRegistry = request.app.state.source_registry
        target = registry.get(payload.source_id)
        manager = request.app.state.knowledge_by_source[target.source_id]
        semantic: SemanticReviewService = request.app.state.semantic_by_source[target.source_id]
        try:
            if target.kind == "sqlserver":
                manager.prepare_for_activation()
            else:
                manager.ensure_current(auto_sync=True)
            profile = manager.ensure_current(auto_sync=False)
            semantic.ensure_for_profile(profile)
        except Exception as error:
            logger.warning(
                "数据源切换预检失败 source_id=%s error_type=%s",
                target.source_id,
                type(error).__name__,
            )
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "data_source_unavailable",
                    "message": f"{target.dataset_label}暂时无法连接或知识尚未就绪，当前数据源没有改变。",
                },
            ) from error
        registry.activate(target.source_id)
        request.app.state.query_exports.clear()
        return {
            **data_sources_payload(request),
            "knowledge": {**manager.status(), **source_envelope(target)},
        }

    @app.get("/api/ai/status")
    def ai_status(request: Request) -> dict[str, Any]:
        """AI 状态接口：只报告是否配置与模型名，绝不返回 Key。"""

        llm: LLMClient | None = request.app.state.llm
        return {
            "configured": llm is not None,
            "provider": llm.provider if llm else None,
            "model": llm.model if llm else None,
            "required": request.app.state.require_ai,
            "role": "精确数据查询 Text-to-SQL、Dashboard 概况规划、澄清、证据回答和新结构语义建议",
        }

    @app.get("/api/examples")
    def examples() -> dict[str, list[str]]:
        """体验接口：给前端提供可直接点击的真实快照问题。"""

        return {
            "examples": [
                "查询物料 110000012 的库存和库位",
                "查询物料 6100001876 的最新采购价和平均价",
                "查询项目 24M148-B 的项目客户、项目机型和项目状态",
                "查询工单 000022 的报工数量和末道工序",
            ]
        }

    @app.get("/api/dashboard")
    def initial_dashboard(request: Request) -> dict[str, Any]:
        """初始 Dashboard：只使用当前知识画像，不擅自执行额外业务查询。"""

        source, manager, _ = active_context(request)
        profile = manager.ensure_current(auto_sync=True)
        dashboard = build_initial_dashboard(profile, load_catalog())
        return {
            **_json_safe(dashboard),
            **source_envelope(source),
        }

    @app.post("/api/dashboard/query")
    def query_dashboard(
        payload: DashboardQueryRequest,
        request: Request,
    ) -> JSONResponse:
        """Dashboard 查询链路：概况理解、只读验证和图表契约彼此独立于精确查询。"""

        source, manager, _ = active_context(request)
        agent: DashboardAgent | None = None

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
            if agent is None:
                answer = "当前 Dashboard 没有成功生成，请稍后重试。"
                generated_by_ai = False
            else:
                answer, generated_by_ai = agent.explain_failure(
                    payload.question,
                    category,
                )
            return JSONResponse(
                {
                    "status": "query_failed",
                    "answer": answer,
                    "answer_generated_by_ai": generated_by_ai,
                    "reference_id": reference_id,
                    "retryable": retryable,
                    **source_envelope(source),
                }
            )

        try:
            profile = manager.ensure_current(auto_sync=True)
            catalog = load_catalog()
            llm: LLMClient | None = request.app.state.llm
            if request.app.state.require_ai and llm is None:
                raise LLMUnavailable(
                    "DeepSeek 尚未配置，Dashboard 概况必须使用 AI 理解。"
                )
            service = ReadOnlyQueryService(
                source,
                catalog,
                database_profile=profile,
            )
            agent = DashboardAgent(
                catalog,
                llm,
                database_profile=profile,
                allow_fallback=not request.app.state.require_ai,
                source=source,
            )
            understanding = agent.understand(
                payload.question,
                confirmed_view=payload.confirmed_view,
                clarification_answer=payload.clarification_answer,
                clarification_history=tuple(
                    (turn.question, turn.answer)
                    for turn in payload.clarification_history
                ),
                limit=payload.limit,
            )
            for source_view in understanding.source_views:
                manager.assert_view_ready(profile, source_view)
            result = service.ask_generated_sql(
                understanding.effective_question,
                understanding.generated_sql,
                understanding.sql_parameters,
                route_decision=understanding.route,
                limit=payload.limit,
            )
            result = agent.localize_result_columns(
                understanding.effective_question,
                result,
            )
            dashboard = build_query_dashboard(
                understanding.effective_question,
                result,
                original_question=payload.question,
                intent_summary=understanding.trace.intent_summary,
                route_reason=understanding.trace.route_reason,
                display_units=understanding.display_units,
                dashboard_title=understanding.title,
                dashboard_summary=understanding.summary,
                visualization_hint=understanding.visualization,
                preferred_dimensions=understanding.dimension_columns,
                preferred_metrics=understanding.metric_columns,
            )
            return JSONResponse(
                {
                    "status": "completed",
                    "dashboard": _json_safe(dashboard),
                    "ai": asdict(understanding.trace),
                    "evidence": {
                        "source_views": list(result.plan.source_views or (result.plan.view_name,)),
                        "total_count": result.total_count,
                        "displayed_count": len(result.rows),
                        "has_more": result.has_more,
                        "notices": list(result.notices),
                    },
                    **source_envelope(source),
                }
            )
        except DashboardClarificationRequired as error:
            return JSONResponse(
                {
                    "status": "clarification_required",
                    "message": str(error),
                    "analysis": error.analysis.model_dump(),
                    "ai": {"provider": error.provider, "model": error.model},
                    **source_envelope(source),
                }
            )
        except LLMUnavailable as error:
            return failure_response(error, "ai_unavailable", retryable=True)
        except KnowledgeReviewRequired as error:
            return failure_response(error, "knowledge_updating", retryable=True)
        except DashboardPlanningError as error:
            return failure_response(error, "unsupported_query", retryable=False)
        except (KeyError, ValueError) as error:
            return failure_response(error, "unsupported_query", retryable=False)
        except Exception as error:
            return failure_response(error, "internal_error", retryable=True)

    @app.post("/api/query")
    def query_data(payload: QueryRequest, request: Request) -> JSONResponse:
        """查询接口：AI 基于知识生成 SQL，守卫只读执行，再由 AI 基于证据回答。"""

        source, manager, _ = active_context(request)
        agent: AIQueryAgent | None = None

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
            if agent is None:
                answer = "当前查询没有成功完成，请稍后重试。"
                generated_by_ai = False
            else:
                answer, generated_by_ai = agent.explain_failure(
                    payload.question,
                    category,
                )
            return JSONResponse(
                {
                    "status": "query_failed",
                    "answer": answer,
                    "answer_generated_by_ai": generated_by_ai,
                    "reference_id": reference_id,
                    "retryable": retryable,
                    **source_envelope(source),
                }
            )

        try:
            profile = manager.ensure_current(auto_sync=True)
            catalog = load_catalog()
            llm: LLMClient | None = request.app.state.llm
            if request.app.state.require_ai and llm is None:
                raise LLMUnavailable(
                    "DeepSeek 尚未配置，客户查询必须使用 AI 理解并生成回答。"
                )
            service = ReadOnlyQueryService(
                source,
                catalog,
                database_profile=profile,
            )
            agent = AIQueryAgent(
                catalog,
                llm,
                database_profile=profile,
                allow_fallback=not request.app.state.require_ai,
                source=source,
            )
            understanding = agent.understand(
                payload.question,
                confirmed_view=payload.confirmed_view,
                clarification_answer=payload.clarification_answer,
                clarification_history=tuple(
                    (turn.question, turn.answer)
                    for turn in payload.clarification_history
                ),
                limit=payload.limit,
            )
            if understanding.route.requires_confirmation:
                raise RouteConfirmationRequired(understanding.route)
            for source_view in understanding.source_views:
                manager.assert_view_ready(profile, source_view)
            if understanding.generated_sql is not None:
                result = service.ask_generated_sql(
                    understanding.effective_question,
                    understanding.generated_sql,
                    understanding.sql_parameters,
                    route_decision=understanding.route,
                    limit=payload.limit,
                )
            else:
                # 无 AI 的测试/诊断模式保留原确定性查询器，生产模式始终走 Text-to-SQL。
                result = service.ask(
                    understanding.effective_question,
                    limit=payload.limit,
                    route_decision=understanding.route,
                    value_hints=understanding.value_hints,
                    operation=understanding.operation,
                    metric_column=understanding.metric_column,
                )
            result = agent.localize_result_columns(
                understanding.effective_question,
                result,
            )
            # 回答层也必须看到完整澄清历史，否则 SQL 使用了用户阈值，文案却可能遗忘阈值。
            answer, answer_generated_by_ai = agent.answer(
                understanding.effective_question,
                result,
            )
            result_payload = _json_safe(asdict(result))
            result_payload["download_id"] = None
            if result.plan.base_sql:
                # 每次成功查询都提供导出；令牌只保存来源绑定的安全计划。
                now = time.monotonic()
                export_store: dict[str, QueryExportPlan] = request.app.state.query_exports
                expired = [
                    key
                    for key, item in export_store.items()
                    if now - item.created_at > 900
                ]
                for key in expired:
                    export_store.pop(key, None)
                while len(export_store) >= 20:
                    oldest = min(export_store, key=lambda key: export_store[key].created_at)
                    export_store.pop(oldest, None)
                download_id = uuid4().hex
                export_store[download_id] = QueryExportPlan(
                    created_at=now,
                    source_id=source.source_id,
                    database_fingerprint=str(
                        profile.get("database", {}).get("content_fingerprint", "")
                    ),
                    schema_fingerprint=str(
                        profile.get("database", {}).get("schema_fingerprint", "")
                    ),
                    sql=result.plan.base_sql,
                    parameters=result.plan.parameters,
                )
                result_payload["download_id"] = download_id
            return JSONResponse(
                {
                    "status": "completed",
                    "answer": answer,
                    "answer_generated_by_ai": answer_generated_by_ai,
                    "result": result_payload,
                    "ai": asdict(understanding.trace),
                    **source_envelope(source),
                }
            )
        except AgentClarificationRequired as error:
            return JSONResponse(
                {
                    "status": "clarification_required",
                    "message": str(error),
                    "analysis": error.analysis.model_dump(),
                    "ai": {"provider": error.provider, "model": error.model},
                    **source_envelope(source),
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
                    **source_envelope(source),
                }
            )
        except ClarificationRequired as error:
            return failure_response(error, "missing_information", retryable=False)
        except KnowledgeReviewRequired as error:
            return failure_response(error, "knowledge_updating", retryable=True)
        except (KeyError, ValueError) as error:
            return failure_response(error, "unsupported_query", retryable=False)
        except Exception as error:
            # 查询接口是客户边界；未知异常不能把堆栈、内部对象或数据库细节发送到浏览器。
            return failure_response(error, "internal_error", retryable=True)

    @app.get("/api/query/exports/{download_id}")
    def download_query_export(download_id: str, request: Request) -> StreamingResponse:
        """下载接口：凭短期令牌重新执行安全 SQL，并流式生成完整 Excel 文件。"""

        export_store: dict[str, QueryExportPlan] = request.app.state.query_exports
        plan = export_store.get(download_id)
        if plan is None or time.monotonic() - plan.created_at > 900:
            export_store.pop(download_id, None)
            raise HTTPException(status_code=404, detail="下载已失效，请重新查询。")

        source, manager, _ = active_context(request)
        if source.source_id != plan.source_id:
            export_store.pop(download_id, None)
            raise HTTPException(status_code=409, detail="数据源已切换，请重新查询后下载。")
        profile = manager.ensure_current(auto_sync=True)
        fingerprint = str(profile.get("database", {}).get("content_fingerprint", ""))
        schema_fingerprint = str(
            profile.get("database", {}).get("schema_fingerprint", "")
        )
        if source.kind == "sqlite" and fingerprint != plan.database_fingerprint:
            export_store.pop(download_id, None)
            raise HTTPException(status_code=409, detail="数据库已更新，请重新查询后下载。")
        if schema_fingerprint != plan.schema_fingerprint:
            export_store.pop(download_id, None)
            raise HTTPException(status_code=409, detail="数据库结构已更新，请重新查询后下载。")

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

    @app.get("/api/knowledge/status")
    def knowledge_status(request: Request) -> dict[str, Any]:
        """治理接口：返回数据库指纹、漂移摘要和待审核兼容性问题。"""

        source, manager, _ = active_context(request)
        return {**manager.status(), **source_envelope(source)}

    def _run_knowledge_sync_job(
        job: KnowledgeSyncJob,
        source: DataSourceConfig,
        manager: Any,
        semantic: SemanticReviewService,
    ) -> None:
        """后台构建候选画像；manager.sync 只在完整成功后原子写入。"""

        jobs_lock: threading.RLock = app.state.knowledge_sync_jobs_lock

        def progress(completed: int, total: int, view: str, _: str) -> None:
            with jobs_lock:
                job.completed_views = completed
                job.total_views = total
                job.current_view = view

        with jobs_lock:
            job.status = "running"
        try:
            if source.kind == "sqlserver":
                manager.sync(progress_callback=progress)
            else:
                manager.sync()
            profile = manager.load_profile()
            if profile is None:
                raise KnowledgeReviewRequired("同步完成后未找到知识画像。")
            semantic.ensure_for_profile(profile)
            with jobs_lock:
                job.status = "completed"
                job.completed_views = int(
                    profile.get("summary", {}).get("business_table_count") or 0
                )
                job.total_views = job.completed_views
                job.current_view = None
                job.finished_at = time.time()
                job.message = "同步完成"
        except Exception as error:
            logger.warning(
                "后台知识同步失败 source_id=%s error_type=%s",
                source.source_id,
                type(error).__name__,
            )
            with jobs_lock:
                job.status = "failed"
                job.current_view = None
                job.finished_at = time.time()
                job.message = "同步失败，上一份有效画像仍在使用。"

    @app.post("/api/knowledge/sync")
    def sync_knowledge(payload: SyncRequest, request: Request) -> dict[str, Any]:
        """启动后台完整画像，不阻塞页面或覆盖当前有效画像。"""

        source, manager, semantic = active_context(request)
        jobs: dict[str, KnowledgeSyncJob] = request.app.state.knowledge_sync_jobs
        jobs_lock: threading.RLock = request.app.state.knowledge_sync_jobs_lock
        with jobs_lock:
            for existing in jobs.values():
                if (
                    existing.source_id == source.source_id
                    and existing.status in {"queued", "running"}
                ):
                    return {
                        **existing.public_dict(),
                        **source_envelope(source),
                        "reason": payload.reason,
                    }
            profile = manager.load_profile() or {}
            total_views = int(
                profile.get("summary", {}).get("business_table_count") or 0
            )
            job = KnowledgeSyncJob(
                job_id=uuid4().hex,
                source_id=source.source_id,
                source_kind=source.kind,
                dataset_label=source.dataset_label,
                status="queued",
                created_at=time.time(),
                total_views=total_views,
            )
            jobs[job.job_id] = job
            finished_jobs = sorted(
                (
                    candidate
                    for candidate in jobs.values()
                    if candidate.status in {"completed", "failed"}
                ),
                key=lambda candidate: candidate.finished_at or candidate.created_at,
                reverse=True,
            )
            for stale in finished_jobs[20:]:
                jobs.pop(stale.job_id, None)
        threading.Thread(
            target=_run_knowledge_sync_job,
            args=(job, source, manager, semantic),
            name=f"knowledge-sync-{source.source_id}",
            daemon=True,
        ).start()
        return {
            **job.public_dict(),
            **source_envelope(source),
            "reason": payload.reason,
        }

    @app.get("/api/knowledge/sync/{job_id}")
    def knowledge_sync_job(job_id: str, request: Request) -> dict[str, Any]:
        """读取后台同步进度；任务结果不包含数据库凭据或业务数据。"""

        jobs: dict[str, KnowledgeSyncJob] = request.app.state.knowledge_sync_jobs
        jobs_lock: threading.RLock = request.app.state.knowledge_sync_jobs_lock
        with jobs_lock:
            job = jobs.get(job_id)
            if job is None:
                raise HTTPException(status_code=404, detail="同步任务不存在或已过期。")
            return job.public_dict()

    @app.get("/api/knowledge/semantic-proposals")
    def semantic_proposals(request: Request) -> dict[str, Any]:
        """语义治理接口：返回 AI 对新增表/字段的建议及人工审核状态。"""

        source, manager, semantic = active_context(request)
        profile = manager.ensure_current(auto_sync=True)
        return {
            **semantic.ensure_for_profile(profile),
            **source_envelope(source),
        }

    @app.post("/api/knowledge/semantic-proposals/{proposal_id}/review")
    def review_semantic_proposal(
        proposal_id: str,
        payload: SemanticReviewRequest,
        request: Request,
    ) -> dict[str, Any]:
        """语义治理接口：只有这个显式人工动作能把 AI 建议写入查询知识。"""

        source, manager, semantic = active_context(request)
        profile = manager.ensure_current(auto_sync=False)
        try:
            reviewed = semantic.review(
                proposal_id,
                decision=payload.decision,
                reviewer_note=payload.reviewer_note,
                profile=profile,
            )
            if payload.decision == "approve":
                manager.sync()
            return {**reviewed, **source_envelope(source)}
        except SemanticReviewError as error:
            raise HTTPException(
                status_code=422,
                detail={"code": "semantic_review_error", "message": str(error)},
            ) from error

    @app.get("/api/knowledge/catalog")
    def knowledge_catalog(
        request: Request,
        include_columns: Annotated[bool, Query()] = False,
    ) -> dict[str, Any]:
        """治理接口：展示人工业务知识；按需附带机器字段画像，避免首页负载过大。"""

        source, manager, _ = active_context(request)
        profile = manager.ensure_current(auto_sync=True)
        catalog = load_catalog()
        tables = profile.get("tables", [])
        if not include_columns:
            tables = [
                {key: value for key, value in table.items() if key != "columns"}
                for table in tables
            ]
        return {
            "catalog_version": catalog.version,
            "views": [asdict(view) for view in catalog.views],
            "relationships": [asdict(item) for item in catalog.relationships],
            "join_policies": list(catalog.join_policies),
            "semantic_equivalences": list(catalog.semantic_equivalences),
            "semantic_conflicts": list(catalog.semantic_conflicts),
            "semantic_source": catalog.semantic_source,
            "tables": tables,
            "generated_limitations": profile.get("generated_limitations", []),
            **source_envelope(source),
        }

    if FRONTEND_DIST_PATH.exists():
        # 生产构建存在时由 FastAPI 同源托管；开发阶段仍使用 Vite HMR。
        app.mount("/", StaticFiles(directory=FRONTEND_DIST_PATH, html=True), name="frontend")
    return app


app = create_app()
