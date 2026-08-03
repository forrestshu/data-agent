"""接口层：提供可直接演示的命令行入口。"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .catalog import load_catalog
from .executor import ClarificationRequired, ReadOnlyQueryService
from .knowledge_sync import KnowledgeSyncService
from .router import QueryRouter, RouteConfirmationRequired
from .settings import DEFAULT_DATABASE_PATH



def build_parser() -> argparse.ArgumentParser:
    """定义 CLI 边界：接收自然语言问题、数据库路径和只路由模式。"""

    parser = argparse.ArgumentParser(description="ERP data-agent 只读查询演示")
    parser.add_argument("question", help="例如：查询物料 110000012 的库存和库位")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--route-only", action="store_true", help="只显示路由，不执行 SQL")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="自动确认模糊路由候选；用于脚本和测试，交互使用时建议省略",
    )
    parser.add_argument("--limit", type=int, default=20)
    return parser


def main() -> None:
    """编排 CLI：模糊候选先询问用户，只有确认后才进入 SQL 执行层。"""

    args = build_parser().parse_args()
    knowledge = KnowledgeSyncService(args.database)
    profile = knowledge.ensure_current(auto_sync=True)
    catalog = load_catalog()
    if args.route_only:
        decision = QueryRouter(catalog).route(args.question)
        print(json.dumps(asdict(decision), ensure_ascii=False, indent=2))
        return

    service = ReadOnlyQueryService(args.database, catalog, database_profile=profile)
    decision = service.router.route(args.question)
    confirmed_view: str | None = None
    if decision.requires_confirmation:
        print(decision.confirmation_question)
        if args.confirm:
            confirmed_view = decision.view_name
        else:
            try:
                answer = input("请输入 y/是 确认，其他内容取消：").strip().lower()
            except EOFError:
                answer = ""
            if answer in {"y", "yes", "是", "确认"}:
                confirmed_view = decision.view_name
            else:
                print("已取消，本次没有执行数据库查询。")
                return
    try:
        result = service.ask(
            args.question,
            limit=args.limit,
            confirmed_view=confirmed_view,
        )
    except (ClarificationRequired, RouteConfirmationRequired) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
