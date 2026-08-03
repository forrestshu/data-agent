"""SQL Server 实时视图的知识画像、结构漂移与兼容性检查。"""

from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import json
import threading
import time
from typing import Any, Callable

from .catalog import load_catalog
from .data_sources import DataSourceConfig
from .knowledge_sync import KnowledgeReviewRequired, KnowledgeSyncService


class SQLServerKnowledgeSyncService:
    """只扫描固定 SQL Server 数据库与 Schema，不读取或保存业务明细。"""

    SCHEMA_CHECK_INTERVAL_SECONDS = 300.0

    _table_map = staticmethod(KnowledgeSyncService._table_map)

    def __init__(self, source: DataSourceConfig) -> None:
        if source.kind != "sqlserver":
            raise ValueError("SQLServerKnowledgeSyncService 只接受 SQL Server 数据源。")
        self.source = source
        self.database_path = None
        self.profile_path = source.profile_path
        self.report_path = source.report_path
        self._sync_lock = threading.Lock()
        self._last_schema_check_at = 0.0
        self._last_schema_fingerprint: str | None = None
        self._last_schema_error: str | None = None

    @staticmethod
    def _schema_fingerprint(tables: list[dict[str, Any]]) -> str:
        schema = [
            {
                "name": table["name"],
                "columns": [
                    (column["name"], column.get("data_type", ""))
                    for column in table.get("columns", [])
                ],
            }
            for table in tables
        ]
        payload = json.dumps(schema, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _metadata_tables(self) -> list[dict[str, Any]]:
        """读取 Cux 中 AiQuery 视图及列类型；不接受配置外的数据库或 Schema。"""

        assert self.source.schema is not None
        sql = """
SELECT
    c.TABLE_NAME,
    c.ORDINAL_POSITION,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS AS c
INNER JOIN INFORMATION_SCHEMA.VIEWS AS v
    ON v.TABLE_SCHEMA = c.TABLE_SCHEMA
   AND v.TABLE_NAME = c.TABLE_NAME
WHERE c.TABLE_SCHEMA = ?
  AND c.TABLE_NAME LIKE 'AiQuery%V'
ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
""".strip()
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        with self.source.connect(timeout_seconds=self.source.query_timeout_seconds) as connection:
            cursor = self.source.execute(connection, sql, (self.source.schema,))
            for row in self.source.fetchall_dicts(cursor):
                grouped[str(row["TABLE_NAME"])].append(
                    {
                        "name": str(row["COLUMN_NAME"]),
                        "data_type": str(row["DATA_TYPE"] or ""),
                        "not_null_declared": str(row["IS_NULLABLE"]).upper() == "NO",
                        "null_count": None,
                        "non_null_count": None,
                        "quality": "unknown",
                    }
                )
        return [
            {"name": name, "row_count": 0, "statistics_status": "not_scanned", "columns": columns}
            for name, columns in sorted(grouped.items())
        ]

    @staticmethod
    def _previous_table_map(
        previous: dict[str, Any] | None,
    ) -> dict[str, dict[str, Any]]:
        if not previous:
            return {}
        return {
            str(table.get("name")): table
            for table in previous.get("tables", [])
            if table.get("name")
        }

    def _reuse_cooled_failure(
        self,
        table: dict[str, Any],
        previous_table: dict[str, Any] | None,
        *,
        same_schema: bool,
    ) -> bool:
        """相同结构下暂缓重复执行已知失败的昂贵统计查询。"""

        if not same_schema or not previous_table:
            return False
        if previous_table.get("statistics_status") != "unknown":
            return False
        failed_at = previous_table.get("statistics_failed_at")
        if not isinstance(failed_at, (int, float)):
            return False
        cooldown = self.source.statistics_retry_cooldown_seconds
        if cooldown <= 0 or time.time() - float(failed_at) >= cooldown:
            return False
        table["row_count"] = int(previous_table.get("row_count") or 0)
        table["statistics_status"] = "unknown"
        table["statistics_error"] = previous_table.get(
            "statistics_error",
            "StatisticsUnavailable",
        )
        table["statistics_failed_at"] = float(failed_at)
        table["statistics_retry_after"] = float(failed_at) + cooldown
        previous_columns = {
            str(column.get("name")): column
            for column in previous_table.get("columns", [])
            if column.get("name")
        }
        for column in table["columns"]:
            previous_column = previous_columns.get(column["name"], {})
            column["null_count"] = previous_column.get("null_count")
            column["non_null_count"] = previous_column.get("non_null_count")
            column["quality"] = previous_column.get("quality", "unknown")
        return True

    def _scan_table_statistics(self, table: dict[str, Any]) -> str:
        """用独立连接扫描一个视图，避免超时污染其他视图连接。"""

        columns = table["columns"]
        expressions = ["COUNT_BIG(*) AS [row_count]"]
        expressions.extend(
            "SUM(CASE WHEN "
            f"{self.source.quote_identifier(column['name'])} IS NULL "
            f"THEN 1 ELSE 0 END) AS [null_{index}]"
            for index, column in enumerate(columns)
        )
        sql = (
            f"SELECT {', '.join(expressions)} "
            f"FROM {self.source.physical_view(table['name'])}"
        )
        try:
            with self.source.connect(
                timeout_seconds=self.source.statistics_timeout_seconds
            ) as connection:
                cursor = self.source.execute(connection, sql)
                raw = cursor.fetchone()
                if raw is None:
                    raise RuntimeError("统计查询没有返回结果。")
                row = self.source.row_dict(cursor, raw)
            row_count = int(row.get("row_count") or 0)
            table["row_count"] = row_count
            table["statistics_status"] = "ready"
            table.pop("statistics_error", None)
            table.pop("statistics_failed_at", None)
            table.pop("statistics_retry_after", None)
            for index, column in enumerate(columns):
                null_count = int(row.get(f"null_{index}") or 0)
                column["null_count"] = null_count
                column["non_null_count"] = row_count - null_count
                column["quality"] = (
                    "all_null"
                    if row_count > 0 and null_count == row_count
                    else "available"
                )
            return "ready"
        except Exception as error:
            failed_at = time.time()
            table["statistics_status"] = "unknown"
            table["statistics_error"] = type(error).__name__
            table["statistics_failed_at"] = failed_at
            table["statistics_retry_after"] = (
                failed_at + self.source.statistics_retry_cooldown_seconds
            )
            for column in columns:
                column["quality"] = "unknown"
            return "unknown"

    def _add_statistics(
        self,
        tables: list[dict[str, Any]],
        *,
        previous: dict[str, Any] | None = None,
        schema_fingerprint: str | None = None,
        progress_callback: Callable[[int, int, str, str], None] | None = None,
    ) -> None:
        """以小规模并发扫描视图；结果仍保持逐视图精确统计。"""

        previous_tables = self._previous_table_map(previous)
        previous_schema = (
            previous.get("database", {}).get("schema_fingerprint")
            if previous
            else None
        )
        same_schema = bool(
            schema_fingerprint
            and previous_schema
            and schema_fingerprint == previous_schema
        )
        total = len(tables)
        completed = 0
        pending: list[dict[str, Any]] = []
        for table in tables:
            if self._reuse_cooled_failure(
                table,
                previous_tables.get(table["name"]),
                same_schema=same_schema,
            ):
                completed += 1
                if progress_callback:
                    progress_callback(
                        completed,
                        total,
                        table["name"],
                        "cooldown",
                    )
            else:
                pending.append(table)

        workers = min(self.source.statistics_workers, max(1, len(pending)))
        if not pending:
            return
        with ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="sqlserver-statistics",
        ) as executor:
            future_to_table = {
                executor.submit(self._scan_table_statistics, table): table
                for table in pending
            }
            for future in as_completed(future_to_table):
                table = future_to_table[future]
                try:
                    result = future.result()
                except Exception:
                    # 单视图工作线程的意外错误也只降级该视图。
                    table["statistics_status"] = "unknown"
                    table["statistics_error"] = "StatisticsWorkerError"
                    table["statistics_failed_at"] = time.time()
                    for column in table["columns"]:
                        column["quality"] = "unknown"
                    result = "unknown"
                completed += 1
                if progress_callback:
                    progress_callback(completed, total, table["name"], result)

    def _inspect_database(
        self,
        *,
        include_statistics: bool,
        previous: dict[str, Any] | None = None,
        progress_callback: Callable[[int, int, str, str], None] | None = None,
    ) -> list[dict[str, Any]]:
        tables = self._metadata_tables()
        if include_statistics:
            self._add_statistics(
                tables,
                previous=previous,
                schema_fingerprint=self._schema_fingerprint(tables),
                progress_callback=progress_callback,
            )
        return tables

    def load_profile(self) -> dict[str, Any] | None:
        if not self.profile_path.exists():
            return None
        try:
            return json.loads(self.profile_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def sync(
        self,
        progress_callback: Callable[[int, int, str, str], None] | None = None,
    ) -> dict[str, Any]:
        """完整同步：结构必须成功，统计可按视图降级为 unknown。"""

        if not self.source.configured:
            raise KnowledgeReviewRequired("公司 SQL Server 尚未完整配置。")
        with self._sync_lock:
            previous = self.load_profile()
            catalog = load_catalog()
            tables = self._inspect_database(
                include_statistics=True,
                previous=previous,
                progress_callback=progress_callback,
            )
            if not tables:
                raise KnowledgeReviewRequired(
                    "prod.Cux 中未找到可读取的 AiQuery 业务视图。"
                )
            generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
            schema_fingerprint = self._schema_fingerprint(tables)
            compatibility = KnowledgeSyncService._compatibility(catalog, tables)
            generated_limitations = KnowledgeSyncService._generated_limitations(tables)
            if previous is None:
                curated_names = {view.name for view in catalog.views}
                # 首次接入时，目录中已审核的 16 个视图是基线，不应被误报成新增语义。
                previous = {
                    "tables": [
                        table
                        for table in tables
                        if table.get("name") in curated_names
                    ]
                }
            drift = KnowledgeSyncService._build_drift(self, previous, tables)
            statistics_unknown = sum(
                1 for table in tables if table.get("statistics_status") != "ready"
            )
            database = {
                **self.source.source_metadata(),
                "server": self.source.connection_target,
                "database_name": self.source.database_name,
                "schema": self.source.schema,
                "live": True,
                "schema_fingerprint": schema_fingerprint,
                # 语义提案只依赖结构；实时库没有稳定的全库内容指纹。
                "content_fingerprint": schema_fingerprint,
            }
            profile: dict[str, Any] = {
                "profile_version": 2,
                "generated_at": generated_at,
                "database": database,
                "summary": {
                    "business_table_count": len(tables),
                    "total_row_count": sum(int(table.get("row_count") or 0) for table in tables),
                    "all_null_column_count": sum(
                        1
                        for table in tables
                        for column in table.get("columns", [])
                        if column.get("quality") == "all_null"
                    ),
                    "statistics_unknown_view_count": statistics_unknown,
                },
                "snapshot_metadata": {},
                "tables": tables,
                "drift": drift,
                "compatibility": compatibility,
                "generated_limitations": generated_limitations,
            }
            report = {
                "status": "ready" if compatibility["query_ready"] else "review_required",
                "generated_at": generated_at,
                "database": database,
                "summary": profile["summary"],
                "drift": drift,
                "compatibility": compatibility,
                **self.source.source_metadata(),
            }
            KnowledgeSyncService._atomic_write(self.profile_path, profile)
            KnowledgeSyncService._atomic_write(self.report_path, report)
            self._last_schema_check_at = time.monotonic()
            self._last_schema_fingerprint = schema_fingerprint
            self._last_schema_error = None
            return report

    def _refresh_schema_cache(self) -> None:
        now = time.monotonic()
        if now - self._last_schema_check_at < self.SCHEMA_CHECK_INTERVAL_SECONDS:
            return
        try:
            tables = self._inspect_database(include_statistics=False)
            self._last_schema_fingerprint = self._schema_fingerprint(tables)
            self._last_schema_error = None
        except Exception:
            self._last_schema_error = "公司数据库暂时无法连接。"
        finally:
            self._last_schema_check_at = now

    def status(self, *, check_remote: bool = True) -> dict[str, Any]:
        base = self.source.source_metadata()
        if not self.source.configured:
            return {
                **base,
                "status": "not_configured",
                "reason": "公司 SQL Server 尚未完整配置。",
            }
        profile = self.load_profile()
        if profile is None:
            return {
                **base,
                "status": "update_required",
                "reason": "尚未生成公司数据库知识画像。",
            }
        if check_remote:
            self._refresh_schema_cache()
        if self._last_schema_error:
            return {
                **base,
                "status": "connection_error",
                "reason": self._last_schema_error,
                "generated_at": profile.get("generated_at"),
            }
        stored = profile.get("database", {})
        if (
            self._last_schema_fingerprint
            and stored.get("schema_fingerprint") != self._last_schema_fingerprint
        ):
            return {
                **base,
                "status": "update_required",
                "reason": "检测到公司数据库视图结构变化，请先同步数据知识。",
                "generated_at": profile.get("generated_at"),
            }
        compatibility = profile.get("compatibility", {})
        return {
            **base,
            "status": "ready" if compatibility.get("query_ready", False) else "review_required",
            "database": stored,
            "summary": profile.get("summary", {}),
            "drift": profile.get("drift", {}),
            "compatibility": compatibility,
            "generated_at": profile.get("generated_at"),
        }

    def ensure_current(self, auto_sync: bool = True) -> dict[str, Any]:
        profile = self.load_profile()
        if profile is None and auto_sync:
            self.sync()
            profile = self.load_profile()
        status = self.status()
        if status["status"] in {"not_configured", "connection_error", "update_required"}:
            raise KnowledgeReviewRequired(str(status.get("reason") or "公司数据库尚未就绪。"))
        if profile is None:
            raise KnowledgeReviewRequired("未找到公司数据库知识画像。")
        return profile

    def prepare_for_activation(self) -> dict[str, Any]:
        """快速切换预检：连接并比较结构，只有缺少画像或漂移时才完整同步。"""

        profile = self.load_profile()
        if profile is None:
            self.sync()
            return self.ensure_current(auto_sync=False)

        tables = self._inspect_database(include_statistics=False)
        if not tables:
            raise KnowledgeReviewRequired(
                "prod.Cux 中未找到可读取的 AiQuery 业务视图。"
            )
        schema_fingerprint = self._schema_fingerprint(tables)
        self._last_schema_check_at = time.monotonic()
        self._last_schema_fingerprint = schema_fingerprint
        self._last_schema_error = None
        stored_fingerprint = profile.get("database", {}).get("schema_fingerprint")
        if stored_fingerprint != schema_fingerprint:
            self.sync()
            profile = self.load_profile()
        if profile is None:
            raise KnowledgeReviewRequired("未找到公司数据库知识画像。")
        return self.ensure_current(auto_sync=False)

    @staticmethod
    def assert_view_ready(profile: dict[str, Any], view_name: str) -> None:
        KnowledgeSyncService.assert_view_ready(profile, view_name)
