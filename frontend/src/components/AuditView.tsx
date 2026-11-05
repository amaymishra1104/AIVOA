import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { getAudit, listInvestigations } from "../api"
import { errorMessage, formatWhen } from "../format"
import { useAppSelector } from "../store/hooks"
import type { AuditEvent, InvestigationSummary } from "../types"

export function AuditView() {
  const navigate = useNavigate()
  const activeId = useAppSelector((state) => state.investigation.id)
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([])
  const [selectedId, setSelectedId] = useState<string>(activeId || "")
  const [events, setEvents] = useState<AuditEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listInvestigations()
      .then((items) => {
        setInvestigations(items)
        if (!selectedId && items.length > 0) {
          setSelectedId(items[0].id)
        }
      })
      .catch((err) => setError(errorMessage(err)))
  }, [selectedId])

  useEffect(() => {
    if (!selectedId) return
    setLoading(true)
    getAudit(selectedId)
      .then((res) => {
        setEvents(res)
        setLoading(false)
      })
      .catch((err) => {
        setError(errorMessage(err))
        setLoading(false)
      })
  }, [selectedId])

  const activeInv = investigations.find((i) => i.id === selectedId)

  return (
    <div className="audit-hub-container">
      <div className="audit-header">
        <div>
          <span className="eyebrow-tag">ALCOA+ DATA INTEGRITY COMPLIANCE</span>
          <h2>21 CFR Part 11 Append-Only Audit Trail</h2>
          <p>
            Immutable, cryptographically timestamped record of all investigation creation events, field-level modifications,
            severity reclassifications, and QA approval electronic signatures.
          </p>
        </div>
        <div className="investigation-picker">
          <label htmlFor="audit-inv-select">Selected Investigation:</label>
          <select
            id="audit-inv-select"
            className="filter-select"
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
          >
            {investigations.map((inv) => (
              <option key={inv.id} value={inv.id}>
                {inv.deviation_number || "Draft"} · {inv.product_name || "API"} ({inv.title.slice(0, 30)}...)
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="banner error">{error}</div>}

      {/* Selected Case Banner */}
      {activeInv && (
        <div className="case-audit-meta-banner">
          <div>
            <strong>Case: {activeInv.deviation_number || "Unassigned"}</strong>
            <span className="text-muted text-sm ml-2">Title: {activeInv.title}</span>
          </div>
          <button
            type="button"
            className="btn-secondary btn-sm"
            onClick={() => navigate(`/workspace/${activeInv.id}`)}
          >
            Open in Workspace →
          </button>
        </div>
      )}

      {/* Timeline List */}
      <div className="audit-timeline">
        {loading ? (
          <div className="text-center py-8 text-muted">Retrieving audit events from secure storage...</div>
        ) : events.length === 0 ? (
          <div className="empty-table-state">
            <div className="empty-state-content">
              <h4>No audit events recorded for this record</h4>
              <p>Edits and approvals committed to the database will automatically generate ALCOA+ log entries.</p>
            </div>
          </div>
        ) : (
          events.map((event, idx) => (
            <div key={event.id} className="audit-timeline-item">
              <div className="timeline-badge">
                <span className="badge-index">{events.length - idx}</span>
              </div>
              <div className="timeline-content">
                <div className="timeline-head">
                  <div className="actor-row">
                    <span className="actor-name">{event.actor}</span>
                    <span className="action-type-tag">{event.action.toUpperCase()}</span>
                  </div>
                  <time className="timestamp font-mono">{formatWhen(event.created_at)}</time>
                </div>
                <div className="summary-text font-medium">{event.summary}</div>

                {event.changes && event.changes.length > 0 && (
                  <div className="changes-diff-box">
                    <span className="diff-title">Field Level Modifications:</span>
                    <ul className="diff-list font-mono text-xs">
                      {event.changes.map((change, cIdx) => (
                        <li key={cIdx} className="diff-item">
                          <span className="diff-path">{change.path}:</span>
                          <span className="diff-before">Before: "{String(change.before ?? "empty")}"</span>
                          <span className="diff-arrow">→</span>
                          <span className="diff-after">After: "{String(change.after ?? "")}"</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

