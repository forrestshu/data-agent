# Data Agent

一个可在 SQL Server 实时库与 SQLite 快照间切换的自然语言查询系统。DeepSeek 负责理解问题和生成参数化 SQL，后端只允许查询语义层批准的视图与字段，并在安全校验后执行。

## 项目结构

```text
data-agent/
├── backend/
│   ├── data_agent_2026_07_15.sqlite  # SQLite 快照
│   ├── src/data_agent/
│   │   ├── api.py          # FastAPI 查询与导出接口
│   │   ├── database.py     # SQLite 访问
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

系统默认使用 SQL Server，前端可切换到 SQLite 本地快照。连接参数通过 `.env` 中的 `SQLSERVER_*` 和 `DATA_AGENT_DEFAULT_SOURCE` 配置；密码不得提交到 Git。两种数据源共享同一份已审核语义目录。

## 环境配置

复制 `.env.example` 为 `.env`，填写 DeepSeek 配置：

```bash
cp .env.example .env
```

数据库访问约束：

- SQLite 使用 `mode=ro&immutable=1` 并执行 `PRAGMA query_only=ON`；
- SQL Server 使用独立只读账号并仅映射 `Cux` 下的已审核视图；
- SQL 安全校验仅允许单条参数化 `SELECT`；
- 禁止写入、外部数据库、系统表、注释和 `SELECT *`；
- 跨视图查询必须使用语义层批准的完整连接键。

## 安装

```bash
uv sync --project backend
pnpm --dir frontend install
```

## 本地开发

```bash
./dev.sh
```

- 前端：<http://127.0.0.1:5173>
- 后端：<http://127.0.0.1:8000>
- 健康检查：<http://127.0.0.1:8000/api/health>

## 验证

```bash
uv run --project backend python -m unittest discover -s backend/tests -q
pnpm --dir frontend exec tsc --noEmit
pnpm --dir frontend lint
```

这些命令运行后端测试、TypeScript 类型检查和前端静态检查，不执行生产构建。
