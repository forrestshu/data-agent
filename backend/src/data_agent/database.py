"""SQLite 只读数据库访问。"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import sqlite3
from typing import Any, Generator, Iterable

from data_agent.settings import DEFAULT_DATABASE_PATH


@dataclass(frozen=True)
class Database:
    """集中 SQLite 路径、连接和结果转换，查询层只依赖这一处。"""

    path: Path
    query_timeout_seconds: int = 10
    export_timeout_seconds: int = 30

    @classmethod
    def from_environment(cls) -> "Database":
        configured = os.getenv("DATA_AGENT_DATABASE")
        path = Path(configured).expanduser().resolve() if configured else DEFAULT_DATABASE_PATH
        return cls(path=path)

    @property
    def dialect(self) -> str:
        return "sqlite"

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
