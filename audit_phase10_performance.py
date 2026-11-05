import os, sys, time, json, urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8077"
FRONTEND_URL = "http://localhost:41731"

perf_metrics = {}

print("=== STARTING PHASE 10: PERFORMANCE MEASUREMENTS ===")

# 1. Frontend Initial Load
t0 = time.time()
with urllib.request.urlopen(FRONTEND_URL) as resp:
    _ = resp.read()
frontend_load_time = time.time() - t0
perf_metrics["frontend_initial_load_sec"] = round(frontend_load_time, 3)
print(f"1. Frontend Initial Load: {frontend_load_time * 1000:.1f}ms")

# 2. Backend Health Response Time
t0 = time.time()
with urllib.request.urlopen(f"{BASE_URL}/api/health") as resp:
    _ = resp.read()
health_time = time.time() - t0
perf_metrics["backend_health_latency_sec"] = round(health_time, 3)
print(f"2. Backend Health Latency: {health_time * 1000:.1f}ms")

# 3. Document Extraction Times
samples = [
    ("Atorvastatin PDF", "samples/DEV-2026-1184_atorvastatin_impurity.pdf", "application/pdf"),
    ("Metformin TXT", "samples/shift_note_metformin_lod.txt", "text/plain"),
    ("Omeprazole EML", "samples/email_omeprazole_near_miss.eml", "message/rfc822")
]

sys.path.insert(0, os.path.abspath("backend"))
from app.services.text_extract import ingest_source

extraction_times = {}
for name, path, mime in samples:
    with open(path, "rb") as f:
        data = f.read()
    t0 = time.time()
    res = ingest_source(data, os.path.basename(path), "", "")
    dur = time.time() - t0
    extraction_times[name] = round(dur, 4)
    print(f"3. Ingestion/Extraction [{name}]: {dur * 1000:.2f}ms ({res.characters} chars)")
perf_metrics["document_extraction_times_sec"] = extraction_times

# 4. Database Query Latency (Supabase PostgreSQL)
from app.db import get_engine, get_sessionmaker
from app.services.repository import list_investigations

engine = get_engine()
session_factory = get_sessionmaker()

db_query_times = []
with session_factory() as db:
    for _ in range(5):
        t0 = time.time()
        rows = list_investigations(db, limit=50)
        db_query_times.append(time.time() - t0)

avg_db_time = sum(db_query_times) / len(db_query_times)
perf_metrics["avg_supabase_query_latency_sec"] = round(avg_db_time, 3)
print(f"4. Supabase PostgreSQL Query Latency (avg 5 runs): {avg_db_time * 1000:.1f}ms (Count: {len(rows)})")

# 5. Live Groq Latency (Single Prompt)
from langchain_groq import ChatGroq
from app.config import get_settings

settings = get_settings()
m = ChatGroq(model_name="openai/gpt-oss-120b", groq_api_key=settings.groq_api_key, max_retries=3, request_timeout=60)
t0 = time.time()
resp = m.invoke("Return one sentence on pharmaceutical validation.")
groq_single_time = time.time() - t0
perf_metrics["groq_single_call_latency_sec"] = round(groq_single_time, 2)
print(f"5. Groq Single Call (120B Model): {groq_single_time:.2f}s")

with open("phase10_performance_results.json", "w", encoding="utf-8") as f:
    json.dump(perf_metrics, f, indent=2)

print("\n=== PHASE 10 COMPLETE ===")

