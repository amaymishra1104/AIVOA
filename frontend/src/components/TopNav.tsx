import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { fetchHealth } from "../api"
import { SEVERITY_LABEL, STATUS_LABEL } from "../format"
import { useAppDispatch, useAppSelector } from "../store/hooks"
import { updateTracked } from "../store/investigationSlice"
import { saveInvestigation } from "../store/thunks"
import type { Health, Status } from "../types"

interface TopNavProps {
  onSearch?: (query: string) => void
}

export function TopNav({ onSearch }: TopNavProps) {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const record = useAppSelector((state) => state.investigation.record)
  const investigationId = useAppSelector((state) => state.investigation.id)
  const dirty = useAppSelector((state) => state.investigation.dirty)
  const saving = useAppSelector((state) => state.investigation.saving)
  const lastSavedAt = useAppSelector((state) => state.investigation.lastSavedAt)

  const [health, setHealth] = useState<Health | null>(null)
  const [searchVal, setSearchVal] = useState("")
  const [notifOpen, setNotifOpen] = useState(false)

  useEffect(() => {
    let cancel = false
    fetchHealth()
      .then((res) => {
        if (!cancel) setHealth(res)
      })
      .catch(() => {})
    return () => {
      cancel = true
    }
  }, [])

  const devNo = record.deviation_number.value.trim() || "Draft"
  const sev = record.severity.value || "unknown"
  const status = (record.status || "draft") as Status

  const handleSave = async () => {
    const res = await dispatch(saveInvestigation())
    if (saveInvestigation.fulfilled.match(res) && !investigationId) {
      navigate(`/workspace/${res.payload.id}`)
    }
  }

  return (
    <header className="enterprise-topnav">
      <div className="topnav-left">
        <div className="workspace-badge">
          <span className="tenant-name">Northline QA Operations</span>
          <span className="tenant-sep">/</span>
          <span className="facility-name">API Unit 3 · Hyderabad</span>
        </div>

        <div className="topnav-search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" x2="16.65" y1="21" y2="16.65" />
          </svg>
          <input
            type="search"
            placeholder="Search deviations, lots, APIs (e.g. ATV-CA-26, LOD)..."
            value={searchVal}
            onChange={(e) => {
              setSearchVal(e.target.value)
              if (onSearch) onSearch(e.target.value)
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && searchVal.trim()) {
                navigate(`/investigations?q=${encodeURIComponent(searchVal.trim())}`)
              }
            }}
          />
        </div>
      </div>

      <div className="topnav-right">
        {/* System Health Chip */}
        <div className="system-health-chip" title={health?.llm_configured ? "Groq Llama-3.3 Live" : "Pre-validated Demo Engine active"}>
          <span className={`status-indicator ${health?.database === "ok" ? "green" : "red"}`} />
          <span className="chip-label">
            {health?.llm_configured ? "Groq Live" : "Demo Engine"}
          </span>
          {health?.database === "ok" && <span className="chip-sub">DB OK</span>}
        </div>

        {/* Current Active Case Context */}
        <div className="topnav-case-context">
          <span className="case-id" onClick={() => navigate(investigationId ? `/workspace/${investigationId}` : "/workspace")}>
            {devNo}
          </span>
          <span className="severity-pill" data-severity={sev}>
            {SEVERITY_LABEL[sev] ?? sev}
          </span>
          <span className="status-pill" data-status={status}>
            {STATUS_LABEL[status] ?? status}
          </span>
        </div>

        {/* Action Controls */}
        <div className="topnav-actions">
          <button
            type="button"
            className="btn-save"
            disabled={saving || (!dirty && Boolean(investigationId))}
            onClick={handleSave}
          >
            {saving ? (
              <>
                <span className="spinner" /> Saving...
              </>
            ) : dirty ? (
              "Save Changes"
            ) : (
              "Saved"
            )}
          </button>

          {/* Notifications button */}
          <div className="notif-wrapper">
            <button
              type="button"
              className="icon-btn"
              title="Audit & Quality Notifications"
              onClick={() => setNotifOpen(!notifOpen)}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              {dirty && <span className="notif-badge" />}
            </button>
            {notifOpen && (
              <div className="notif-dropdown">
                <div className="notif-head">
                  <strong>Quality Notifications</strong>
                  <button type="button" className="text-btn" onClick={() => setNotifOpen(false)}>Close</button>
                </div>
                <div className="notif-body">
                  <div className="notif-item">
                    <span className="notif-dot blue" />
                    <div>
                      <p className="notif-text">ICH Q10 Quality System Active</p>
                      <span className="notif-time">ALCOA+ Audit Trail Enabled</span>
                    </div>
                  </div>
                  {lastSavedAt && (
                    <div className="notif-item">
                      <span className="notif-dot green" />
                      <div>
                        <p className="notif-text">Investigation Synchronized</p>
                        <span className="notif-time">{new Date(lastSavedAt).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  )}
                  {dirty && (
                    <div className="notif-item">
                      <span className="notif-dot amber" />
                      <div>
                        <p className="notif-text">Workspace has uncommitted edits</p>
                        <span className="notif-time">Press Save to commit to audit trail</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* User Profile */}
          <div className="user-profile-badge">
            <div className="user-avatar">
              {(record.prepared_by.value.trim() || "QA")[0].toUpperCase()}
            </div>
            <div className="user-info">
              <input
                className="user-name-input"
                title="Click to edit investigator name"
                value={record.prepared_by.value}
                placeholder="Investigator Name"
                onChange={(e) => dispatch(updateTracked({ path: "prepared_by", value: e.target.value }))}
              />
              <span className="user-role">Lead Investigator</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

