import type {
  AIStatus,
  ClarificationTurn,
  DashboardQueryResponse,
  DashboardSpec,
  QueryResponse,
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
