"""知识同步层：把 SQLite 中可验证的结构与数据质量事实写回语义层。"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from .catalog import KnowledgeCatalog, load_catalog
from .settings import CATALOG_PATH, DATABASE_PROFILE_PATH, SYNC_REPORT_PATH


class KnowledgeReviewRequired(RuntimeError):
    """安全边界：数据库破坏了已审核白名单时，阻止对应视图继续查询。"""


def _quote_identifier(identifier: str) -> str:
    """数据库检查层：引用由 SQLite 元数据返回的标识符，避免特殊字符破坏 SQL。"""

    return f'"{identifier.replace(chr(34), chr(34) * 2)}"'


class KnowledgeSyncService:
    """同步服务：检测快照变化，生成画像，并保留人工维护的业务语义。"""

    def __init__(
        self,
        database_path: Path,
        catalog_path: Path = CATALOG_PATH,
        profile_path: Path = DATABASE_PROFILE_PATH,
        report_path: Path = SYNC_REPORT_PATH,
    ) -> None:
        self.database_path = database_path.resolve()
        self.catalog_path = catalog_path.resolve()
        self.profile_path = profile_path.resolve()
        self.report_path = report_path.resolve()
        # 同一个进程内只允许一个同步任务写知识文件，避免并发请求互相覆盖。
        self._sync_lock = threading.Lock()

    def _connect(self) -> sqlite3.Connection:
        """数据层：以只读 URI 打开快照，同时允许 SQLite 正确读取已有 WAL。"""

        if not self.database_path.exists():
            raise FileNotFoundError(f"数据库不存在：{self.database_path}")
        connection = sqlite3.connect(
            f"file:{self.database_path}?mode=ro",
            uri=True,
            timeout=10,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        return connection

    def quick_signature(self) -> dict[str, int]:
        """检测层：用文件大小与纳秒修改时间快速判断数据库或 WAL 是否变化。"""

        stat = self.database_path.stat()
        wal_path = Path(f"{self.database_path}-wal")
        wal_stat = wal_path.stat() if wal_path.exists() else None
        wal_size = wal_stat.st_size if wal_stat else 0
        return {
            "file_size": stat.st_size,
            "modified_ns": stat.st_mtime_ns,
            "wal_size": wal_size,
            # 空 WAL 不包含业务变化，忽略其创建时间，避免只读连接导致误报。
            "wal_modified_ns": wal_stat.st_mtime_ns if wal_stat and wal_size > 0 else 0,
        }

    def _content_fingerprint(self) -> str:
        """检测层：同步时完整哈希数据库与 WAL，识别只有数据内容发生的变化。"""

        digest = hashlib.sha256()
        for path in (self.database_path, Path(f"{self.database_path}-wal")):
            if not path.exists() or path.stat().st_size == 0:
                continue
            digest.update(path.name.encode("utf-8"))
            with path.open("rb") as source:
                while chunk := source.read(1024 * 1024):
                    digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _metadata(connection: sqlite3.Connection) -> dict[str, str]:
        """画像层：读取快照自带元数据；旧数据库没有该表时返回空对象。"""

        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='_snapshot_metadata'"
        ).fetchone()
        if not exists:
            return {}
        return {
            str(row["key"]): str(row["value"])
            for row in connection.execute("SELECT key, value FROM _snapshot_metadata")
        }

    @staticmethod
    def _business_table_names(connection: sqlite3.Connection) -> list[str]:
        """画像层：只收录 ERP AiQuery 业务表，排除导入器自己的元数据表。"""

        return [
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name LIKE 'AiQuery%' ORDER BY name"
            )
        ]

    @staticmethod
    def _column_null_counts(
        connection: sqlite3.Connection,
        table_name: str,
        column_names: list[str],
    ) -> tuple[int, dict[str, int]]:
        """画像层：一次表扫描统计总行数和各字段空值数，避免每列重复扫描。"""

        expressions = ["COUNT(*) AS row_count"]
        expressions.extend(
            f"SUM(CASE WHEN {_quote_identifier(name)} IS NULL THEN 1 ELSE 0 END)"
            f" AS {_quote_identifier(f'null_{index}')}"
            for index, name in enumerate(column_names)
        )
        row = connection.execute(
            f"SELECT {', '.join(expressions)} FROM {_quote_identifier(table_name)}"
        ).fetchone()
        assert row is not None
        row_count = int(row["row_count"])
        null_counts = {
            name: int(row[f"null_{index}"] or 0)
            for index, name in enumerate(column_names)
        }
        return row_count, null_counts

    def _inspect_database(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """画像层：提取表、字段类型、行数与空值画像，不读取或保存具体业务明细。"""

        tables: list[dict[str, Any]] = []
        with self._connect() as connection:
            metadata = self._metadata(connection)
            for table_name in self._business_table_names(connection):
                pragma_rows = connection.execute(
                    f"PRAGMA table_info({_quote_identifier(table_name)})"
                ).fetchall()
                column_names = [str(row["name"]) for row in pragma_rows]
                row_count, null_counts = self._column_null_counts(
                    connection, table_name, column_names
                )
                columns = []
                for row in pragma_rows:
                    name = str(row["name"])
                    null_count = null_counts[name]
                    columns.append(
                        {
                            "name": name,
                            "data_type": str(row["type"] or ""),
                            "sqlite_type": str(row["type"] or ""),
                            "not_null_declared": bool(row["notnull"]),
                            "null_count": null_count,
                            "non_null_count": row_count - null_count,
                            "quality": "all_null"
                            if row_count > 0 and null_count == row_count
                            else "available",
                        }
                    )
                tables.append(
                    {
                        "name": table_name,
                        "row_count": row_count,
                        "columns": columns,
                    }
                )
        return metadata, tables

    @staticmethod
    def _schema_fingerprint(tables: list[dict[str, Any]]) -> str:
        """检测层：只对表名、字段名和类型哈希，用于区分结构漂移与数据更新。"""

        schema = [
            {
                "name": table["name"],
                "columns": [
                    (
                        column["name"],
                        column.get("data_type") or column.get("sqlite_type", ""),
                    )
                    for column in table["columns"]
                ],
            }
            for table in tables
        ]
        payload = json.dumps(schema, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _load_previous_profile(self) -> dict[str, Any] | None:
        """状态层：读取上一次机器画像，用来生成本次新增、删除和行数变化报告。"""

        if not self.profile_path.exists():
            return None
        try:
            return json.loads(self.profile_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    @staticmethod
    def _table_map(profile: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
        """比较层：把画像表数组转换为按表名索引的对象。"""

        if not profile:
            return {}
        return {table["name"]: table for table in profile.get("tables", [])}

    def _build_drift(
        self,
        previous: dict[str, Any] | None,
        tables: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """比较层：产出新旧快照之间可供前端展示的结构和数据量变化。"""

        old_tables = self._table_map(previous)
        new_tables = {table["name"]: table for table in tables}
        shared_names = sorted(old_tables.keys() & new_tables.keys())
        new_columns: dict[str, list[str]] = {}
        removed_columns: dict[str, list[str]] = {}
        type_changes: dict[str, list[dict[str, str]]] = {}
        row_count_changes: list[dict[str, int | str]] = []

        for name in shared_names:
            old_columns = {item["name"]: item for item in old_tables[name]["columns"]}
            current_columns = {item["name"]: item for item in new_tables[name]["columns"]}
            added = sorted(current_columns.keys() - old_columns.keys())
            removed = sorted(old_columns.keys() - current_columns.keys())
            if added:
                new_columns[name] = added
            if removed:
                removed_columns[name] = removed
            changes = [
                {
                    "column": column,
                    "before": str(
                        old_columns[column].get("data_type")
                        or old_columns[column].get("sqlite_type", "")
                    ),
                    "after": str(
                        current_columns[column].get("data_type")
                        or current_columns[column].get("sqlite_type", "")
                    ),
                }
                for column in sorted(old_columns.keys() & current_columns.keys())
                if (
                    old_columns[column].get("data_type")
                    or old_columns[column].get("sqlite_type", "")
                )
                != (
                    current_columns[column].get("data_type")
                    or current_columns[column].get("sqlite_type", "")
                )
            ]
            if changes:
                type_changes[name] = changes
            before = int(old_tables[name]["row_count"])
            after = int(new_tables[name]["row_count"])
            if before != after:
                row_count_changes.append(
                    {"table": name, "before": before, "after": after, "delta": after - before}
                )

        return {
            "new_tables": sorted(new_tables.keys() - old_tables.keys()),
            "removed_tables": sorted(old_tables.keys() - new_tables.keys()),
            "new_columns": new_columns,
            "removed_columns": removed_columns,
            "type_changes": type_changes,
            "row_count_changes": row_count_changes,
        }

    @staticmethod
    def _compatibility(catalog: KnowledgeCatalog, tables: list[dict[str, Any]]) -> dict[str, Any]:
        """安全层：验证人工白名单仍存在；新表和新字段只登记，不自动赋予业务含义。"""

        table_map = {table["name"]: table for table in tables}
        invalid_views: list[dict[str, Any]] = []
        for view in catalog.views:
            table = table_map.get(view.name)
            if table is None:
                invalid_views.append({"view": view.name, "reason": "missing_table", "missing": []})
                continue
            actual_columns = {column["name"] for column in table["columns"]}
            required_columns = (
                set(view.filter_columns)
                | set(view.output_columns)
                | set(view.join_columns)
            )
            missing = sorted(required_columns - actual_columns)
            if missing:
                invalid_views.append(
                    {"view": view.name, "reason": "missing_curated_columns", "missing": missing}
                )
        curated_names = {view.name for view in catalog.views}
        pending_tables = sorted(set(table_map) - curated_names)
        return {
            "query_ready": not invalid_views,
            "invalid_views": invalid_views,
            "pending_review_tables": pending_tables,
            "policy": "新增表/字段只进入机器画像，业务用途与查询白名单需人工审核。",
        }

    @staticmethod
    def _generated_limitations(tables: list[dict[str, Any]]) -> list[dict[str, str]]:
        """质量层：自动标出全空字段；新快照恢复数据后，该提示会自动消失。"""

        limitations: list[dict[str, str]] = []
        for table in tables:
            for column in table["columns"]:
                if column["quality"] == "all_null":
                    limitations.append(
                        {
                            "code": "all_null",
                            "view": table["name"],
                            "column": column["name"],
                            "message": f"{table['name']}.{column['name']} 在当前快照中全部为空，不做推测。",
                        }
                    )
        return limitations

    @staticmethod
    def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
        """持久化层：先写同目录临时文件再替换，确保读者只看到完整 JSON。"""

        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f"{path.suffix}.tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)

    def _update_catalog_snapshot(self, profile: dict[str, Any]) -> None:
        """知识层：只更新可验证的快照元数据，不改人工维护的 purpose/keywords/白名单。"""

        raw = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        raw["catalog_version"] = profile["generated_at"]
        raw["database_snapshot"] = {
            "file_name": profile["database"]["file_name"],
            "content_fingerprint": profile["database"]["content_fingerprint"],
            "schema_fingerprint": profile["database"]["schema_fingerprint"],
            "snapshot_started_at": profile["database"].get("snapshot_started_at"),
            "profile_generated_at": profile["generated_at"],
        }
        raw["generated_profile"] = self.profile_path.name
        raw["generated_limitations"] = profile["generated_limitations"]
        self._atomic_write(self.catalog_path, raw)

    def sync(self) -> dict[str, Any]:
        """同步入口：扫描当前 SQLite，更新语义层状态文件，并返回完整同步报告。"""

        with self._sync_lock:
            previous = self._load_previous_profile()
            catalog = load_catalog(self.catalog_path)
            signature_before = self.quick_signature()
            metadata, tables = self._inspect_database()
            generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
            content_fingerprint = self._content_fingerprint()
            quick = self.quick_signature()
            # 数据库若在扫描期间变化，本次表画像与哈希可能来自不同版本，必须放弃写入。
            if signature_before != quick:
                raise KnowledgeReviewRequired(
                    "SQLite 在知识同步期间发生变化，请等待快照写入完成后重试。"
                )
            compatibility = self._compatibility(catalog, tables)
            profile: dict[str, Any] = {
                "profile_version": 1,
                "generated_at": generated_at,
                "database": {
                    "file_name": self.database_path.name,
                    "path": str(self.database_path),
                    **quick,
                    "content_fingerprint": content_fingerprint,
                    "schema_fingerprint": self._schema_fingerprint(tables),
                    "snapshot_started_at": metadata.get("snapshot_started_at"),
                    "snapshot_finished_at": metadata.get("snapshot_finished_at"),
                },
                "summary": {
                    "business_table_count": len(tables),
                    "total_row_count": sum(int(table["row_count"]) for table in tables),
                    "all_null_column_count": sum(
                        1
                        for table in tables
                        for column in table["columns"]
                        if column["quality"] == "all_null"
                    ),
                },
                "snapshot_metadata": metadata,
                "tables": tables,
                "drift": self._build_drift(previous, tables),
                "compatibility": compatibility,
                "generated_limitations": self._generated_limitations(tables),
            }
            report = {
                "status": "ready" if compatibility["query_ready"] else "review_required",
                "generated_at": generated_at,
                "database": profile["database"],
                "summary": profile["summary"],
                "drift": profile["drift"],
                "compatibility": compatibility,
            }
            self._atomic_write(self.profile_path, profile)
            self._atomic_write(self.report_path, report)
            self._update_catalog_snapshot(profile)
            return report

    def load_profile(self) -> dict[str, Any] | None:
        """状态层：向查询服务与 API 提供最近一次完整数据库画像。"""

        return self._load_previous_profile()

    def status(self) -> dict[str, Any]:
        """状态入口：快速判断画像是否与当前文件一致，不触发昂贵的全表扫描。"""

        if not self.database_path.exists():
            return {"status": "database_missing", "database_path": str(self.database_path)}
        profile = self.load_profile()
        if profile is None:
            return {
                "status": "update_required",
                "reason": "尚未生成数据库知识画像。",
                "database_path": str(self.database_path),
            }
        stored = profile.get("database", {})
        current = self.quick_signature()
        signature_keys = ("file_size", "modified_ns", "wal_size", "wal_modified_ns")
        changed = any(int(stored.get(key, -1)) != current[key] for key in signature_keys)
        if changed:
            return {
                "status": "update_required",
                "reason": "检测到 SQLite 文件内容可能已变化。",
                "database_path": str(self.database_path),
                "stored_signature": {key: stored.get(key) for key in signature_keys},
                "current_signature": current,
                "last_profile": profile.get("generated_at"),
            }
        compatibility = profile.get("compatibility", {})
        return {
            "status": "ready" if compatibility.get("query_ready", False) else "review_required",
            "database_path": str(self.database_path),
            "database": stored,
            "summary": profile.get("summary", {}),
            "drift": profile.get("drift", {}),
            "compatibility": compatibility,
            "generated_at": profile.get("generated_at"),
        }

    def ensure_current(self, auto_sync: bool = True) -> dict[str, Any]:
        """查询前置条件：检测到新快照时自动同步，返回与当前文件匹配的画像。"""

        current_status = self.status()
        if current_status["status"] == "update_required" and auto_sync:
            self.sync()
            current_status = self.status()
        if current_status["status"] == "database_missing":
            raise FileNotFoundError(current_status["database_path"])
        if current_status["status"] == "update_required":
            raise KnowledgeReviewRequired("知识画像落后于 SQLite，请先执行同步。")
        profile = self.load_profile()
        if profile is None:
            raise KnowledgeReviewRequired("未找到数据库知识画像。")
        return profile

    @staticmethod
    def assert_view_ready(profile: dict[str, Any], view_name: str) -> None:
        """查询安全边界：只阻止缺表或缺少已审核字段的受影响视图。"""

        invalid = {
            item["view"]: item
            for item in profile.get("compatibility", {}).get("invalid_views", [])
        }
        if view_name in invalid:
            detail = invalid[view_name]
            raise KnowledgeReviewRequired(
                f"{view_name} 与知识白名单不兼容，需要审核：{detail['reason']} "
                f"{', '.join(detail.get('missing', []))}"
            )
