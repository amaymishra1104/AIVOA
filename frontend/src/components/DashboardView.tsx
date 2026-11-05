import { useEffect, useState, useMemo } from "react"
import { useNavigate } from "react-router-dom"
import { fetchDashboardStats } from "../api"
import { formatWhen, SEVERITY_LABEL, STATUS_LABEL } from "../format"
import type { DashboardStats, Status } from "../types"

export function DashboardView() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters for recent investigations table
  const [search, setSearch] = useState("")
  const [severityFilter, setSeverityFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sortBy, setSortBy] = useState<"updated" | "severity" | "id">("updated")
  const [page, setPage] = useState(1)
  const pageSize = 6

  const loadData = () => {
    setLoading(true)
    setError(null)
    fetchDashboardStats()
      .then((data) => {
        setStats(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load dashboard statistics.")
        setLoading(false)
      })
  }

  useEffect(() => {
    loadData()
  }, [])

  // Filtered investigations list
  const filteredInvestigations = useMemo(() => {
    if (!stats?.recent_investigations) return []
    return stats.recent_investigations
      .filter((inv) => {
        const matchesSearch =
          !search ||
          inv.deviation_number.toLowerCase().includes(search.toLowerCase()) ||
          inv.title.toLowerCase().includes(search.toLowerCase()) ||
          inv.product_name.toLowerCase().includes(search.toLowerCase()) ||
          inv.batch_lot.toLowerCase().includes(search.toLowerCase())
        const matchesSeverity = severityFilter === "all" || inv.severity === severityFilter
        const matchesStatus = statusFilter === "all" || inv.status === statusFilter
        return matchesSearch && matchesSeverity && matchesStatus
      })
      .sort((a, b) => {
        if (sortBy === "id") return a.deviation_number.localeCompare(b.deviation_number)
        if (sortBy === "severity") {
          const rank: Record<string, number> = { critical: 3, major: 2, minor: 1, unknown: 0 }
          return (rank[b.severity] ?? 0) - (rank[a.severity] ?? 0)
        }
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      })
  }, [stats, search, severityFilter, statusFilter, sortBy])

  const totalPages = Math.ceil(filteredInvestigations.length / pageSize) || 1
  const paginatedList = filteredInvestigations.slice((page - 1) * pageSize, page * pageSize)

  const kpis = stats?.kpis
  const charts = stats?.charts

  return (
    <div className="dashboard-container">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <div>
          <span className="eyebrow-tag">EXECUTIVE QUALITY INTELLIGENCE</span>
          <h1 className="dashboard-title">API Manufacturing Quality Dashboard</h1>
          <p className="dashboard-subtitle">
            Real-time Root Cause Analysis, 6M Ishikawa distribution, and CAPA operational oversight (ICH Q7 / Q9 / Q10).
          </p>
        </div>
        <div className="dashboard-header-actions">
          <button type="button" className="btn-secondary" onClick={loadData}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
              <path d="M21 3v5h-5" />
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
              <path d="M8 16H3v5" />
            </svg>
            Refresh Metrics
          </button>
          <button type="button" className="btn-primary" onClick={() => navigate("/ingest")}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New AI Investigation
          </button>
        </div>
      </div>

      {error && <div className="banner error">{error}</div>}

      {/* KPI Cards Grid */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon-row">
            <span className="kpi-label">TOTAL INVESTIGATIONS</span>
            <div className="kpi-icon blue">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{loading ? "—" : kpis?.total_investigations ?? 0}</div>
          <div className="kpi-subtext">Cumulative tracked records in database</div>
        </div>

        <div className="kpi-card highlight-amber">
          <div className="kpi-icon-row">
            <span className="kpi-label">OPEN DEVIATIONS</span>
            <div className="kpi-icon amber">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{loading ? "—" : kpis?.open_deviations ?? 0}</div>
          <div className="kpi-subtext">Drafts, Under Investigation & Pending QA</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-row">
            <span className="kpi-label">ACTIVE INVESTIGATIONS</span>
            <div className="kpi-icon teal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{loading ? "—" : kpis?.in_progress ?? 0}</div>
          <div className="kpi-subtext">Actively undergoing 5 Whys & 6M analysis</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-row">
            <span className="kpi-label">PENDING CAPAS</span>
            <div className="kpi-icon purple">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{loading ? "—" : kpis?.pending_capas ?? 0}</div>
          <div className="kpi-subtext">
            Completion rate: <strong>{loading ? "—" : `${kpis?.capa_completion_rate ?? 0}%`}</strong>
          </div>
        </div>

        <div className={`kpi-card ${kpis && kpis.overdue_capas > 0 ? "highlight-red" : ""}`}>
          <div className="kpi-icon-row">
            <span className="kpi-label">OVERDUE CAPAS</span>
            <div className="kpi-icon red">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{loading ? "—" : kpis?.overdue_capas ?? 0}</div>
          <div className="kpi-subtext">Requires immediate QA Committee escalation</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon-row">
            <span className="kpi-label">CLOSED / APPROVED</span>
            <div className="kpi-icon green">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            </div>
          </div>
          <div className="kpi-value">{loading ? "—" : kpis?.closed_investigations ?? 0}</div>
          <div className="kpi-subtext">
            Avg closure time: <strong>{loading ? "—" : `${kpis?.avg_closure_time_days ?? 0} days`}</strong>
          </div>
        </div>
      </div>

      {/* Analytics Charts Section */}
      <div className="dashboard-charts-grid">
        {/* Severity Classification Distribution */}
        <div className="chart-panel">
          <div className="panel-head">
            <h3>Severity Classification Breakdown</h3>
            <span className="panel-badge">ICH Q9 Risk Level</span>
          </div>
          <div className="severity-bar-container">
            {charts?.severity_distribution.map((item) => (
              <div key={item.label} className="severity-bar-item">
                <div className="bar-header">
                  <span className="bar-label">{item.label}</span>
                  <span className="bar-count">{item.count}</span>
                </div>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${kpis && kpis.total_investigations > 0 ? (item.count / kpis.total_investigations) * 100 : 0}%`,
                      backgroundColor: item.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 6M Ishikawa Category Distribution */}
        <div className="chart-panel">
          <div className="panel-head">
            <h3>Root Cause 6M Distribution</h3>
            <span className="panel-badge">API Manufacturing Dimensions</span>
          </div>
          <div className="category-bars">
            {charts?.category_distribution.map((item) => {
              const maxCount = Math.max(...(charts.category_distribution.map((c) => c.count) || [1]), 1)
              return (
                <div key={item.category} className="cat-bar-item">
                  <span className="cat-label">{item.category}</span>
                  <div className="cat-track">
                    <div
                      className="cat-fill"
                      style={{
                        width: `${maxCount > 0 ? (item.count / maxCount) * 100 : 0}%`,
                      }}
                    />
                  </div>
                  <span className="cat-value">{item.count}</span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Investigation Pipeline Status Breakdown */}
        <div className="chart-panel">
          <div className="panel-head">
            <h3>Investigation Lifecycle Funnel</h3>
            <span className="panel-badge">QMS Progression</span>
          </div>
          <div className="status-funnel">
            {charts?.status_distribution.map((item, idx) => (
              <div key={item.status} className="funnel-step">
                <div className="step-idx">{idx + 1}</div>
                <div className="step-info">
                  <span className="step-name">{item.status}</span>
                  <span className="step-count">{item.count} deviations</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Investigations Table Section */}
      <div className="table-panel">
        <div className="table-panel-head">
          <div>
            <h3>Recent Investigations Directory</h3>
            <p>Database records reflecting actual GMP investigations and containment actions.</p>
          </div>
          <div className="table-filters">
            <input
              type="search"
              placeholder="Filter by deviation #, product, or batch..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              className="table-search-input"
            />
            <select
              value={severityFilter}
              onChange={(e) => {
                setSeverityFilter(e.target.value)
                setPage(1)
              }}
              className="filter-select"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="major">Major</option>
              <option value="minor">Minor</option>
              <option value="unknown">Unclassified</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
              className="filter-select"
            >
              <option value="all">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="under_investigation">Under investigation</option>
              <option value="pending_qa">Pending QA</option>
              <option value="closed">Closed / Approved</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "updated" | "severity" | "id")}
              className="filter-select"
            >
              <option value="updated">Sort by Last Updated</option>
              <option value="severity">Sort by Severity</option>
              <option value="id">Sort by Deviation ID</option>
            </select>
          </div>
        </div>

        {/* Data Table */}
        <div className="enterprise-table-wrapper">
          <table className="enterprise-table">
            <thead>
              <tr>
                <th>DEVIATION ID</th>
                <th>INCIDENT TITLE</th>
                <th>PRODUCT & BATCH</th>
                <th>SEVERITY</th>
                <th>STATUS</th>
                <th>LAST UPDATED</th>
                <th className="text-right">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-6 text-muted">
                    Loading quality investigations from database...
                  </td>
                </tr>
              ) : paginatedList.length === 0 ? (
                <tr>
                  <td colSpan={7} className="empty-table-state">
                    <div className="empty-state-content">
                      <div className="empty-icon">📂</div>
                      <h4>No investigations matching current criteria</h4>
                      <p>Upload a new deviation report or clear active filters to inspect records.</p>
                      <button type="button" className="btn-primary" onClick={() => navigate("/ingest")}>
                        Ingest New Incident
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                paginatedList.map((item) => (
                  <tr key={item.id} onClick={() => navigate(`/workspace/${item.id}`)} className="clickable-row">
                    <td className="font-mono font-bold text-teal">{item.deviation_number || "Unassigned"}</td>
                    <td className="font-medium text-slate-800 max-w-xs truncate" title={item.title}>
                      {item.title || "Untitled Deviation"}
                    </td>
                    <td>
                      <div className="product-lot-cell">
                        <span className="product-name">{item.product_name || "API"}</span>
                        <span className="lot-badge font-mono">{item.batch_lot || "N/A"}</span>
                      </div>
                    </td>
                    <td>
                      <span className="severity-pill" data-severity={item.severity}>
                        {SEVERITY_LABEL[item.severity] ?? item.severity}
                      </span>
                    </td>
                    <td>
                      <span className="status-pill" data-status={item.status}>
                        {STATUS_LABEL[item.status as Status] ?? item.status}
                      </span>
                    </td>
                    <td className="text-muted text-sm">{formatWhen(item.updated_at)}</td>
                    <td className="text-right">
                      <button
                        type="button"
                        className="btn-table-action"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/workspace/${item.id}`)
                        }}
                      >
                        Open Workspace →
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {filteredInvestigations.length > pageSize && (
          <div className="table-pagination">
            <span className="page-indicator">
              Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, filteredInvestigations.length)} of{" "}
              {filteredInvestigations.length} investigations
            </span>
            <div className="pagination-buttons">
              <button
                type="button"
                className="btn-secondary btn-sm"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </button>
              <span className="page-number">
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                className="btn-secondary btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

