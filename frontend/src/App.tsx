import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import type { CSSProperties, FormEvent } from 'react'
import {
  AlertCircle,
  BarChart3,
  Check,
  Download,
  FileCode2,
  LoaderCircle,
  LayoutDashboard,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Square,
  Sparkles,
  Sun,
  TrendingUp,
  X,
} from 'lucide-react'
import {
  askDashboardQuestion,
  askQuestion,
  getAIStatus,
  getDashboard,
  getQueryExportUrl,
} from './api'
import type {
  AIStatus,
  ClarificationTurn,
  ClarificationAnalysis,
  DashboardSpec,
  DashboardWidget,
  QueryResult,
  RouteDecision,
} from './types'
import './App.css'

type AppSection = 'query' | 'dashboard'
type ColorTheme = 'light' | 'dark'

const NUMBER_FORMATTER = new Intl.NumberFormat('zh-CN', {
  maximumFractionDigits: 6,
})

const COMPACT_NUMBER_FORMATTER = new Intl.NumberFormat('zh-CN', {
  notation: 'compact',
  maximumFractionDigits: 2,
})

const RESULT_COLUMNS_PER_VIEW = 5
const QUERY_PREVIEW_LIMIT = 100

function getInitialTheme(): ColorTheme {
  try {
    const savedTheme = window.localStorage.getItem('data-agent-theme')
    if (savedTheme === 'light' || savedTheme === 'dark') {
      document.documentElement.dataset.theme = savedTheme
      return savedTheme
    }
  } catch {
    // 禁用本地存储时仍可根据系统外观启动。
  }
  const preferredTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  document.documentElement.dataset.theme = preferredTheme
  return preferredTheme
}

const SECTION_META: Record<AppSection, { title: string; icon: typeof Search }> = {
  query: { title: '数据查询', icon: Search },
  dashboard: { title: '数据看板', icon: LayoutDashboard },
}

/** 展示层：把数据库单元格转换为保留空值含义的客户可读文本。 */
function formatCell(value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'number') return NUMBER_FORMATTER.format(value)
  return String(value)
}

function formatDashboardValue(value: unknown, compact = false, unit = ''): string {
  if (typeof value !== 'number') return formatCell(value)
  const formatted = (compact ? COMPACT_NUMBER_FORMATTER : NUMBER_FORMATTER).format(value)
  return unit ? `${formatted} ${unit}` : formatted
}

/** SQL 展示层：把绑定参数安全转换为可读字面量，仅用于前端核对和复制。 */
function formatSqlParameter(value: unknown): string {
  if (value === null || value === undefined) return 'NULL'
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : 'NULL'
  if (typeof value === 'boolean') return value ? '1' : '0'
  const text = typeof value === 'string' ? value : JSON.stringify(value)
  return `'${(text ?? String(value)).replaceAll("'", "''")}'`
}

/** SQL 展示层：只替换语句正文中的占位符，跳过字符串、标识符和注释里的问号。 */
function bindSqlForDisplay(sql: string, parameters: unknown[]): string {
  let parameterIndex = 0
  let result = ''
  let quote: "'" | '"' | ']' | null = null
  let lineComment = false
  let blockComment = false

  for (let index = 0; index < sql.length; index += 1) {
    const current = sql[index]
    const next = sql[index + 1]

    if (lineComment) {
      result += current
      if (current === '\n') lineComment = false
      continue
    }
    if (blockComment) {
      result += current
      if (current === '*' && next === '/') {
        result += next
        index += 1
        blockComment = false
      }
      continue
    }
    if (quote) {
      result += current
      if (quote === ']' && current === ']') quote = null
      if (quote !== ']' && current === quote) {
        if (next === quote) {
          result += next
          index += 1
        } else {
          quote = null
        }
      }
      continue
    }
    if (current === '-' && next === '-') {
      result += current + next
      index += 1
      lineComment = true
      continue
    }
    if (current === '/' && next === '*') {
      result += current + next
      index += 1
      blockComment = true
      continue
    }
    if (current === "'" || current === '"') {
      quote = current
      result += current
      continue
    }
    if (current === '[') {
      quote = ']'
      result += current
      continue
    }
    if (current === '?' && parameterIndex < parameters.length) {
      result += formatSqlParameter(parameters[parameterIndex])
      parameterIndex += 1
      continue
    }
    result += current
  }

  return result
}

/** 表格布局层：每列固定占结果区五分之一，超过五列后由结果区横向滚动。 */
function getFixedResultColumnWidths(
  columns: string[],
  containerWidth: number,
): number[] {
  const columnWidth = Math.max(1, containerWidth / RESULT_COLUMNS_PER_VIEW)
  return columns.map(() => columnWidth)
}

/** 澄清文案层：把模型返回的直接问题与“例如/比如”说明拆成两个视觉层级。 */
function splitClarificationPrompt(value?: string | null): { question: string; helper: string | null } {
  const prompt = value?.trim() || '请补充查询对象或指标。'
  const helperMarker = prompt.match(/(?:例如|比如)[：:]?/)
  if (!helperMarker || helperMarker.index === undefined) {
    return { question: prompt, helper: null }
  }

  const question = prompt.slice(0, helperMarker.index).trim().replace(/[，,]\s*$/, '')
  const helper = prompt.slice(helperMarker.index).trim()
  return {
    question: question || '请补充查询信息。',
    helper: helper || null,
  }
}

/** Dashboard 兼容层：旧模型未返回结构化选项时，从“还是”问句提取两个快捷回答。 */
function dashboardClarificationOptions(
  clarification: ClarificationAnalysis,
): string[] {
  const provided = clarification.clarification_options
    ?.map((option) => option.trim())
    .filter(Boolean)
  if (provided && provided.length >= 2) return provided.slice(0, 4)

  const prompt = clarification.clarification_question?.trim().replace(/[？?]$/, '') ?? ''
  const parts = prompt.split(/[，,]\s*还是|还是/).map((part) => (
    part
      .replace(/^(?:您|你)?希望/, '')
      .replace(/^(?:请问|是要)/, '')
      .trim()
  ))
  return parts.length === 2 && parts.every(Boolean) ? parts : []
}

function dashboardClarificationKind(
  clarification: ClarificationAnalysis,
  options: string[],
): 'choice' | 'number' | 'text' {
  if (options.length >= 2) return 'choice'
  if (clarification.clarification_kind) return clarification.clarification_kind
  const prompt = clarification.clarification_question ?? ''
  return /阈值|判定标准|多少(?:件|天|元|%|％)?/.test(prompt) ? 'number' : 'text'
}

/** 对话展示层：成功回答和查询失败原因共用同一个自然语言回答框。 */
function AssistantAnswer({
  answer,
  sql,
  parameters = [],
}: {
  answer: string
  sql?: string | null
  parameters?: unknown[]
}) {
  const [showSql, setShowSql] = useState(false)
  const displaySql = useMemo(
    () => (sql ? bindSqlForDisplay(sql, parameters) : ''),
    [parameters, sql],
  )
  const spacedAnswer = answer
    .replace(/[ \t]*\*\*([\s\S]+?)\*\*[ \t]*/g, ' **$1** ')
    .replace(/\*\* {2,}\*\*/g, '** **')
  const answerParts = spacedAnswer.split(/(\*\*[\s\S]+?\*\*)/g)

  useEffect(() => {
    setShowSql(false)
  }, [sql])

  return (
    <section className="answer-section" aria-labelledby="answer-title" aria-live="polite">
      <div className="section-heading">
        <h2 id="answer-title" className="answer-heading">
          <img src="/in-order-logo.png" alt="IN-ORDER" width="128" height="14" />
          <span aria-hidden="true">：</span>
        </h2>
      </div>
      <div className={`answer-box${sql ? ' has-sql-control' : ''}`}>
        <p>
          {answerParts.map((part, index) => (
            part.startsWith('**') && part.endsWith('**')
              ? <strong key={index}>{part.slice(2, -2)}</strong>
              : part
          ))}
        </p>
        {sql && showSql && (
          <div id="answer-sql-panel" className="answer-sql-panel">
            <span className="answer-sql-label">查询 SQL</span>
            <pre><code>{displaySql}</code></pre>
          </div>
        )}
        {sql && (
          <button
            type="button"
            className={`answer-sql-toggle${showSql ? ' is-active' : ''}`}
            aria-expanded={showSql}
            aria-controls="answer-sql-panel"
            aria-label={showSql ? '收起查询 SQL' : '查看查询 SQL'}
            title={showSql ? '收起查询 SQL' : '查看查询 SQL'}
            onClick={() => setShowSql((current) => !current)}
          >
            <FileCode2 size={20} aria-hidden="true" />
            <span>SQL</span>
          </button>
        )}
      </div>
    </section>
  )
}

function DashboardBarChart({ widget }: { widget: DashboardWidget }) {
  const maxValue = Math.max(
    1,
    ...widget.data.map((item) => Math.abs(item.value)),
  )
  return (
    <div
      className="dashboard-bars"
      role="img"
      aria-label={`${widget.title}。${widget.data.map((item) => `${item.label} ${formatDashboardValue(item.value, false, item.unit ?? widget.unit)}`).join('；')}`}
    >
      {widget.data.map((item, index) => (
        <div className="dashboard-bar-row" key={`${item.label}-${index}`}>
          <span className="dashboard-bar-label" title={item.detail ?? item.label}>
            {item.label}
          </span>
          <span className="dashboard-bar-track" aria-hidden="true">
            <span
              className={item.value < 0 ? 'is-negative' : ''}
              style={{ width: `${Math.max(3, Math.abs(item.value) / maxValue * 100)}%` }}
            />
          </span>
          <strong>{formatDashboardValue(item.value, true, item.unit ?? widget.unit)}</strong>
        </div>
      ))}
    </div>
  )
}

function DashboardLineChart({ widget }: { widget: DashboardWidget }) {
  const data = widget.data.slice(0, 12)
  const width = 640
  const height = 220
  const paddingX = 28
  const paddingY = 24
  const values = data.map((item) => item.value)
  const minValue = Math.min(...values, 0)
  const maxValue = Math.max(...values, 1)
  const range = Math.max(1, maxValue - minValue)
  const points = data.map((item, index) => {
    const x = data.length === 1
      ? width / 2
      : paddingX + index / (data.length - 1) * (width - paddingX * 2)
    const y = height - paddingY - (item.value - minValue) / range * (height - paddingY * 2)
    return { ...item, x, y }
  })

  return (
    <div className="dashboard-line-chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={`${widget.title}趋势图。${data.map((item) => `${item.label} ${formatDashboardValue(item.value, false, item.unit ?? widget.unit)}`).join('；')}`}
      >
        {[0.25, 0.5, 0.75].map((ratio) => (
          <line
            key={ratio}
            className="dashboard-gridline"
            x1={paddingX}
            x2={width - paddingX}
            y1={paddingY + ratio * (height - paddingY * 2)}
            y2={paddingY + ratio * (height - paddingY * 2)}
          />
        ))}
        <polyline
          className="dashboard-line"
          points={points.map((point) => `${point.x},${point.y}`).join(' ')}
        />
        {points.map((point, index) => (
          <circle
            key={`${point.label}-${index}`}
            className="dashboard-line-point"
            cx={point.x}
            cy={point.y}
            r={5}
            tabIndex={0}
          >
            <title>{`${point.label}：${formatDashboardValue(point.value, false, point.unit ?? widget.unit)}`}</title>
          </circle>
        ))}
      </svg>
      <div className="dashboard-line-labels" aria-hidden="true">
        <span>{data[0]?.label ?? '—'}</span>
        <span>{data.at(-1)?.label ?? '—'}</span>
      </div>
    </div>
  )
}

function DashboardTable({ widget }: { widget: DashboardWidget }) {
  return (
    <div className="dashboard-table-scroll" aria-label={`${widget.title}数据表`}>
      <table className="dashboard-table">
        <thead>
          <tr>
            {widget.columns.map((column) => <th key={column}>{column}</th>)}
          </tr>
        </thead>
        <tbody>
          {widget.rows.map((row, index) => (
            <tr key={index}>
              {widget.columns.map((column) => (
                <td key={column}>
                  {formatDashboardValue(row[column], false, widget.column_units[column] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** Bento 排布：前 3 张形成 8+4 的完整矩形，其余每行自动均分 12 列。 */
function getDashboardGridStyle(widgetCount: number, index: number): CSSProperties {
  let column = '1 / 13'
  let row = 'auto'

  if (widgetCount === 2) {
    column = index === 0 ? '1 / 9' : '9 / 13'
    row = '1'
  } else if (widgetCount >= 3) {
    if (index === 0) {
      column = '1 / 9'
      row = '1 / 3'
    } else if (index === 1) {
      column = '9 / 13'
      row = '1'
    } else if (index === 2) {
      column = '9 / 13'
      row = '2'
    } else {
      const tailCount = widgetCount - 3
      const tailIndex = index - 3
      const tailRow = Math.floor(tailIndex / 3)
      const position = tailIndex % 3
      const itemsInRow = Math.min(3, tailCount - tailRow * 3)
      const span = 12 / itemsInRow
      const start = position * span + 1
      column = `${start} / ${start + span}`
      row = String(tailRow + 3)
    }
  }

  return {
    '--dashboard-column': column,
    '--dashboard-row': row,
  } as CSSProperties
}

function DashboardWidgetView({
  widget,
  index,
  widgetCount,
  mode,
}: {
  widget: DashboardWidget
  index: number
  widgetCount: number
  mode: DashboardSpec['mode']
}) {
  const WidgetIcon = widget.kind === 'line'
    ? TrendingUp
    : widget.kind === 'table'
      ? TableProperties
      : BarChart3
  return (
    <article
      className={`dashboard-widget dashboard-widget-enter dashboard-widget-${widget.size} dashboard-widget-${widget.kind}`}
      aria-labelledby={`dashboard-widget-${widget.id}`}
      style={{
        ...getDashboardGridStyle(widgetCount, index),
        animationDelay: `${index * 70}ms`,
      }}
    >
      <header className="dashboard-widget-header">
        <div className="dashboard-widget-heading">
          <div className="dashboard-widget-title-row">
            <WidgetIcon size={17} aria-hidden="true" />
            <h3 id={`dashboard-widget-${widget.id}`}>{widget.title}</h3>
          </div>
          {widget.subtitle && <p>{widget.subtitle}</p>}
        </div>
        <span className="relevance-badge">
          {mode === 'query' ? '回答贡献' : '概览权重'} {Math.round(widget.relevance * 100)}%
        </span>
      </header>
      <div className="dashboard-widget-body">
        {widget.kind === 'metric' && (
          <div className="dashboard-metric">
            <strong>{formatDashboardValue(widget.value, false, widget.unit)}</strong>
            <span>当前结果</span>
          </div>
        )}
        {widget.kind === 'bar' && <DashboardBarChart widget={widget} />}
        {widget.kind === 'line' && <DashboardLineChart widget={widget} />}
        {widget.kind === 'table' && <DashboardTable widget={widget} />}
      </div>
      {widget.source && <footer>来源：{widget.source}</footer>}
    </article>
  )
}

function DashboardGenerationGrid() {
  const stages = ['理解核心问题', '选择关联指标', '组织图表布局']
  return (
    <div className="dashboard-generation" role="status" aria-live="polite">
      <div className="dashboard-generation-status">
        <Sparkles size={17} aria-hidden="true" />
        <div>
          <strong>正在生成新的数据看板</strong>
          <span>面板会按重要程度依次就位</span>
        </div>
      </div>
      <div className="dashboard-grid dashboard-generation-grid" aria-hidden="true">
        {stages.map((stage, index) => (
          <div
            className="dashboard-skeleton-panel"
            key={stage}
            style={{
              ...getDashboardGridStyle(stages.length, index),
              animationDelay: `${index * 180}ms`,
            }}
          >
            <span className="dashboard-skeleton-icon" />
            <span className="dashboard-skeleton-title">{stage}</span>
            <span className="dashboard-skeleton-line is-long" />
            <span className="dashboard-skeleton-line" />
            <span className="dashboard-skeleton-chart" />
          </div>
        ))}
      </div>
    </div>
  )
}

function DashboardView({
  dashboard,
  loading,
  composer,
  onSurfaceInteraction,
}: {
  dashboard: DashboardSpec | null
  loading: boolean
  composer: React.ReactNode
  onSurfaceInteraction: () => void
}) {
  if (!dashboard) {
    return (
      <section className="dashboard-section" aria-label="正在准备数据看板">
        <div className="dashboard-heading dashboard-heading-with-composer">
          <h2>正在准备数据看板</h2>
          {composer}
        </div>
        <DashboardGenerationGrid />
      </section>
    )
  }
  return (
    <section
      className="dashboard-section"
      aria-labelledby="dashboard-title"
      aria-busy={loading}
      onPointerDown={(event) => {
        const target = event.target as HTMLElement
        if (!target.closest('.dashboard-composer')) onSurfaceInteraction()
      }}
    >
      <div className="dashboard-heading dashboard-heading-with-composer">
        <h2 id="dashboard-title">
          {dashboard.title}
        </h2>
        {composer}
      </div>
      {loading ? (
        <DashboardGenerationGrid />
      ) : (
        <div
          className="dashboard-grid"
          data-widget-count={dashboard.widgets.length}
          key={`${dashboard.mode}-${dashboard.question ?? dashboard.generated_at}`}
        >
          {dashboard.widgets.map((widget, index) => (
            <DashboardWidgetView
              widget={widget}
              index={index}
              widgetCount={dashboard.widgets.length}
              mode={dashboard.mode}
              key={widget.id}
            />
          ))}
        </div>
      )}
    </section>
  )
}

/** 查询结果组件：成功时在自然语言回答后展示可核对的数据记录。 */
function QueryResultView({ result, answer }: { result: QueryResult; answer: string }) {
  const tableContainerRef = useRef<HTMLDivElement>(null)
  const [columnWidths, setColumnWidths] = useState<number[]>([])
  const [tableContainerWidth, setTableContainerWidth] = useState(0)
  const [expandedCell, setExpandedCell] = useState<
    | { kind: 'header'; columnIndex: number }
    | { kind: 'data'; rowIndex: number; columnIndex: number }
    | null
  >(null)
  const columns = useMemo(
    () => (result.rows[0] ? Object.keys(result.rows[0]) : []),
    [result.rows],
  )

  /** 响应式布局状态：结果或可用空间变化时，把全部结果列重算为统一的五分之一宽度。 */
  useLayoutEffect(() => {
    const container = tableContainerRef.current
    if (!container || columns.length === 0) return undefined

    const updateColumnWidths = () => {
      const containerWidth = container.clientWidth
      const nextWidths = getFixedResultColumnWidths(columns, containerWidth)
      setTableContainerWidth((currentWidth) => (
        currentWidth === containerWidth ? currentWidth : containerWidth
      ))
      setColumnWidths((currentWidths) => (
        currentWidths.length === nextWidths.length
        && currentWidths.every((width, index) => width === nextWidths[index])
          ? currentWidths
          : nextWidths
      ))
    }

    updateColumnWidths()
    const observer = new ResizeObserver(updateColumnWidths)
    observer.observe(container)
    return () => observer.disconnect()
  }, [columns])

  useEffect(() => {
    setExpandedCell(null)
  }, [result])

  useEffect(() => {
    const closeExpandedCell = (event: PointerEvent) => {
      const target = event.target
      if (target instanceof Element && target.closest('[data-result-expandable="true"]')) return
      setExpandedCell(null)
    }
    document.addEventListener('pointerdown', closeExpandedCell)
    return () => document.removeEventListener('pointerdown', closeExpandedCell)
  }, [])

  const dataColumnsWidth = columnWidths.reduce((total, width) => total + width, 0)
  const fillerColumnWidth = Math.max(0, tableContainerWidth - dataColumnsWidth)
  const tableWidth = Math.max(tableContainerWidth, dataColumnsWidth)
  const hasFillerColumn = fillerColumnWidth > 0
  const sourceViews = (
    result.plan.source_views?.length
      ? result.plan.source_views
      : [result.plan.view_name || result.route.view_name]
  ).filter(Boolean)

  return (
    <div className="query-output" aria-live="polite">
      <AssistantAnswer
        answer={answer}
        sql={result.plan.base_sql ?? result.plan.sql}
        parameters={result.plan.parameters}
      />

      <section className="data-section" aria-labelledby="result-title">
        <div className="section-heading">
          <h2 id="result-title">查询结果</h2>
          <span className="result-count">
            显示 {result.rows.length.toLocaleString('zh-CN')} / 共 {result.total_count.toLocaleString('zh-CN')} 条结果
          </span>
        </div>
        <div className="data-frame">
          {result.rows.length > 0 ? (
            <div
              ref={tableContainerRef}
              className="table-scroll data-table-scroll"
              tabIndex={0}
              aria-label="查询结果数据表"
            >
              <table
                className="result-table"
                style={tableWidth > 0 ? { width: tableWidth } : undefined}
              >
                <colgroup>
                  {columns.map((column, index) => (
                    <col
                      key={column}
                      style={columnWidths[index] ? { width: columnWidths[index] } : undefined}
                    />
                  ))}
                  {hasFillerColumn && (
                    <col className="result-table-filler-column" style={{ width: fillerColumnWidth }} />
                  )}
                </colgroup>
                <thead>
                  <tr>
                    {columns.map((column, columnIndex) => {
                      const columnLabel = result.column_labels[column] ?? column
                      const isExpanded = expandedCell?.kind === 'header'
                        && expandedCell.columnIndex === columnIndex
                      const expandsLeft = !hasFillerColumn && columnIndex === columns.length - 1
                      return (
                        <th
                          scope="col"
                          key={column}
                          className={`${typeof result.rows[0]?.[column] === 'number' ? 'numeric ' : ''}${isExpanded ? 'is-cell-expanded' : ''}`.trim()}
                        >
                          <button
                            type="button"
                            data-result-expandable="true"
                            className={`result-header-value${isExpanded ? ' is-expanded' : ''}${expandsLeft ? ' expands-left' : ''}`}
                            aria-expanded={isExpanded}
                            aria-label={`${columnLabel}，原字段 ${column}。${isExpanded ? '已完整显示' : '点击查看完整字段名'}`}
                            title={isExpanded ? '已完整显示' : `${columnLabel}（${column}）`}
                            onClick={() => setExpandedCell((currentCell) => (
                              currentCell?.kind === 'header' && currentCell.columnIndex === columnIndex
                                ? currentCell
                                : { kind: 'header', columnIndex }
                            ))}
                            onKeyDown={(event) => {
                              if (event.key === 'Escape') setExpandedCell(null)
                            }}
                          >
                            {columnLabel}
                          </button>
                        </th>
                      )
                    })}
                    {hasFillerColumn && <th className="result-table-filler" aria-hidden="true" />}
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row, rowIndex) => (
                    <tr key={`${rowIndex}-${columns.map((column) => row[column]).join('-')}`}>
                      {columns.map((column, columnIndex) => {
                        const displayValue = formatCell(row[column])
                        const columnLabel = result.column_labels[column] ?? column
                        const isExpanded = expandedCell?.kind === 'data'
                          && expandedCell.rowIndex === rowIndex
                          && expandedCell.columnIndex === columnIndex
                        const expandsLeft = !hasFillerColumn && columnIndex === columns.length - 1
                        return (
                          <td
                            key={column}
                            className={`${typeof row[column] === 'number' ? 'numeric ' : ''}${isExpanded ? 'is-cell-expanded' : ''}`.trim()}
                          >
                            <button
                              type="button"
                              data-result-expandable="true"
                              className={`result-cell-value${isExpanded ? ' is-expanded' : ''}${expandsLeft ? ' expands-left' : ''}`}
                              aria-expanded={isExpanded}
                              aria-label={`${columnLabel}：${displayValue}。${isExpanded ? '已完整显示' : '点击查看完整内容'}`}
                              title={isExpanded ? '已完整显示' : displayValue}
                              onClick={() => setExpandedCell((currentCell) => (
                                currentCell?.kind === 'data'
                                && currentCell.rowIndex === rowIndex
                                && currentCell.columnIndex === columnIndex
                                  ? currentCell
                                  : { kind: 'data', rowIndex, columnIndex }
                              ))}
                              onKeyDown={(event) => {
                                if (event.key === 'Escape') setExpandedCell(null)
                              }}
                            >
                              {displayValue}
                            </button>
                          </td>
                        )
                      })}
                      {hasFillerColumn && <td className="result-table-filler" aria-hidden="true" />}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-row">没有找到符合条件的数据。</div>
          )}
          <div className="result-overflow-note">
            <span className="result-source-views">
              {sourceViews.length > 0
                ? `来源视图：${sourceViews.join('、')}`
                : '来源视图：—'}
            </span>
            {result.download_id && (
              <a href={getQueryExportUrl(result.download_id)}>
                <Download size={16} />下载完整 Excel
              </a>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

/** 查询页面：维护客户提问、临时澄清和结果展示三个可见层级。 */
function QueryPage({
  question,
  setQuestion,
  result,
  answer,
  confirmation,
  clarification,
  clarificationText,
  setClarificationText,
  loading,
  onSubmit,
  onConfirm,
  onClarify,
  onCancelConfirmation,
}: {
  question: string
  setQuestion: (value: string) => void
  result: QueryResult | null
  answer: string
  confirmation: RouteDecision | null
  clarification: ClarificationAnalysis | null
  clarificationText: string
  setClarificationText: (value: string) => void
  loading: boolean
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  onConfirm: (viewName: string) => void
  onClarify: () => void
  onCancelConfirmation: () => void
}) {
  const clarificationPrompt = splitClarificationPrompt(clarification?.clarification_question)
  const clarificationInputRef = useRef<HTMLTextAreaElement>(null)

  /** 追问输入随换行向下生长，避免在单行初始高度内出现纵向滚动条。 */
  useLayoutEffect(() => {
    const input = clarificationInputRef.current
    if (!input) return
    input.style.height = '64px'
    input.style.height = `${Math.max(64, input.scrollHeight)}px`
  }, [clarification, clarificationText])

  return (
    <section className={`query-page${result ? ' has-result' : ''}`} aria-label="自然语言数据查询">
      <form className="query-composer" onSubmit={onSubmit}>
        <div className="section-heading input-heading">
          <label htmlFor="question">输入问题</label>
        </div>
        <div className="composer-box">
          <textarea
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return
              event.preventDefault()
              if (!event.repeat && question.trim() && !loading) {
                event.currentTarget.form?.requestSubmit()
              }
            }}
            placeholder="例如：查询物料 6100001876 的最新采购价和平均价"
            rows={4}
            maxLength={500}
            disabled={loading}
          />
          <button
            className={`primary-action ${loading ? 'is-loading' : question.trim() ? 'is-ready' : 'is-idle'}`}
            type="submit"
            disabled={loading || !question.trim()}
            aria-label={loading ? '正在查询' : question.trim() ? '开始查询' : '输入问题后开始查询'}
            title={loading ? '正在查询' : question.trim() ? '开始查询' : '输入问题后开始查询'}
          >
            {loading
              ? <Square size={12} fill="currentColor" strokeWidth={0} aria-hidden="true" />
              : <Search size={19} aria-hidden="true" />}
          </button>
        </div>
      </form>

      {confirmation && (
        <section className="inline-dialog" role="alertdialog" aria-labelledby="confirm-title">
          <AlertCircle size={20} />
          <div>
            <h2 id="confirm-title">确认查询对象</h2>
            <p>{confirmation.confirmation_question ?? confirmation.reason}</p>
            <div className="dialog-actions">
              <button onClick={() => onConfirm(confirmation.view_name)}>确认并查询</button>
              <button className="text-action" onClick={onCancelConfirmation}>取消</button>
            </div>
          </div>
        </section>
      )}

      {clarification && (
        <section className="clarification-section" aria-labelledby="clarify-title">
          <h2 id="clarify-title" className="clarification-question">{clarificationPrompt.question}</h2>
          {clarificationPrompt.helper && (
            <p className="clarification-helper">{clarificationPrompt.helper}</p>
          )}
          <div className="composer-box clarification-composer">
            <textarea
              ref={clarificationInputRef}
              value={clarificationText}
              onChange={(event) => setClarificationText(event.target.value)}
              onKeyDown={(event) => {
                if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return
                event.preventDefault()
                if (!event.repeat && clarificationText.trim() && !loading) onClarify()
              }}
              placeholder="输入补充说明"
              aria-label="输入补充说明"
              rows={1}
              maxLength={500}
              disabled={loading}
            />
            <button
              className={`primary-action clarification-action ${loading ? 'is-loading' : clarificationText.trim() ? 'is-ready' : 'is-idle'}`}
              type="button"
              onClick={onClarify}
              disabled={loading || !clarificationText.trim()}
              aria-label={loading ? '正在查询' : clarificationText.trim() ? '继续查询' : '输入补充说明后继续查询'}
              title={loading ? '正在查询' : clarificationText.trim() ? '继续查询' : '输入补充说明后继续查询'}
            >
              {loading
                ? <Square size={12} fill="currentColor" strokeWidth={0} aria-hidden="true" />
                : <Search size={19} aria-hidden="true" />}
            </button>
          </div>
        </section>
      )}

      {loading && (
        <div className="query-loading" aria-live="polite">
          <LoaderCircle size={20} className="spin" />
          <span>思考</span>
        </div>
      )}

      {answer && !result && !loading && !confirmation && !clarification && (
        <AssistantAnswer answer={answer} />
      )}
      {result && !loading && <QueryResultView result={result} answer={answer} />}
    </section>
  )
}

function DashboardClarificationPanel({
  clarification,
  confirmation,
  answer,
  setAnswer,
  loading,
  onAnswer,
  onConfirm,
}: {
  clarification: ClarificationAnalysis | null
  confirmation: RouteDecision | null
  answer: string
  setAnswer: (value: string) => void
  loading: boolean
  onAnswer: (answer: string) => void
  onConfirm: (viewName: string) => void
}) {
  if (confirmation) {
    return (
      <section className="dashboard-clarification" aria-labelledby="dashboard-confirm-title">
        <div className="dashboard-clarification-heading">
          <AlertCircle size={19} aria-hidden="true" />
          <div>
            <h2 id="dashboard-confirm-title">确认数据看板查询方向</h2>
            <p>{confirmation.confirmation_question ?? confirmation.reason}</p>
          </div>
        </div>
        <button
          className="dashboard-choice"
          type="button"
          disabled={loading}
          onClick={() => onConfirm(confirmation.view_name)}
        >
          <Check size={16} aria-hidden="true" />
          确认并生成
        </button>
      </section>
    )
  }
  if (!clarification) return null

  const prompt = splitClarificationPrompt(clarification.clarification_question)
  const options = dashboardClarificationOptions(clarification)
  const kind = dashboardClarificationKind(clarification, options)
  const inputUnit = clarification.clarification_unit?.trim() ?? ''
  return (
    <section className="dashboard-clarification" aria-labelledby="dashboard-clarify-title">
      <div className="dashboard-clarification-heading">
        <AlertCircle size={19} aria-hidden="true" />
        <div>
          <h2 id="dashboard-clarify-title">生成前需要确认</h2>
          <p>{prompt.question}</p>
          {prompt.helper && <span>{prompt.helper}</span>}
        </div>
      </div>

      {kind === 'choice' ? (
        <div className="dashboard-choice-list" role="group" aria-label="选择一个查询口径">
          {options.map((option) => (
            <button
              className="dashboard-choice"
              type="button"
              key={option}
              disabled={loading}
              onClick={() => onAnswer(option)}
            >
              {option}
            </button>
          ))}
        </div>
      ) : (
        <form
          className="dashboard-clarification-form"
          onSubmit={(event) => {
            event.preventDefault()
            if (answer.trim()) onAnswer(answer.trim())
          }}
        >
          <label htmlFor="dashboard-clarification-answer">
            {kind === 'number' ? '填写数值' : '补充说明'}
          </label>
          <div className="dashboard-clarification-input-row">
            <input
              id="dashboard-clarification-answer"
              type={kind === 'number' ? 'number' : 'text'}
              inputMode={kind === 'number' ? 'decimal' : 'text'}
              value={answer}
              step={kind === 'number' ? 'any' : undefined}
              placeholder={kind === 'number' ? '请输入数值' : '请输入补充说明'}
              disabled={loading}
              onChange={(event) => setAnswer(event.target.value)}
            />
            {inputUnit && <span className="dashboard-input-unit">{inputUnit}</span>}
            <button type="submit" disabled={loading || !answer.trim()}>
              {loading ? <LoaderCircle size={16} className="spin" /> : <Check size={16} />}
              确认并生成
            </button>
          </div>
        </form>
      )}
    </section>
  )
}

/** Dashboard 页面：独立维护问题输入，并调用概况分析链路，不改变数据查询 Tab。 */
function DashboardPage({
  question,
  setQuestion,
  dashboard,
  loading,
  notice,
  clarification,
  confirmation,
  clarificationAnswer,
  setClarificationAnswer,
  onSubmit,
  onClarify,
  onConfirm,
}: {
  question: string
  setQuestion: (value: string) => void
  dashboard: DashboardSpec | null
  loading: boolean
  notice: string | null
  clarification: ClarificationAnalysis | null
  confirmation: RouteDecision | null
  clarificationAnswer: string
  setClarificationAnswer: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  onClarify: (answer: string) => void
  onConfirm: (viewName: string) => void
}) {
  const hasQueryDashboard = dashboard?.mode === 'query'
  const [composerExpanded, setComposerExpanded] = useState(!hasQueryDashboard)

  useEffect(() => {
    setComposerExpanded(!hasQueryDashboard)
  }, [dashboard?.question, hasQueryDashboard])

  const composer = (
    <form
      className="query-composer dashboard-composer"
      onSubmit={(event) => {
        setComposerExpanded(false)
        onSubmit(event)
      }}
    >
      <div className="section-heading input-heading">
        <label htmlFor="dashboard-question">询问数据看板</label>
      </div>
      <div className="composer-box">
        <textarea
          id="dashboard-question"
          value={question}
          placeholder="例如：查看采购订单到货进度、销售订单发货情况，或项目工单完工情况"
          onChange={(event) => setQuestion(event.target.value)}
          onFocus={() => setComposerExpanded(true)}
          onKeyDown={(event) => {
            if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return
            event.preventDefault()
            if (!event.repeat && question.trim() && !loading) {
              event.currentTarget.form?.requestSubmit()
            }
          }}
          rows={3}
          maxLength={500}
          disabled={loading}
          aria-expanded={composerExpanded}
        />
        <button
          className={`primary-action ${loading ? 'is-loading' : question.trim() ? 'is-ready' : 'is-idle'}`}
          type="submit"
          disabled={loading || !question.trim()}
          aria-label={loading ? '正在重排数据看板' : question.trim() ? '生成数据看板' : '输入问题后生成数据看板'}
          title={loading ? '正在重排数据看板' : question.trim() ? '生成数据看板' : '输入问题后生成数据看板'}
        >
          {loading
            ? <Square size={12} fill="currentColor" strokeWidth={0} aria-hidden="true" />
            : <Search size={18} aria-hidden="true" />}
        </button>
      </div>
    </form>
  )

  return (
    <section
      className={`dashboard-page${hasQueryDashboard ? ' has-query-dashboard' : ''}${composerExpanded ? ' is-composer-expanded' : ' is-composer-compact'}${clarification || confirmation || notice ? ' has-interruption' : ''}`}
      aria-label="动态数据看板"
    >
      {notice && (
        <div className="dashboard-notice" role="status">
          <AlertCircle size={17} />
          <span>{notice}</span>
        </div>
      )}
      <DashboardClarificationPanel
        clarification={clarification}
        confirmation={confirmation}
        answer={clarificationAnswer}
        setAnswer={setClarificationAnswer}
        loading={loading}
        onAnswer={onClarify}
        onConfirm={onConfirm}
      />
      <DashboardView
        dashboard={dashboard}
        loading={loading}
        composer={composer}
        onSurfaceInteraction={() => setComposerExpanded(false)}
      />
    </section>
  )
}

/** 应用根组件：保存查询与 Dashboard 两个页面的共享状态。 */
function App() {
  const [activeSection, setActiveSection] = useState<AppSection>('query')
  const [theme, setTheme] = useState<ColorTheme>(getInitialTheme)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    () => window.matchMedia('(max-width: 760px)').matches,
  )
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState<QueryResult | null>(null)
  const [answer, setAnswer] = useState('')
  const [confirmation, setConfirmation] = useState<RouteDecision | null>(null)
  const [clarification, setClarification] = useState<ClarificationAnalysis | null>(null)
  const [clarificationText, setClarificationText] = useState('')
  const [clarificationHistory, setClarificationHistory] = useState<ClarificationTurn[]>([])
  const [dashboard, setDashboard] = useState<DashboardSpec | null>(null)
  const [dashboardQuestion, setDashboardQuestion] = useState('')
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [dashboardNotice, setDashboardNotice] = useState<string | null>(null)
  const [dashboardClarification, setDashboardClarification] =
    useState<ClarificationAnalysis | null>(null)
  const [dashboardConfirmation, setDashboardConfirmation] =
    useState<RouteDecision | null>(null)
  const [dashboardClarificationAnswer, setDashboardClarificationAnswer] = useState('')
  const [dashboardClarificationHistory, setDashboardClarificationHistory] =
    useState<ClarificationTurn[]>([])
  const [aiStatus, setAIStatus] = useState<AIStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  /** 外观状态：同步根节点、浏览器主题色并记住用户选择。 */
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    document.documentElement.style.colorScheme = theme
    document.querySelector('meta[name="theme-color"]')?.setAttribute(
      'content',
      theme === 'dark' ? '#1b1c1f' : '#eceef1',
    )
    try {
      window.localStorage.setItem('data-agent-theme', theme)
    } catch {
      // 主题仍在当前页面生效，只是无法跨刷新保存。
    }
  }, [theme])

  /** 初始化数据流：读取 AI 状态和静态 Dashboard。 */
  useEffect(() => {
    let active = true
    Promise.all([getAIStatus(), getDashboard()])
      .then(([nextAI, nextDashboard]) => {
        if (!active) return
        setAIStatus(nextAI)
        setDashboard(nextDashboard)
      })
      .catch((loadError: unknown) => {
        if (active) setError(loadError instanceof Error ? loadError.message : '初始化失败')
      })
    return () => { active = false }
  }, [])

  /** 查询状态机：保留原问题，支持 AI 追问、低置信度确认和最终结果。 */
  async function executeQuery(options: {
    confirmedView?: string
    clarificationAnswer?: string
    startNew?: boolean
  } = {}): Promise<void> {
    const cleanedQuestion = question.trim()
    if (!cleanedQuestion) {
      setError('请先输入要查询的业务问题。')
      return
    }
    const { confirmedView, clarificationAnswer, startNew = false } = options
    let nextHistory = startNew ? [] : clarificationHistory
    if (clarificationAnswer?.trim() && clarification) {
      // 对话状态层：把当前追问和回答追加到历史，下一轮不会覆盖之前信息。
      nextHistory = [
        ...nextHistory,
        {
          question: clarification.clarification_question ?? '请补充查询信息。',
          answer: clarificationAnswer.trim(),
        },
      ]
    }
    if (startNew) setClarificationHistory([])
    setLoading(true)
    setError(null)
    // 新查询开始时清空旧对话分支，避免历史追问与本次失败提示同时出现。
    setConfirmation(null)
    setClarification(null)
    setClarificationText('')
    setResult(null)
    setAnswer('')
    try {
      const response = await askQuestion(
        cleanedQuestion,
        QUERY_PREVIEW_LIMIT,
        confirmedView,
        clarificationAnswer,
        nextHistory,
      )
      if (response.status === 'confirmation_required') {
        setConfirmation(response.route)
        setClarification(null)
        setResult(null)
        setAnswer('')
      } else if (response.status === 'clarification_required') {
        setClarificationHistory(nextHistory)
        setClarification(response.analysis)
        setConfirmation(null)
        setResult(null)
        setAnswer('')
      } else if (response.status === 'query_failed') {
        setConfirmation(null)
        setClarification(null)
        setResult(null)
        setAnswer(response.answer)
      } else {
        setClarificationHistory(nextHistory)
        setConfirmation(null)
        setClarification(null)
        setClarificationText('')
        setResult(response.result)
        setAnswer(response.answer)
      }
    } catch {
      // 浏览器断网等无法到达后端的情况没有模型可用，仍只展示客户可理解的回答。
      setResult(null)
      setAnswer('当前暂时无法连接查询服务，请稍后重试。你的问题和数据不会因此改变。')
    } finally {
      setLoading(false)
    }
  }

  /** 表单边界：阻止浏览器刷新，把问题交给统一查询状态机。 */
  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    void executeQuery({ startNew: true })
  }

  async function executeDashboard(options: {
    confirmedView?: string
    clarificationAnswer?: string
    startNew?: boolean
  } = {}): Promise<void> {
    const cleanedQuestion = dashboardQuestion.trim()
    if (!cleanedQuestion) {
      setDashboardNotice('请先输入希望数据看板回答的问题。')
      return
    }
    const { confirmedView, clarificationAnswer, startNew = false } = options
    let nextHistory = startNew ? [] : dashboardClarificationHistory
    if (clarificationAnswer?.trim() && dashboardClarification) {
      nextHistory = [
        ...nextHistory,
        {
          question: dashboardClarification.clarification_question ?? '请补充数据看板查询信息。',
          answer: clarificationAnswer.trim(),
        },
      ]
    }
    if (startNew) setDashboardClarificationHistory([])
    setDashboardLoading(true)
    setDashboardNotice(null)
    setDashboardClarification(null)
    setDashboardConfirmation(null)
    try {
      const response = await askDashboardQuestion(
        cleanedQuestion,
        100,
        confirmedView,
        clarificationAnswer,
        nextHistory,
      )
      if (response.status === 'completed') {
        setDashboardClarificationHistory(nextHistory)
        setDashboardClarificationAnswer('')
        setDashboard(response.dashboard)
        setDashboardQuestion('')
      } else if (response.status === 'clarification_required') {
        setDashboardClarificationHistory(nextHistory)
        setDashboardClarification(response.analysis)
      } else if (response.status === 'query_failed') {
        setDashboardNotice(response.answer)
      }
    } catch {
      setDashboardNotice('当前暂时无法生成数据看板，请确认查询服务可用后重试。')
    } finally {
      setDashboardLoading(false)
    }
  }

  function handleDashboardSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    void executeDashboard({ startNew: true })
  }

  /** 导航状态：切换页面后在窄屏自动收起覆盖面板，桌面端保持用户选择。 */
  function selectSection(section: AppSection): void {
    setActiveSection(section)
    if (window.matchMedia('(max-width: 760px)').matches) {
      setSidebarCollapsed(true)
    }
  }

  const navItems: Array<{ id: AppSection; label: string; icon: typeof Search }> =
    (Object.entries(SECTION_META) as Array<[AppSection, (typeof SECTION_META)[AppSection]]>)
      .map(([id, meta]) => ({ id, label: meta.title, icon: meta.icon }))
  const pageMeta = SECTION_META[activeSection]
  const PageIcon = pageMeta.icon

  return (
    <div className={`app-layout ${sidebarCollapsed ? 'is-collapsed' : ''}`}>
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <aside className="app-sidebar" aria-label="主导航">
        <div className="sidebar-brand">
          <span>Data Agent</span>
          <button
            className="collapse-button"
            aria-label={sidebarCollapsed ? '展开左侧面板' : '收起左侧面板'}
            onClick={() => setSidebarCollapsed((current) => !current)}
          >
            {sidebarCollapsed ? <PanelLeftOpen size={19} /> : <PanelLeftClose size={19} />}
          </button>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = activeSection === item.id
            return (
              <button
                key={item.id}
                className={active ? 'is-active' : ''}
                aria-current={active ? 'page' : undefined}
                title={sidebarCollapsed ? item.label : undefined}
                onClick={() => selectSection(item.id)}
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>
        <div
          className="sidebar-foot"
          role="status"
          aria-label={`${aiStatus?.configured ? 'AI 服务正常' : 'AI 服务未配置'}，模型 ${aiStatus?.model ?? 'deepseek-v4-flash'}，SQLite 本地数据库`}
          title={aiStatus?.configured ? 'AI 服务正常' : 'AI 服务未配置'}
        >
          <span className={aiStatus?.configured ? 'service-dot is-online' : 'service-dot'} aria-hidden="true" />
          <span className="service-copy">
            <span className="service-model">{aiStatus?.model ?? 'deepseek-v4-flash'}</span>
            <span className="service-dataset">
              SQLite 本地数据库
            </span>
          </span>
        </div>
      </aside>

      <div className="content-shell">
        <header className="app-topbar">
          <h1><PageIcon size={20} aria-hidden="true" />{pageMeta.title}</h1>
          <button
            className="theme-toggle"
            type="button"
            aria-label={theme === 'dark' ? '切换为浅色模式' : '切换为深色模式'}
            onClick={() => setTheme((currentTheme) => currentTheme === 'dark' ? 'light' : 'dark')}
          >
            {theme === 'dark' ? <Moon size={18} /> : <Sun size={18} />}
            <span>{theme === 'dark' ? '深色模式' : '浅色模式'}</span>
          </button>
        </header>

        <main id="main-content" className="page-content">
          {error && (
            <div className="error-line" role="alert">
              <AlertCircle size={18} /><span>{error}</span>
              <button aria-label="关闭错误提示" onClick={() => setError(null)}><X size={17} /></button>
            </div>
          )}

          {activeSection === 'query' && (
            <QueryPage
              question={question}
              setQuestion={setQuestion}
              result={result}
              answer={answer}
              confirmation={confirmation}
              clarification={clarification}
              clarificationText={clarificationText}
              setClarificationText={setClarificationText}
              loading={loading}
              onSubmit={handleSubmit}
              onConfirm={(viewName) => void executeQuery({ confirmedView: viewName })}
              onClarify={() => void executeQuery({ clarificationAnswer: clarificationText })}
              onCancelConfirmation={() => setConfirmation(null)}
            />
          )}
          {activeSection === 'dashboard' && (
            <DashboardPage
              question={dashboardQuestion}
              setQuestion={setDashboardQuestion}
              dashboard={dashboard}
              loading={dashboardLoading}
              notice={dashboardNotice}
              clarification={dashboardClarification}
              confirmation={dashboardConfirmation}
              clarificationAnswer={dashboardClarificationAnswer}
              setClarificationAnswer={setDashboardClarificationAnswer}
              onSubmit={handleDashboardSubmit}
              onClarify={(nextAnswer) => void executeDashboard({
                clarificationAnswer: nextAnswer,
              })}
              onConfirm={(viewName) => void executeDashboard({
                confirmedView: viewName,
              })}
            />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
