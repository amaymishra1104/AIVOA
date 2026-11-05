import { useEffect, useState, type FormEvent } from "react"
import { fetchSampleBlob, listSamples } from "../api"
import { errorMessage, formatWhen } from "../format"
import { ANALYZE_PHASES } from "../phases"
import { useAppDispatch, useAppSelector } from "../store/hooks"
import { clearAssistantError } from "../store/assistantSlice"
import type { SampleInfo } from "../types"
import { runAnalysis, runChat } from "../workflows"

const QUICK_PROMPTS = [
  "Why is this deviation classified as Major or Critical?",
  "What evidence supports the primary root cause?",
  "What additional documents should I collect to resolve gaps?",
  "Explain the 6M fishbone investigation breakdown",
  "Suggest stronger preventive actions for recurrence prevention",
  "Summarize the current investigation for QA review",
]

export function AssistantPanel() {
  const dispatch = useAppDispatch()
  const messages = useAppSelector((state) => state.assistant.messages)
  const phase = useAppSelector((state) => state.assistant.phase)
  const activeNode = useAppSelector((state) => state.assistant.activeNode)
  const phaseLog = useAppSelector((state) => state.assistant.phaseLog)
  const error = useAppSelector((state) => state.assistant.error)
  const record = useAppSelector((state) => state.investigation.record)
  const status = useAppSelector((state) => state.investigation.record.status)

  const [draft, setDraft] = useState("")
  const [chat, setChat] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [samples, setSamples] = useState<SampleInfo[]>([])
  const [sampleError, setSampleError] = useState<string | null>(null)
  const [sourceExpanded, setSourceExpanded] = useState(false)

  const busy = phase !== "idle"
  const canAnalyse = !busy && (file !== null || draft.trim().length >= 40)

  useEffect(() => {
    let cancel = false
    listSamples()
      .then((items) => {
        if (!cancel) setSamples(items)
      })
      .catch((reason: unknown) => {
        if (!cancel) setSampleError(errorMessage(reason))
      })
    return () => {
      cancel = true
    }
  }, [])

  async function onAnalyse() {
    if (!canAnalyse) return
    if (
      (status === "approved" || status === "pending_qa") &&
      !window.confirm("This replaces the drafted investigation with a new analysis. Reviewer comments are kept. Continue?")
    ) {
      return
    }
    dispatch(clearAssistantError())
    await runAnalysis(dispatch, { record, messages }, { text: draft, file })
  }

  async function onChat(event?: FormEvent) {
    if (event) event.preventDefault()
    const message = chat.trim()
    if (!message || busy) return
    setChat("")
    await runChat(dispatch, { record, messages }, message)
  }

  function handleQuickPrompt(promptText: string) {
    setChat(promptText)
  }

  async function loadSample(sample: SampleInfo) {
    setSampleError(null)
    try {
      const blob = await fetchSampleBlob(sample.filename)
      if (sample.filename.endsWith(".txt")) {
        setDraft(await blob.text())
        setFile(null)
        setSourceExpanded(true)
        return
      }
      const type = sample.filename.endsWith(".pdf") ? "application/pdf" : "message/rfc822"
      setFile(new File([blob], sample.filename, { type }))
      setDraft("")
      setSourceExpanded(true)
    } catch (reason) {
      setSampleError(errorMessage(reason))
    }
  }

  const devNo = record.deviation_number.value || "Draft Record"
  const product = record.product_name.value || "API"
  const batch = record.batch_lot.value || "N/A"

  return (
    <aside className="enterprise-copilot-panel">
      {/* Copilot Header */}
      <header className="copilot-head">
        <div className="copilot-title-row">
          <div className="copilot-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a8 8 0 0 0-8 8c0 4.42 5 10 8 12 3-2 8-7.58 8-12a8 8 0 0 0-8-8z" />
              <circle cx="12" cy="10" r="3" />
            </svg>
          </div>
          <div>
            <h3>AI Investigation Copilot</h3>
            <span className="copilot-sub">Context-Aware Quality Intelligence (ICH Q7/Q9)</span>
          </div>
        </div>

        {/* Current Active Context Bar */}
        <div className="copilot-context-bar">
          <span className="ctx-item font-mono font-bold text-teal">{devNo}</span>
          <span className="ctx-item truncate max-w-[140px]">{product}</span>
          <span className="ctx-item font-mono text-xs">{batch}</span>
        </div>
      </header>

      {(error || sampleError) && <p className="banner error">{error || sampleError}</p>}

      {/* Stepper Display During Active Pipeline Run */}
      {phaseLog.length > 0 && (
        <div className="copilot-stepper-box">
          <span className="stepper-title">Analysis Pipeline Progress:</span>
          <ol className="stepper" aria-label="Analysis progress">
            {ANALYZE_PHASES.map((step) => {
              const count = phaseLog.filter((item) => item === step.id).length
              const active = activeNode === step.id
              const done = count > 0 && !active
              const state = active ? "active" : done ? "done" : "wait"
              return (
                <li key={step.id} data-state={state}>
                  {step.label}
                  {count > 1 && <em> (retried)</em>}
                </li>
              )
            })}
          </ol>
        </div>
      )}

      {/* Message Thread */}
      <div className="copilot-thread" aria-live="polite">
        {messages.length === 0 && (
          <div className="thread-empty-state">
            <div className="empty-copilot-icon">🔬</div>
            <h4>Copilot Standing By</h4>
            <p>
              Ask questions about the current investigation, request alternative root causes, or analyze supporting evidence.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <article key={`${message.at}-${index}`} className={`copilot-msg ${message.role}`}>
            <header className="msg-header">
              <span className="msg-sender">
                {message.role === "user" ? "Investigator" : "Pharmaceutical AI Copilot"}
              </span>
              <time className="msg-time">{formatWhen(message.at)}</time>
            </header>
            <div className="msg-body whitespace-pre-wrap">{message.content}</div>
          </article>
        ))}

        {busy && (
          <div className="copilot-busy-indicator">
            <span className="spinner" />
            <span>{phase === "chatting" ? "Synthesizing pharmaceutical analysis..." : "Evaluating incident evidence..."}</span>
          </div>
        )}
      </div>

      {/* Suggested Quick Action Prompts */}
      <div className="quick-prompts-wrapper">
        <span className="quick-prompts-label">INVESTIGATIVE INQUIRIES:</span>
        <div className="quick-prompts-scroll">
          {QUICK_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="quick-prompt-chip"
              onClick={() => handleQuickPrompt(p)}
              disabled={busy}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Collapsible Source Ingestion Accordion */}
      <div className="source-accordion">
        <button
          type="button"
          className="accordion-toggle"
          onClick={() => setSourceExpanded(!sourceExpanded)}
        >
          <span>{sourceExpanded ? "▼ Hide Source Intake Box" : "▶ Re-ingest Source Document"}</span>
          <span className="text-xs text-muted">PDF / EML / Shift Note</span>
        </button>

        {sourceExpanded && (
          <div className="accordion-content">
            <div className="samples-row">
              {samples.map((sample) => (
                <button
                  key={sample.filename}
                  type="button"
                  className="sample-mini-btn"
                  onClick={() => void loadSample(sample)}
                  disabled={busy}
                >
                  {sample.title}
                </button>
              ))}
            </div>

            <textarea
              rows={4}
              className="source-mini-textarea"
              value={draft}
              placeholder="Paste incident narrative or drop file..."
              onChange={(e) => setDraft(e.target.value)}
            />

            <div className="source-mini-actions">
              <label className="btn-secondary btn-sm">
                Attach File
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
              {file && <span className="file-tag font-mono text-xs">{file.name}</span>}
              <button
                type="button"
                className="btn-primary btn-sm"
                disabled={!canAnalyse}
                onClick={() => void onAnalyse()}
              >
                {phase === "running" ? "Analyzing..." : "Analyze with AI"}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Chat Input Bar */}
      <form onSubmit={(e) => void onChat(e)} className="copilot-input-form">
        <input
          type="text"
          className="copilot-input-field"
          value={chat}
          placeholder="Ask Copilot a question or request section edit..."
          onChange={(e) => setChat(e.target.value)}
          disabled={busy}
        />
        <button
          type="submit"
          className="btn-send"
          disabled={busy || chat.trim().length === 0}
        >
          {phase === "chatting" ? (
            <span className="spinner" />
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          )}
        </button>
      </form>
    </aside>
  )
}
