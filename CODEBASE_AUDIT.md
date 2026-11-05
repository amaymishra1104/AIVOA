# Northline RCA – Comprehensive Codebase Audit
**Module**: AI-Powered Root Cause Analysis for Pharmaceutical API Manufacturing  
**Date**: November 2026  
**Auditor**: Senior AI Product Engineer & Staff Full-Stack Architect  

---

## Executive Summary

Northline RCA is an AI-assisted root cause analysis platform engineered for active pharmaceutical ingredient (API) manufacturing quality operations (ICH Q7 / Q9 / Q10). A systematic audit of the existing repository was performed spanning the frontend React/Redux architecture, FastAPI backend services, LangGraph workflow execution, database persistence, and automated test suites.

The core prototype demonstrates solid conceptual foundations: a LangGraph-orchestrated multi-stage reasoning pipeline, structured Pydantic schemas, evidence grounding verification, and an audit trail mechanism. However, significant architectural gaps, compatibility issues, and missing enterprise features prevent it from functioning as a true pharmaceutical quality management system (QMS).

---

## 1. What Is Implemented Correctly

### Backend & AI Architecture
* **LangGraph Orchestrated Reasoning**: Multi-step pipeline (`extract_fields` → `investigate` → `identify_causes` → `evidence_gaps` → `recommend_capa` → `assemble`) separating fact extraction from investigative reasoning.
* **Evidence Grounding Verification (`app.services.grounding`)**: Deterministic quote and n-gram overlap validator checking whether AI-generated evidence citations exist in the ingested document.
* **State Immutability & Safe Operations (`app.services.operations`)**: Allow-listed dictionary mutations preventing unconstrained LLM writes to the database document.
* **Append-Only Audit Trail (`AuditEvent`)**: Automatic document diffing via `diff_documents` logging user actions, timestamps, and path-level changes.
* **Sample Data Suite**: Three realistic API manufacturing deviation documents:
  - `DEV-2026-1184_atorvastatin_impurity.pdf`: Critical/major crystallization temperature excursion resulting in RS-3 impurity Out-of-Specification (OOS).
  - `shift_note_metformin_lod.txt`: Metformin HCl fluidized bed/tray dryer Loss-on-Drying (LOD) failure.
  - `email_omeprazole_near_miss.eml`: Staging error involving methanol vs isopropanol for omeprazole intermediate.

### Frontend
* **Redux Toolkit Architecture**: Standardized slices for `investigationSlice`, `assistantSlice`, and `librarySlice` with typed action creators and async thunks.
* **Server-Sent Events (SSE) Streaming**: Reactive client receiving real-time phase updates (`extract_fields`, `investigate`, etc.) during long-running analysis workflows.
* **Review Badges & Highlighting**: Visual indicators differentiating AI-extracted values from user-confirmed facts.

---

## 2. What Was Broken & Fixed

1. **Python 3.12 Generic Syntax Incompatibility**:
   - *File*: `backend/app/services/llm.py`
   - *Issue*: Used PEP 695 type parameter syntax `def complete_structured[T: BaseModel](...)` and `def _coerce[T: BaseModel](...)`. When running on Python 3.11 (the host environment), this threw a critical `SyntaxError: expected '('` during test collection and module import.
   - *Status*: **FIXED**. Refactored to standard `typing.TypeVar("T", bound=BaseModel)` compatible with Python 3.10+.
2. **Missing Backend Dependencies in Environment**:
   - `langchain-groq` and `psycopg[binary]` were absent from the active Python environment, failing test imports.
   - *Status*: **FIXED**. Installed and verified with 27 passing tests.
3. **Missing Node Modules in Frontend**:
   - Frontend had not been built or initialized (`node_modules` missing).
   - *Status*: **FIXED**. Ran clean install, verified TypeScript compilation (`tsc -b`) and Vite production build.

---

## 3. What Is Partially Implemented

1. **Investigation Library & History**:
   - Currently implemented only as slide-over drawer panels (`LibraryDrawer`, `AuditDrawer`) within the investigation workspace.
   - Lacks search, filtering by severity/status/date, sorting, or pagination.
2. **5 Whys Analysis**:
   - Implemented as a simple linear card stack. Lacks dynamic branching, investigator commentary, and per-step verification controls.
3. **Fishbone (Ishikawa) Diagram**:
   - Implemented as a read-only SVG render (`Fishbone.tsx`). It does not allow investigators to click individual bones, reassign causes to other 6M categories, or link missing evidence directly to fishbone ribs.
4. **CAPA Management**:
   - Simple list inside the form with basic type and status attributes. Lacks an enterprise CAPA tracking view with effectiveness check deadlines, assignees, and cross-investigation visibility.
5. **AI Assistant / Chat**:
   - Basic chat panel executing single-operation plans. It lacks quick-action investigative prompts (e.g., "Suggest preventive actions", "Verify critical classification rationale", "Detect contradictions") and does not present a reviewable diff modal before applying LLM edits.

---

## 4. What Is Completely Missing

1. **Enterprise Layout & Navigation Shell (Phase 2)**:
   - No persistent left sidebar with main modules: *Overview / Dashboard*, *Investigations Directory*, *New Investigation*, *Workspace*, *CAPA Management*, *Evidence Library*, *Audit Trail*, and *Settings*.
   - No enterprise top bar with global search, workspace context, and user avatar.
2. **Advanced Analytics & Executive Dashboard (Phase 3)**:
   - No metrics for Total Investigations, Open Deviations, Active Investigations, Pending CAPAs, Overdue CAPAs, or Closed Cases.
   - No charts for investigations over time, 6M category distribution, CAPA completion rate, or average closure time.
3. **Dedicated Evidence Management Module (Phase 7)**:
   - No central repository for uploading and linking multi-document evidence (BMRs, equipment logs, calibration certificates, HPLC chromatograms, cleaning logs).
   - Missing document gap detection with direct "Upload evidence to resolve gap" action.
4. **Honest Demonstration Mode / Fallback for Groq (Phase 15)**:
   - If `GROQ_API_KEY` is unset or rate-limited, the system currently errors out with a 503 `llm_not_configured` or 502 failure.
   - Lacks an honest, clearly labeled Pharmaceutical Knowledge Engine demo mode that processes the sample files without spoofing live LLM generation.
5. **Investigation Export & GMP Reporting**:
   - No mechanism to export a clean, printable FDA/EU GMP compliant investigation summary (PDF or printable view).

---

## 5. What Should Be Optimized

1. **Database Queries & Indexing**:
   - Add indexes for `severity`, `product_name`, and `batch_lot` on `Investigation`.
   - Add server-side search, filtering, and pagination on `/api/investigations`.
2. **AI Prompt Engineering & API Specificity**:
   - Deepen prompt domain knowledge for API manufacturing Unit Operations: crystallization, reaction kinetics, solvent washing, tray drying, micronization, HPLC assay, and residual solvents.
3. **Frontend Bundle & State Management**:
   - Split large view components into dedicated modules for Overview, Investigations, Workspace, CAPA, Evidence, and Audit.
   - Prevent unnecessary re-renders by selecting narrow slices of state.

---

## 6. What Should Be Redesigned

1. **Visual Language & Design System**:
   - Replace the warm beige/paper palette (`#fbf7f0`, serif fonts) with a crisp, authoritative pharmaceutical enterprise design: slate and neutral backgrounds (`#f8fafc`, `#ffffff`), deep teal/navy accents (`#0f766e`, `#0f172a`), refined typography, high information density, and polished status badges.
2. **Primary Application Workflow**:
   - Transition from a single-screen form with drawers into a full multi-view enterprise workspace with unified routing (`/`, `/investigations`, `/workspace`, `/capa`, `/evidence`, `/audit`, `/settings`).

