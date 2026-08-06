"""本地 Web 开发服务器入口。"""

from __future__ import annotations

import uvicorn


def main() -> None:
    """启动 FastAPI，并默认启用开发环境热更新。"""

    uvicorn.run("data_agent.api:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
