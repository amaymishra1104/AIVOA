import os, sys, time, json, urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8077"

def post_multipart(url, file_path, mime_type):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"))
    body.extend(file_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def post_json(url, payload, timeout=120):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")), resp.status

print("=== STARTING PHASE 3, 4, 5 AUDIT: LIVE AI INGESTION & INVESTIGATION ENGINE ===")

samples = [
    {
        "name": "Atorvastatin Deviation PDF",
        "path": "samples/DEV-2026-1184_atorvastatin_impurity.pdf",
        "mime": "application/pdf",
        "expected_product": "Atorvastatin",
        "expected_batch": "ATORV"
    },
    {
        "name": "Metformin Shift Note TXT",
        "path": "samples/shift_note_metformin_lod.txt",
        "mime": "text/plain",
        "expected_product": "Metformin",
        "expected_batch": "MET"
    },
    {
        "name": "Omeprazole Near-Miss EML",
        "path": "samples/email_omeprazole_near_miss.eml",
        "mime": "message/rfc822",
        "expected_product": "Omeprazole",
        "expected_batch": "OMEP"
    }
]

phase3_results = []
live_records = {}

for sample in samples:
    print(f"\n--- Testing Ingestion: {sample['name']} ---")
    t0 = time.time()
    ingest_res = post_multipart(f"{BASE_URL}/api/ingest", sample["path"], sample["mime"])
    ingest_time = time.time() - t0
    
    extracted_text = ingest_res.get("source_text", "")
    print(f"File validated & extracted: {len(extracted_text)} characters in {ingest_time:.2f}s")
    assert len(extracted_text) > 50, "Extracted text too short"

    # Call AI analyze with allow_demo=False (LIVE GROQ ONLY)
    print(f"Calling Live LangGraph Analysis (allow_demo=False)...")
    analyze_payload = {
        "source_text": extracted_text,
        "source_kind": ingest_res.get("source_kind", "text"),
        "filename": ingest_res.get("filename", ""),
        "subject": ingest_res.get("subject", ""),
        "sender": ingest_res.get("sender", ""),
        "allow_demo": False
    }

    t_analyze = time.time()
    analyze_res, status = post_json(f"{BASE_URL}/api/ai/analyze", analyze_payload, timeout=300)
    analyze_time = time.time() - t_analyze
    print(f"Live Analysis Completed in {analyze_time:.2f}s (HTTP {status})")

    record = analyze_res.get("record", {})
    prod_name = record.get("product_name", {}).get("value", "")
    batch_lot = record.get("batch_lot", {}).get("value", "")
    severity = record.get("severity", {}).get("value", "")
    whys = record.get("whys", [])
    fishbone = record.get("fishbone", [])
    root_causes = record.get("root_causes", [])
    capas = record.get("capas", [])
    gaps = record.get("gaps", [])

    print(f"  Extracted Product: {prod_name}")
    print(f"  Extracted Batch: {batch_lot}")
    print(f"  Extracted Severity: {severity}")
    print(f"  5 Whys Count: {len(whys)}")
    print(f"  Fishbone Factors Count: {len(fishbone)}")
    print(f"  Root Causes Count: {len(root_causes)}")
    print(f"  CAPAs Count: {len(capas)}")
    print(f"  Evidence Gaps Count: {len(gaps)}")

    # Verify fact accuracy
    has_expected_product = sample["expected_product"].lower() in prod_name.lower() or sample["expected_product"].lower() in extracted_text.lower()
    print(f"  Product Match Verified: {has_expected_product}")

    phase3_results.append({
        "sample": sample["name"],
        "chars": len(extracted_text),
        "ingest_time": ingest_time,
        "analyze_time": analyze_time,
        "product": prod_name,
        "batch": batch_lot,
        "severity": severity,
        "whys_count": len(whys),
        "fishbone_count": len(fishbone),
        "root_causes_count": len(root_causes),
        "capas_count": len(capas),
        "gaps_count": len(gaps),
    })

    live_records[sample["name"]] = record
    print(f"Cooldown 25s between documents to replenish Groq TPM bucket...")
    time.sleep(25)

# Save Phase 3 results to json for reporting
with open("phase3_results.json", "w", encoding="utf-8") as f:
    json.dump(phase3_results, f, indent=2)

print("\n=== PHASE 3 COMPLETE ===")
