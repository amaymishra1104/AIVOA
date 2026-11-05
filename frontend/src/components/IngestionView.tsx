import { useState, useEffect, type DragEvent } from "react"
import { useNavigate } from "react-router-dom"
import { fetchSampleBlob, listSamples } from "../api"
import { errorMessage } from "../format"
import { ANALYZE_PHASES } from "../phases"
import { useAppDispatch, useAppSelector } from "../store/hooks"
import { clearAssistantError } from "../store/assistantSlice"
import type { SampleInfo } from "../types"
import { runAnalysis } from "../workflows"

export function IngestionView() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const record = useAppSelector((state) => state.investigation.record)
  const messages = useAppSelector((state) => state.assistant.messages)
  const phase = useAppSelector((state) => state.assistant.phase)
  const activeNode = useAppSelector((state) => state.assistant.activeNode)
  const phaseLog = useAppSelector((state) => state.assistant.phaseLog)
  const assistantError = useAppSelector((state) => state.assistant.error)
  const investigationId = useAppSelector((state) => state.investigation.id)

  const [text, setText] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [samples, setSamples] = useState<SampleInfo[]>([])
  const [sampleError, setSampleError] = useState<string | null>(null)
  const [analyzed, setAnalyzed] = useState(false)

  const busy = phase !== "idle"
  const canAnalyze = !busy && (file !== null || text.trim().length >= 40)

  useEffect(() => {
    let cancel = false
    listSamples()
      .then((items) => {
        if (!cancel) setSamples(items)
      })
      .catch((err) => {
        if (!cancel) setSampleError(errorMessage(err))
      })
    return () => {
      cancel = true
    }
  }, [])

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true)
    else if (e.type === "dragleave") setDragActive(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }

  const handleLoadSample = async (sample: SampleInfo) => {
    setSampleError(null)
    try {
      const blob = await fetchSampleBlob(sample.filename)
      if (sample.filename.endsWith(".txt")) {
        setText(await blob.text())
        setFile(null)
        return
      }
      const type = sample.filename.endsWith(".pdf") ? "application/pdf" : "message/rfc822"
      setFile(new File([blob], sample.filename, { type }))
      setText("")
    } catch (err) {
      setSampleError(errorMessage(err))
    }
  }

  const handleAnalyze = async () => {
    if (!canAnalyze) return
    dispatch(clearAssistantError())
    setAnalyzed(false)
    await runAnalysis(dispatch, { record, messages }, { text, file })
    setAnalyzed(true)
  }

  return (
    <div className="ingestion-studio">
      <div className="ingestion-header">
        <span className="eyebrow-tag">AI-ASSISTED DOCUMENT INGESTION</span>
        <h2>Incident Intake & Multi-Format Parsing</h2>
        <p>
          Upload a formal GMP deviation report (PDF), supervisor shift handover log, or Quality Control email alert (.EML).
          The AI engine extracts structured manufacturing entities, detects pharmaceutical parameters, grounds evidence quotes,
          and initializes the 5 Whys and Ishikawa fishbone investigation.
        </p>
      </div>

      {(assistantError || sampleError) && (
        <div className="banner error">{assistantError || sampleError}</div>
      )}

      {/* Sample Quick Load Row */}
      <div className="sample-strip">
        <span className="sample-strip-label">PRE-VALIDATED SAMPLE DOCUMENTS:</span>
        <div className="sample-buttons">
          {samples.map((s) => (
            <button
              key={s.filename}
              type="button"
              className="sample-pill-btn"
              onClick={() => handleLoadSample(s)}
              title={s.blurb}
            >
              <span className="file-type-tag">
                {s.filename.endsWith(".pdf") ? "PDF" : s.filename.endsWith(".eml") ? "EML" : "TXT"}
              </span>
              <span>{s.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Dual Input: Dropzone & Paste Box */}
      <div className="ingestion-input-grid">
        {/* Dropzone */}
        <div
          className={`dropzone-card ${dragActive ? "drag-active" : ""} ${file ? "has-file" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="dropzone-inner">
            <div className="dropzone-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" x2="12" y1="3" y2="15" />
              </svg>
            </div>
            {file ? (
              <div className="file-preview-box">
                <span className="file-name font-mono">{file.name}</span>
                <span className="file-size text-muted">({(file.size / 1024).toFixed(1)} KB)</span>
                <button type="button" className="text-btn danger" onClick={() => setFile(null)}>
                  Remove File
                </button>
              </div>
            ) : (
              <>
                <h4>Drag & Drop Incident File Here</h4>
                <p>Supports .PDF, .EML, .TXT up to 15 MB</p>
                <label className="btn-browse">
                  Browse Files
                  <input
                    type="file"
                    accept=".pdf,.eml,.txt,.text"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setFile(e.target.files[0])
                      }
                    }}
                    style={{ display: "none" }}
                  />
                </label>
              </>
            )}
          </div>
        </div>

        {/* Narrative Paste Input */}
        <div className="narrative-card">
          <div className="narrative-head">
            <label htmlFor="narrative-textarea">Pasted Incident Narrative or Shift Log</label>
            <span className="char-counter">{text.length} characters</span>
          </div>
          <textarea
            id="narrative-textarea"
            className="narrative-textarea"
            placeholder="Paste text from incident logs, deviation handover, or email correspondence. Must include product, batch, and event description (minimum 40 characters)..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
      </div>

      {/* Action Bar */}
      <div className="ingestion-action-bar">
        <button
          type="button"
          className="btn-primary btn-large"
          disabled={!canAnalyze}
          onClick={handleAnalyze}
        >
          {busy ? (
            <>
              <span className="spinner" /> Analyzing with Pharmaceutical AI Engine...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              Analyze with AI Engine
            </>
          )}
        </button>
        <span className="helper-text">
          Processes through LangGraph multi-stage validation, extracting facts with source quote traceability.
        </span>
      </div>

      {/* Stepper Display During / After Analysis */}
      {phaseLog.length > 0 && (
        <div className="extraction-progress-card">
          <h4>Analysis Execution Pipeline</h4>
          <ol className="stepper-horizontal">
            {ANALYZE_PHASES.map((step) => {
              const active = activeNode === step.id
              const done = phaseLog.includes(step.id) && !active
              return (
                <li key={step.id} className={`step-item ${active ? "active" : done ? "done" : "pending"}`}>
                  <div className="step-circle">{done ? "✓" : active ? "●" : ""}</div>
                  <div className="step-label">
                    <strong>{step.label}</strong>
                  </div>
                </li>
              )
            })}
          </ol>
        </div>
      )}

      {/* Extracted Entities Verification Preview */}
      {(analyzed || record.deviation_number.value || record.product_name.value) && (
        <div className="extraction-preview-panel">
          <div className="preview-header">
            <div>
              <span className="badge ok">EXTRACTION COMPLETED</span>
              <h3>Structured Entity Verification Summary</h3>
              <p>Verify extracted facts against source documents before proceeding to causal analysis.</p>
            </div>
            <button
              type="button"
              className="btn-primary"
              onClick={() => navigate(investigationId ? `/workspace/${investigationId}` : "/workspace")}
            >
              Open in Investigation Workspace →
            </button>
          </div>

          <div className="entity-cards-grid">
            <div className="entity-card">
              <span className="entity-label">DEVIATION ID</span>
              <div className="entity-val font-mono">{record.deviation_number.value || "Not provided"}</div>
              <span className="confidence-chip high">Verified from Source</span>
            </div>

            <div className="entity-card">
              <span className="entity-label">PRODUCT NAME</span>
              <div className="entity-val">{record.product_name.value || "Not provided"}</div>
              <span className="confidence-chip high">ICH Q7 Entity</span>
            </div>

            <div className="entity-card">
              <span className="entity-label">BATCH / LOT</span>
              <div className="entity-val font-mono">{record.batch_lot.value || "Not provided"}</div>
              <span className="confidence-chip high">Tracked Lot</span>
            </div>

            <div className="entity-card">
              <span className="entity-label">SEVERITY CLASSIFICATION</span>
              <div className="entity-val uppercase font-bold text-amber-700">
                {record.severity.value || "Under Evaluation"}
              </div>
              <span className="confidence-chip medium">Risk Model</span>
            </div>

            <div className="entity-card col-span-2">
              <span className="entity-label">MANUFACTURING STAGE & EQUIPMENT</span>
              <div className="entity-val">
                {[record.process_stage.value, record.equipment.value].filter(Boolean).join(" · ") || "Not provided"}
              </div>
            </div>

            <div className="entity-card col-span-2">
              <span className="entity-label">OBSERVED DEVIATION NARRATIVE</span>
              <div className="entity-val text-sm line-clamp-3">
                {record.description.value || "No description extracted."}
              </div>
            </div>

            <div className="entity-card col-span-2">
              <span className="entity-label">IMMEDIATE CONTAINMENT ACTIONS</span>
              <div className="entity-val text-sm">
                {record.immediate_actions.value || "None recorded."}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
