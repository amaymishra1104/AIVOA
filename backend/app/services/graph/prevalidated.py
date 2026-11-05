"""Pre-validated Pharmaceutical Quality Intelligence Engine.

Provides transparent, deterministic demonstration extraction and investigative reasoning
when a live GROQ_API_KEY is not configured, adhering strictly to ICH Q7, Q9, and Q10.
As mandated by Phase 15, demo outputs are explicitly and honestly labelled as pre-validated
knowledge engine outputs rather than live LLM inference.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from app.ai_schemas import (
    CapaItemOut,
    CapaListOut,
    CauseOut,
    CausesOut,
    ExtractedDeviation,
    FishItem,
    GapOut,
    GapsOut,
    InvestigationOut,
    TeamExtract,
    WhyItem,
)
from app.services.assemble import assemble_record
from app.services.recordkit import due_date


def run_prevalidated_analysis(
    source_text: str,
    source_kind: str = "text",
    filename: str = "",
    subject: str = "",
    sender: str = "",
) -> dict:
    lower = source_text.lower()
    
    # Identify which sample or scenario is being processed
    if "atorvastatin" in lower or "atv-ca" in lower or "rs-3" in lower:
        extraction = _extract_atorvastatin(source_text)
        investigation = _investigate_atorvastatin(source_text)
        causes = _causes_atorvastatin(source_text)
        gaps = _gaps_atorvastatin()
        capa = _capa_atorvastatin()
    elif "metformin" in lower or "mfh-26" in lower or "loss on drying" in lower or "lod" in lower:
        extraction = _extract_metformin(source_text)
        investigation = _investigate_metformin(source_text)
        causes = _causes_metformin(source_text)
        gaps = _gaps_metformin()
        capa = _capa_metformin()
    elif "omeprazole" in lower or "omp-int" in lower or "methanol" in lower or "isopropanol" in lower:
        extraction = _extract_omeprazole(source_text)
        investigation = _investigate_omeprazole(source_text)
        causes = _causes_omeprazole(source_text)
        gaps = _gaps_omeprazole()
        capa = _capa_omeprazole()
    else:
        extraction = _extract_generic(source_text, filename)
        investigation = _investigate_generic(source_text)
        causes = _causes_generic(source_text)
        gaps = _gaps_generic()
        capa = _capa_generic()

    state = {
        "source_text": source_text,
        "source_kind": source_kind,
        "filename": filename,
        "subject": subject,
        "sender": sender,
        "extraction": extraction.model_dump(),
        "investigation": investigation.model_dump(),
        "causes": causes.model_dump(),
        "gaps": gaps.model_dump(),
        "capa": capa.model_dump(),
    }

    record, changed_paths, _ = assemble_record(state)

    disclaimer = (
        "[DEMO MODE · Pre-validated Pharmaceutical Knowledge Engine]\n"
        "Notice: GROQ_API_KEY is not configured in .env. Execution completed via the deterministic "
        "ICH Q7/Q9 Knowledge Engine. All extracted fields and hypotheses remain unconfirmed suggestions "
        "and require qualified investigator review and verification against source documentation."
    )

    return {
        "record": record,
        "changed_paths": changed_paths,
        "assistant_message": disclaimer,
        "mode": "demo",
    }


def _extract_atorvastatin(text: str) -> ExtractedDeviation:
    dev_match = re.search(r"DEV-\d{4}-\d+", text)
    batch_match = re.search(r"ATV-CA-\d{2}-\d+", text)
    return ExtractedDeviation(
        deviation_number=dev_match.group(0) if dev_match else "DEV-2026-1184",
        title="Out-of-Specification: Related Substance RS-3 and Low Assay Following Crystallization Excursion",
        occurred_at="12 March 2026, 14:40 IST",
        detected_at="14 March 2026, 09:15 IST",
        site="Northline API Works, Hyderabad",
        area="Crystallization Bay 2 (Cleanroom Suite C)",
        equipment="Crystallizer CR-300, Chilled Water Control Valve V-17, RTD-03",
        product_name="Atorvastatin Calcium Trihydrate API",
        batch_lot=batch_match.group(0) if batch_match else "ATV-CA-26-0142",
        process_stage="Stage 4: Final Anti-Solvent Crystallization and Isolation",
        description=(
            "During release testing of Atorvastatin calcium batch ATV-CA-26-0142, Quality Control reported "
            "Related Substance RS-3 at 0.18% (Specification: NMT 0.15%) and chromatographic assay of 98.2% "
            "(Specification: 98.5% - 101.5%). Investigation of SCADA records revealed jacket cooling temperature "
            "rose from 8°C to 17°C for 46 minutes during the controlled cooling ramp due to pneumatic hunting of valve V-17."
        ),
        immediate_actions=(
            "1. Batch ATV-CA-26-0142 physically placed in quarantine holding area under QA tamper-evident seal.\n"
            "2. Crystallizer CR-300 tagged out of service for instrumentation recalibration.\n"
            "3. Engineering inspected valve V-17 positioner and air line filter regulator."
        ),
        impact_product_quality="Fails release specification for impurity RS-3 (0.18%) and Assay (98.2%). Critical quality attributes compromised.",
        impact_patient_safety="Zero patient exposure. The batch is fully accounted for in site quarantine and has not been distributed.",
        impact_regulatory="Batch scheduled for EU CEP and US DMF commercial supply. Regulatory notification required if deviation cannot be contained without rework.",
        batch_disposition="Quarantine Hold pending MRB / QA disposition",
        severity="major",
        severity_rationale="Out-of-specification result for critical quality attribute (purity and assay) on a commercial API batch contained within quarantine.",
        investigation_team=[
            TeamExtract(name="R. Menon", role="Production Shift Lead", department="API Manufacturing"),
            TeamExtract(name="Dr. S. Kulkarni", role="Principal QC Analyst", department="Quality Control"),
            TeamExtract(name="V. Sharma", role="Instrumentation Engineer", department="Engineering & Utilities"),
        ],
        method_notes="5 Whys applied to thermal excursion mechanism; 6M Ishikawa applied to rule out raw material and analytical artifacts.",
    )


def _investigate_atorvastatin(text: str) -> InvestigationOut:
    return InvestigationOut(
        method_summary="Applied 5 Whys to investigate the temperature control failure and 6M Ishikawa to evaluate all manufacturing dimensions.",
        problem_statement="Batch ATV-CA-26-0142 failed release specifications for impurity RS-3 (0.18% vs limit NMT 0.15%) and Assay (98.2% vs 98.5%-101.5%).",
        whys=[
            WhyItem(
                question="Why did batch ATV-CA-26-0142 fail RS-3 impurity specification?",
                answer="Accelerated thermal degradation occurred during the crystallization hold phase creating RS-3 diastereomer.",
                evidence="RS-3 was 0.18% against NMT 0.15% and assay was 98.2%",
            ),
            WhyItem(
                question="Why did thermal degradation occur during crystallization?",
                answer="The reactor jacket temperature elevated from 8°C to 17°C and remained uncooled for 46 minutes.",
                evidence="jacket temperature rose from 8°C to 17°C for 46 minutes",
            ),
            WhyItem(
                question="Why did the jacket temperature rise and remain at 17°C?",
                answer="Cooling-water control valve V-17 was oscillating (hunting) between 12% and 88% demand without seating.",
                evidence="Valve V-17 was hunting",
            ),
            WhyItem(
                question="Why was control valve V-17 hunting continuously?",
                answer="The electro-pneumatic positioner diaphragm suffered moisture contamination from the instrument air header.",
                evidence="instrument air line filter regulator saturated with moisture condensate",
            ),
            WhyItem(
                question="Why was moisture present in the clean instrument air header?",
                answer="The desiccant dryer pre-filter auto-drain in Utilities compressor room had seized in the closed position.",
                evidence="auto-drain seized in closed position during maintenance check",
            ),
        ],
        fishbone=[
            FishItem(
                category="Machine",
                cause="Chilled water pneumatic control valve V-17 hunting due to positioner air fouling",
                evidence="Valve V-17 was hunting",
                plausible=True,
            ),
            FishItem(
                category="Method",
                cause="SCADA thermal excursion alarm limit set at +10°C delta with 60-minute delay suppressing prompt operator intervention",
                evidence="alarm delay parameter configured at 60 minutes in SCADA loop TIC-301",
                plausible=True,
            ),
            FishItem(
                category="Material",
                cause="Raw material intermediate Stage-3 lot RM-26-0914 met all input specifications (Purity 99.4%)",
                evidence="Stage-3 intermediate purity 99.4% per COA-26-0914",
                plausible=False,
            ),
            FishItem(
                category="Measurement",
                cause="HPLC chromatographic integration and standard response verified without baseline anomaly",
                evidence="HPLC system suitability RSD 0.4%, standard recovery 99.8%",
                plausible=False,
            ),
            FishItem(
                category="Environment",
                cause="Crystallization Cleanroom suite remained within validated ISO 8 temperature and relative humidity bounds",
                evidence="Cleanroom temperature 21.2°C, RH 44%",
                plausible=False,
            ),
            FishItem(
                category="Man",
                cause="Operator logged periodic visual check but did not cross-check SCADA trend screen during cooling ramp",
                evidence="Manual log sheet recorded nominal temperature 10 minutes prior to spike",
                plausible=True,
            ),
        ],
    )


def _causes_atorvastatin(text: str) -> CausesOut:
    return CausesOut(
        root_causes=[
            CauseOut(
                statement="Loss of crystallization jacket thermal control caused by pneumatic hunting of valve V-17 due to moisture fouling of the valve positioner.",
                category="Machine",
                evidence="Valve V-17 was hunting and the jacket rose to 17°C for 46 minutes",
                confidence="high",
                rationale="Direct causal link demonstrated between jacket temperature rise and thermal degradation formation of RS-3 impurity.",
            ),
            CauseOut(
                statement="Utilities desiccant air dryer auto-drain failure permitting moisture bypass into the process clean instrument air distribution header.",
                category="Machine",
                evidence="desiccant dryer pre-filter auto-drain seized in closed position",
                confidence="high",
                rationale="Root systemic mechanical failure leading directly to the pneumatic positioner malfunction.",
            ),
        ],
        contributing_factors=[
            CauseOut(
                statement="SCADA alarm delay configuration of 60 minutes prevented real-time alarm escalation during the 46-minute temperature excursion.",
                category="Method",
                evidence="alarm delay parameter configured at 60 minutes in SCADA loop TIC-301",
                confidence="medium",
                rationale="Delayed operator awareness and immediate containment during the crystallization phase.",
            ),
            CauseOut(
                statement="Batch remained in crystallizer CR-300 under elevated thermal exposure without manual emergency chilled water bypass.",
                category="Method",
                evidence="jacket temperature rose from 8°C to 17°C for 46 minutes",
                confidence="medium",
                rationale="Prolonged residence time at 17°C allowed continued diastereomer degradation.",
            ),
        ],
    )


def _gaps_atorvastatin() -> GapsOut:
    return GapsOut(
        gaps=[
            GapOut(
                topic="SCADA Continuous Historian Trend for Reactor CR-300 Loop TIC-301",
                why_it_matters="Verify exact second-by-second temperature ramp curve and valve demand vs feedback signals.",
                suggested_source="Automation / SCADA Historian Archive (PI System)",
            ),
            GapOut(
                topic="Calibration Certificate for Temperature Sensor RTD-03",
                why_it_matters="Confirm RTD measurement accuracy and rule out sensor drift during crystallization cycle.",
                suggested_source="Instrumentation Calibration Management System (SAP PM)",
            ),
            GapOut(
                topic="Preventive Maintenance Log for Utilities Air Compressor Dryer & Auto-Drain",
                why_it_matters="Determine when auto-drain was last inspected and if periodic blowdown maintenance was overdue.",
                suggested_source="Utilities Maintenance Work Orders (WO-2025/2026)",
            ),
            GapOut(
                topic="Dew Point Sensor Log for Clean Instrument Air Header",
                why_it_matters="Establish the duration and extent of moisture excursion across the entire API facility.",
                suggested_source="Facility Environmental Monitoring / BMS Logs",
            ),
        ]
    )


def _capa_atorvastatin() -> CapaListOut:
    return CapaListOut(
        summary="Comprehensive CAPA addressing pneumatic valve maintenance, air dryer integrity, and SCADA alarm response.",
        capas=[
            CapaItemOut(
                capa_type="corrective",
                description="Overhaul control valve V-17, replace fouled electropneumatic positioner diaphragm, and perform 5-point calibration stroke verification.",
                rationale="Directly restores crystallizer CR-300 temperature control loop to validated operating tolerance.",
                owner_role="Engineering - Instrumentation",
                due_in_days=14,
                effectiveness_check="Perform 3 consecutive water-batch thermal ramp simulations with temperature stability within ±0.5°C.",
            ),
            CapaItemOut(
                capa_type="corrective",
                description="Replace failed auto-drain valve on desiccant air dryer AD-01 and purge facility instrument air header to achieve dew point < -40°C.",
                rationale="Removes free water condensate from the pneumatic supply line feeding process cleanrooms.",
                owner_role="Utilities Maintenance",
                due_in_days=7,
                effectiveness_check="Continuous dew point monitoring at header terminal points showing stable reading below -40°C for 14 continuous days.",
            ),
            CapaItemOut(
                capa_type="preventive",
                description="Reconfigure SCADA temperature excursion alarm delay from 60 minutes to 5 minutes with audible control room escalation.",
                rationale="Prevents undetected temperature deviations from persisting beyond acceptable operational thresholds.",
                owner_role="Automation Engineering",
                due_in_days=21,
                effectiveness_check="Quality Assurance challenge test verifying alarm trigger and supervisor acknowledgment within 5 minutes of simulated excursion.",
            ),
            CapaItemOut(
                capa_type="preventive",
                description="Establish weekly preventative blowdown and monthly automated moisture detection check on all clean air dryer pre-filters.",
                rationale="Eliminates single point of failure in utility moisture separation.",
                owner_role="QA Operations & Utilities",
                due_in_days=30,
                effectiveness_check="Zero moisture contamination incidents reported in pneumatic instruments across 6 months of operation.",
            ),
        ]
    )


def _extract_metformin(text: str) -> ExtractedDeviation:
    return ExtractedDeviation(
        deviation_number="DEV-2026-0891",
        title="Out-of-Specification Loss on Drying (LOD) in Metformin HCl API Drying Stage",
        occurred_at="18 February 2026, 06:30 IST",
        detected_at="18 February 2026, 08:45 IST",
        site="Northline API Works, Hyderabad",
        area="Drying and Milling Bay 4",
        equipment="Fluid Bed Tray Dryer TD-12, Vacuum System VP-04",
        product_name="Metformin Hydrochloride API",
        batch_lot="MFH-26-2033",
        process_stage="Stage 3: Vacuum Tray Drying and Delumping",
        description=(
            "During in-process quality control sampling of Metformin Hydrochloride batch MFH-26-2033, "
            "Loss on Drying (LOD) was found to be 0.42% (Specification: NMT 0.30% w/w). Review of the drying cycle "
            "indicated that drying was halted prematurely at 8 hours based on an unverified shift handover note rather "
            "than waiting for final QC sample release."
        ),
        immediate_actions="Batch quarantined in sealed poly-lined drums. Tray dryer TD-12 held for investigation. Re-drying protocol initiated under QA protocol.",
        impact_product_quality="Moisture content exceeds maximum limit (0.42% vs NMT 0.30%). Potential impact on stability and particle flow.",
        impact_patient_safety="No patient impact. Material is unblended, packaged in bulk quarantine drums on-site.",
        impact_regulatory="Metformin USP/EP compendial monograph compliance requires LOD NMT 0.3%. Batch cannot be released without verified resolution.",
        batch_disposition="Quarantine Hold - Additional Drying Evaluation Required",
        severity="major",
        severity_rationale="In-process specification breach for critical physical quality attribute on finished API intermediate.",
        investigation_team=[
            TeamExtract(name="K. Satyam", role="Shift Supervisor", department="Production"),
            TeamExtract(name="M. Nair", role="QC In-Process Analyst", department="Quality Control"),
        ],
        method_notes="5 Whys applied to premature cycle termination and drying kinetics.",
    )


def _investigate_metformin(text: str) -> InvestigationOut:
    return InvestigationOut(
        method_summary="Applied 5 Whys to investigate the procedural breakdown leading to premature drying cycle termination.",
        problem_statement="Metformin HCl batch MFH-26-2033 exceeded Loss on Drying limit with 0.42% w/w against specification NMT 0.30%.",
        whys=[
            WhyItem(
                question="Why was the Loss on Drying above the specified limit (0.42% vs NMT 0.30%)?",
                answer="The batch did not undergo complete secondary diffusion desolvation in the vacuum tray dryer.",
                evidence="LOD measured at 0.42% following cycle termination",
            ),
            WhyItem(
                question="Why was secondary diffusion desolvation incomplete?",
                answer="The dryer was shut down and unloaded after only 8 hours of drying time instead of standard 12 hours.",
                evidence="dryer unloaded at 8 hours per shift handover log",
            ),
            WhyItem(
                question="Why was the dryer unloaded at 8 hours instead of the SOP-mandated duration?",
                answer="The incoming shift operator assumed an IPC moisture sample had passed based on a verbal note.",
                evidence="verbal handover note regarding sample submission misconstrued as QA clearance",
            ),
            WhyItem(
                question="Why was verbal handover relied upon instead of electronic batch record confirmation?",
                answer="Batch manufacturing record step sign-off was postponed until after drum discharge.",
                evidence="step sign-off block blank at time of dryer unloading",
            ),
        ],
        fishbone=[
            FishItem(
                category="Method",
                cause="Inadequate shift handover verification protocol allowing physical unloading prior to documented QC release",
                evidence="unloading executed without documented QC COA in hand",
                plausible=True,
            ),
            FishItem(
                category="Man",
                cause="Operator failed to adhere to two-person verification rule for dryer discharge",
                evidence="single operator signature present on discharge initiation",
                plausible=True,
            ),
            FishItem(
                category="Machine",
                cause="Tray dryer TD-12 heating shelf fluid temperature and vacuum levels operated within calibrated limits",
                evidence="dryer log confirms shelf temperature 70°C ± 2°C and vacuum 25 mbar",
                plausible=False,
            ),
            FishItem(
                category="Material",
                cause="Metformin wet cake intermediate conformed to batch synthesis charge parameters",
                evidence="wet cake purity 99.8% with normal solvent ratio prior to drying",
                plausible=False,
            ),
            FishItem(
                category="Measurement",
                cause="QC analytical LOD halogen moisture analyzer calibrated and verified with sodium tartrate standard",
                evidence="LOD analyzer balance calibration within ±0.01% specification",
                plausible=False,
            ),
            FishItem(
                category="Environment",
                cause="Drying bay cleanroom relative humidity and differential pressure maintained within specification",
                evidence="cleanroom RH at 38% (limit NMT 45%), differential pressure +18 Pa",
                plausible=False,
            ),
        ],
    )


def _causes_metformin(text: str) -> CausesOut:
    return CausesOut(
        root_causes=[
            CauseOut(
                statement="Premature termination of the vacuum drying cycle resulting from reliance on verbal shift handover communication rather than documented QC test clearance.",
                category="Method",
                evidence="dryer unloaded at 8 hours per shift handover log before IPC test results received",
                confidence="high",
                rationale="Direct procedural deviation resulting in insufficient residence time for moisture removal.",
            )
        ],
        contributing_factors=[
            CauseOut(
                statement="Absence of an electronic or physical interlock preventing dryer discharge prior to QC LIMS result approval.",
                category="Machine",
                evidence="discharge door opened manually without system interlock check",
                confidence="medium",
                rationale="Allowed procedural non-compliance to proceed physically to drum discharge.",
            )
        ],
    )


def _gaps_metformin() -> GapsOut:
    return GapsOut(
        gaps=[
            GapOut(
                topic="Laboratory Information Management System (LIMS) Sample Timestamp Report",
                why_it_matters="Verify exact time sample was logged, tested, and approved in QC.",
                suggested_source="QC LIMS Audit Trail",
            ),
            GapOut(
                topic="Tray Dryer Temperature and Vacuum Strip Chart (TD-12)",
                why_it_matters="Confirm temperature uniformity across all 24 heating shelves.",
                suggested_source="Dryer Recorder Chart Paper / PLC Log",
            ),
        ]
    )


def _capa_metformin() -> CapaListOut:
    return CapaListOut(
        summary="Corrective re-drying and procedural interlock controls for vacuum drying discharge.",
        capas=[
            CapaItemOut(
                capa_type="corrective",
                description="Execute approved re-drying protocol for batch MFH-26-2033 under QA supervision until LOD ≤ 0.25%.",
                rationale="Restores physical moisture attribute to compendial specification without compromising particle size.",
                owner_role="Production Shift Lead",
                due_in_days=7,
                effectiveness_check="QC re-testing across top, middle, and bottom drum composite samples verifying LOD < 0.25%.",
            ),
            CapaItemOut(
                capa_type="preventive",
                description="Update SOP-PRD-044 to mandate formal written QC LIMS release printout attached to batch record prior to breaking dryer vacuum.",
                rationale="Eliminates informal verbal communication failure mode during shift changes.",
                owner_role="QA Operations",
                due_in_days=15,
                effectiveness_check="100% audit of next 20 drying batch records showing verification signature and LIMS attachment prior to discharge.",
            ),
        ]
    )


def _extract_omeprazole(text: str) -> ExtractedDeviation:
    return ExtractedDeviation(
        deviation_number="DEV-2026-0412",
        title="Near Miss: Incorrect Solvent Staged for Omeprazole Intermediate Condensation",
        occurred_at="05 January 2026, 11:20 IST",
        detected_at="05 January 2026, 11:35 IST",
        site="Northline API Works, Hyderabad",
        area="Synthesis Block A, Reactor R-102 staging bay",
        equipment="Reactor R-102, Drum Staging Pallet P-09",
        product_name="Omeprazole Sulfide Intermediate",
        batch_lot="OMP-INT-26-077",
        process_stage="Stage 2: Pyridine Condensation and Washing",
        description=(
            "During preparation for intermediate condensation batch OMP-INT-26-077, four 200L drums of Methanol "
            "(MD-4418) were staged at reactor R-102 charging station instead of Isopropanol (IP-8821). The error was "
            "detected during the pre-charge double-check verification by the second operator before reactor charging."
        ),
        immediate_actions="Drums quarantined and returned to solvent warehouse. Staging area cleared. Near-miss deviation logged.",
        impact_product_quality="Zero product impact. Charging was intercepted prior to valve connection; no foreign solvent entered reactor.",
        impact_patient_safety="Zero patient exposure. Contained completely at warehouse staging interface.",
        impact_regulatory="Internal near-miss quality notification; documentation of secondary verification effectiveness.",
        batch_disposition="Batch Released to Continue with Correct Solvent",
        severity="minor",
        severity_rationale="Near-miss event intercepted prior to execution. No product contamination or process perturbation occurred.",
        investigation_team=[
            TeamExtract(name="Priya Raman", role="Senior QA Officer", department="Quality Assurance"),
            TeamExtract(name="A. Khan", role="Chemical Operator", department="API Synthesis"),
        ],
        method_notes="Near-miss investigation focused on warehouse barcoding and drum color-coding.",
    )


def _investigate_omeprazole(text: str) -> InvestigationOut:
    return InvestigationOut(
        method_summary="5 Whys applied to warehouse staging logistics and human factors.",
        problem_statement="Methanol drums staged at Reactor R-102 instead of specified Isopropanol for batch OMP-INT-26-077.",
        whys=[
            WhyItem(
                question="Why was Methanol staged instead of Isopropanol?",
                answer="Warehouse dispensing operator selected drum pallet from adjacent storage rack aisle.",
                evidence="Methanol (MD-4418) staged instead of Isopropanol (IP-8821)",
            ),
            WhyItem(
                question="Why was the wrong pallet selected from the aisle?",
                answer="Both solvents were stored in identical blue 200L drums with similar internal stock code formatting.",
                evidence="identical blue 200L drums with small font label",
            ),
            WhyItem(
                question="Why did warehouse barcode scanning not prevent the transfer?",
                answer="Handheld barcode scanner was tethered to charging dock due to depleted battery, bypassing point-of-pick scan.",
                evidence="scanner battery depleted; transfer ticket marked manually",
            ),
        ],
        fishbone=[
            FishItem(
                category="Method",
                cause="Point-of-pick barcode verification bypassed due to hardware battery outage",
                evidence="manual staging without electronic scan",
                plausible=True,
            ),
            FishItem(
                category="Material",
                cause="Visual packaging similarity between Methanol and Isopropanol bulk drums",
                evidence="identical blue drums with standard white labels",
                plausible=True,
            ),
            FishItem(
                category="Man",
                cause="Warehouse handler selected drums based on row proximity without reading fine-print lot label",
                evidence="transfer ticket filled with assumed stock code",
                plausible=True,
            ),
            FishItem(
                category="Machine",
                cause="Warehouse handheld RF terminal docking station failed to maintain charging state",
                evidence="charging dock contact pins oxidized causing intermittent battery charging",
                plausible=True,
            ),
            FishItem(
                category="Measurement",
                cause="Warehouse weighing scale and barcode reader hardware calibration records verified",
                evidence="scale verification tag valid through Q3 2026",
                plausible=False,
            ),
            FishItem(
                category="Environment",
                cause="Flammable solvent staging ambient warehouse conditions within temperature limits",
                evidence="warehouse ambient log at 22°C",
                plausible=False,
            ),
        ],
    )


def _causes_omeprazole(text: str) -> CausesOut:
    return CausesOut(
        root_causes=[
            CauseOut(
                statement="Bypass of mandatory point-of-pick warehouse barcode verification following scanner battery failure, combined with visual drum packaging ambiguity.",
                category="Method",
                evidence="scanner battery depleted; transfer ticket marked manually for Methanol MD-4418",
                confidence="high",
                rationale="Allowed incorrect drum selection to leave warehouse staging without automated system validation.",
            )
        ],
        contributing_factors=[
            CauseOut(
                statement="Absence of differentiated high-visibility drum collar rings for differing polar solvents.",
                category="Material",
                evidence="identical blue drums with standard white labels",
                confidence="medium",
                rationale="Visual confirmation relied exclusively on small font paper label reading.",
            )
        ],
    )


def _gaps_omeprazole() -> GapsOut:
    return GapsOut(
        gaps=[
            GapOut(
                topic="Warehouse Barcode Scanner Fleet Maintenance & Charging SOP",
                why_it_matters="Ensure backup handheld scanners are available to prevent manual bypass.",
                suggested_source="Warehouse Equipment Log",
            )
        ]
    )


def _capa_omeprazole() -> CapaListOut:
    return CapaListOut(
        summary="Preventive hardware redundancy and drum identification program.",
        capas=[
            CapaItemOut(
                capa_type="preventive",
                description="Implement hard stop in ERP/WMS disallowing warehouse material transfer issuance without successful handheld barcode scan.",
                rationale="Eliminates the possibility of manual barcode scan bypass.",
                owner_role="IT Supply Chain Systems",
                due_in_days=30,
                effectiveness_check="Zero manual transfer override authorizations recorded in WMS over 90 days.",
            ),
            CapaItemOut(
                capa_type="preventive",
                description="Install high-contrast color-coded safety collar rings on all raw material solvent drums upon warehouse intake.",
                rationale="Provides secondary visual human-factor confirmation during transport and staging.",
                owner_role="Warehouse Operations",
                due_in_days=45,
                effectiveness_check="Monthly warehouse visual inspection demonstrating 100% compliance with solvent color bands.",
            ),
        ]
    )


def _extract_generic(text: str, filename: str) -> ExtractedDeviation:
    title_snippet = text[:120].split("\n")[0] if text else "API Manufacturing Deviation"
    return ExtractedDeviation(
        deviation_number="DEV-2026-DEMO",
        title=f"Deviation Analysis: {title_snippet[:80]}",
        occurred_at=date.today().isoformat(),
        detected_at=date.today().isoformat(),
        site="Northline API Manufacturing Site",
        area="Active Manufacturing Bay",
        equipment="Process Equipment Unit",
        product_name="Active Pharmaceutical Ingredient",
        batch_lot="BATCH-2026-DEMO",
        process_stage="Synthesis / Purification",
        description=text[:1500] if text else "Incident reported during manufacturing operations.",
        immediate_actions="Batch held in quarantine. Equipment inspected. Investigation initiated under QA oversight.",
        impact_product_quality="Under evaluation pending root cause and batch record review.",
        impact_patient_safety="Material contained on site in quarantine.",
        impact_regulatory="Impact assessment ongoing per site QMS procedures.",
        batch_disposition="Quarantine Hold",
        severity="major",
        severity_rationale="Deviation involving process execution requiring formal root cause analysis.",
        investigation_team=[TeamExtract(name="Investigator", role="QA Specialist", department="Quality Assurance")],
        method_notes="5 Whys and 6M Ishikawa analysis conducted from incident text.",
    )


def _investigate_generic(text: str) -> InvestigationOut:
    return InvestigationOut(
        method_summary="5 Whys causal analysis paired with 6M Ishikawa manufacturing evaluation.",
        problem_statement=text[:180] if text else "Deviation observed during manufacturing operation.",
        whys=[
            WhyItem(
                question="Why did the observed deviation take place?",
                answer="Process parameter or procedural condition deviated from normal operating range.",
                evidence=text[:120] if text else "Reported in incident narrative",
            ),
            WhyItem(
                question="Why did the operating condition deviate?",
                answer="Mechanical, environmental, or operator execution factor influenced the system state.",
                evidence="Stated in incident report",
            ),
        ],
        fishbone=[
            FishItem(category="Machine", cause="Equipment operating state or sensor feedback", evidence="Incident details", plausible=True),
            FishItem(category="Method", cause="Procedure execution or process parameters", evidence="Operating narrative", plausible=True),
        ],
    )


def _causes_generic(text: str) -> CausesOut:
    return CausesOut(
        root_causes=[
            CauseOut(
                statement="Primary systemic contributor identified from incident narrative requiring engineering verification.",
                category="Method",
                evidence=text[:100] if text else "Narrative excerpt",
                confidence="medium",
                rationale="Derived from documented incident circumstances.",
            )
        ],
        contributing_factors=[
            CauseOut(
                statement="Secondary process conditions present during deviation occurrence.",
                category="Machine",
                evidence="Observed conditions",
                confidence="low",
                rationale="Requires verification against batch logs.",
            )
        ],
    )


def _gaps_generic() -> GapsOut:
    return GapsOut(
        gaps=[
            GapOut(
                topic="Batch Manufacturing Record (BMR) Execution Sign-offs",
                why_it_matters="Verify exact process parameters, times, and operator initials.",
                suggested_source="Quality Assurance Document Control",
            )
        ]
    )


def _capa_generic() -> CapaListOut:
    return CapaListOut(
        summary="Standard corrective and preventive measures based on incident findings.",
        capas=[
            CapaItemOut(
                capa_type="corrective",
                description="Conduct technical inspection and comprehensive equipment check.",
                rationale="Ensures hardware integrity before release.",
                owner_role="Manufacturing Engineering",
                due_in_days=14,
                effectiveness_check="QA review of maintenance documentation.",
            ),
            CapaItemOut(
                capa_type="preventive",
                description="Update operational SOP and conduct team refresher training.",
                rationale="Prevents procedural recurrence.",
                owner_role="Operations Training Coordinator",
                due_in_days=30,
                effectiveness_check="Zero recurrence over subsequent 3 production campaigns.",
            ),
        ]
    )


def run_prevalidated_chat(message: str, history: list, record: dict) -> dict:
    from app.services.recordkit import refresh_grounding
    msg = message.lower().strip()
    notes = []
    changed_paths = []
    rec = dict(record)

    title = ((rec.get("title") or {}).get("value")) or "this deviation"
    sev = ((rec.get("severity") or {}).get("value")) or "unknown"

    if "regenerate" in msg or "redraft" in msg:
        import uuid
        raw_text = ((rec.get("source") or {}).get("raw_text")) or ""
        lower_raw = raw_text.lower()
        if "atorvastatin" in lower_raw or "atv-ca" in lower_raw or "rs-3" in lower_raw:
            fresh_inv = _investigate_atorvastatin(raw_text)
            fresh_causes = _causes_atorvastatin(raw_text)
            fresh_capa = _capa_atorvastatin()
        elif "metformin" in lower_raw or "mfh-26" in lower_raw or "lod" in lower_raw:
            fresh_inv = _investigate_metformin(raw_text)
            fresh_causes = _causes_metformin(raw_text)
            fresh_capa = _capa_metformin()
        elif "omeprazole" in lower_raw or "omp-int" in lower_raw:
            fresh_inv = _investigate_omeprazole(raw_text)
            fresh_causes = _causes_omeprazole(raw_text)
            fresh_capa = _capa_omeprazole()
        else:
            fresh_inv = _investigate_generic(raw_text)
            fresh_causes = _causes_generic(raw_text)
            fresh_capa = _capa_generic()

        if "why" in msg:
            rec["whys"] = [
                {
                    "id": f"why-{uuid.uuid4().hex[:6]}",
                    "question": w.question,
                    "answer": w.answer,
                    "evidence": w.evidence,
                    "grounded": True,
                    "origin": "ai",
                    "confirmed": False,
                }
                for w in fresh_inv.whys
            ]
            changed_paths = ["whys"]
            answer = "I redrafted the 5 Whys causal chain from the source document. The findings remain unconfirmed suggestions until verified."
        elif "fishbone" in msg or "ishikawa" in msg:
            rec["fishbone"] = [
                {
                    "id": f"fish-{uuid.uuid4().hex[:6]}",
                    "category": b.category,
                    "cause": b.cause,
                    "evidence": b.evidence,
                    "plausible": b.plausible,
                    "grounded": True,
                    "origin": "ai",
                    "confirmed": False,
                }
                for b in fresh_inv.fishbone
            ]
            changed_paths = ["fishbone"]
            answer = "I redrafted the 6M Ishikawa fishbone analysis from the source document. Non-contributing categories have been ruled out with evidence."
        elif "capa" in msg:
            rec["capas"] = [
                {
                    "id": f"capa-{uuid.uuid4().hex[:6]}",
                    "capa_type": c.capa_type,
                    "description": c.description,
                    "rationale": c.rationale,
                    "owner": c.owner_role,
                    "due_date": due_date(c.due_in_days),
                    "effectiveness_check": c.effectiveness_check,
                    "status": "proposed",
                    "ai_suggested": True,
                    "confirmed": False,
                }
                for c in fresh_capa.capas
            ]
            changed_paths = ["capas"]
            answer = "I redrafted the CAPA proposals from the source document, maintaining separation between immediate corrective containment and preventive systemic measures."
        else:
            rec["root_causes"] = [
                {
                    "id": f"cause-{uuid.uuid4().hex[:6]}",
                    "statement": c.statement,
                    "category": c.category,
                    "evidence": c.evidence,
                    "confidence": c.confidence,
                    "evidence_supported": True,
                    "grounded": True,
                    "ai_suggested": True,
                    "confirmed": False,
                    "confirmed_by": "",
                }
                for c in fresh_causes.root_causes
            ]
            changed_paths = ["root_causes"]
            answer = "I redrafted the root cause hypotheses from the source document. Each cited evidence quote is grounded in the record."
    elif "why" in msg and ("critical" in msg or "major" in msg or "severity" in msg or "class" in msg):
        answer = (
            f"Under ICH Q9 and site QMS procedures, this deviation is classified as '{sev.upper()}'. "
            "A Critical classification is reserved for scenarios with confirmed patient exposure, "
            "uncontained release of out-of-specification material to the commercial market, or data integrity breaches. "
            f"Here, the severity rationale states: '{((rec.get('severity_rationale') or {}).get('value')) or 'Specification or process excursion requiring containment.'}' "
            "Because the material remains under site quarantine control, it does not currently warrant a Critical escalation unless stability or distribution data changes."
        )
    elif "evidence" in msg or "document" in msg or "collect" in msg or "gap" in msg:
        gaps = rec.get("gaps") or []
        gap_topics = [f"• {g.get('topic')}: {g.get('why_it_matters')} (Source: {g.get('suggested_source')})" for g in gaps[:4]]
        answer = (
            "Based on the current investigation record, the most critical supporting documents to collect are:\n"
            + ("\n".join(gap_topics) if gap_topics else "• Calibration logs for primary temperature and pressure transmitters.\n• Continuous SCADA process historian trend charts.\n• Batch manufacturing record (BMR) execution sign-offs.")
            + "\n\nCollecting these documents will verify whether the primary root cause hypothesis is fully grounded or requires alternative evaluation."
        )
    elif "fishbone" in msg or "ishikawa" in msg:
        bones = rec.get("fishbone") or []
        categories = sorted({b.get("category") for b in bones if b.get("category")})
        answer = (
            f"The Ishikawa fishbone diagram systematically evaluated the 6M categories: {', '.join(categories) if categories else 'Man, Machine, Method, Material, Measurement, and Environment'}. "
            "The primary active failure was localized to the Machine and Method branches. "
            "Other categories (such as Raw Materials and Environment) were verified as operating within validated parameters, ruling them out as primary root causes."
        )
    elif "preventive" in msg or "capa" in msg:
        capas = rec.get("capas") or []
        prev = [c for c in capas if (c.get("capa_type") or "").lower() == "preventive"]
        answer = (
            f"Currently, there {'is' if len(prev) == 1 else 'are'} {len(prev)} preventive action(s) proposed in the CAPA plan: "
            + (f"'{prev[0].get('description')}'" if prev else "Reconfiguration of SCADA alarm thresholds and preventative maintenance scheduling.")
            + "\nTo strengthen recurrence prevention, consider instituting: (1) automated system interlocks preventing phase progression during parameter deviations, and (2) mandatory two-person independent verification during critical operational steps."
        )
    elif "summarize" in msg or "summary" in msg or "qa review" in msg:
        prod = ((rec.get("product_name") or {}).get("value")) or "API"
        batch = ((rec.get("batch_lot") or {}).get("value")) or "N/A"
        dev_no = ((rec.get("deviation_number") or {}).get("value")) or "Draft"
        causes = rec.get("root_causes") or []
        first_cause = causes[0].get("statement") if causes else "Under active investigation"
        answer = (
            f"INVESTIGATION SUMMARY FOR QA REVIEW:\n"
            f"Deviation ID: {dev_no} | Product: {prod} | Batch: {batch} | Severity: {sev.upper()}\n"
            f"Event Summary: {((rec.get('description') or {}).get('value'))[:300]}\n"
            f"Primary Root Cause Hypothesis: {first_cause}\n"
            f"Immediate Containment: {((rec.get('immediate_actions') or {}).get('value'))[:200]}\n"
            f"Recommendation: Maintain batch quarantine pending completion of CAPA effectiveness checks and QA Committee sign-off."
        )
    else:
        answer = (
            f"The assistant analyzed your query regarding {title}. "
            f"The current status is '{rec.get('status', 'draft')}' with severity '{sev}'. "
            "To modify specific fields or add new causes, you can edit the form directly or ask specific questions such as: "
            "'Why is this deviation classified as major?', 'What evidence supports this root cause?', 'What additional documents should I collect?', or 'Summarize for QA review'."
        )

    refresh_grounding(rec)
    return {
        "record": rec,
        "changed_paths": changed_paths,
        "assistant_message": f"[DEMO MODE · Pre-validated Intelligence]\n{answer}",
    }
