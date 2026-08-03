/** 前端契约层：与 FastAPI JSON 响应保持一致的核心类型。 */
export type KnowledgeStatusName =
  | 'ready'
  | 'review_required'
  | 'update_required'
  | 'database_missing'
  | 'not_configured'
  | 'connection_error'

export type DataSourceId = 'sqlite_internal' | 'sqlserver_company'
export type DataSourceKind = 'sqlite' | 'sqlserver'

export interface DataSourceSummary {
  source_id: DataSourceId
  source_kind: DataSourceKind
  display_name: string
  dataset_label: string
  database: string
  schema: string | null
  target: string
  configured: boolean
  read_only: boolean
  status: KnowledgeStatusName | 'unknown'
  reason?: string | null
  generated_at?: string | null
}

export interface DataSourcesResponse {
  active_source_id: DataSourceId
  sources: DataSourceSummary[]
  knowledge?: KnowledgeStatus
}

export interface KnowledgeSyncJob {
  job_id: string
  source_id: DataSourceId
  source_kind: DataSourceKind
  dataset_label: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  created_at: number
  completed_views: number
  total_views: number
  current_view: string | null
  finished_at: number | null
  message: string | null
}

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
  operation: 'detail' | 'list' | 'count_rows' | 'count_distinct' | 'sum' | 'average' | 'minimum' | 'maximum' | 'text_to_sql'
  metric_column: string | null
  filter_column: string | null
  filter_value: string | null
  match_mode: string
  sql: string
  sql_chinese: string
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
  generated_at: string
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
  operation?: QueryPlan['operation'] | null
  metric_column?: string | null
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

export interface SemanticProposal {
  id: string
  kind: 'new_table' | 'new_column'
  target_view: string
  target_column: string | null
  confidence: number
  reason: string
  review_question: string
  suggestion: Record<string, unknown>
  status: 'pending' | 'approved' | 'rejected'
  reviewed_at: string | null
  reviewer_note: string | null
}

export interface SemanticReviewState {
  status: string
  database_fingerprint: string | null
  generated_at: string | null
  provider?: string
  model?: string
  proposals: SemanticProposal[]
  pending_changes?: unknown[]
}

export interface RowCountChange {
  table: string
  before: number
  after: number
  delta: number
}

export interface DriftSummary {
  new_tables?: string[]
  removed_tables?: string[]
  new_columns?: Record<string, string[]>
  removed_columns?: Record<string, string[]>
  type_changes?: Record<string, unknown[]>
  row_count_changes?: RowCountChange[]
}

export interface Compatibility {
  query_ready?: boolean
  invalid_views?: Array<{
    view: string
    reason: string
    missing: string[]
  }>
  pending_review_tables?: string[]
  policy?: string
}

export interface KnowledgeStatus {
  status: KnowledgeStatusName
  reason?: string
  database_path?: string
  generated_at?: string
  database?: {
    file_name?: string
    server?: string
    database_name?: string
    schema?: string
    live?: boolean
    schema_fingerprint?: string
    content_fingerprint?: string
    snapshot_started_at?: string
  }
  source_id?: DataSourceId
  source_kind?: DataSourceKind
  dataset_label?: string
  summary?: {
    business_table_count?: number
    total_row_count?: number
    all_null_column_count?: number
    statistics_unknown_view_count?: number
  }
  drift?: DriftSummary
  compatibility?: Compatibility
}

export interface CatalogView {
  name: string
  chinese_name: string
  domain: string
  purpose: string
  description: string
  grain: string
  filter_columns: string[]
  output_columns: string[]
  join_columns: string[]
  column_semantics: Record<string, { label_zh: string; description: string }>
}

export interface CatalogRelationship {
  id: string
  topic: string
  left_view: string
  right_view: string
  keys: Array<[string, string]>
  cardinality: string
  status: 'approved' | 'approved_with_risk' | 'advisory_not_enforceable'
  required_all_keys: boolean
  description: string
  coverage_evidence: string
  grain_warning: string
}

export interface CatalogResponse {
  catalog_version: string
  views: CatalogView[]
  relationships: CatalogRelationship[]
  join_policies: Array<{ id: string; rule: string }>
  semantic_equivalences: Array<Record<string, unknown>>
  semantic_conflicts: Array<{ id: string; rule: string }>
  semantic_source: {
    document?: string
    evidence_snapshot?: string
    observed_at?: string
    scope?: string
  }
  tables: Array<{ name: string; row_count: number }>
  generated_limitations: Array<{
    view: string
    column: string
    message: string
  }>
}
