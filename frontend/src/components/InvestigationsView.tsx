import { useEffect, useState, useMemo } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { deleteInvestigation } from "../api"
import { errorMessage, formatWhen, SEVERITY_LABEL, STATUS_LABEL } from "../format"
import { useAppDispatch, useAppSelector } from "../store/hooks"
import { fetchLibrary } from "../store/thunks"
import type { Status } from "../types"

export function InvestigationsView() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const [searchParams] = useSearchParams()

  const items = useAppSelector((state) => state.library.items)
  const loading = useAppSelector((state) => state.library.loading)
  const error = useAppSelector((state) => state.library.error)

  const [search, setSearch] = useState(searchParams.get("q") || "")
  const [severityFilter, setSeverityFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sortBy, setSortBy] = useState<"updated" | "severity" | "id">("updated")
  const [page, setPage] = useState(1)
  const [actionError, setActionError] = useState<string | null>(null)
  const pageSize = 10

  useEffect(() => {
    void dispatch(fetchLibrary())
  }, [dispatch])

  useEffect(() => {
    const q = searchParams.get("q")
    if (q) setSearch(q)
  }, [searchParams])

  const filtered = useMemo(() => {
    return items
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
  }, [items, search, severityFilter, statusFilter, sortBy])

  const totalPages = Math.ceil(filtered.length / pageSize) || 1
  const paginated = filtered.slice((page - 1) * pageSize, page * pageSize)

  const handleDelete = async (e: React.MouseEvent, id: string, devNo: string) => {
    e.stopPropagation()
    if (!window.confirm(`Permanently delete investigation ${devNo || id} and its complete audit history?`)) {
      return
    }
    try {
      await deleteInvestigation(id)
      void dispatch(fetchLibrary())
    } catch (err) {
      setActionError(errorMessage(err))
    }
  }

  return (
    <div className="directory-container">
      <div className="directory-header">
        <div>
          <span className="eyebrow-tag">CENTRAL INVESTIGATION DIRECTORY</span>
          <h2>Quality Investigations Repository</h2>
          <p>
            Permanent pharmaceutical records containing 5 Whys, Ishikawa fishbone diagrams, evidence citations,
            and approved CAPAs under 21 CFR Part 11 / EU Annex 11 data integrity principles.
          </p>
        </div>
        <button type="button" className="btn-primary" onClick={() => navigate("/ingest")}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New Investigation
        </button>
      </div>

      {(error || actionError) && <div className="banner error">{error || actionError}</div>}

      {/* Filter and Search Bar */}
      <div className="directory-filter-bar">
        <div className="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" x2="16.65" y1="21" y2="16.65" />
          </svg>
          <input
            type="search"
            placeholder="Search by deviation ID, API name, lot number..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
          />
        </div>

        <div className="filters-group">
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
            <option value="under_investigation">Under Investigation</option>
            <option value="pending_qa">Pending QA</option>
            <option value="approved">Approved</option>
            <option value="closed">Closed</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as "updated" | "severity" | "id")}
            className="filter-select"
          >
            <option value="updated">Sort by Updated Date</option>
            <option value="severity">Sort by Risk Severity</option>
            <option value="id">Sort by Deviation ID</option>
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="enterprise-table-wrapper">
        <table className="enterprise-table">
          <thead>
            <tr>
              <th>DEVIATION ID</th>
              <th>INCIDENT TITLE</th>
              <th>PRODUCT & BATCH</th>
              <th>SEVERITY</th>
              <th>STATUS</th>
              <th>LAST MODIFIED</th>
              <th className="text-right">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-muted">
                  Loading investigation library from PostgreSQL...
                </td>
              </tr>
            ) : paginated.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-table-state">
                  <div className="empty-state-content">
                    <div className="empty-icon">📋</div>
                    <h4>No investigations found</h4>
                    <p>No saved investigations match the active search criteria.</p>
                    <button type="button" className="btn-secondary" onClick={() => { setSearch(""); setSeverityFilter("all"); setStatusFilter("all"); }}>
                      Reset All Filters
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              paginated.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => navigate(`/workspace/${item.id}`)}
                  className="clickable-row"
                >
                  <td className="font-mono font-bold text-teal">
                    {item.deviation_number || "Unassigned"}
                  </td>
                  <td className="font-medium text-slate-800 max-w-sm truncate" title={item.title}>
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
                    <div className="row-actions-group">
                      <button
                        type="button"
                        className="btn-table-action"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/workspace/${item.id}`)
                        }}
                      >
                        Open
                      </button>
                      <button
                        type="button"
                        className="btn-table-delete"
                        title="Delete investigation"
                        onClick={(e) => handleDelete(e, item.id, item.deviation_number)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      {filtered.length > pageSize && (
        <div className="table-pagination">
          <span className="page-indicator">
            Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, filtered.length)} of {filtered.length} investigations
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
  )
}

