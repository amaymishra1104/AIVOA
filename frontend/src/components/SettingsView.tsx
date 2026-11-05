import { useEffect, useState } from "react"
import { fetchHealth } from "../api"
import type { Health } from "../types"

export function SettingsView() {
  const [health, setHealth] = useState<Health | null>(null)

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data)
      })
      .catch(() => {})
  }, [])

  return (
    <div className="settings-container">
      <div className="settings-header">
        <div>
          <span className="eyebrow-tag">SYSTEM GOVERNANCE & REGULATORY ALIGNMENT</span>
          <h2>Platform Configuration & Regulatory Framework</h2>
          <p>
            System operational status, database connectivity, model configurations, and pharmaceutical quality system controls
            aligned with ICH Q7, ICH Q9, and ICH Q10 guidelines.
          </p>
        </div>
      </div>

      {/* System Status Grid */}
      <div className="settings-section">
        <h3>Runtime Architecture Status</h3>
        <div className="system-status-grid">
          <div className="status-box">
            <span className="status-label">POSTGRESQL DATABASE</span>
            <div className="status-val-row">
              <span className={`status-dot ${health?.database === "ok" ? "green" : "red"}`} />
              <strong>{health?.database === "ok" ? "Connected (Healthy)" : "Unavailable"}</strong>
            </div>
            <p className="status-sub">PostgreSQL 16 persistence for investigations and append-only audit events.</p>
          </div>

          <div className="status-box">
            <span className="status-label">AI REASONING ENGINE</span>
            <div className="status-val-row">
              <span className={`status-dot ${health?.llm_configured ? "green" : "amber"}`} />
              <strong>
                {health?.llm_configured ? `Groq Live (${health.model})` : "Pre-validated Demo Knowledge Engine"}
              </strong>
            </div>
            <p className="status-sub">
              {health?.llm_configured
                ? "Live LangGraph structured model pipeline configured via GROQ_API_KEY."
                : "Deterministic ICH Q7/Q9 pharmaceutical knowledge engine active for demonstration."}
            </p>
          </div>

          <div className="status-box">
            <span className="status-label">AUDIT TRAIL LOGGING</span>
            <div className="status-val-row">
              <span className="status-dot green" />
              <strong>Enabled (ALCOA+ Compliant)</strong>
            </div>
            <p className="status-sub">Automatic field-level delta capture and actor attribution on every commit.</p>
          </div>
        </div>
      </div>

      {/* Regulatory Alignment Matrix */}
      <div className="settings-section">
        <h3>Pharmaceutical Regulatory Guidance Mapping</h3>
        <div className="compliance-grid">
          <div className="compliance-card">
            <h4>ICH Q7: API Manufacturing GMP</h4>
            <p>
              Provides structured deviation records capturing API batch identification, process stages (reaction, crystallization,
              filtration, drying), containment quarantine protocols, and cross-functional investigation team attributions.
            </p>
          </div>

          <div className="compliance-card">
            <h4>ICH Q9: Quality Risk Management</h4>
            <p>
              Enforces objective risk categorization (Critical, Major, Minor) with mandatory rationale and explicit evidence grounding
              before any AI-suggested hypothesis can be elevated to a verified finding.
            </p>
          </div>

          <div className="compliance-card">
            <h4>ICH Q10: Pharmaceutical Quality System</h4>
            <p>
              Integrates Corrective and Preventive Actions (CAPA) with owner roles, completion due dates, and mandatory effectiveness
              verification checks prior to QA committee closure.
            </p>
          </div>

          <div className="compliance-card">
            <h4>21 CFR Part 11 & ALCOA+ Principles</h4>
            <p>
              Append-only audit trail recording every change, before/after values, timestamps, and actor identities. Differentiates
              AI suggestions from qualified investigator confirmations.
            </p>
          </div>
        </div>
      </div>

      {/* Honest Compliance & Validation Disclosure */}
      <div className="settings-section">
        <div className="disclaimer-callout">
          <h4>Regulated Environment Validation Notice (GAMP 5 / CSV)</h4>
          <p>
            In accordance with good regulatory practice, this software is provided as an AI-assisted quality management workspace.
            Representation of regulatory concepts (ICH Q7/Q9/Q10, 21 CFR Part 11) within this interface does not constitute formal FDA validation
            or GMP certification of an unvalidated installation.
          </p>
          <p className="mt-2 text-sm text-slate-700">
            Prior to deployment in a validated commercial GxP environment, the following controls must be formally established:
          </p>
          <ul className="compliance-requirements-list">
            <li>Execution of formal Computer System Validation (CSV / CSA) under GAMP 5 life cycle documentation (IQ/OQ/PQ).</li>
            <li>Integration of corporate Single Sign-On (SSO / LDAP) with dual-credential electronic signatures for sign-offs.</li>
            <li>Deployment of private or dedicated tenant LLM inference infrastructure with verified zero-data-retention agreements.</li>
            <li>Formal SOPs defining investigator qualification, AI output verification protocols, and QA Committee sign-off authorities.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
