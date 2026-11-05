# Northline RCA – REST API & Integration Specification
**Protocol**: HTTP/1.1 / JSON / Server-Sent Events (SSE)  
**Base URL**: `/api`  
**Authentication**: Prepared for Bearer JWT token header (`Authorization: Bearer <token>`)  

---

## 1. System & Health Endpoints

### `GET /api/health`
Inspects database connectivity and LLM operational readiness.
* **Response `200 OK` (or `503 Service Unavailable` if database offline)**:
```json
{
  "status": "ok",
  "database": "ok",
  "model": "llama-3.3-70b-versatile",
  "llm_configured": true
}
```

---

## 2. Executive Dashboard & Metrics Endpoints

### `GET /api/dashboard/stats`
Computes live quality metrics, risk breakdowns, and recent investigations from database records.
* **Response `200 OK`**:
```json
{
  "kpis": {
    "total_investigations": 12,
    "open_deviations": 5,
    "in_progress": 3,
    "pending_capas": 8,
    "overdue_capas": 1,
    "closed_investigations": 7,
    "total_capas": 16,
    "capa_completion_rate": 50.0,
    "avg_closure_time_days": 14.2
  },
  "charts": {
    "severity_distribution": [
      { "label": "Critical", "count": 2, "color": "#dc2626" },
      { "label": "Major", "count": 6, "color": "#d97706" },
      { "label": "Minor", "count": 3, "color": "#2563eb" },
      { "label": "Unclassified", "count": 1, "color": "#64748b" }
    ],
    "category_distribution": [
      { "category": "Machine", "count": 8 },
      { "category": "Method", "count": 5 },
      { "category": "Man", "count": 3 },
      { "category": "Material", "count": 2 },
      { "category": "Measurement", "count": 1 },
      { "category": "Environment", "count": 1 }
    ],
    "status_distribution": [
      { "status": "Draft", "count": 2 },
      { "status": "Under Investigation", "count": 3 },
      { "status": "Pending QA", "count": 0 },
      { "status": "Approved / Closed", "count": 7 }
    ]
  },
  "recent_investigations": [
    {
      "id": "e674a2b9-...",
      "deviation_number": "DEV-2026-1184",
      "title": "RS-3 and assay OOS after a crystallization excursion",
      "product_name": "Atorvastatin calcium",
      "batch_lot": "ATV-CA-26-0142",
      "severity": "major",
      "status": "under_investigation",
      "created_at": "2026-03-12T14:40:00Z",
      "updated_at": "2026-03-14T09:15:00Z"
    }
  ]
}
```

### `GET /api/dashboard/capas`
Returns centralized cross-investigation list of all Corrective and Preventive Actions.
* **Response `200 OK`**:
```json
{
  "capas": [
    {
      "investigation_id": "e674a2b9-...",
      "deviation_number": "DEV-2026-1184",
      "product_name": "Atorvastatin calcium",
      "batch_lot": "ATV-CA-26-0142",
      "capa_id": "capa_01",
      "capa_type": "corrective",
      "description": "Overhaul control valve V-17 positioner diaphragm",
      "rationale": "Restores temperature ramp control tolerance",
      "owner": "Engineering - Instrumentation",
      "due_date": "2026-04-15",
      "effectiveness_check": "Perform 3 consecutive thermal ramp simulations",
      "status": "in_progress",
      "ai_suggested": true,
      "confirmed": true
    }
  ]
}
```

### `GET /api/dashboard/evidence`
Returns all verified source document records and AI-detected documentation gaps.
* **Response `200 OK`**:
```json
{
  "evidence": [
    {
      "id": "src_e674a2b9",
      "investigation_id": "e674a2b9-...",
      "deviation_number": "DEV-2026-1184",
      "product_name": "Atorvastatin calcium",
      "title": "DEV-2026-1184_atorvastatin_impurity.pdf",
      "kind": "pdf",
      "filename": "DEV-2026-1184_atorvastatin_impurity.pdf",
      "sender": "",
      "subject": "",
      "char_count": 4820,
      "excerpt": "During crystallization hold, jacket temperature rose from 8°C to 17°C...",
      "status": "Verified Source Record",
      "classification": "Supporting"
    },
    {
      "id": "gap_gap_01",
      "investigation_id": "e674a2b9-...",
      "deviation_number": "DEV-2026-1184",
      "product_name": "Atorvastatin calcium",
      "title": "Gap: Calibration Certificate for Temperature Sensor RTD-03",
      "kind": "evidence_gap",
      "filename": "Instrumentation Calibration Management System",
      "sender": "AI Evidence Audit",
      "subject": "Confirm RTD accuracy and rule out drift",
      "char_count": 0,
      "excerpt": "Why it matters: Confirm RTD accuracy...",
      "status": "Evidence Missing",
      "classification": "Gap Requirement"
    }
  ]
}
```

---

## 3. Ingestion & AI Reasoning Endpoints

### `POST /api/ingest`
Accepts multipart form uploads (`file`: PDF/EML/TXT) and pasted text, normalizing content into a unified source string.
* **Request (`multipart/form-data`)**:
  - `file`: Binary file upload (max 15 MB)
  - `text`: String text content
  - `kind`: Optional format hint (`pdf`, `email`, `text`)
* **Response `200 OK`**:
```json
{
  "source_text": "Normalized source narrative...",
  "source_kind": "pdf",
  "filename": "DEV-2026-1184.pdf",
  "subject": "",
  "sender": "",
  "characters": 3450
}
```

### `POST /api/ai/analyze`
Executes synchronous analysis through the LangGraph pipeline or pre-validated knowledge engine.
* **Request (`application/json`)**:
```json
{
  "source_text": "Deviation narrative...",
  "source_kind": "text",
  "filename": "incident.txt",
  "subject": "",
  "sender": "",
  "allow_demo": true
}
```
* **Response `200 OK`**:
```json
{
  "record": { /* Full RCARecord schema */ },
  "changed_paths": ["deviation_number", "title", "root_causes", ...],
  "assistant_message": "Analysis completed. Every cause remains a hypothesis...",
  "mode": "live" // or "demo"
}
```

### `POST /api/ai/analyze/stream`
Streams real-time Server-Sent Events (SSE) emitting phase updates as each LangGraph node processes, followed by the finalized investigation record.
* **Event Stream**:
```
event: phase
data: {"node": "extract_fields"}

event: phase
data: {"node": "investigate"}

event: phase
data: {"node": "identify_causes"}

event: phase
data: {"node": "evidence_gaps"}

event: phase
data: {"node": "recommend_capa"}

event: result
data: {
  "record": { ... },
  "changed_paths": [ ... ],
  "assistant_message": "..."
}
```

### `POST /api/ai/chat`
Context-aware copilot endpoint for conversational inquiries, section redrafting, and field modifications.
* **Request (`application/json`)**:
```json
{
  "message": "Why is this deviation classified as major?",
  "history": [ { "role": "user", "content": "..." } ],
  "record": { /* Current RCARecord state */ },
  "allow_demo": true
}
```
* **Response `200 OK`**:
```json
{
  "record": { /* Updated RCARecord state */ },
  "changed_paths": [],
  "assistant_message": "Under ICH Q9, this deviation is classified as Major because..."
}
```

---

## 4. Investigation Persistence & Audit Trail Endpoints

### `GET /api/investigations`
Lists investigation summaries with server-side filtering, search, and pagination.
* **Query Parameters**:
  - `q`: Search keyword matching deviation ID, title, product name, or batch
  - `status`: Filter by status (`draft`, `under_investigation`, `pending_qa`, `approved`, `closed`)
  - `severity`: Filter by severity (`critical`, `major`, `minor`, `unknown`)
  - `limit`: Number of records (default 100)
  - `offset`: Pagination offset (default 0)
* **Response `200 OK`**:
```json
{
  "investigations": [
    {
      "id": "e674a2b9-...",
      "deviation_number": "DEV-2026-1184",
      "title": "RS-3 OOS after crystallization excursion",
      "product_name": "Atorvastatin calcium",
      "batch_lot": "ATV-CA-26-0142",
      "severity": "major",
      "status": "under_investigation",
      "updated_at": "2026-03-14T09:15:00Z"
    }
  ]
}
```

### `POST /api/investigations`
Creates and persists a new investigation document. Automatically appends a `create` audit event.
* **Request (`application/json`)**:
```json
{
  "record": { /* Full RCARecord */ },
  "actor": "Dr. S. Kulkarni"
}
```

### `GET /api/investigations/{id}`
Retrieves complete envelope with the full `RCARecord` document, creation timestamp, and update timestamp.

### `PUT /api/investigations/{id}`
Updates an existing investigation. Calculates path-level changes and logs an append-only audit event.

### `DELETE /api/investigations/{id}`
Deletes an investigation and cascades deletion to associated audit events (`204 No Content`).

### `GET /api/investigations/{id}/audit`
Retrieves chronological, append-only 21 CFR Part 11 audit events with actor attribution and field-level diffs.
* **Response `200 OK`**:
```json
{
  "events": [
    {
      "id": 1,
      "investigation_id": "e674a2b9-...",
      "created_at": "2026-03-12T14:40:00Z",
      "actor": "R. Menon",
      "action": "create",
      "summary": "Investigation created",
      "changes": []
    },
    {
      "id": 2,
      "investigation_id": "e674a2b9-...",
      "created_at": "2026-03-12T15:20:00Z",
      "actor": "Dr. S. Kulkarni",
      "action": "update",
      "summary": "Investigation updated",
      "changes": [
        { "path": "batch_lot.value", "before": "ATV-CA-26-0142", "after": "ATV-CA-26-0142-R" }
      ]
    }
  ]
}
```

---

## 5. Sample Document Repository Endpoints

### `GET /api/samples`
Returns catalog of pre-validated demo incident documents.

### `GET /api/samples/{filename}`
Streams the binary sample file (`application/pdf`, `message/rfc822`, `text/plain`).

