# Northline RCA – Comprehensive Implementation Plan
**Objective**: Transform the Northline RCA prototype into an enterprise-grade AI-powered Root Cause Analysis platform for Pharmaceutical API Manufacturing.

---

## Architecture Overview

```
                                      +---------------------------------------------+
                                      |          Enterprise React Frontend          |
                                      |  (Redux Toolkit, Enterprise Design System)  |
                                      +---------------------------------------------+
                                                             |
                        +------------------------------------+------------------------------------+
                        |                                    |                                    |
            +-----------------------+            +-----------------------+            +-----------------------+
            |  Dashboard & Metrics  |            | Investigation Hub     |            | CAPA & Evidence Mgmt  |
            |  - Real-time KPIs     |            |  - Multi-doc Ingest   |            |  - Centralized CAPAs  |
            |  - 6M Distribution    |            |  - 5 Whys Interactive |            |  - Evidence Library   |
            |  - Closure Trends     |            |  - Ishikawa Fishbone  |            |  - Gap Resolution     |
            +-----------------------+            +-----------------------+            +-----------------------+
                                                             |
                                           REST API & SSE Event Stream
                                                             |
                                      +---------------------------------------------+
                                      |              FastAPI Backend                |
                                      |       (Python 3.11+, Pydantic V2)           |
                                      +---------------------------------------------+
                                                             |
                        +------------------------------------+------------------------------------+
                        |                                    |                                    |
            +-----------------------+            +-----------------------+            +-----------------------+
            | LangGraph RCA Engine  |            | Knowledge Engine Mode |            | Persistence & Audit   |
            |  - Document Extract   |            |  - Pre-validated API  |            |  - PostgreSQL/SQLite  |
            |  - 5 Whys & 6M Graph  |            |    Manufacturing demo |            |  - Append-only Audit  |
            |  - Grounding Checker  |            |  - Transparent status |            |  - Relational indexes |
            +-----------------------+            +-----------------------+            +-----------------------+
```

---

## Detailed Implementation Workstreams

### Workstream 1: Enterprise Shell & Design System (Phases 2 & 13)
* **Design Tokens & Theme**:
  - Implement a pharmaceutical enterprise palette: pure whites, slate surfaces (`#f8fafc`, `#f1f5f9`), slate border rules (`#e2e8f0`), deep slate typography (`#0f172a`), clinical teal primaries (`#0d9488`, `#0f766e`), warning amber (`#d97706`), danger crimson (`#dc2626`), and success emerald (`#16a34a`).
* **Sidebar Navigation (`Sidebar.tsx`)**:
  - Persistent left navigation with clean icons and indicators:
    1. *Dashboard / Overview* (`/`)
    2. *Investigations* (`/investigations`)
    3. *New Investigation Ingestion* (`/workspace/new`)
    4. *Active Workspace* (`/workspace/:id`)
    5. *CAPA Management* (`/capa`)
    6. *Evidence Library* (`/evidence`)
    7. *Audit Trail* (`/audit`)
    8. *Settings & System Status* (`/settings`)
* **Top Navigation Bar (`TopNav.tsx`)**:
  - Organization title ("Northline QA / API Operations - Unit 3"), breadcrumbs, global investigation quick-search, live connection status (PostgreSQL + Groq / Demo mode), and active user profile.

---

### Workstream 2: Advanced Dashboard & Metrics Engine (Phase 3)
* **Backend Analytics Endpoint (`GET /api/dashboard/stats`)**:
  - Compute live metrics from the database:
    - Total Investigations count
    - Open Deviations count (`draft`, `under_investigation`, `pending_qa`)
    - Investigations in Progress
    - Pending CAPAs (`proposed`, `accepted`, `in_progress`)
    - Overdue CAPAs (calculated against `due_date`)
    - Closed / Approved Investigations
    - Severity breakdown (`critical`, `major`, `minor`, `unknown`)
    - 6M Fishbone category distribution
    - Average days to closure
* **Frontend Dashboard (`DashboardView.tsx`)**:
  - 6 KPI metric cards with trends and status badges.
  - Interactive SVG analytics charts:
    - Severity classification breakdown.
    - Root Cause 6M distribution (Man, Machine, Method, Material, Measurement, Environment).
    - Status pipeline funnel.
  - Recent Investigations Table:
    - Search by ID, Title, Batch, Product.
    - Filter by Severity and Status.
    - Sorting by Updated Date, Severity.
    - One-click navigation into investigation workspace.

---

### Workstream 3: Advanced AI Document Ingestion & Extraction (Phase 4)
* **Multi-Format Ingestion**:
  - Support PDF, EML, TXT, and pasted narrative.
  - Handle multi-document extraction with document type auto-detection.
* **Granular Extraction Metadata**:
  - Enhance `ExtractedDeviation` and frontend representation with explicit evidence quotes, source references, confidence levels (`high`, `medium`, `low`), and verification statuses (`AI Extracted`, `Investigator Verified`).
* **Honest Demonstration Mode & Live Groq Switching**:
  - Provide a deterministic, pre-validated Pharmaceutical Quality Intelligence demo fallback for the 3 sample files (Atorvastatin OOS, Metformin LOD, Omeprazole Near Miss) when Groq API key is not configured or rate-limited.
  - Transparently display status: `Live Groq (llama-3.3-70b-versatile)` vs `Pre-validated Demo Mode`.

---

### Workstream 4: Advanced RCA Engine: 5 Whys, Interactive Fishbone & Hypotheses (Phases 5 & 6)
* **5 Whys Analysis (`FiveWhysView.tsx`)**:
  - Interactive steps: add, delete, reorder, edit questions and answers.
  - Explicit evidence quote field for each why step with live grounding verification indicator (`Grounded in source` vs `Hypothesis / External`).
  - Investigator comments field on each step.
* **Interactive Ishikawa Fishbone (`InteractiveFishbone.tsx`)**:
  - Fully clickable SVG diagram mapping all 6 categories (Man, Machine, Method, Material, Measurement, Environment).
  - Add contributing causes directly onto specific ribs.
  - Highlight ribs with evidence gaps or ungrounded hypotheses in visual amber.
* **Root Cause Hypotheses Categorization**:
  - Visual distinction between:
    - `UNVERIFIED HYPOTHESIS` (AI-generated, lacking verified evidence)
    - `EVIDENCE-SUPPORTED HYPOTHESIS` (Deterministic evidence quote matched in source)
    - `INVESTIGATOR-CONFIRMED ROOT CAUSE` (Explicitly signed off by qualified human reviewer)
  - Investigator Confirmation Modal requiring rationale and confirmation name.

---

### Workstream 5: Evidence Library & Gap Management (Phase 7)
* **Central Evidence Management (`EvidenceView.tsx`)**:
  - Central registry of all evidence artifacts linked to investigations: BMR excerpts, calibration records, maintenance work orders, HPLC/GC chromatograms, SOP references, training logs.
  - Classification: Supporting vs Contradictory.
* **AI Evidence Gap Detection**:
  - Display AI-detected evidence gaps with scientific rationale.
  - Interactive "Resolve Gap" action allowing upload of supplementary evidence documents to close gaps and update hypothesis confidence.

---

### Workstream 6: Enterprise CAPA Management (Phase 8)
* **Centralized CAPA Dashboard (`CapaView.tsx`)**:
  - Cross-investigation table of all corrective and preventive actions.
  - Clear separation of Corrective Actions (immediate containment/remediation) vs Preventive Actions (systemic recurrence prevention).
  - Fields: CAPA ID, Related Deviation, Type, Description, Scientific Rationale, Owner Role, Due Date, Effectiveness Check Method, Status (`Proposed`, `Accepted`, `In Progress`, `Completed`, `Effectiveness Verified`).
  - Status transition controls and overdue highlighting.

---

### Workstream 7: Contextual AI Copilot & Review Workflow (Phases 9 & 10)
* **Context-Aware Copilot**:
  - Suggested quick prompts for pharmaceutical investigators:
    - *"Why is this deviation classified as Major/Critical?"*
    - *"What evidence supports the primary root cause?"*
    - *"What additional documents should be retrieved from Quality Control?"*
    - *"Detect any contradictions between the narrative and the fishbone."*
    - *"Suggest stronger preventive actions for recurrence prevention."*
* **Human-in-the-Loop Diff Modal**:
  - Before applying any multi-field AI modifications, display a clear side-by-side diff modal with Accept / Reject controls to maintain data integrity (ALCOA+).

---

### Workstream 8: Database, Compliance & Testing (Phases 11, 12, 16, 17)
* **Backend Database Enhancements**:
  - Add dashboard statistics calculation in `repository.py`.
  - Add indexes for rapid search and filtering.
  - Provide automated tests verifying dashboard stats, sample ingestion, evidence grounding, CAPA filtering, and audit trail integrity.
* **Documentation Deliverables**:
  - `CODEBASE_AUDIT.md` (Completed)
  - `IMPLEMENTATION_PLAN.md` (This document)
  - `ARCHITECTURE.md`
  - `API_DOCUMENTATION.md`
  - `TEST_REPORT.md`
  - `DEMO_SCRIPT.md`
  - `README.md`

