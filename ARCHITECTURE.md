# Northline RCA – System Architecture & Technical Specification
**Module**: AI-Assisted Root Cause Analysis for Pharmaceutical Active Pharmaceutical Ingredient (API) Manufacturing  
**Standard Compliance**: ICH Q7 (GMP for APIs), ICH Q9 (Quality Risk Management), ICH Q10 (Pharmaceutical Quality System), 21 CFR Part 11 / EU Annex 11 (Electronic Records & Signatures)  

---

## 1. System Overview & Architectural Topology

Northline RCA is an enterprise quality intelligence platform architected to accelerate root cause analysis (RCA) and corrective/preventive action (CAPA) formulation for chemical synthesis and API manufacturing operations.

```
+----------------------------------------------------------------------------------------------------+
|                                    PRESENTATION LAYER (SPA)                                        |
|  React 19 + Redux Toolkit + TypeScript + Vite                                                      |
|  - Enterprise App Shell (Persistent Navigation, Breadcrumbs, Tenant & Case Status)                 |
|  - Executive Quality Dashboard (Real-time KPIs, 6M Distribution, Pipeline Funnels)                 |
|  - Ingestion Studio (Multi-document parsing, PDF/EML/TXT, Extraction Verification)                 |
|  - Investigation Hub (Interactive 5 Whys, Clickable 6M Ishikawa SVG, Grounded Hypotheses)          |
|  - Quality Governance (CAPA Management, Evidence Library, Append-Only Audit Trail)                 |
+----------------------------------------------------------------------------------------------------+
                                      |                                  ^
                        REST (JSON)   |                                  |  SSE Event Stream
                                      v                                  |
+----------------------------------------------------------------------------------------------------+
|                                   APPLICATION BACKEND LAYER                                        |
|  FastAPI + Pydantic V2 (Python 3.11+)                                                              |
|  - Ingestion & Extraction Normalizer (pypdf, email.policy, RFC 822 decoding)                       |
|  - State Mutation Gateway (Allow-listed dictionary operations, strict path authorization)          |
|  - Audit Differencing Engine (Path-level JSON walk diff, ALCOA+ contemporaneous logging)           |
|  - Persistence Repository Layer (SQLAlchemy 2.0 ORM, Relational Indexes, Transaction Management)   |
+----------------------------------------------------------------------------------------------------+
                     |                                                    |
                     v                                                    v
+-------------------------------------------+      +-------------------------------------------------+
|          AI & REASONING LAYER             |      |             PERSISTENCE LAYER                   |
|  LangGraph 1.2+ & Groq (Llama-3.3-70B)    |      |  PostgreSQL 16 / SQLite Engine                  |
|  - Node Pipeline (Extract -> Investigate  |      |  - `investigations`: Primary JSON document      |
|    -> Causes -> Gaps -> CAPA -> Assemble) |      |    with indexed relational columns:             |
|  - Deterministic Grounding Checker        |      |    (deviation_number, severity, status, product)|
|    (Quote & token verification)           |      |  - `audit_events`: Append-only audit trail     |
|  - Pre-validated Pharmaceutical Engine    |      |    with sequence ID, actor, timestamp, and diff |
|    (Deterministic demonstration fallback) |      +-------------------------------------------------+
+-------------------------------------------+
```

---

## 2. Core Modules & Component Architecture

### 2.1 Enterprise Presentation Layer
* **Application Shell (`Layout.tsx`, `Sidebar.tsx`, `TopNav.tsx`)**:
  - Consistent layout providing left sidebar navigation across 8 quality modules: Overview, Investigations, Ingestion Studio, Workspace, CAPA Management, Evidence Library, Audit Trail, and Settings.
  - Top navigation bar featuring tenant context ("Northline QA Operations / API Unit 3"), real-time database and LLM status indicator, active case badge, global deviation search, and ALCOA+ investigator attribution.
* **Executive Quality Dashboard (`DashboardView.tsx`)**:
  - 6 KPI metric cards computed directly from actual database records: Total Investigations, Open Deviations, Active Investigations, Pending CAPAs, Overdue CAPAs, and Closed Investigations.
  - Analytical visualizations for ICH Q9 Severity Classification, 6M Ishikawa Manufacturing Category distribution, and Investigation Lifecycle status funnels.
  - Filterable, searchable, and paginated recent investigations directory.
* **Document Ingestion Studio (`IngestionView.tsx`)**:
  - Drag-and-drop ingestion supporting multi-format files: PDF (formal deviation reports), EML (QC alert emails), and plain text / shift logs.
  - 1-click pre-validated sample document loader (Atorvastatin OOS, Metformin LOD, Omeprazole Near Miss).
  - Real-time SSE streaming stepper visualizing the LangGraph node progression.
  - Post-extraction entity verification cards displaying extracted values, confidence levels, and source grounding badges.
* **Investigation Workspace & Interactive Fishbone (`Workspace.tsx`, `Fishbone.tsx`, `InvestigationSection.tsx`)**:
  - Structured form sections covering Identification, Product & Process Parameters, Narrative, Impact Assessment, 5 Whys Causal Chains, 6M Fishbone, Probable Root Causes, Evidence Gaps, CAPA Proposals, and QA Electronic Sign-off.
  - Interactive Ishikawa diagram allowing investigators to click any of the 6 manufacturing bones (Man, Machine, Method, Material, Measurement, Environment), view evaluated factors, toggle plausibility, and add new causes directly onto specific ribs.
* **Contextual AI Copilot (`AssistantPanel.tsx`)**:
  - Context-aware copilot maintaining the active investigation record, chat history, and source document excerpts.
  - 6 pre-built quick prompt chips for common GMP investigator inquiries (e.g. classification justification, evidence support check, gap collection recommendations, preventive action suggestions).

---

## 3. LangGraph Workflow & Reasoning Pipeline

The core analytical pipeline is orchestrated as a directed cyclic graph with structured state transitions:

```
               +-------------------+
               |  prepare_source   | -> Truncates to 18,000 characters; normalizes whitespace
               +-------------------+
                         |
                         v
               +-------------------+
               |  extract_fields   | -> Deterministic extraction (temp=0.0)
               +-------------------+
                         |
         [Valid?] -------+------- [Empty?]
            |                        |
            v                        v (Retry once with targeted re-prompt)
   +-----------------+      +-----------------+
   |   investigate   | <--- |  extract_fields |
   +-----------------+
            |
            v
   +-----------------+
   | identify_causes | -> Generates 1-3 root causes & 1-4 contributing factors
   +-----------------+
            |
            v
   +-----------------+
   |  evidence_gaps  | -> Identifies missing documentation (max 6 gaps)
   +-----------------+
            |
            v
   +-----------------+
   | recommend_capa  | -> Proposes Corrective & Preventive actions (7-90 days due date)
   +-----------------+
            |
            v
   +-----------------+
   |    assemble     | -> Python assembly; marks fields origin=ai, confirmed=False
   +-----------------+
            |
            v
   +-----------------+
   | refresh_ground  | -> Deterministic quote and token verification against source
   +-----------------+
```

### Deterministic Evidence Grounding Algorithm (`app.services.grounding`)
To prevent hallucinated findings from being treated as facts:
1. Exact substring match: Checks if the evidence quote exists literally in the source document.
2. Numeric verification: Extracts all numeric values (temperatures, percentages, durations, valve numbers). If any number in the quote is absent from the source, the quote is marked **ungrounded**.
3. Informative token overlap: Filters English and pharmaceutical stop-words. Computes token set intersection against the source tokens. Requires $\ge 3$ overlapping tokens and $\ge 45\%$ token density.
4. Unconfirmed hypotheses failing grounding are automatically down-weighted to `confidence="low"` and `evidence_supported=False`.

---

## 4. Dual Reasoning Architecture: Live Groq & Knowledge Engine Fallback

In compliance with Phase 15 execution rules, Northline RCA implements a dual-mode reasoning architecture:
1. **Live Inference Mode**: When `GROQ_API_KEY` is configured in `.env`, the system dispatches live calls to `llama-3.3-70b-versatile` through `ChatGroq` with schema-enforced structured outputs.
2. **Pre-validated Knowledge Engine Mode**: When running without an API key, the system transparently activates the deterministic Pharmaceutical Quality Intelligence Engine (`prevalidated.py`).
   - Grounded strictly in the three sample deviation scenarios and generic API incident narratives.
   - Distinctly and honestly labelled in the UI: `[DEMO MODE · Pre-validated Pharmaceutical Knowledge Engine]`.
   - Never spoofed as live LLM inference; clearly signals that outputs represent pre-validated domain intelligence.

---

## 5. Persistence, Concurrency & ALCOA+ Audit Trail

* **PostgreSQL / SQLite Dual Engine**:
  - Relational indexes on `deviation_number`, `status`, `severity`, `product_name`, `batch_lot`, and `updated_at`.
  - Primary document stored as a structured JSON object (`RCARecord`) preserving field metadata (`value`, `origin`, `confirmed`).
* **Append-Only Audit Trail (`AuditEvent`)**:
  - Automatically triggered upon every `create_investigation` and `update_investigation` call.
  - Recursive JSON tree difference algorithm (`diff_documents`) generating fine-grained path-level diffs (e.g. `batch_lot.value: "ATV-CA-26-0142" -> "ATV-CA-26-0142-R"`).
  - Actor attribution, action taxonomy (`create`, `update`, `status`, `approval`), and ISO 8601 UTC timestamps.

