import { useEffect, useState, useMemo } from "react"
import { useNavigate } from "react-router-dom"
import { fetchCrossCapas } from "../api"
import { CAPA_STATUS_LABEL } from "../format"
import type { CrossCapaItem } from "../types"

export function CapaView() {
  const navigate = useNavigate()
  const [capas, setCapas] = useState<CrossCapaItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [typeFilter, setTypeFilter] = useState<"all" | "corrective" | "preventive">("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [search, setSearch] = useState("")

  const loadCapas = () => {
    setLoading(true)
    setError(null)
    fetchCrossCapas()
      .then((items) => {
        setCapas(items)
        setLoading(false)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load CAPAs.")
        setLoading(false)
      })
  }

  useEffect(() => {
    loadCapas()
  }, [])

  const filtered = useMemo(() => {
    return capas.filter((c) => {
      const matchesType = typeFilter === "all" || c.capa_type.toLowerCase() === typeFilter
      const matchesStatus = statusFilter === "all" || c.status.toLowerCase() === statusFilter
      const matchesSearch =
        !search ||
        c.description.toLowerCase().includes(search.toLowerCase()) ||
        c.deviation_number.toLowerCase().includes(search.toLowerCase()) ||
        c.product_name.toLowerCase().includes(search.toLowerCase()) ||
        c.owner.toLowerCase().includes(search.toLowerCase())
      return matchesType && matchesStatus && matchesSearch
    })
  }, [capas, typeFilter, statusFilter, search])

  const today = new Date().toISOString().slice(0, 10)
  const correctiveCount = capas.filter((c) => c.capa_type.toLowerCase() === "corrective").length
  const preventiveCount = capas.filter((c) => c.capa_type.toLowerCase() === "preventive").length
  const overdueCount = capas.filter((c) => c.due_date && c.due_date < today && !["completed", "verified"].includes(c.status.toLowerCase())).length

  return (
    <div className="capa-hub-container">
      <div className="capa-header">
        <div>
          <span className="eyebrow-tag">ICH Q10 QUALITY MANAGEMENT</span>
          <h2>Enterprise CAPA Tracking Hub</h2>
          <p>
            Corrective Actions (immediate containment and restoration) and Preventive Actions (systemic recurrence prevention)
            linked directly to root cause investigations across all API manufacturing suites.
          </p>
        </div>
        <div className="capa-stats-chips">
          <div className="stat-chip corrective">
            <strong>{correctiveCount}</strong> Corrective
          </div>
          <div className="stat-chip preventive">
            <strong>{preventiveCount}</strong> Preventive
          </div>
          <div className={`stat-chip ${overdueCount > 0 ? "overdue" : ""}`}>
            <strong>{overdueCount}</strong> Overdue
          </div>
        </div>
      </div>

      {error && <div className="banner error">{error}</div>}

      {/* Filter Tabs */}
      <div className="capa-filter-bar">
        <div className="tab-buttons">
          <button
            type="button"
            className={`tab-btn ${typeFilter === "all" ? "active" : ""}`}
            onClick={() => setTypeFilter("all")}
          >
            All Actions ({capas.length})
          </button>
          <button
            type="button"
            className={`tab-btn ${typeFilter === "corrective" ? "active" : ""}`}
            onClick={() => setTypeFilter("corrective")}
          >
            Corrective ({correctiveCount})
          </button>
          <button
            type="button"
            className={`tab-btn ${typeFilter === "preventive" ? "active" : ""}`}
            onClick={() => setTypeFilter("preventive")}
          >
            Preventive ({preventiveCount})
          </button>
        </div>

        <div className="filter-controls">
          <input
            type="search"
            placeholder="Search action description, owner, API..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="table-search-input"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Statuses</option>
            <option value="proposed">Proposed</option>
            <option value="accepted">Accepted</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="verified">Effectiveness Verified</option>
          </select>
        </div>
      </div>

      {/* CAPA Cards / Table */}
      <div className="enterprise-table-wrapper">
        <table className="enterprise-table">
          <thead>
            <tr>
              <th>CAPA TYPE</th>
              <th>ACTION DESCRIPTION & RATIONALE</th>
              <th>RELATED DEVIATION</th>
              <th>OWNER ROLE</th>
              <th>TARGET DATE</th>
              <th>EFFECTIVENESS CHECK</th>
              <th>STATUS</th>
              <th className="text-right">ACTION</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-muted">
                  Loading enterprise CAPAs...
                </td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={8} className="empty-table-state">
                  <div className="empty-state-content">
                    <div className="empty-icon">🛡️</div>
                    <h4>No CAPA recommendations found</h4>
                    <p>No actions match the selected filter criteria.</p>
                  </div>
                </td>
              </tr>
            ) : (
              filtered.map((item, idx) => {
                const isOverdue =
                  item.due_date &&
                  item.due_date < today &&
                  !["completed", "verified"].includes(item.status.toLowerCase())
                const isCorrective = item.capa_type.toLowerCase() === "corrective"
                return (
                  <tr
                    key={`${item.investigation_id}_${item.capa_id}_${idx}`}
                    onClick={() => navigate(`/workspace/${item.investigation_id}`)}
                    className="clickable-row"
                  >
                    <td>
                      <span className={`capa-type-pill ${isCorrective ? "corrective" : "preventive"}`}>
                        {isCorrective ? "Corrective" : "Preventive"}
                      </span>
                    </td>
                    <td className="max-w-md">
                      <div className="capa-desc-cell">
                        <strong className="text-slate-900">{item.description}</strong>
                        {item.rationale && (
                          <span className="capa-rationale text-xs text-muted">
                            Rationale: {item.rationale}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="capa-dev-cell font-mono">
                        <span className="font-bold text-teal">{item.deviation_number}</span>
                        <span className="text-xs text-muted truncate max-w-xs block">{item.product_name}</span>
                      </div>
                    </td>
                    <td className="text-sm font-medium">{item.owner || "Unassigned"}</td>
                    <td>
                      <span className={`due-date-cell font-mono text-sm ${isOverdue ? "text-danger font-bold" : ""}`}>
                        {item.due_date || "Not set"}
                        {isOverdue && <span className="overdue-tag">OVERDUE</span>}
                      </span>
                    </td>
                    <td className="text-xs text-slate-700 max-w-xs truncate" title={item.effectiveness_check}>
                      {item.effectiveness_check || "Pending Definition"}
                    </td>
                    <td>
                      <span className={`status-pill ${item.status}`}>
                        {CAPA_STATUS_LABEL[item.status] ?? item.status}
                      </span>
                    </td>
                    <td className="text-right">
                      <button
                        type="button"
                        className="btn-table-action"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/workspace/${item.investigation_id}`)
                        }}
                      >
                        Inspect →
                      </button>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

