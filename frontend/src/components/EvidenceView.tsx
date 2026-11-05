import { useEffect, useState, useMemo } from "react"
import { useNavigate } from "react-router-dom"
import { fetchCrossEvidence } from "../api"
import type { CrossEvidenceItem } from "../types"

export function EvidenceView() {
  const navigate = useNavigate()
  const [items, setItems] = useState<CrossEvidenceItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<"all" | "supporting" | "gaps">("all")
  const [search, setSearch] = useState("")

  const loadEvidence = () => {
    setLoading(true)
    setError(null)
    fetchCrossEvidence()
      .then((data) => {
        setItems(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load evidence library.")
        setLoading(false)
      })
  }

  useEffect(() => {
    loadEvidence()
  }, [])

  const filtered = useMemo(() => {
    return items.filter((item) => {
      const isGap = item.kind === "evidence_gap"
      if (filter === "supporting" && isGap) return false
      if (filter === "gaps" && !isGap) return false
      const matchesSearch =
        !search ||
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        item.deviation_number.toLowerCase().includes(search.toLowerCase()) ||
        item.product_name.toLowerCase().includes(search.toLowerCase()) ||
        item.excerpt.toLowerCase().includes(search.toLowerCase())
      return matchesSearch
    })
  }, [items, filter, search])

  const gapCount = items.filter((i) => i.kind === "evidence_gap").length
  const sourceCount = items.filter((i) => i.kind !== "evidence_gap").length

  return (
    <div className="evidence-hub-container">
      <div className="evidence-header">
        <div>
          <span className="eyebrow-tag">DATA INTEGRITY & TRACEABILITY</span>
          <h2>Evidence Management & Gap Detection Library</h2>
          <p>
            Centralized repository of verified GMP source records (Batch Records, HPLC Chromatograms, Calibration Certificates, BMS logs)
            and AI-detected evidence gaps requiring collection before batch disposition.
          </p>
        </div>
        <div className="evidence-summary-chips">
          <div className="stat-chip green">
            <strong>{sourceCount}</strong> Verified Records
          </div>
          <div className="stat-chip amber">
            <strong>{gapCount}</strong> Identified Gaps
          </div>
        </div>
      </div>

      {error && <div className="banner error">{error}</div>}

      {/* Tabs and Search */}
      <div className="evidence-filter-bar">
        <div className="tab-buttons">
          <button
            type="button"
            className={`tab-btn ${filter === "all" ? "active" : ""}`}
            onClick={() => setFilter("all")}
          >
            All Items ({items.length})
          </button>
          <button
            type="button"
            className={`tab-btn ${filter === "supporting" ? "active" : ""}`}
            onClick={() => setFilter("supporting")}
          >
            Verified Source Records ({sourceCount})
          </button>
          <button
            type="button"
            className={`tab-btn ${filter === "gaps" ? "active" : ""}`}
            onClick={() => setFilter("gaps")}
          >
            Missing Evidence Gaps ({gapCount})
          </button>
        </div>

        <div className="filter-controls">
          <input
            type="search"
            placeholder="Search evidence records or missing documentation..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="table-search-input"
          />
        </div>
      </div>

      {/* Evidence Grid */}
      <div className="evidence-cards-grid">
        {loading ? (
          <div className="col-span-full text-center py-12 text-muted">
            Loading evidence repository...
          </div>
        ) : filtered.length === 0 ? (
          <div className="col-span-full empty-table-state">
            <div className="empty-state-content">
              <div className="empty-icon">📁</div>
              <h4>No evidence records matching current filter</h4>
              <p>Upload new incident documents to generate verified citations and gap analysis.</p>
            </div>
          </div>
        ) : (
          filtered.map((item, idx) => {
            const isGap = item.kind === "evidence_gap"
            return (
              <div
                key={`${item.investigation_id}_${item.id}_${idx}`}
                className={`evidence-card ${isGap ? "is-gap" : "is-source"}`}
                onClick={() => navigate(`/workspace/${item.investigation_id}`)}
              >
                <div className="card-top-row">
                  <span className={`evidence-type-badge ${isGap ? "gap" : "source"}`}>
                    {isGap ? "DOCUMENTATION GAP" : `${item.kind.toUpperCase()} RECORD`}
                  </span>
                  <span className="font-mono text-xs font-bold text-teal">{item.deviation_number}</span>
                </div>

                <h4 className="evidence-card-title">{item.title}</h4>

                <div className="evidence-card-meta">
                  {item.filename && (
                    <span className="meta-item font-mono text-xs truncate">
                      📄 {item.filename}
                    </span>
                  )}
                  {item.product_name && (
                    <span className="meta-item text-xs truncate">
                      💊 {item.product_name}
                    </span>
                  )}
                </div>

                <div className="evidence-card-excerpt">
                  <p>{item.excerpt}</p>
                </div>

                <div className="card-bottom-row">
                  <span className={`status-pill ${isGap ? "pending" : "ok"}`}>
                    {item.status}
                  </span>
                  <button type="button" className="btn-table-action">
                    Inspect Investigation →
                  </button>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

