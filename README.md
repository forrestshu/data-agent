# ERP Data Agent

这是一个 React + TypeScript + FastAPI + DeepSeek 的 ERP 自然语言查询系统。系统支持
SQLite 内部测试集和 `prod.Cux` SQL Server 公司数据库，并可在“系统信息”中全局切换。
DeepSeek 根据语义层生成当前方言的参数化 `SELECT`，后端通过独立 SQL 守卫
校验后只读执行，并返回自然语言回答与真实数据依据。

## 主要能力

- 语义层向模型提供 16 个 ERP 视图、154 个字段的用途与粒度、字段语义、批准关系和当前数据库结构；
- DeepSeek 负责意图理解、参数化 Text-to-SQL 与基于查询证据的自然语言回答；
- 支持明细、模糊匹配、聚合、分组、排序、排行、子查询以及有明确关联条件的跨视图查询；
- 意图不明确时，前端展示 AI 的具体追问并继续对话；
- 多轮澄清完整保留此前“系统追问 + 用户回答”，并阻止模型重复询问已回答信息；
- 口语或近似意图必须由用户确认后才能查询；
- SQLite 使用 `mode=ro` 与 `PRAGMA query_only=ON`；SQL Server 使用只读账号并固定映射到 `prod.Cux`；
- SQL 守卫按 SQLite/T-SQL 方言只允许已审核视图、字段和完整关联键，拒绝写入、系统表、外部数据库、跨 Schema、注释、`SELECT *`、恒真 JOIN、缺少 `Company` 的部分键 JOIN 和未批准关系；
- React 使用可展开/收起左侧导航，将查询、知识治理和基本设置分成三个独立页面；
- 查询页只展示问题输入、AI 自然语言回答和查询数据记录；
- 查询结果返回完整匹配总数，页面最多预览 100 行，并始终提供完整 Excel 下载；
- 技术异常完整写入后端日志，客户侧只显示 AI 整理后的自然语言原因；
- 知识治理页集中知识健康、视图解析和新增语义审核；
- 系统信息页展示活动数据源、全局切换、数据库概况、DeepSeek 模型与 API 边界；
- 检测 SQLite 文件、WAL、结构、行数和字段空值画像变化；
- 数据库改变后自动更新语义层的机器事实；
- 新表、新字段由 AI 生成语义候选，人工批准后才开放查询；
- 语义层未定义的相对业务概念不会擅自套用阈值；例如“快没有库存”会先询问用户本次判定标准；
- 已审核表或字段消失时，阻止受影响视图，避免继续产生错误结果。

## 本地运行

先配置后端 AI 和 SQL Server 环境。不要把 Key 或数据库密码写入前端或提交到仓库：

```bash
cp .env.example .env
# 编辑 .env：DEEPSEEK_API_KEY=替换为已轮换的新 Key
# 同时配置 DATA_AGENT_SQLSERVER_HOST、DATABASE、SCHEMA、USERNAME、PASSWORD
```

默认模型为 `deepseek-v4-flash`，可通过 `DEEPSEEK_MODEL` 覆盖。客户查询强制使用 AI；未配置或远端暂时不可用时不使用本地数据摘要冒充查询结果，而是返回不含技术细节的自然语言说明。

安装并构建：

```bash
uv sync
pnpm --dir frontend install
pnpm --dir frontend build
```

启动包含前端静态页面的 FastAPI：

```bash
uv run data-agent-api
```

打开 <http://127.0.0.1:8000>。API 文档位于
<http://127.0.0.1:8000/docs>。

前端热更新开发模式：

```bash
uv run data-agent-api
pnpm --dir frontend dev
```

Vite 页面位于 <http://127.0.0.1:5173>，`/api` 会代理到 FastAPI。

## 更换或更新 SQLite

默认数据库路径定义在 `src/data_agent/settings.py`。部署时可以通过环境变量切换：

```bash
DATA_AGENT_DATABASE=/absolute/path/new-snapshot.sqlite uv run data-agent-api
```

系统启动、每次查询前都会比较数据库快速签名；发现变化后自动执行知识同步。
也可以在网页点击“同步语义”，或者调用。接口会立即返回后台任务，旧画像在完整同步
成功前继续服务查询：

```bash
curl -X POST http://127.0.0.1:8000/api/knowledge/sync \
  -H 'Content-Type: application/json' \
  -d '{"reason":"new-snapshot"}'
```

使用返回的 `job_id` 查询进度：

```bash
curl http://127.0.0.1:8000/api/knowledge/sync/JOB_ID
```

SQL Server 统计按视图使用最多两个独立连接并发执行；相同结构下的已知失败统计默认
冷却一小时，避免反复等待超时。并发数和冷却时间可分别通过
`DATA_AGENT_SQLSERVER_STATISTICS_WORKERS` 与
`DATA_AGENT_SQLSERVER_STATISTICS_RETRY_COOLDOWN_SECONDS` 调整。

同步生成或更新：

- `src/data_agent/semantic_layer/database_profile.json`：当前数据库机器画像；
- `src/data_agent/semantic_layer/knowledge_sync_report.json`：本次变化报告；
- `src/data_agent/semantic_layer/view_catalog.json`：正式业务语义、字段解释、关联关系、数据库指纹和自动质量限制；
- `src/data_agent/semantic_layer/semantic_proposals.json`：新增表/字段的 AI 语义建议及人工审核状态。

`purpose`、`grain`、`keywords`、`aliases`、`filter_columns`、
`output_columns`、`join_columns`、`column_semantics` 和 `relationships` 属于人工审核语义，
其解释以 `docs/16张视图说明与字段关联分析.md` 为准。普通行数据变化只更新
确定性画像，不调用大模型；新增表/字段才生成 AI 建议，且不会在人工批准前写入
正式知识层。每次查询使用的是“已审核语义 + 当前实际结构”的紧凑知识上下文，不会把
数据库业务行整体发送给模型。

## 数据源切换

系统只允许两个固定数据源 ID：`sqlite_internal` 和 `sqlserver_company`。活动数据源
保存在被忽略的 `.data-agent/active_source.json` 中，文件只含 ID，不含连接信息。
也可以通过 API 切换；后端只执行连接和结构指纹预检，已有画像且结构一致时不会重新
扫描行数和空值。首次接入或结构变化时才执行完整画像，失败时继续保留原数据源：

```bash
curl -X PUT http://127.0.0.1:8000/api/data-sources/active \
  -H 'Content-Type: application/json' \
  -d '{"source_id":"sqlserver_company"}'
```

SQL Server 机器画像、同步报告和语义审核状态保存在
`.data-agent/knowledge/sqlserver_company/`，不会覆盖 SQLite 的语义层文件。

## 验收标准

- `/api/health` 返回 `service=ok` 且知识状态为 `ready`；
- 标准、口语、模糊匹配和聚合问题能在两种数据源上返回自然语言回答、受控参数化 SQL 和真实数据；
- 歧义问题能返回具体追问，用户补充后继续原查询；
- 连续澄清时，后续请求包含全部旧问答，模型不得重新询问已经回答的问题；
- “所有物料的库存数量合计”等全局统计不要求具体物料号，并返回模型生成、守卫校验后的聚合结果；
- 模型契约或执行异常只记录在后端日志，客户页面不显示 JSON、SQL、内部视图或异常命令；
- 业务含义确实存在歧义时先追问；“螺栓之类”等数据模糊匹配可直接使用绑定参数查询；
- “哪些物料快没有库存了”在用户补充本次阈值后，返回完整总数、重点摘要和前 100 行预览；
- 每次成功查询提供 15 分钟有效的下载令牌，Excel 包含完整结果且文本经过公式注入防护；
- 07-15 快照相对 07-08 的行数变化能被同步器识别；
- 数据库结构不兼容时，对应视图被阻止；
- AI 语义建议在人工批准前不会修改查询白名单；
- Python 测试、TypeScript 类型检查、lint 与生产构建全部通过。

## 系统阅读地图

- `src/data_agent/api.py`：HTTP 接口和前后端边界；
- `src/data_agent/llm.py`：DeepSeek 配置与 OpenAI 兼容调用边界；
- `src/data_agent/ai_agent.py`：语义层约束的 Text-to-SQL、澄清和证据回答；
- `src/data_agent/router.py`：自然语言意图路由；
- `src/data_agent/sql_guard.py`：模型 SQL 的语法树白名单、安全限制和条数上限；
- `src/data_agent/data_sources.py`：双数据源配置、连接适配与活动源持久化；
- `src/data_agent/executor.py`：二次 SQL 校验、超时限制与双源只读执行；
- `src/data_agent/knowledge_sync.py`：SQLite 变化检测、画像和兼容性守卫；
- `src/data_agent/sqlserver_knowledge_sync.py`：SQL Server 结构检查、限时画像和兼容性守卫；
- `src/data_agent/semantic_review.py`：新增结构的 AI 语义提案与人工审核；
- `src/data_agent/semantic_layer/`：人工业务知识与机器数据库事实；
- `frontend/src/App.tsx`：左侧导航、三页面切换、查询对话和知识治理状态机；
- `tests/`：路由、端到端、HTTP API 与快照升级测试。
