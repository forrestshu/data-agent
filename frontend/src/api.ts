import type {
  AIStatus,
  CatalogResponse,
  ClarificationTurn,
  DashboardQueryResponse,
  DashboardSpec,
  DataSourceId,
  DataSourcesResponse,
  KnowledgeSyncJob,
  KnowledgeStatus,
  QueryResponse,
  SemanticReviewState,
} from './types'

const API_ROOT = import.meta.env.VITE_API_ROOT ?? '/api'

/** 网络边界：把 FastAPI 的结构化错误统一转换成用户可读异常。 */
async function readJson<T>(response: Response): Promise<T> {
  const payload = (await response.json()) as T & {
    detail?: string | { message?: string }
  }
  if (!response.ok) {
    const detail = payload.detail
    const message =
      typeof detail === 'string'
        ? detail
        : detail?.message ?? `请求失败（HTTP ${response.status}）`
    throw new Error(message)
  }
  return payload
}

/** 查询接口：发送自然语言问题，并可携带用户明确确认的视图。 */
export async function askQuestion(
  question: string,
  limit: number,
  confirmedView?: string,
  clarificationAnswer?: string,
  clarificationHistory: ClarificationTurn[] = [],
): Promise<QueryResponse> {
  const response = await fetch(`${API_ROOT}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      limit,
      confirmed_view: confirmedView ?? null,
      clarification_answer: clarificationAnswer ?? null,
      clarification_history: clarificationHistory,
    }),
  })
  return readJson<QueryResponse>(response)
}

/** Dashboard 概况接口：独立于精确数据查询，允许模型推断排序、分布和趋势口径。 */
export async function askDashboardQuestion(
  question: string,
  limit: number,
  confirmedView?: string,
  clarificationAnswer?: string,
  clarificationHistory: ClarificationTurn[] = [],
): Promise<DashboardQueryResponse> {
  const response = await fetch(`${API_ROOT}/dashboard/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      limit,
      confirmed_view: confirmedView ?? null,
      clarification_answer: clarificationAnswer ?? null,
      clarification_history: clarificationHistory,
    }),
  })
  return readJson<DashboardQueryResponse>(response)
}

/** 下载边界：浏览器只拿短期令牌，不接触 SQL，也不先加载完整结果。 */
export function getQueryExportUrl(downloadId: string): string {
  return `${API_ROOT}/query/exports/${encodeURIComponent(downloadId)}`
}

/** AI 状态接口：只读取模型是否已在后端配置，不接触或展示 API Key。 */
export async function getAIStatus(): Promise<AIStatus> {
  return readJson<AIStatus>(await fetch(`${API_ROOT}/ai/status`))
}

/** Dashboard 初始态：使用当前知识画像生成无需额外业务查询的基础图表。 */
export async function getDashboard(): Promise<DashboardSpec> {
  return readJson<DashboardSpec>(await fetch(`${API_ROOT}/dashboard`))
}

/** 数据源接口：只读取安全摘要，不接触账号、密码或连接串。 */
export async function getDataSources(): Promise<DataSourcesResponse> {
  return readJson<DataSourcesResponse>(await fetch(`${API_ROOT}/data-sources`))
}

/** 全局切换：后端完成连接和画像预检后才提交活动数据源。 */
export async function switchDataSource(
  sourceId: DataSourceId,
): Promise<DataSourcesResponse> {
  const response = await fetch(`${API_ROOT}/data-sources/active`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_id: sourceId }),
  })
  return readJson<DataSourcesResponse>(response)
}

/** 治理接口：读取当前快照、画像版本和兼容性状态。 */
export async function getKnowledgeStatus(): Promise<KnowledgeStatus> {
  return readJson<KnowledgeStatus>(await fetch(`${API_ROOT}/knowledge/status`))
}

/** 治理接口：扫描 SQLite 并更新语义层的机器事实。 */
export async function syncKnowledge(): Promise<KnowledgeSyncJob> {
  const response = await fetch(`${API_ROOT}/knowledge/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason: 'web-console' }),
  })
  return readJson<KnowledgeSyncJob>(response)
}

/** 后台同步进度：完整画像完成前继续使用上一份有效画像。 */
export async function getKnowledgeSyncJob(jobId: string): Promise<KnowledgeSyncJob> {
  return readJson<KnowledgeSyncJob>(
    await fetch(`${API_ROOT}/knowledge/sync/${encodeURIComponent(jobId)}`),
  )
}

/** 目录接口：读取 16 个已审核业务视图与各表行数。 */
export async function getCatalog(): Promise<CatalogResponse> {
  return readJson<CatalogResponse>(await fetch(`${API_ROOT}/knowledge/catalog`))
}

/** 语义提案接口：读取 AI 对新增表/字段的建议及人工审核状态。 */
export async function getSemanticProposals(): Promise<SemanticReviewState> {
  return readJson<SemanticReviewState>(
    await fetch(`${API_ROOT}/knowledge/semantic-proposals`),
  )
}

/** 人工审核接口：只有这个动作能批准 AI 建议进入正式查询知识。 */
export async function reviewSemanticProposal(
  proposalId: string,
  decision: 'approve' | 'reject',
): Promise<SemanticReviewState> {
  const response = await fetch(
    `${API_ROOT}/knowledge/semantic-proposals/${proposalId}/review`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, reviewer_note: 'web-console' }),
    },
  )
  return readJson<SemanticReviewState>(response)
}

/** 体验接口：加载与当前快照匹配的示例问题。 */
export async function getExamples(): Promise<string[]> {
  const payload = await readJson<{ examples: string[] }>(
    await fetch(`${API_ROOT}/examples`),
  )
  return payload.examples
}
