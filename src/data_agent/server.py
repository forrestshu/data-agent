"""开发服务器入口：让 `uv run data-agent-api` 启动 FastAPI。"""

from __future__ import annotations

import uvicorn


def main() -> None:
    """进程入口：启用热重载并监听本机 8000 端口。"""

    uvicorn.run("data_agent.api:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
