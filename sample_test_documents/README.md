# SYNTHETIC TEST DOCUMENTS: NORTHLINE RCA

> [!NOTE]
> **NOTICE: SYNTHETIC TEST DATA ONLY**  
> All documents in this directory represent realistic synthetic pharmaceutical manufacturing deviation scenarios designed for automated AI extraction, 5 Whys causal analysis, Ishikawa 6M fishbone generation, evidence gap identification, and CAPA formulation testing.  
> **NO REAL PATIENT, CLINICAL, OR PROPRIETARY COMMERCIAL DATA IS CONTAINED IN THESE FILES.**

---

## Catalog of Test Documents

### 1. Atorvastatin Calcium Trihydrate OOS (PDF)
- **File**: `DEV-2026-1184_atorvastatin_impurity.pdf`
- **Format**: Adobe PDF (2 Pages, 48,418 bytes)
- **Scenario**: Out-of-Specification (OOS) finished API event for related substance Impurity-D / RS-3 (0.18% vs limit NMT 0.15%) following a crystallizer jacket temperature spike (8°C to 17°C) caused by pneumatic hunting of valve V-17 from moisture in the clean instrument air header and actuator diaphragm rupture.
- **Frontend Safe**: Yes. Upload via drag-and-drop dropzone or select from sample catalog.

### 2. Metformin Hydrochloride LOD Failure (TXT)
- **File**: `shift_note_metformin_lod.txt`
- **Format**: UTF-8 Plain Text (22 Lines, 2,141 bytes)
- **Scenario**: Supervisor shift handover note reporting Loss on Drying (LOD) moisture failure (0.42% vs limit NMT 0.30%) caused by premature cycle truncation at 4.5 hours by the bay operator and a choked air handler supply-air damper (40% open instead of 100%).
- **Frontend Safe**: Yes. Upload as `.txt` or paste directly into the incident narrative box.

### 3. Omeprazole Sulfide Intermediate Near Miss (EML)
- **File**: `email_omeprazole_near_miss.eml`
- **Format**: RFC-822 MIME Email Message (38 Lines, 2,396 bytes)
- **Scenario**: QA email alert detailing a solvent staging near-miss where Methanol (MD-4418) was staged instead of Ethanol (ED-2201) after an operator overrode a barcode scanner warning with supervisor credentials. Intercepted by the chemist during pre-charge line clearance check prior to reactor addition.
- **Frontend Safe**: Yes. Upload as `.eml` via drag-and-drop.

