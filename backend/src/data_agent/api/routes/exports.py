"""查询结果导出路由。"""

from __future__ import annotations

import logging
from tempfile import SpooledTemporaryFile
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

from data_agent.api.deps import active_context
from data_agent.knowledge.semantic_catalog import load_semantic_catalog
from data_agent.query.execution.executor import ReadOnlyQueryExecutor
from data_agent.query.execution.exports import QueryExportRegistry
from data_agent.query.execution.guard import SQLGuard


logger = logging.getLogger(__name__)
router = APIRouter()


def _safe_excel_value(value: Any) -> Any:
    """Excel 安全层：阻止数据库文本被电子表格解释为公式。"""

    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        value = value[:32_767]
        if value.startswith(("=", "+", "-", "@")):
            return "'" + value
    return value


@router.get("/api/query/exports/{download_id}")
def download_query_export(download_id: str, request: Request) -> StreamingResponse:
    """下载接口：凭短期令牌重新执行安全 SQL，并流式生成完整 Excel 文件。"""

    export_store: QueryExportRegistry = request.app.state.query_exports
    plan = export_store.get(download_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="下载已失效，请重新查询。")

    source, profile = active_context(request)
    catalog = load_semantic_catalog()
    guard = SQLGuard(catalog, profile, max_rows=500, source=source)
    executor = ReadOnlyQueryExecutor(
        source,
        catalog,
        database_profile=profile,
        guard=guard,
    )
    output = SpooledTemporaryFile(max_size=8 * 1024 * 1024, mode="w+b")
    workbook = Workbook(write_only=True)
    worksheet = workbook.create_sheet("查询结果")

    try:
        with executor.open_generated_export(plan.sql, plan.parameters) as (columns, rows):
            worksheet.append(columns)
            for row in rows:
                worksheet.append(tuple(_safe_excel_value(value) for value in row))
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
