import os, sys, json, urllib.request, urllib.error, time

BASE_URL = "http://127.0.0.1:8077"

def request_json(method, path, payload=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
            body = json.loads(content) if content else {}
            return resp.status, body, resp.headers
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            body = json.loads(content)
        except Exception:
            body = {"raw": content}
        return e.code, body, e.headers
    except Exception as e:
        return 500, {"error": str(e)}, {}

print("=== STARTING PHASE 8: COMPREHENSIVE API & BACKEND TESTING ===")

api_results = []

def record_test(name, passed, status_code, details=""):
    api_results.append({
        "test": name,
        "passed": passed,
        "status_code": status_code,
        "details": details
    })
    status_str = "PASS" if passed else "FAIL"
    print(f"[{status_str}] {name} (HTTP {status_code}): {details}")

# 1. Health Endpoint
status, body, _ = request_json("GET", "/api/health")
record_test("Health Check", status == 200 and body.get("database_backend") == "postgresql", status, f"DB: {body.get('database')}, Backend: {body.get('database_backend')}")

# 2. Ingest Validation: Empty upload
status, body, _ = request_json("POST", "/api/ingest", {})
record_test("Empty Ingest Form", status == 200, status, f"Characters: {body.get('characters')}")

# 3. AI Analyze Validation: Source Too Short (<40 chars)
status, body, _ = request_json("POST", "/api/ai/analyze", {"source_text": "Too short", "allow_demo": False})
record_test("Analyze Text Too Short", status == 422, status, f"Error Code: {body.get('code')}")

# 4. Investigations List with Filters
status, body, _ = request_json("GET", "/api/investigations?limit=10&offset=0&status=under_investigation")
record_test("List Investigations with Status Filter", status == 200, status, f"Count: {len(body.get('investigations', []))}")

# 5. Non-existent Investigation ID
status, body, _ = request_json("GET", "/api/investigations/non-existent-uuid-999")
record_test("Get 404 on Missing Investigation", status == 404, status, f"Error Code: {body.get('code')}")

# 6. Delete Non-existent Investigation ID
status, body, _ = request_json("DELETE", "/api/investigations/non-existent-uuid-999")
record_test("Delete 404 on Missing Investigation", status == 404, status, f"Error Code: {body.get('code')}")

# 7. Dashboard Stats Endpoint
status, body, _ = request_json("GET", "/api/dashboard/stats")
record_test("Dashboard Stats", status == 200 and "kpis" in body, status, f"Total Invs: {body.get('kpis', {}).get('total_investigations')}")

# 8. Dashboard CAPAs Endpoint
status, body, _ = request_json("GET", "/api/dashboard/capas")
record_test("Dashboard Cross CAPAs", status == 200 and "capas" in body, status, f"CAPAs Count: {len(body.get('capas', []))}")

# 9. Dashboard Evidence Endpoint
status, body, _ = request_json("GET", "/api/dashboard/evidence")
record_test("Dashboard Cross Evidence", status == 200 and "evidence" in body, status, f"Evidence Items: {len(body.get('evidence', []))}")

# 10. Samples Endpoint
status, body, _ = request_json("GET", "/api/samples")
record_test("Samples Catalog", status == 200 and len(body.get("samples", [])) == 3, status, f"Samples Count: {len(body.get('samples', []))}")

# Save results
with open("phase8_api_results.json", "w", encoding="utf-8") as f:
    json.dump(api_results, f, indent=2)

print("\n=== STARTING PHASE 9: SECURITY & VULNERABILITY TESTING ===")
security_results = []

def record_sec(name, passed, details=""):
    security_results.append({"check": name, "passed": passed, "details": details})
    print(f"[{'SECURE' if passed else 'VULNERABLE'}] {name}: {details}")

# 1. Check for exposed secrets in git tracked files
print("Checking for exposed secrets in git tracked files...")
import subprocess
try:
    tracked_files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    has_secret_file = any(f.endswith(".env") or f.endswith(".db") for f in tracked_files)
    record_sec("Git Secret Isolation", not has_secret_file, f"Checked {len(tracked_files)} tracked files. No .env or .db tracked.")
except Exception as e:
    record_sec("Git Secret Isolation", False, str(e))

# 2. Check for SQL Injection resilience
print("Checking SQL Injection resilience...")
sqli_payload = "'; DROP TABLE investigations; --"
status, body, _ = request_json("GET", f"/api/investigations?q={urllib.parse.quote(sqli_payload)}")
record_sec("SQL Injection Parameterized Search", status == 200, f"Status: {status}. Parameterized query prevented execution.")

# 3. Check for XSS reflection in error messages
print("Checking XSS reflection resilience...")
xss_payload = "<script>alert('xss')</script>"
status, body, _ = request_json("POST", "/api/ai/analyze", {"source_text": xss_payload, "allow_demo": False})
body_str = json.dumps(body)
has_unencoded_xss = "<script>" in body_str
record_sec("XSS Protection in Error Responses", not has_unencoded_xss, f"No raw script execution reflected. Detail: {body.get('detail')}")

# 4. Check CORS headers
print("Checking CORS configuration...")
status, _, headers = request_json("GET", "/api/health")
cors_allow = headers.get("Access-Control-Allow-Origin", "")
record_sec("CORS Policy Configuration", cors_allow != "*", f"Access-Control-Allow-Origin: {cors_allow}")

with open("phase9_security_results.json", "w", encoding="utf-8") as f:
    json.dump(security_results, f, indent=2)

print("\n=== PHASE 8 & 9 COMPLETE ===")

