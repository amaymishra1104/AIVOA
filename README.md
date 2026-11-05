# Northline RCA – AI-Powered Root Cause Analysis for Pharmaceutical API Manufacturing

Northline RCA is an enterprise-grade AI-assisted quality management workspace engineered for Active Pharmaceutical Ingredient (API) chemical synthesis and manufacturing operations. It complies with **ICH Q7** (GMP for APIs), **ICH Q9** (Quality Risk Management), **ICH Q10** (Pharmaceutical Quality System), and **21 CFR Part 11 / EU Annex 11** data integrity principles.

An investigator uploads or pastes an incident narrative (PDF deviation report, supervisor shift note, or QC email alert). A LangGraph workflow analyzes the source, populates structured quality entities with deterministic quote verification, and drafts a 5 Whys causal chain, 6M Ishikawa fishbone diagram, root cause hypotheses, missing evidence gaps, and Corrective/Preventive Action (CAPA) proposals.

> [!IMPORTANT]
> **Human-in-the-Loop Regulatory Principle**: AI outputs remain unconfirmed hypotheses until an authorized, qualified quality investigator formally reviews and confirms them against verified evidence. The system strictly separates extracted source facts, AI-generated hypotheses, and investigator-confirmed findings.

---

## Key Enterprise Modules

1. **Executive Quality Dashboard (`/`)**:
   - Live KPI cards: Total Investigations, Open Deviations, Active Investigations, Pending CAPAs, Overdue CAPAs, and Closed Investigations.
   - Real-time analytics: ICH Q9 Severity Classification, 6M Ishikawa Manufacturing Category Distribution, and Investigation Lifecycle Funnel.
   - Searchable, filterable (Severity/Status), and paginated recent investigations directory.
2. **AI Document Ingestion Studio (`/ingest`)**:
   - Multi-format ingestion supporting PDF, EML (RFC 822 email), and plain text logs up to 15 MB.
   - 1-click sample document loader with real-time SSE progress streaming.
   - Post-extraction entity verification cards showing extracted values, confidence levels, and source citation status.
3. **Investigation Workspace & Interactive Fishbone (`/workspace`, `/workspace/:id`)**:
   - Structured 9-section form: Identification, Product & Process, Narrative, Impact Assessment, 5 Whys, 6M Fishbone, Root Causes, Evidence Gaps, and CAPA.
   - Clickable SVG Ishikawa diagram allowing investigators to inspect each of the 6 manufacturing bones (Man, Machine, Method, Material, Measurement, Environment), toggle plausibility, and add contributing factors.
4. **Centralized CAPA Management Hub (`/capa`)**:
   - Cross-facility table separating Corrective Actions (immediate containment) from Preventive Actions (systemic recurrence prevention).
   - Owner roles, target completion dates, overdue alerts, and defined Effectiveness Verification methods.
5. **Evidence Library & Gap Detection (`/evidence`)**:
   - Central repository of verified GMP source records and AI-detected documentation gaps.
6. **21 CFR Part 11 Audit Trail (`/audit`)**:
   - Chronological, append-only audit trail logging user attributions, actions (`create`, `update`, `status`, `approval`), timestamps, and fine-grained field-level before/after diffs.
7. **Context-Aware AI Copilot**:
   - Integrated Copilot panel with quick prompt chips for common investigative inquiries (severity justification, evidence grounding checks, gap resolution, preventive action advice, and QA summary generation).
8. **Dual Reasoning Engine (Live Groq + Pre-validated Knowledge Engine)**:
   - When `GROQ_API_KEY` is provided, live LLM inference is performed via `llama-3.3-70b-versatile`.
   - When no API key is provided, the platform transparently activates the deterministic Pharmaceutical Quality Intelligence Engine, clearly labelled as `[DEMO MODE]` without mock spoofing.

---

## Demonstration Scenarios (`samples/`)

| Sample File | Scenario & Causal Mechanism |
| :--- | :--- |
| `samples/DEV-2026-1184_atorvastatin_impurity.pdf` | **Atorvastatin Calcium Trihydrate API** (Batch ATV-CA-26-0142). Out-of-Specification: Related substance RS-3 (0.18% vs limit NMT 0.15%) and low assay (98.2%) after crystallizer CR-300 jacket temperature rose from 8°C to 17°C for 46 minutes due to pneumatic hunting of valve V-17 caused by moisture in the clean instrument air header. |
| `samples/shift_note_metformin_lod.txt` | **Metformin Hydrochloride API** (Batch MFH-26-2033). Supervisor note reporting Loss-on-Drying (LOD) moisture failure (0.42% vs limit NMT 0.30%) caused by premature cycle termination at 8 hours based on an unverified shift handover note. |
| `samples/email_omeprazole_near_miss.eml` | **Omeprazole Sulfide Intermediate** (Batch OMP-INT-26-077). Near miss where Methanol drums (MD-4418) were staged at reactor R-102 instead of Isopropanol (IP-8821) after a barcode scanner battery died and manual transfer was bypassed. Caught prior to charge. |

---

## Technical Stack

* **Frontend**: React 19, Redux Toolkit, TypeScript, Vite, React Router 7.
* **Backend**: Python 3.11+, FastAPI, Pydantic V2, SQLAlchemy 2.0, pypdf, python-multipart.
* **AI & Orchestration**: LangGraph, ChatGroq (`llama-3.3-70b-versatile`), deterministic token quote grounding.
* **Persistence**: PostgreSQL 16 (or local SQLite fallback).

---

## Quickstart & Local Installation

### Prerequisites
* Python 3.11+
* Node.js v18+ (Node v20/v22 recommended) and npm
* Docker (optional, for local PostgreSQL container)

### 1. Configure Environment
Copy the sample environment file in the repository root:
```bash
cp .env.example .env
```
Edit `.env` (optional):
```ini
# Optional: Live Groq API key (if blank, honest Demo Mode activates automatically)
GROQ_API_KEY=

# Default Groq model
GROQ_MODEL=llama-3.3-70b-versatile

# PostgreSQL connection string (or leave default for local Postgres, or use SQLite)
DATABASE_URL=postgresql+psycopg://rca:rca@localhost:54329/rca
```

> [!NOTE]
> If PostgreSQL / Docker is not running, the application and test suites seamlessly use SQLite fallback:
> `DATABASE_URL=sqlite+pysqlite:///rca.db`

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```
*(Or `cd backend && pip install -r requirements.txt`)*

### 3. Start PostgreSQL (Optional via Docker)
```bash
docker compose up -d
```
*Port 54329 is mapped to container port 5432 to avoid clashing with standard Postgres installations.*

### 4. Start the FastAPI Backend
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8077 --reload
```
*API interactive documentation will be available at `http://127.0.0.1:8077/docs`.*

### 5. Start the React Frontend
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
*Open `http://localhost:41731/` in your browser.*

---

## Running Automated Tests

Run the complete backend test suite:
```bash
cd backend
pytest -v
```
*34 automated tests verify health, API routes, document ingestion, 5 Whys, fishbone operations, evidence grounding verification, search & filters, dashboard statistics, and demo mode.*

Run frontend TypeScript verification and production build:
```bash
cd frontend
npm run build
npm run lint
```

---

## Complete Project Documentation

* [Codebase Audit Report](CODEBASE_AUDIT.md)
* [System Implementation Plan](IMPLEMENTATION_PLAN.md)
* [Technical Architecture Specification](ARCHITECTURE.md)
* [REST API Documentation](API_DOCUMENTATION.md)
* [Comprehensive Test Report](TEST_REPORT.md)
* [Demonstration Walkthrough Script](DEMO_SCRIPT.md)
