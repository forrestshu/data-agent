"""本地 Web 开发服务器入口。"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    """启动本地 FastAPI 服务器。"""

    uvicorn.run(
        "data_agent.api:app",
        host=os.getenv("DATA_AGENT_HOST", "127.0.0.1"),
        port=int(os.getenv("DATA_AGENT_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
