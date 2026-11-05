import os, sys, json, time, urllib.request, urllib.error
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8077"

def post_json(path, payload, timeout=120):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")), resp.status

def put_json(path, payload, timeout=60):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")), resp.status

def get_json(path, timeout=60):
    url = f"{BASE_URL}{path}"
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")), resp.status

print("=== STARTING PHASE 4, 5, 6, 7 AUDIT: ENGINE, COPILOT, SUPABASE ROUNDTRIP & AUDIT TRAIL ===")

# --- PHASE 4: INVESTIGATION ENGINE FUNCTIONALITY ---
print("\n--- PHASE 4: Deep Testing 5 Whys, Fishbone, Causes, Gaps & CAPAs ---")

initial_record = {
    "status": "under_investigation",
    "deviation_number": {"value": "DEV-2026-MET-401", "origin": "user", "confirmed": True},
    "title": {"value": "Loss on Drying (LOD) Excursion in Fluidized Bed Dryer FBD-03", "origin": "user", "confirmed": True},
    "product_name": {"value": "Metformin Hydrochloride API", "origin": "user", "confirmed": True},
    "batch_lot": {"value": "MFH-26-2033", "origin": "user", "confirmed": True},
    "severity": {"value": "major", "origin": "user", "confirmed": True},
    "severity_rationale": {"value": "Critical quality attribute out of specification; potential batch rejection.", "origin": "ai", "confirmed": False},
    "whys": [
        {"id": "why-1", "question": "Why did the LOD test result reach 1.8% vs limit 0.5%?", "answer": "Excess residual moisture remained in the Metformin HCl dried granules.", "confirmed": False, "grounded": True},
        {"id": "why-2", "question": "Why was residual moisture not removed during standard 45-min cycle?", "answer": "Inlet air temperature failed to reach 65°C setpoint during Phase 2 drying.", "confirmed": False, "grounded": True},
        {"id": "why-3", "question": "Why did inlet air temperature fail to reach setpoint?", "answer": "Steam control valve CV-301 actuator diaphragm ruptured, sticking valve at 20% open.", "confirmed": False, "grounded": True},
        {"id": "why-4", "question": "Why did the actuator diaphragm rupture?", "answer": "Elastomer exceeded recommended 12-month PM replacement schedule by 5 months.", "confirmed": False, "grounded": True}
    ],
    "fishbone": [
        {"id": "fish-1", "category": "Equipment", "cause": "Steam valve CV-301 pneumatic actuator diaphragm torn", "plausible": True, "confirmed": False, "grounded": True},
        {"id": "fish-2", "category": "Measurement", "cause": "Temperature sensor TT-301 calibration verified accurate", "plausible": False, "confirmed": False, "grounded": True},
        {"id": "fish-3", "category": "Method", "cause": "Drying cycle recipe parameters matched approved batch record", "plausible": False, "confirmed": False, "grounded": True}
    ],
    "root_causes": [
        {"id": "rc-1", "statement": "Preventative maintenance interval lapse on steam valve actuator diaphragm", "category": "Equipment", "confidence": "high", "evidence_supported": True, "confirmed": False}
    ],
    "gaps": [
        {"id": "gap-1", "topic": "CMMS Maintenance Log for FBD-03", "why_it_matters": "Verify date of last overhaul for actuator", "suggested_source": "SAP PM Work Order History", "resolved": False}
    ],
    "capas": [
        {"id": "capa-1", "capa_type": "corrective", "description": "Replace ruptured actuator diaphragm on CV-301 with high-temp fluorocarbon elastomer.", "owner": "Equipment Maintenance Lead", "due_date": "2026-11-15", "status": "open", "confirmed": False},
        {"id": "capa-2", "capa_type": "preventive", "description": "Revise CMMS PM task PM-FBD-004 to enforce mandatory annual replacement with QA lock out.", "owner": "Reliability Engineering Manager", "due_date": "2026-12-01", "status": "proposed", "confirmed": False}
    ],
    "source": {"raw_text": "Metformin FBD-03 LOD failure report."}
}

# 1. Create Investigation in Supabase
print("Saving initial investigation to Supabase...")
create_payload = {
    "record": initial_record,
    "actor": "qa_investigator@northline.pharma"
}
saved_resp, status = post_json("/api/investigations", create_payload)
assert status == 200, f"Expected 200, got {status}"
inv_id = saved_resp["id"]
print(f"Investigation created in Supabase with ID: {inv_id}")

# 2. Test Investigator Modifications:
# - Add 5th Why
# - Edit 1st Why
# - Confirm Root Cause
# - Progress CAPA 1 status to in_progress
# - Resolve Gap 1
print("Applying Investigator Modifications...")
modified_record = dict(initial_record)
modified_record["whys"].append({
    "id": "why-5",
    "question": "Why did the CMMS fail to trigger work order before schedule lapse?",
    "answer": "Equipment classification hierarchy mapped FBD-03 valve to non-critical asset tier.",
    "confirmed": True,
    "grounded": True
})
modified_record["whys"][0]["confirmed"] = True
modified_record["root_causes"][0]["confirmed"] = True
modified_record["root_causes"][0]["confirmed_by"] = "Dr. H. Vance, Senior QA Auditor"
modified_record["capas"][0]["status"] = "in_progress"
modified_record["gaps"][0]["resolved"] = True

update_payload = {
    "record": modified_record,
    "actor": "dr_vance_qa@northline.pharma"
}
updated_resp, status = put_json(f"/api/investigations/{inv_id}", update_payload)
assert status == 200, f"Expected 200, got {status}"
print("Investigation updated in Supabase successfully.")

# --- PHASE 5: AI COPILOT TESTING ---
print("\n--- PHASE 5: Testing AI Copilot with Investigation Context ---")
chat_payload = {
    "record": modified_record,
    "message": "What evidence supports the primary root cause regarding the actuator diaphragm?",
    "allow_demo": False
}
print("Querying Copilot via Groq (allow_demo=False)...")
chat_resp, status = post_json("/api/ai/chat", chat_payload, timeout=90)
assert status == 200, f"Expected 200, got {status}"
assistant_msg = chat_resp.get("assistant_message", "")
print("Copilot Response:")
print(f"  {assistant_msg[:250]}...")
assert len(assistant_msg) > 30, "Copilot response too short"
print("Copilot response verified.")

# --- PHASE 6: SUPABASE POSTGRESQL ROUND-TRIP PERSISTENCE TEST ---
print("\n--- PHASE 6: Supabase PostgreSQL Persistence Round-Trip Verification ---")
# Direct verification from fresh query
reopened_resp, status = get_json(f"/api/investigations/{inv_id}")
assert status == 200, f"Expected 200, got {status}"
reopened_rec = reopened_resp.get("record", {})

print(f"Reopened Investigation: {reopened_rec.get('deviation_number', {}).get('value')}")
print(f" - Product: {reopened_rec.get('product_name', {}).get('value')}")
print(f" - Whys Count: {len(reopened_rec.get('whys', []))} (Expected 5)")
assert len(reopened_rec.get("whys", [])) == 5, "Why count mismatch"

print(f" - Confirmed Root Causes: {sum(1 for rc in reopened_rec.get('root_causes', []) if rc.get('confirmed'))}")
assert reopened_rec.get("root_causes", [])[0].get("confirmed") is True, "Root cause confirmation lost"

print(f" - CAPA 1 Status: {reopened_rec.get('capas', [])[0].get('status')} (Expected: in_progress)")
assert reopened_rec.get("capas", [])[0].get("status") == "in_progress", "CAPA status lost"

print(f" - Gap 1 Resolved: {reopened_rec.get('gaps', [])[0].get('resolved')} (Expected: True)")
assert reopened_rec.get("gaps", [])[0].get("resolved") is True, "Gap resolved status lost"

# --- PHASE 7: AUDIT TRAIL VERIFICATION ---
print("\n--- PHASE 7: Audit Trail & Human Review Integrity Verification ---")
audit_resp, status = get_json(f"/api/investigations/{inv_id}/audit")
assert status == 200, f"Expected 200, got {status}"
events = audit_resp.get("events", [])
print(f"Audit Trail Events Count: {len(events)}")
assert len(events) >= 2, "Expected at least 2 audit events"

for idx, ev in enumerate(events):
    print(f"  Event {idx+1}: Action={ev.get('action')}, Actor={ev.get('actor')}, CreatedAt={ev.get('created_at')}")

assert events[0].get("action") == "create", "First event should be create"
assert events[0].get("actor") == "qa_investigator@northline.pharma", "First actor mismatch"
assert events[1].get("action") == "update", "Second event should be update"
assert events[1].get("actor") == "dr_vance_qa@northline.pharma", "Second actor mismatch"
print("Audit Trail fully verified.")

# Save results for documentation
audit_results = {
    "inv_id": inv_id,
    "whys_count": len(reopened_rec.get("whys", [])),
    "root_cause_confirmed": reopened_rec.get("root_causes", [])[0].get("confirmed"),
    "capa_status": reopened_rec.get("capas", [])[0].get("status"),
    "gap_resolved": reopened_rec.get("gaps", [])[0].get("resolved"),
    "audit_events_count": len(events),
    "copilot_tested": True
}
with open("phase4_5_6_7_results.json", "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("\n=== PHASE 4, 5, 6, 7 COMPLETE: ALL TESTS PASSED! ===")
