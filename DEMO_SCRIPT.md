# Northline RCA – Complete Demonstration Script & Walkthrough
**Target Audience**: Pharmaceutical Quality Assurance (QA) Directors, QC Lab Managers, Process Safety Engineers, GxP Auditors  
**Scenario Focus**: Active Pharmaceutical Ingredient (API) Manufacturing Deviations (Crystallization Excursions, In-Process LOD Out-of-Specification, and Material Staging Near Misses)  

---

## Demonstration Overview

This script guides an evaluator through the end-to-end capabilities of Northline RCA, demonstrating how AI transforms unstructured manufacturing deviations into evidence-grounded, ICH Q7/Q9 compliant investigations without black-box automation.

The walkthrough highlights:
1. Multi-format incident document intake (PDF, EML, Shift Notes).
2. Automated extraction with deterministic evidence quote grounding.
3. Interactive 5 Whys causal branching.
4. Interactive 6M Ishikawa fishbone diagram with plausibility toggles.
5. Root cause hypothesis grading (`UNVERIFIED HYPOTHESIS` vs `INVESTIGATOR-CONFIRMED ROOT CAUSE`).
6. AI evidence gap detection.
7. Corrective vs Preventive Action (CAPA) tracking.
8. Context-aware AI Copilot.
9. 21 CFR Part 11 append-only audit trail logging.

---

## Step 1: Launch Application & Inspect Quality Dashboard

1. Navigate to `http://localhost:41731/` in your browser.
2. **Observe**:
   - The **Executive Quality Dashboard** loads with live database KPIs: Total Investigations, Open Deviations, Active Investigations, Pending CAPAs, Overdue CAPAs, and Closed Investigations.
   - Analytical visualizations display real-time **Severity Breakdown** (ICH Q9 Risk Levels), **Root Cause 6M Distribution**, and the **Investigation Lifecycle Funnel**.
   - Notice the persistent enterprise shell: Left sidebar with 8 quality modules and top navigation displaying facility context (`Northline QA Operations / API Unit 3`), database health indicator, and active investigator identity.

---

## Step 2: Document Ingestion Studio (Phase 4)

1. Click **"New Ingestion"** in the left sidebar or the **"New AI Investigation"** button on the dashboard.
2. Under **"PRE-VALIDATED SAMPLE DOCUMENTS"**, click:
   - **`Deviation PDF`** (`DEV-2026-1184_atorvastatin_impurity.pdf`).
3. **Observe**:
   - The PDF document is automatically staged in the dropzone: `DEV-2026-1184_atorvastatin_impurity.pdf`.
4. Click **"Analyze with AI Engine"**.
5. **Observe**:
   - The real-time analysis pipeline executes through each stage:
     - `1. Read the file` -> `2. Prepare the source` -> `3. Extract the deviation` -> `4. 5 Whys and fishbone` -> `5. Root causes` -> `6. Evidence gaps` -> `7. CAPA proposals` -> `8. Fill the record`.
   - The **Structured Entity Verification Summary** displays extracted values with confidence badges:
     - Deviation ID: `DEV-2026-1184`
     - Product: `Atorvastatin Calcium Trihydrate API`
     - Batch/Lot: `ATV-CA-26-0142`
     - Severity: `Major`
     - Process Stage: `Stage 4: Final Anti-Solvent Crystallization and Isolation`
     - Immediate Actions: Batch quarantined under QA tamper-evident seal; Crystallizer CR-300 tagged out.
6. Click **"Open in Investigation Workspace →"**.

---

## Step 3: Investigation Workspace & Causal Reasoning (Phase 5)

1. In the **Workspace**, observe the sub-header showing the active deviation number, title, and open hypothesis counter.
2. Scroll to **Section 01 (Identification)** & **Section 02 (Product & Process)**:
   - Notice that extracted facts display an **"AI extracted"** badge.
   - Click **"Accept extracted facts"** at the top of Section 01. The badges immediately transition to **"Accepted"** (Green).
3. Scroll to **Section 05 (Investigation - 5 Whys & Ishikawa Fishbone)**:
   - **5 Whys Analysis**:
     - *Why 1*: "Why did batch ATV-CA-26-0142 fail RS-3 impurity specification?" -> "Accelerated thermal degradation occurred during the crystallization hold phase..."
     - *Why 2*: "The reactor jacket temperature elevated from 8°C to 17°C and remained uncooled for 46 minutes."
     - *Why 3*: "Cooling-water control valve V-17 was oscillating (hunting)..."
     - *Why 4*: "Electro-pneumatic positioner diaphragm suffered moisture contamination..."
     - *Why 5*: "Desiccant dryer auto-drain in Utilities room seized in closed position."
     - Notice the **"Quote verified in source"** grounding badge on each step.
   - **Interactive Fishbone Diagram**:
     - Click on the **"Machine"** bone rib or the **"Machine"** legend pill.
     - Observe the **Category Inspection Panel** update to show contributing factors:
       - *Factor*: "Chilled water pneumatic control valve V-17 hunting due to positioner air fouling".
       - Toggle the **"Active Contributor (Plausible)"** checkbox to test plausibility toggles.
       - Click **"+ Add Cause to Machine"** to demonstrate investigator extensibility.

---

## Step 4: Root Cause Hypotheses & Human Confirmation (Phase 5C & 10)

1. Scroll to **Section 06 (Root causes and contributing factors)**.
2. Note the clear regulatory distinction:
   - Hypotheses that have not been accepted are marked **`AI SUGGESTED`** with a **`Quote verified in source`** grounding check.
3. Click **"Confirm as root cause"** on the primary cause:
   - *"Loss of crystallization jacket thermal control caused by pneumatic hunting of valve V-17..."*
4. **Observe**:
   - The badge transitions immediately to **`CONFIRMED`** (Green).
   - The open suggestion counter in the workspace sub-header decrements.
   - The human-in-the-loop requirement is enforced: the AI suggested the hypothesis, but only the qualified investigator confirms it as an official root cause.

---

## Step 5: Evidence Gaps & CAPA Formulation (Phases 7 & 8)

1. Scroll to **Section 07 (Evidence still missing)**:
   - Observe AI-detected evidence gaps:
     - Continuous SCADA trend chart for reactor CR-300 loop TIC-301.
     - Calibration certificate for temperature sensor RTD-03.
     - Preventive maintenance log for utilities air compressor auto-drain.
   - Each gap explains *why it matters* and *where to get it*.
2. Scroll to **Section 08 (Corrective and preventive actions)**:
   - **Corrective Actions**: Immediate mechanical overhaul of valve V-17, diaphragm replacement, auto-drain replacement, instrument air purge.
   - **Preventive Actions**: Reconfiguring SCADA alarm delay from 60 minutes to 5 minutes with audible escalation; weekly preventative blowdown checks.
   - Notice the assigned owner roles (`Engineering - Instrumentation`, `Utilities Maintenance`), due dates, and defined **Effectiveness Checks**.

---

## Step 6: Contextual AI Copilot Interaction (Phase 9)

1. Look at the right-hand **AI Copilot** panel.
2. Under **"INVESTIGATIVE INQUIRIES"**, click the prompt chip:
   - *"Why is this deviation classified as Major or Critical?"*
3. Click the send arrow button.
4. **Observe**:
   - The Copilot analyzes the active record under ICH Q9 principles:
     - Explains that Critical is reserved for patient exposure or uncontained distribution.
     - Confirms that because batch ATV-CA-26-0142 is contained within quarantine, a Major classification is appropriate.
5. Try another quick prompt:
   - *"What additional documents should I collect to resolve gaps?"*
   - Copilot summarizes the specific historian logs and calibration certificates required.

---

## Step 7: Saving the Record & 21 CFR Part 11 Audit Trail (Phases 11 & 12)

1. Click **"Save Changes"** in the top navigation or press `Ctrl + S`.
2. Notice the confirmation note: `✓ Record committed to PostgreSQL audit trail`.
3. In the left sidebar, click **"Audit Trail"**.
4. **Observe**:
   - Chronological, immutable audit event entries.
   - Shows actor attribution (`Investigator`), action (`create` / `update`), and exact field-level diffs showing before and after values for every changed attribute.
5. In the left sidebar, click **"Overview"** (Dashboard):
   - Notice that the KPI cards have updated dynamically: Open Deviations, Active Investigations, and 6M Distribution now reflect the newly saved investigation.
6. Click **"CAPA Management"** in the left sidebar:
   - Observe that the corrective and preventive actions from the investigation now appear in the cross-facility CAPA tracking table with due date monitoring.

---

## Step 8: Multi-Scenario Testing

To demonstrate adaptability across diverse API manufacturing operations:
1. Click **"New Ingestion"**.
2. Select **`Shift note`** (`shift_note_metformin_lod.txt`):
   - Ingest and analyze Metformin HCl Loss-on-Drying (LOD) tray drying failure.
   - Observe Method branch focus and re-drying CAPA proposals.
3. Select **`QA email`** (`email_omeprazole_near_miss.eml`):
   - Ingest and analyze Omeprazole solvent staging near miss.
   - Observe Material/Method staging focus and warehouse barcode scanner interlock CAPA.

