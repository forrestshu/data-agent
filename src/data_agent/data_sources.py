"""双数据源配置、连接适配与活动数据源持久化。"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import sqlite3
import threading
from typing import Any, Generator, Iterable, Iterator, Literal

from mssql_python import connect as connect_mssql

from .settings import (
    ACTIVE_SOURCE_PATH,
    CATALOG_PATH,
    DATABASE_PROFILE_PATH,
    DEFAULT_DATABASE_PATH,
    SEMANTIC_PROPOSALS_PATH,
    SQLSERVER_KNOWLEDGE_ROOT,
    SYNC_REPORT_PATH,
)


SourceKind = Literal["sqlite", "sqlserver"]
SQLITE_SOURCE_ID = "sqlite_internal"
SQLSERVER_SOURCE_ID = "sqlserver_company"
ALLOWED_SOURCE_IDS = frozenset({SQLITE_SOURCE_ID, SQLSERVER_SOURCE_ID})


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _safe_connection_value(value: str) -> str:
    """用 ODBC 花括号转义连接值，避免分号等字符改变连接参数。"""

    return "{" + value.replace("}", "}}") + "}"


@dataclass(frozen=True)
class DataSourceConfig:
    """不向前端暴露凭据的数据源定义。"""

    source_id: str
    kind: SourceKind
    display_name: str
    dataset_label: str
    database_name: str
    profile_path: Path
    report_path: Path
    proposals_path: Path
    database_path: Path | None = None
    host: str | None = None
    port: int | None = None
    schema: str | None = None
    username: str | None = None
    password: str | None = field(default=None, repr=False)
    encrypt: bool = True
    trust_server_certificate: bool = True
    login_timeout_seconds: int = 8
    query_timeout_seconds: int = 8
    export_timeout_seconds: int = 60
    statistics_timeout_seconds: int = 30
    statistics_workers: int = 2
    statistics_retry_cooldown_seconds: int = 3600

    @property
    def dialect(self) -> str:
        return "sqlite" if self.kind == "sqlite" else "tsql"

    @property
    def configured(self) -> bool:
        if self.kind == "sqlite":
            return self.database_path is not None and self.database_path.exists()
        return all((self.host, self.port, self.database_name, self.schema, self.username, self.password))

    @property
    def connection_target(self) -> str:
        if self.kind == "sqlite":
            return self.database_path.name if self.database_path else "未配置"
        return f"{self.host}:{self.port}"

    def public_dict(self) -> dict[str, Any]:
        """前端契约：只返回可展示配置，绝不返回账号、密码或连接串。"""

        return {
            "source_id": self.source_id,
            "source_kind": self.kind,
            "display_name": self.display_name,
            "dataset_label": self.dataset_label,
            "database": self.database_name,
            "schema": self.schema,
            "target": self.connection_target,
            "configured": self.configured,
            "read_only": True,
        }

    def _connection_string(self) -> str:
        if self.kind != "sqlserver" or not self.configured:
            raise RuntimeError("公司 SQL Server 尚未完整配置。")
        assert self.host is not None
        assert self.port is not None
        assert self.username is not None
        assert self.password is not None
        parts = [
            f"Server={_safe_connection_value(f'{self.host},{self.port}')}",
            f"Database={_safe_connection_value(self.database_name)}",
            f"UID={_safe_connection_value(self.username)}",
            f"PWD={_safe_connection_value(self.password)}",
            f"Encrypt={'yes' if self.encrypt else 'no'}",
            (
                "TrustServerCertificate="
                f"{'yes' if self.trust_server_certificate else 'no'}"
            ),
            "ApplicationIntent=ReadOnly",
        ]
        return ";".join(parts)

    @contextmanager
    def connect(
        self,
        *,
        timeout_seconds: int | None = None,
    ) -> Generator[Any, None, None]:
        """按数据源建立只读连接，并统一由上下文释放。"""

        if self.kind == "sqlite":
            if self.database_path is None or not self.database_path.exists():
                raise FileNotFoundError(f"数据库不存在：{self.database_path}")
            connection = sqlite3.connect(
                f"file:{self.database_path.resolve()}?mode=ro",
                uri=True,
                timeout=10,
            )
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only = ON")
        else:
            query_timeout = (
                self.query_timeout_seconds
                if timeout_seconds is None
                else max(1, int(timeout_seconds))
            )
            connection = connect_mssql(
                self._connection_string(),
                autocommit=True,
                timeout=query_timeout,
            )
        try:
            yield connection
        finally:
            connection.close()

    def execute(
        self,
        connection: Any,
        sql: str,
        parameters: Iterable[Any] = (),
    ) -> Any:
        """统一 DB-API 执行入口；两种驱动都支持 qmark 参数。"""

        values = tuple(parameters)
        if self.kind == "sqlite":
            return connection.execute(sql, values)
        cursor = connection.cursor()
        return cursor.execute(sql, values)

    @staticmethod
    def cursor_columns(cursor: Any) -> tuple[str, ...]:
        return tuple(str(item[0]) for item in (cursor.description or ()))

    def row_dict(self, cursor: Any, row: Any) -> dict[str, Any]:
        if isinstance(row, sqlite3.Row):
            return dict(row)
        return dict(zip(self.cursor_columns(cursor), tuple(row), strict=False))

    def fetchall_dicts(self, cursor: Any) -> tuple[dict[str, Any], ...]:
        return tuple(self.row_dict(cursor, row) for row in cursor.fetchall())

    def quote_identifier(self, identifier: str) -> str:
        if self.kind == "sqlite":
            return f'"{identifier.replace(chr(34), chr(34) * 2)}"'
        return f"[{identifier.replace(']', ']]')}]"

    def physical_view(self, logical_name: str) -> str:
        quoted_view = self.quote_identifier(logical_name)
        if self.kind == "sqlite":
            return quoted_view
        assert self.schema is not None
        return f"{self.quote_identifier(self.schema)}.{quoted_view}"

    def cast_text(self, expression: str) -> str:
        if self.kind == "sqlite":
            return f"CAST({expression} AS TEXT)"
        return f"CAST({expression} AS nvarchar(max))"

    def first_row_sql(self, select_sql: str) -> str:
        if self.kind == "sqlite":
            return f"{select_sql} LIMIT 1"
        return select_sql.replace("SELECT ", "SELECT TOP 1 ", 1)

    def limit_sql(self, select_sql: str, limit: int) -> str:
        safe_limit = max(1, int(limit))
        if self.kind == "sqlite":
            return f"{select_sql} LIMIT {safe_limit}"
        return select_sql.replace("SELECT ", f"SELECT TOP {safe_limit} ", 1)

    def profile_type(self, column: dict[str, Any]) -> str:
        return str(column.get("data_type") or column.get("sqlite_type") or "")

    def source_metadata(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_kind": self.kind,
            "dataset_label": self.dataset_label,
            "display_name": self.display_name,
        }


def build_source_configs() -> dict[str, DataSourceConfig]:
    """从环境变量装配两个固定数据源，避免接受任意连接目标。"""

    configured_sqlite = os.getenv("DATA_AGENT_DATABASE")
    sqlite_path = (
        Path(configured_sqlite).expanduser().resolve()
        if configured_sqlite
        else DEFAULT_DATABASE_PATH
    )
    sqlserver_root = SQLSERVER_KNOWLEDGE_ROOT
    sources = {
        SQLITE_SOURCE_ID: DataSourceConfig(
            source_id=SQLITE_SOURCE_ID,
            kind="sqlite",
            display_name="SQLite 本地快照",
            dataset_label="内部测试集",
            database_name=sqlite_path.name,
            database_path=sqlite_path,
            profile_path=DATABASE_PROFILE_PATH,
            report_path=SYNC_REPORT_PATH,
            proposals_path=SEMANTIC_PROPOSALS_PATH,
        ),
        SQLSERVER_SOURCE_ID: DataSourceConfig(
            source_id=SQLSERVER_SOURCE_ID,
            kind="sqlserver",
            display_name="SQL Server 公司数据库",
            dataset_label="公司数据库",
            host=os.getenv("DATA_AGENT_SQLSERVER_HOST"),
            port=int(os.getenv("DATA_AGENT_SQLSERVER_PORT", "1433")),
            database_name=os.getenv("DATA_AGENT_SQLSERVER_DATABASE", "prod"),
            schema=os.getenv("DATA_AGENT_SQLSERVER_SCHEMA", "Cux"),
            username=os.getenv("DATA_AGENT_SQLSERVER_USERNAME"),
            password=os.getenv("DATA_AGENT_SQLSERVER_PASSWORD"),
            encrypt=_env_bool("DATA_AGENT_SQLSERVER_ENCRYPT", True),
            trust_server_certificate=_env_bool(
                "DATA_AGENT_SQLSERVER_TRUST_SERVER_CERTIFICATE",
                True,
            ),
            login_timeout_seconds=int(
                os.getenv("DATA_AGENT_SQLSERVER_LOGIN_TIMEOUT_SECONDS", "8")
            ),
            query_timeout_seconds=int(
                os.getenv("DATA_AGENT_SQLSERVER_QUERY_TIMEOUT_SECONDS", "8")
            ),
            export_timeout_seconds=int(
                os.getenv("DATA_AGENT_SQLSERVER_EXPORT_TIMEOUT_SECONDS", "60")
            ),
            statistics_timeout_seconds=int(
                os.getenv("DATA_AGENT_SQLSERVER_STATISTICS_TIMEOUT_SECONDS", "30")
            ),
            statistics_workers=max(
                1,
                min(
                    4,
                    int(os.getenv("DATA_AGENT_SQLSERVER_STATISTICS_WORKERS", "2")),
                ),
            ),
            statistics_retry_cooldown_seconds=max(
                0,
                int(
                    os.getenv(
                        "DATA_AGENT_SQLSERVER_STATISTICS_RETRY_COOLDOWN_SECONDS",
                        "3600",
                    )
                ),
            ),
            profile_path=sqlserver_root / "database_profile.json",
            report_path=sqlserver_root / "knowledge_sync_report.json",
            proposals_path=sqlserver_root / "semantic_proposals.json",
        ),
    }
    return sources


class DataSourceRegistry:
    """全局活动数据源状态；只持久化固定 source_id，不保存连接信息。"""

    def __init__(
        self,
        *,
        active_source_id: str | None = None,
        persist: bool = True,
        state_path: Path = ACTIVE_SOURCE_PATH,
    ) -> None:
        self.sources = build_source_configs()
        self.state_path = state_path
        self.persist = persist
        self._lock = threading.RLock()
        self._active_source_id = self._resolve_initial_source(active_source_id)

    def _resolve_initial_source(self, override: str | None) -> str:
        if override in ALLOWED_SOURCE_IDS:
            return str(override)
        if self.persist and self.state_path.exists():
            try:
                stored = json.loads(self.state_path.read_text(encoding="utf-8"))
                source_id = stored.get("active_source_id")
                if source_id in ALLOWED_SOURCE_IDS:
                    return str(source_id)
            except (OSError, json.JSONDecodeError):
                pass
        configured = os.getenv("DATA_AGENT_DEFAULT_SOURCE", SQLSERVER_SOURCE_ID)
        if configured in ALLOWED_SOURCE_IDS:
            return configured
        return SQLSERVER_SOURCE_ID

    @property
    def active_source_id(self) -> str:
        with self._lock:
            return self._active_source_id

    def active(self) -> DataSourceConfig:
        with self._lock:
            return self.sources[self._active_source_id]

    def get(self, source_id: str) -> DataSourceConfig:
        if source_id not in ALLOWED_SOURCE_IDS:
            raise KeyError("不支持的数据源。")
        return self.sources[source_id]

    def activate(self, source_id: str) -> DataSourceConfig:
        """验证完成后原子切换；调用方负责先完成连接和知识检查。"""

        source = self.get(source_id)
        with self._lock:
            if self.persist:
                self.state_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = self.state_path.with_suffix(".tmp")
                temporary.write_text(
                    json.dumps(
                        {"active_source_id": source_id},
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                os.replace(temporary, self.state_path)
            self._active_source_id = source_id
        return source

    def list_public(self) -> list[dict[str, Any]]:
        return [
            self.sources[source_id].public_dict()
            for source_id in (SQLITE_SOURCE_ID, SQLSERVER_SOURCE_ID)
        ]


def sqlite_source_for_path(database_path: Path) -> DataSourceConfig:
    """兼容旧测试和 CLI：把路径包装成不持久化的 SQLite 数据源。"""

    resolved = database_path.resolve()
    return DataSourceConfig(
        source_id=SQLITE_SOURCE_ID,
        kind="sqlite",
        display_name="SQLite 本地快照",
        dataset_label="内部测试集",
        database_name=resolved.name,
        database_path=resolved,
        profile_path=DATABASE_PROFILE_PATH,
        report_path=SYNC_REPORT_PATH,
        proposals_path=SEMANTIC_PROPOSALS_PATH,
    )
