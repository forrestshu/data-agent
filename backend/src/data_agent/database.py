"""受 SQL Guard 约束的 SQLite 与 SQL Server 数据源。"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import time
from typing import Any, Generator, Iterable, Protocol

import pymssql


class DatabaseSource(Protocol):
    id: str
    label: str
    dialect: str
    schema: str | None
    query_timeout_seconds: int
    export_timeout_seconds: int

    def connect(self, *, timeout_seconds: int | None = None) -> Any: ...
    def execute(self, connection: Any, sql: str, parameters: Iterable[Any] = ()) -> Any: ...
    def cursor_columns(self, cursor: Any) -> tuple[str, ...]: ...
    def row_dict(self, cursor: Any, row: Any) -> dict[str, Any]: ...
    def fetchall_dicts(self, cursor: Any) -> tuple[dict[str, Any], ...]: ...
    def install_deadline(self, connection: Any, deadline: float) -> None: ...
    def clear_deadline(self, connection: Any) -> None: ...
    def validate_execution(self, connection: Any, sql: str, parameters: Iterable[Any]) -> None: ...


@dataclass(frozen=True)
class Database:
    """本地只读 SQLite 快照。"""

    path: Path
    query_timeout_seconds: int = 10
    export_timeout_seconds: int = 30
    id: str = "sqlite"
    label: str = "SQLite 本地快照"
    dialect: str = "sqlite"
    schema: str | None = None

    @contextmanager
    def connect(self, *, timeout_seconds: int | None = None) -> Generator[sqlite3.Connection, None, None]:
        if not self.path.exists():
            raise FileNotFoundError(f"数据库不存在：{self.path}")
        connection = sqlite3.connect(
            f"file:{self.path.resolve()}?mode=ro&immutable=1",
            uri=True,
            timeout=float(timeout_seconds or self.query_timeout_seconds),
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def execute(
        connection: sqlite3.Connection,
        sql: str,
        parameters: Iterable[Any] = (),
    ) -> sqlite3.Cursor:
        return connection.execute(sql, tuple(parameters))

    @staticmethod
    def cursor_columns(cursor: sqlite3.Cursor) -> tuple[str, ...]:
        return tuple(str(item[0]) for item in (cursor.description or ()))

    @staticmethod
    def row_dict(cursor: sqlite3.Cursor, row: sqlite3.Row | tuple[Any, ...]) -> dict[str, Any]:
        if isinstance(row, sqlite3.Row):
            return dict(row)
        return dict(zip(Database.cursor_columns(cursor), tuple(row), strict=False))

    @staticmethod
    def fetchall_dicts(cursor: sqlite3.Cursor) -> tuple[dict[str, Any], ...]:
        return tuple(Database.row_dict(cursor, row) for row in cursor.fetchall())

    @staticmethod
    def install_deadline(connection: sqlite3.Connection, deadline: float) -> None:
        connection.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 1_000)

    @staticmethod
    def clear_deadline(connection: sqlite3.Connection) -> None:
        connection.set_progress_handler(None, 0)

    @staticmethod
    def validate_execution(connection: sqlite3.Connection, sql: str, parameters: Iterable[Any]) -> None:
        connection.execute(f"EXPLAIN QUERY PLAN {sql}", tuple(parameters)).fetchall()


def _qmark_to_format(sql: str) -> str:
    """把受 Guard 校验的 qmark 参数转换为 pymssql 使用的 format 参数。"""

    result: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(sql):
        current = sql[index]
        if quote:
            result.append(current)
            if current == quote:
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    result.append(sql[index + 1])
                    index += 1
                else:
                    quote = None
        elif current in {"'", '"'}:
            quote = current
            result.append(current)
        elif current == "?":
            result.append("%s")
        else:
            result.append(current)
        index += 1
    return "".join(result)


@dataclass(frozen=True)
class SQLServerDatabase:
    """只允许执行 Guard 已批准 SELECT 的 SQL Server 数据源。"""

    host: str
    port: int
    user: str
    password: str
    database: str
    schema: str = "Cux"
    query_timeout_seconds: int = 10
    export_timeout_seconds: int = 30
    id: str = "sqlserver"
    label: str = "SQL Server 实时库"
    dialect: str = "tsql"

    @contextmanager
    def connect(self, *, timeout_seconds: int | None = None) -> Generator[Any, None, None]:
        connection = pymssql.connect(
            server=self.host,
            port=str(self.port),
            user=self.user,
            password=self.password,
            database=self.database,
            login_timeout=5,
            timeout=timeout_seconds or self.query_timeout_seconds,
            autocommit=True,
        )
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def execute(connection: Any, sql: str, parameters: Iterable[Any] = ()) -> Any:
        cursor = connection.cursor()
        cursor.execute(_qmark_to_format(sql), tuple(parameters))
        return cursor

    @staticmethod
    def cursor_columns(cursor: Any) -> tuple[str, ...]:
        return tuple(str(item[0]) for item in (cursor.description or ()))

    @staticmethod
    def row_dict(cursor: Any, row: tuple[Any, ...]) -> dict[str, Any]:
        return dict(zip(SQLServerDatabase.cursor_columns(cursor), tuple(row), strict=False))

    @staticmethod
    def fetchall_dicts(cursor: Any) -> tuple[dict[str, Any], ...]:
        columns = SQLServerDatabase.cursor_columns(cursor)
        return tuple(dict(zip(columns, tuple(row), strict=False)) for row in cursor.fetchall())

    @staticmethod
    def install_deadline(connection: Any, deadline: float) -> None:
        del connection, deadline

    @staticmethod
    def clear_deadline(connection: Any) -> None:
        del connection

    @staticmethod
    def validate_execution(connection: Any, sql: str, parameters: Iterable[Any]) -> None:
        del connection, sql, parameters
