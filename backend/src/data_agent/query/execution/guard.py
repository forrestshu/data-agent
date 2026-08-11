"""SQL 安全层：按活动方言约束模型 SELECT，再交给只读执行器。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlglot import exp, parse
from sqlglot.errors import OptimizeError, ParseError
from sqlglot.optimizer.qualify import qualify

from data_agent.knowledge.semantic_catalog import SemanticCatalog
from data_agent.database import Database


class SQLValidationError(ValueError):
    """安全边界异常：SQL 不是单条、只读、已审核且资源受限的查询。"""


@dataclass(frozen=True)
class ValidatedSQL:
    """验证结果：保留前端预览 SQL 与完整结果 SQL，二者共享同一安全校验。"""

    sql: str
    base_sql: str
    count_sql: str
    parameters: tuple[Any, ...]
    source_views: tuple[str, ...]


class SQLGuard:
    """确定性守卫：模型可以写查询，但不能决定安全策略和可访问范围。

    全链路应复用同一实例：Agent 规划/repair 与 Executor 执行前强制校验共用，
    禁止在各调用点各自 new 导致 max_rows/白名单语义漂移。
    """

    FORBIDDEN_FUNCTIONS = {
        "load_extension",
        "readfile",
        "writefile",
        "randomblob",
        "zeroblob",
    }

    def __init__(
        self,
        catalog: SemanticCatalog,
        database_profile: dict[str, Any],
        max_rows: int = 500,
        source: Database | None = None,
    ) -> None:
        """从语义目录建立已审核表列和关系权限；机器画像只证明结构真实存在。"""

        self.max_rows = max_rows
        self.catalog = catalog
        self.source = source
        self.dialect = "sqlite"
        actual_tables = {
            str(table["name"]): {
                str(column["name"])
                for column in table.get("columns", [])
                if isinstance(column, dict) and column.get("name")
            }
            for table in database_profile.get("tables", [])
            if isinstance(table, dict) and table.get("name")
        }
        self.allowed_schema: dict[str, set[str]] = {}
        for view in catalog.views:
            approved = (
                set(view.filter_columns)
                | set(view.output_columns)
                | set(view.join_columns)
            )
            actual = actual_tables.get(view.name, set())
            self.allowed_schema[view.name] = approved & actual
        self._table_lookup = {name.casefold(): name for name in self.allowed_schema}
        self._column_lookup = {
            table: {column.casefold(): column for column in columns}
            for table, columns in self.allowed_schema.items()
        }
        self.relationships = tuple(
            relationship
            for relationship in catalog.relationships
            if relationship.executable
        )

    @staticmethod
    def _cte_names(tree: exp.Expression) -> set[str]:
        """识别临时 CTE 名称，避免把它们误判成语义层业务视图。"""

        return {
            cte.alias_or_name.casefold()
            for cte in tree.find_all(exp.CTE)
            if cte.alias_or_name
        }

    def _physical_tables(self, tree: exp.Expression) -> tuple[str, ...]:
        """从 AST 提取真实业务表；拒绝系统表、未知表和未审核或失效视图。"""

        cte_names = self._cte_names(tree)
        names: list[str] = []
        for table in tree.find_all(exp.Table):
            if table.name.casefold() in cte_names:
                continue
            database = table.args.get("db")
            catalog = table.args.get("catalog")
            if database is not None and database.name.casefold() not in {"", "main"}:
                raise SQLValidationError("查询只能访问当前只读数据库。")
            if catalog is not None:
                raise SQLValidationError("查询不能访问外部数据库。")
            canonical = self._table_lookup.get(table.name.casefold())
            if canonical is None:
                raise SQLValidationError("查询使用了语义层未开放的数据对象。")
            if canonical not in names:
                names.append(canonical)
        if not names:
            raise SQLValidationError("查询必须读取至少一个已审核业务视图。")
        return tuple(names)

    def _validate_columns(
        self,
        tree: exp.Expression,
        source_views: tuple[str, ...],
    ) -> None:
        """字段权限层：按查询作用域解析字段，避免输出别名绕过已审核列白名单。"""

        # sqlglot 的限定器会分别解析物理表、CTE、派生表、输出别名和多表歧义；
        # 输入 schema 只包含语义层已批准字段，因此未知字段必然无法解析。
        schema = {
            table_name: {column: "TEXT" for column in columns}
            for table_name, columns in self.allowed_schema.items()
            if table_name in source_views
        }
        try:
            validation_tree = tree.copy()
            for table in validation_tree.find_all(exp.Table):
                if table.name.casefold() not in self._cte_names(validation_tree):
                    table.set("db", None)
                    table.set("catalog", None)
            qualify(
                validation_tree,
                dialect=self.dialect,
                schema=schema,
                expand_stars=False,
                validate_qualify_columns=True,
                quote_identifiers=False,
                identify=False,
            )
        except OptimizeError as error:
            raise SQLValidationError(
                "查询字段不在语义层开放范围内，或字段来源不明确。"
            ) from error

    def _validate_join_column_roles(
        self,
        tree: exp.Select,
        source_views: tuple[str, ...],
    ) -> None:
        """用途权限层：只为关系开放的公司键不得被直接筛选或输出。"""

        cte_names = self._cte_names(tree)
        alias_to_view: dict[str, str] = {}
        for table in tree.find_all(exp.Table):
            if table.name.casefold() in cte_names:
                continue
            canonical = self._table_lookup.get(table.name.casefold())
            if canonical is not None:
                alias_to_view[table.alias_or_name.casefold()] = canonical
                alias_to_view[table.name.casefold()] = canonical
        join_only = {
            view.name: {
                column.casefold()
                for column in set(view.join_columns)
                - set(view.filter_columns)
                - set(view.output_columns)
            }
            for view in self.catalog.views
        }
        for column in tree.find_all(exp.Column):
            view_name = alias_to_view.get(column.table.casefold()) if column.table else None
            if view_name is None and len(source_views) == 1:
                view_name = source_views[0]
            if view_name is None or column.name.casefold() not in join_only.get(view_name, set()):
                continue
            if column.find_ancestor(exp.Join) is None:
                raise SQLValidationError("公司代码仅开放为跨视图关联键，不能直接筛选或输出。")

    def _validate_joins(self, tree: exp.Select) -> None:
        """关系权限层：每个物理 JOIN 必须完整使用一条已批准关系的全部键。"""

        cte_names = self._cte_names(tree)
        alias_to_view: dict[str, str] = {}
        for table in tree.find_all(exp.Table):
            if table.name.casefold() in cte_names:
                continue
            canonical = self._table_lookup.get(table.name.casefold())
            if canonical is not None:
                alias_to_view[table.alias_or_name.casefold()] = canonical
                alias_to_view[table.name.casefold()] = canonical

        for join in tree.find_all(exp.Join):
            on = join.args.get("on")
            using = join.args.get("using")
            if on is None and using is None:
                raise SQLValidationError("多表查询必须提供明确关联条件。")
            if isinstance(on, exp.Boolean) and bool(on.this):
                raise SQLValidationError("禁止笛卡尔积或恒真 JOIN 条件。")

            target = join.this
            if not isinstance(target, exp.Table):
                raise SQLValidationError("多表查询暂不允许把派生表直接作为 JOIN 目标。")
            if target.name.casefold() in cte_names:
                raise SQLValidationError("跨视图关系必须直接使用语义层批准的业务视图。")
            target_view = self._table_lookup.get(target.name.casefold())
            if target_view is None:
                continue
            candidates = [
                relationship
                for relationship in self.relationships
                if target_view in {relationship.left_view, relationship.right_view}
                and (
                    relationship.left_view in set(alias_to_view.values())
                    and relationship.right_view in set(alias_to_view.values())
                )
            ]
            if using is not None:
                using_names = {
                    item.name.casefold()
                    for item in using
                    if isinstance(item, exp.Identifier)
                }
                matched_using = next(
                    (
                        relationship
                        for relationship in candidates
                        if all(
                        left.casefold() == right.casefold()
                        and left.casefold() in using_names
                        for left, right in relationship.keys
                        )
                    ),
                    None,
                )
                if matched_using is None:
                    raise SQLValidationError(
                        "JOIN 必须完整使用语义层批准的公司键和业务键。"
                    )
                if (
                    matched_using.status == "approved_with_risk"
                    and tree.find(exp.AggFunc) is not None
                ):
                    raise SQLValidationError(
                        "该关系存在多对多或粒度放大风险，不能在直接 JOIN 后汇总数量或金额。"
                    )
                continue

            assert on is not None
            observed: set[tuple[str, str, str, str]] = set()
            for equality in on.find_all(exp.EQ):
                left = equality.left
                right = equality.right
                if not isinstance(left, exp.Column) or not isinstance(right, exp.Column):
                    continue
                if not left.table or not right.table:
                    continue
                left_alias = left.table.casefold()
                right_alias = right.table.casefold()
                left_view = alias_to_view.get(left_alias)
                right_view = alias_to_view.get(right_alias)
                if left_view is None or right_view is None:
                    continue
                observed.add((left_view, left.name.casefold(), right_view, right.name.casefold()))
                observed.add((right_view, right.name.casefold(), left_view, left.name.casefold()))

            def matches(relationship: Any) -> bool:
                if relationship.right_view == target_view:
                    required = {
                        (
                            relationship.left_view,
                            left.casefold(),
                            relationship.right_view,
                            right.casefold(),
                        )
                        for left, right in relationship.keys
                    }
                else:
                    required = {
                        (
                            relationship.right_view,
                            right.casefold(),
                            relationship.left_view,
                            left.casefold(),
                        )
                        for left, right in relationship.keys
                    }
                return required.issubset(observed) and any(
                    item[0] == target_view or item[2] == target_view for item in required
                )

            matched = next(
                (relationship for relationship in candidates if matches(relationship)),
                None,
            )
            if matched is None:
                raise SQLValidationError(
                    "JOIN 必须完整使用语义层批准的 Company 公司键和业务关联键。"
                )
            if matched.status == "approved_with_risk" and tree.find(exp.AggFunc) is not None:
                raise SQLValidationError(
                    "该关系存在多对多或粒度放大风险，不能在直接 JOIN 后汇总数量或金额。"
                )

    def _physical_tree(self, tree: exp.Select) -> exp.Select:
        """把逻辑视图名映射到当前 SQLite 数据库。"""

        physical = tree.copy()
        cte_names = self._cte_names(physical)
        for table in physical.find_all(exp.Table):
            if table.name.casefold() in cte_names:
                continue
            canonical = self._table_lookup[table.name.casefold()]
            table.set("this", exp.to_identifier(canonical))
            table.set("db", None)
            table.set("catalog", None)
        return physical

    def validate(
        self,
        sql: str,
        parameters: list[Any] | tuple[Any, ...],
        requested_limit: int,
        preserve_complete: bool = False,
        preserve_query_limit: bool = True,
    ) -> ValidatedSQL:
        """安全入口：完整 SQL 用于计数/导出，交互 SQL最多返回请求上限行。"""

        cleaned = sql.strip()
        if not cleaned or len(cleaned) > 12_000:
            raise SQLValidationError("查询语句为空或过长。")
        if "--" in cleaned or "/*" in cleaned:
            raise SQLValidationError("查询语句不能包含注释。")
        try:
            statements = parse(cleaned, read=self.dialect)
        except ParseError as error:
            raise SQLValidationError("查询语句无法解析。") from error
        if len(statements) != 1 or not isinstance(statements[0], exp.Select):
            raise SQLValidationError("只允许单条 SELECT 查询。")
        tree = statements[0]

        if tree.find(exp.Into) is not None:
            raise SQLValidationError("禁止使用 SELECT INTO 创建或写入数据对象。")
        for star in tree.find_all(exp.Star):
            if not isinstance(star.parent, exp.Count):
                raise SQLValidationError("必须明确选择字段，不能使用 SELECT *。")
        self._validate_joins(tree)
        for function in tree.find_all(exp.Anonymous):
            if function.name.casefold() in self.FORBIDDEN_FUNCTIONS:
                raise SQLValidationError("查询使用了禁止函数。")
        safe_parameters = tuple(parameters)
        if len(safe_parameters) > 50:
            raise SQLValidationError("查询参数过多。")
        if any(
            not isinstance(value, (str, int, float, bool, type(None)))
            for value in safe_parameters
        ):
            raise SQLValidationError("查询参数类型不受支持。")
        placeholder_count = sum(1 for _ in tree.find_all(exp.Placeholder))
        if placeholder_count != len(safe_parameters):
            raise SQLValidationError("查询参数数量与占位符不一致。")

        source_views = self._physical_tables(tree)
        self._validate_columns(tree, source_views)
        self._validate_join_column_roles(tree, source_views)

        # 模型只有在用户明确要求“前 N 条/Top N”时才应自带 LIMIT；该限制属于查询语义，
        # 因此 base_sql 保留它。没有显式 LIMIT 时，base_sql 表示所有匹配结果。
        current_limit = tree.args.get("limit")
        if current_limit is not None:
            expression = current_limit.expression
            if not isinstance(expression, exp.Literal) or not expression.is_int:
                raise SQLValidationError("返回条数必须是固定整数。")
            if not preserve_query_limit:
                # 模型经常把前端预览上限误写进业务 SQL；用户未要求 Top N 时必须移除。
                tree.set("limit", None)
                current_limit = None
        physical_tree = self._physical_tree(tree)
        base_sql = physical_tree.sql(dialect=self.dialect)
        count_tree = physical_tree.copy()
        count_with = count_tree.args.get("with_")
        count_tree.set("with_", None)
        if count_tree.args.get("limit") is None:
            # 计数不需要排序。
            count_tree.set("order", None)
        count_function = "COUNT(*)"
        count_prefix = (
            f"{count_with.sql(dialect=self.dialect)} "
            if count_with is not None
            else ""
        )
        count_sql = count_prefix + (
            f"SELECT {count_function} AS total_count "
            f"FROM ({count_tree.sql(dialect=self.dialect)}) AS query_result"
        )

        if preserve_complete:
            preview_sql = base_sql
        else:
            effective_limit = max(1, min(requested_limit, self.max_rows))
            if current_limit is not None:
                effective_limit = min(effective_limit, int(current_limit.expression.this))
            preview_tree = physical_tree.copy()
            preview_tree.set("limit", None)
            preview_sql = preview_tree.limit(effective_limit).sql(dialect=self.dialect)
        return ValidatedSQL(
            sql=preview_sql,
            base_sql=base_sql,
            count_sql=count_sql,
            parameters=safe_parameters,
            source_views=source_views,
        )
