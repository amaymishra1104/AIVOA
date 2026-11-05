import { useCallback, useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { SEVERITY_LABEL } from "../format"
import { useAppDispatch, useAppSelector } from "../store/hooks"
import { setStatus, updateTracked } from "../store/investigationSlice"
import { loadInvestigation, saveInvestigation } from "../store/thunks"
import { resetWorkspace } from "../store/workspace"
import type { Status } from "../types"
import { AssistantPanel } from "./AssistantPanel"
import { AuditDrawer, LibraryDrawer } from "./Drawers"
import { FormPane } from "./FormPane"

export function Workspace() {
  const { id } = useParams()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const record = useAppSelector((state) => state.investigation.record)
  const investigationId = useAppSelector((state) => state.investigation.id)
  const dirty = useAppSelector((state) => state.investigation.dirty)
  const saving = useAppSelector((state) => state.investigation.saving)
  const saveError = useAppSelector((state) => state.investigation.saveError)
  const lastSavedAt = useAppSelector((state) => state.investigation.lastSavedAt)
  const [tab, setTab] = useState<"form" | "assistant" | "both">("both")
  const [libraryOpen, setLibraryOpen] = useState(false)
  const [auditOpen, setAuditOpen] = useState(false)

  const routeId = useRef<string | undefined>(undefined)
  useEffect(() => {
    const previous = routeId.current
    routeId.current = id
    if (previous && !id) {
      dispatch(resetWorkspace())
      return
    }
    if (!id || investigationId === id) return
    void dispatch(loadInvestigation(id))
  }, [id, investigationId, dispatch])

  useEffect(() => {
    const number = record.deviation_number.value.trim()
    document.title = number ? `${number} · Northline RCA` : "Workspace · Northline RCA"
  }, [record.deviation_number.value])

  useEffect(() => {
    const onBefore = (event: BeforeUnloadEvent) => {
      if (!dirty) return
      event.preventDefault()
      event.returnValue = ""
    }
    window.addEventListener("beforeunload", onBefore)
    return () => window.removeEventListener("beforeunload", onBefore)
  }, [dirty])

  const onSave = useCallback(async () => {
    const result = await dispatch(saveInvestigation())
    if (saveInvestigation.fulfilled.match(result) && !id) {
      navigate(`/workspace/${result.payload.id}`)
    }
  }, [dispatch, id, navigate])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "s") {
        event.preventDefault()
        void onSave()
      }
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [onSave])

  const openSuggestions = record.root_causes.filter((cause) => !(cause.confirmed && cause.evidence.trim())).length
  const severity = record.severity.value || "unknown"

  return (
    <div className="workspace-view-root">
      {/* Workspace Control Strip */}
      <div className="workspace-subbar">
        <div className="case-identity-group">
          <div className="case-title-row">
            <span className="case-id-badge font-mono">
              {record.deviation_number.value.trim() || "Unassigned"}
            </span>
            <span className="case-headline">
              {record.title.value.trim() || "Untitled Deviation Record"}
            </span>
          </div>

          <div className="case-tags-row">
            <span className="severity-pill" data-severity={severity}>
              {SEVERITY_LABEL[severity] ?? severity}
            </span>

            <label className="status-selector-wrap">
              <span className="sr">Status</span>
              <select
                value={record.status}
                onChange={(event) => {
                  const value = event.target.value as Status
                  if (value === "approved") return
                  dispatch(setStatus(value))
                }}
              >
                {record.status === "approved" && <option value="approved">Approved</option>}
                <option value="draft">Draft</option>
                <option value="under_investigation">Under investigation</option>
                <option value="pending_qa">Pending QA</option>
                <option value="closed">Closed</option>
              </select>
            </label>

            {record.product_name.value && (
              <span className="product-tag">
                {record.product_name.value} {record.batch_lot.value ? `(${record.batch_lot.value})` : ""}
              </span>
            )}

            {openSuggestions > 0 && record.root_causes.length > 0 && (
              <span className="open-suggestions-chip">
                {openSuggestions} unconfirmed {openSuggestions === 1 ? "hypothesis" : "hypotheses"}
              </span>
            )}
          </div>
        </div>

        <div className="workspace-subbar-actions">
          <label className="investigator-input-label">
            <span>Investigator:</span>
            <input
              value={record.prepared_by.value}
              placeholder="Investigator name"
              onChange={(event) => dispatch(updateTracked({ path: "prepared_by", value: event.target.value }))}
            />
          </label>

          <button type="button" className="btn-secondary btn-sm" onClick={() => setLibraryOpen(true)}>
            Library Drawer
          </button>

          <button
            type="button"
            className="btn-secondary btn-sm"
            disabled={!investigationId}
            onClick={() => setAuditOpen(true)}
          >
            Audit Trail
          </button>

          <button
            type="button"
            className="btn-secondary btn-sm"
            onClick={() => {
              if (dirty && !window.confirm("Discard unsaved changes and create new investigation?")) return
              dispatch(resetWorkspace())
              navigate("/ingest")
            }}
          >
            New
          </button>

          <button
            type="button"
            className="btn-primary btn-sm"
            disabled={saving || (!dirty && Boolean(investigationId))}
            onClick={() => void onSave()}
          >
            {saving ? "Saving…" : !investigationId ? "Save Draft" : dirty ? "Save" : "Saved"}
          </button>
        </div>
      </div>

      {saveError && <p className="banner error">{saveError}</p>}
      {lastSavedAt && !dirty && !saveError && (
        <div className="save-timestamp-bar">
          <span>✓ Record committed to PostgreSQL audit trail at {new Date(lastSavedAt).toLocaleTimeString()}</span>
        </div>
      )}

      {/* View Mode Switcher for smaller screens */}
      <div className="workspace-view-tabs">
        <button
          type="button"
          className={tab === "both" ? "active" : ""}
          onClick={() => setTab("both")}
        >
          Split Workspace (Form + Copilot)
        </button>
        <button
          type="button"
          className={tab === "form" ? "active" : ""}
          onClick={() => setTab("form")}
        >
          Investigation Form (Full Width)
        </button>
        <button
          type="button"
          className={tab === "assistant" ? "active" : ""}
          onClick={() => setTab("assistant")}
        >
          AI Copilot & Source
        </button>
      </div>

      {/* Main Dual Workspace Pane */}
      <div className="workspace-split-body" data-view-mode={tab}>
        <div className="form-pane-wrapper">
          <FormPane />
        </div>
        <div className="copilot-pane-wrapper">
          <AssistantPanel />
        </div>
      </div>

      <LibraryDrawer open={libraryOpen} dirty={dirty} onClose={() => setLibraryOpen(false)} />
      <AuditDrawer open={auditOpen} investigationId={investigationId} onClose={() => setAuditOpen(false)} />
    </div>
  )
}
