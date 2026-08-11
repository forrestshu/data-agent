/** 前端契约层：与 FastAPI JSON 响应保持一致的核心类型。 */

export interface RouteDecision {
  view_name: string
  confidence: number
  reason: string
  matched_terms: string[]
  alternatives: string[]
  match_type: 'exact' | 'fuzzy' | 'confirmed' | 'ai'
  requires_confirmation: boolean
  confirmation_question: string | null
}

export interface QueryPlan {
  view_name: string
  sql: string
  parameters: unknown[]
  source_views?: string[]
  base_sql?: string | null
}

export interface QueryResult {
  question: string
  route: RouteDecision
  plan: QueryPlan
  rows: Record<string, unknown>[]
  column_labels: Record<string, string>
  notices: string[]
  total_count: number
  has_more: boolean
  download_id: string | null
}

export type DashboardWidgetKind = 'metric' | 'bar' | 'line' | 'table'
export type DashboardWidgetSize = 'hero' | 'wide' | 'standard' | 'compact'

export interface DashboardDatum {
  label: string
  value: number
  detail?: string
  unit?: string
}

export interface DashboardWidget {
  id: string
  kind: DashboardWidgetKind
  title: string
  subtitle: string
  relevance: number
  size: DashboardWidgetSize
  value: string | number | null
  data: DashboardDatum[]
  columns: string[]
  rows: Record<string, unknown>[]
  source: string
  unit: string
  column_units: Record<string, string>
}

export interface DashboardSpec {
  mode: 'initial' | 'query'
  title: string
  question: string | null
  summary: string
  layout_reason: string
  widgets: DashboardWidget[]
}

export interface DashboardEvidence {
  source_views: string[]
  total_count: number
  displayed_count: number
  has_more: boolean
  notices: string[]
}

/** 多轮澄清契约：每次都把此前问答完整发回后端，避免模型遗忘。 */
export interface ClarificationTurn {
  question: string
  answer: string
}

export interface AITrace {
  provider: string
  model: string
  mode: string
  intent_summary: string
  confidence: number
  route_reason: string
}

export interface ClarificationAnalysis {
  status: 'clarification_required'
  view_name: string | null
  confidence: number
  intent_summary: string
  route_reason: string
  clarification_question: string | null
  clarification_kind?: 'choice' | 'number' | 'text'
  clarification_options?: string[]
  clarification_unit?: string | null
  matched_concepts: string[]
  query_values: string[]
}

export type QueryResponse =
  | {
      status: 'completed'
      answer: string
      answer_generated_by_ai: boolean
      result: QueryResult
      ai: AITrace
    }
  | {
      status: 'confirmation_required'
      message: string
      route: RouteDecision
    }
  | {
      status: 'clarification_required'
      message: string
      analysis: ClarificationAnalysis
      ai: { provider: string; model: string }
    }
  | {
      status: 'query_failed'
      answer: string
      answer_generated_by_ai: boolean
      reference_id: string
      retryable: boolean
    }

export type DashboardQueryResponse =
  | {
      status: 'completed'
      dashboard: DashboardSpec
      ai: AITrace
      evidence: DashboardEvidence
    }
  | {
      status: 'clarification_required'
      message: string
      analysis: ClarificationAnalysis
      ai: { provider: string; model: string }
    }
  | {
      status: 'query_failed'
      answer: string
      answer_generated_by_ai: boolean
      reference_id: string
      retryable: boolean
    }

export interface AIStatus {
  configured: boolean
  provider: string | null
  model: string | null
  required: boolean
  role: string
}
