# ERP Data Agent

一个面向 ERP SQLite 快照的自然语言查询系统。DeepSeek 负责理解问题和生成参数化 SQL，后端只允许查询语义层批准的视图与字段，并通过只读 SQLite 连接执行。

## 项目结构

```text
data-agent/
├── backend/
│   ├── data_agent_2026_07_15.sqlite  # SQLite 快照
│   ├── src/data_agent/
│   │   ├── api.py          # FastAPI 查询与导出接口
│   │   ├── database.py     # SQLite 只读访问
│   │   ├── llm.py          # DeepSeek 客户端
│   │   ├── settings.py     # 路径配置
│   │   ├── knowledge/      # 静态业务语义与数据库画像
│   │   ├── prompts/        # 模型提示词 Markdown
│   │   └── query/          # 查询规划、安全校验与执行
│   └── tests/
└── frontend/               # React + Vite
```

默认数据库：

```text
backend/data_agent_2026_07_15.sqlite
```

可以通过 `DATA_AGENT_DATABASE` 指向另一份 SQLite 文件。系统不会自动扫描、同步或更新知识画像。

## 环境配置

复制 `.env.example` 为 `.env`，填写 DeepSeek 配置：

```bash
cp .env.example .env
```

数据库始终以只读模式打开：

- URI 使用 `mode=ro&immutable=1`；
- 连接执行 `PRAGMA query_only=ON`；
- SQL 守卫仅允许单条参数化 `SELECT`；
- 禁止写入、外部数据库、系统表、注释和 `SELECT *`；
- 跨视图查询必须使用语义层批准的完整连接键。

## 安装

```bash
uv sync --project backend
pnpm --dir frontend install
```

## 本地开发

终端一：

```bash
uv run --project backend data-agent
```

终端二：

```bash
pnpm --dir frontend dev
```

- 前端：<http://127.0.0.1:5173>
- 后端：<http://127.0.0.1:8000>
- 健康检查：<http://127.0.0.1:8000/api/health>

## 验证

```bash
./scripts/check.sh
```

该脚本运行后端测试、端到端测试和 TypeScript 类型检查，不执行生产构建。
