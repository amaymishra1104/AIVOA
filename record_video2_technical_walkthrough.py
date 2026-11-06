"""
Script: record_video2_technical_walkthrough.py
Records the full Northline RCA Technical Walkthrough video at 1920x1080 30FPS MP4.
Target duration: ~8 minutes (480 seconds).
Explains source code, architecture, frontend, backend, ingestion, LangGraph, Groq,
evidence grounding, Supabase database, and automated test execution.
"""

import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = r"C:\NorthlineRCA_Submission"
os.makedirs(OUTPUT_DIR, exist_ok=True)
SCRATCH_DIR = r"C:\Users\Amay\OneDrive\Pictures\OneDrive\Desktop\northline-rca\scratch_video2"
os.makedirs(SCRATCH_DIR, exist_ok=True)

FINAL_MP4 = os.path.join(OUTPUT_DIR, "Northline_RCA_Technical_Walkthrough.mp4")
VIEWER_HTML = os.path.abspath("technical_walkthrough_viewer.html")
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def move_mouse_smooth(page, target_x, target_y, duration=0.8, steps=20):
    page.mouse.move(target_x, target_y, steps=steps)
    time.sleep(duration * 0.2)

def scroll_code(page, selector, target_y, duration=2.0, steps=30):
    """Smooth scroll within code body element."""
    step_time = duration / steps
    current = page.evaluate(f"document.querySelector('{selector}') ? document.querySelector('{selector}').scrollTop : 0")
    diff = target_y - current
    if abs(diff) < 5:
        return
    for i in range(1, steps + 1):
        progress = i / steps
        ease = progress * progress * (3 - 2 * progress)
        y = current + diff * ease
        page.evaluate(f"if (document.querySelector('{selector}')) document.querySelector('{selector}').scrollTop = {y}")
        time.sleep(step_time)

def inject_cursor(page):
    page.evaluate("""
        () => {
            if (document.getElementById('tech-cursor')) return;
            const dot = document.createElement('div');
            dot.id = 'tech-cursor';
            dot.style = 'position:fixed;top:0;left:0;width:18px;height:18px;background:rgba(14,165,233,0.85);border:2px solid #ffffff;border-radius:50%;pointer-events:none;z-index:9999999;box-shadow:0 0 12px rgba(14,165,233,0.8);transition:transform 0.08s ease;transform:translate(-50%,-50%);';
            document.body.appendChild(dot);
            window.addEventListener('mousemove', e => {
                dot.style.left = e.clientX + 'px';
                dot.style.top = e.clientY + 'px';
            });
            window.addEventListener('mousedown', () => {
                dot.style.transform = 'translate(-50%,-50%) scale(0.7)';
            });
            window.addEventListener('mouseup', () => {
                dot.style.transform = 'translate(-50%,-50%) scale(1.0)';
            });
        }
    """)

print("=== STARTING TECHNICAL WALKTHROUGH RECORDING (1920x1080 30FPS) ===")
start_time = time.time()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=SCRATCH_DIR,
        record_video_size={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    viewer_url = "file:///" + VIEWER_HTML.replace("\\", "/")
    page.goto(viewer_url, wait_until="networkidle")
    inject_cursor(page)
    time.sleep(2)

    # -------------------------------------------------------------
    # 0:00 - 0:45 (45s): SLIDE 0 — ARCHITECTURE OVERVIEW
    # -------------------------------------------------------------
    print("[0:00 - 0:45] Slide 1: System Architecture Overview...")
    page.evaluate("goToSlide(0)")
    move_mouse_smooth(page, 450, 280, duration=1.0) # React SPA
    time.sleep(8)
    move_mouse_smooth(page, 950, 280, duration=1.0) # FastAPI
    time.sleep(8)
    move_mouse_smooth(page, 450, 520, duration=1.0) # Supabase
    time.sleep(10)
    move_mouse_smooth(page, 950, 520, duration=1.0) # LangGraph & Groq
    time.sleep(15)

    # -------------------------------------------------------------
    # 0:45 - 1:50 (65s): SLIDE 1 — FRONTEND IMPLEMENTATION
    # -------------------------------------------------------------
    print("[0:45 - 1:50] Slide 2: Frontend Implementation & Redux...")
    move_mouse_smooth(page, 510, 32, duration=0.8) # Click nav pill
    page.evaluate("goToSlide(1)")
    time.sleep(3)
    move_mouse_smooth(page, 550, 280, duration=1.0)
    time.sleep(10) # Review State interface
    scroll_code(page, "#slide-1 .code-body", 180, duration=2.0)
    move_mouse_smooth(page, 600, 420, duration=1.0) # Highlight applyServerRecord
    time.sleep(15)
    move_mouse_smooth(page, 600, 550, duration=1.0) # Highlight confirmRootCause
    time.sleep(15)
    move_mouse_smooth(page, 1720, 340, duration=1.0) # Notes panel
    time.sleep(18)

    # -------------------------------------------------------------
    # 1:50 - 2:50 (60s): SLIDE 2 — API & BACKEND
    # -------------------------------------------------------------
    print("[1:50 - 2:50] Slide 3: FastAPI Gateway & Schemas...")
    move_mouse_smooth(page, 620, 32, duration=0.8)
    page.evaluate("goToSlide(2)")
    time.sleep(3)
    move_mouse_smooth(page, 550, 320, duration=1.0) # Lifespan & DB init
    time.sleep(15)
    scroll_code(page, "#slide-2 .code-body", 150, duration=2.0)
    move_mouse_smooth(page, 550, 480, duration=1.0) # AnalyzeRequest schema
    time.sleep(18)
    move_mouse_smooth(page, 1720, 320, duration=1.0) # Notes panel
    time.sleep(20)

    # -------------------------------------------------------------
    # 2:50 - 3:50 (60s): SLIDE 3 — DOCUMENT EXTRACTION
    # -------------------------------------------------------------
    print("[2:50 - 3:50] Slide 4: Multi-Format Document Ingestion...")
    move_mouse_smooth(page, 720, 32, duration=0.8)
    page.evaluate("goToSlide(3)")
    time.sleep(3)
    move_mouse_smooth(page, 550, 320, duration=1.0) # PDF parser
    time.sleep(16)
    move_mouse_smooth(page, 550, 420, duration=1.0) # EML parser
    time.sleep(16)
    move_mouse_smooth(page, 550, 520, duration=1.0) # Plain text parser
    time.sleep(10)
    move_mouse_smooth(page, 1720, 320, duration=1.0) # Metrics
    time.sleep(13)

    # -------------------------------------------------------------
    # 3:50 - 5:30 (100s): SLIDE 4 — LANGGRAPH & GROQ INFERENCE
    # -------------------------------------------------------------
    print("[3:50 - 5:30] Slide 5: LangGraph 5-Node Graph & Groq LLM...")
    move_mouse_smooth(page, 850, 32, duration=0.8)
    page.evaluate("goToSlide(4)")
    time.sleep(3)
    move_mouse_smooth(page, 550, 260, duration=1.0) # Context-pruned runner
    time.sleep(22)
    scroll_code(page, "#slide-4 .code-body", 120, duration=2.0)
    move_mouse_smooth(page, 600, 380, duration=1.0) # complete_structured
    time.sleep(20)
    scroll_code(page, "#slide-4 .code-body", 220, duration=2.0)
    move_mouse_smooth(page, 600, 520, duration=1.0) # 429 rate limit backoff
    time.sleep(25)
    move_mouse_smooth(page, 1720, 320, duration=1.0) # Notes panel
    time.sleep(28)

    # -------------------------------------------------------------
    # 5:30 - 6:30 (60s): SLIDE 5 — EVIDENCE GROUNDING & REGULATORY
    # -------------------------------------------------------------
    print("[5:30 - 6:30] Slide 6: Evidence Grounding & Regulatory Safeguards...")
    move_mouse_smooth(page, 1020, 32, duration=0.8)
    page.evaluate("goToSlide(5)")
    time.sleep(3)
    move_mouse_smooth(page, 550, 280, duration=1.0) # Exact substring
    time.sleep(15)
    move_mouse_smooth(page, 550, 400, duration=1.0) # Numerical verification
    time.sleep(15)
    move_mouse_smooth(page, 550, 540, duration=1.0) # Lexical overlap
    time.sleep(12)
    move_mouse_smooth(page, 1720, 320, duration=1.0) # Notes
    time.sleep(13)

    # -------------------------------------------------------------
    # 6:30 - 7:30 (60s): SLIDE 6 — DATABASE PERSISTENCE & MIGRATIONS
    # -------------------------------------------------------------
    print("[6:30 - 7:30] Slide 7: Supabase Cloud PostgreSQL & Audit Trail...")
    move_mouse_smooth(page, 1180, 32, duration=0.8)
    page.evaluate("goToSlide(6)")
    time.sleep(3)
    move_mouse_smooth(page, 550, 300, duration=1.0) # Investigation table
    time.sleep(16)
    scroll_code(page, "#slide-6 .code-body", 160, duration=2.0)
    move_mouse_smooth(page, 550, 480, duration=1.0) # AuditEvent table
    time.sleep(18)
    move_mouse_smooth(page, 1720, 320, duration=1.0) # Notes
    time.sleep(21)

    # -------------------------------------------------------------
    # 7:30 - 8:00 (30s): SLIDE 7 — VERIFICATION SUITE & CONCLUSION
    # -------------------------------------------------------------
    print("[7:30 - 8:00] Slide 8: Automated Test Suite & Architecture Verdict...")
    move_mouse_smooth(page, 1340, 32, duration=0.8)
    page.evaluate("goToSlide(7)")
    time.sleep(3)
    move_mouse_smooth(page, 500, 350, duration=1.0) # Pytest 34 passed
    time.sleep(12)
    move_mouse_smooth(page, 500, 600, duration=1.0) # npm run build
    time.sleep(12)

    video_raw = page.video.path()
    context.close()
    browser.close()

elapsed = time.time() - start_time
print(f"Playwright recording finished in {elapsed:.1f} seconds. Raw video at: {video_raw}")

# Convert to 1080p 30FPS MP4 with FFmpeg
print(f"Converting to {FINAL_MP4} via FFmpeg...")
cmd = [
    FFMPEG_EXE, "-y",
    "-i", video_raw,
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    FINAL_MP4
]
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("FFmpeg error:", res.stderr)
    sys.exit(1)

size_mb = os.path.getsize(FINAL_MP4) / (1024 * 1024)
print(f"SUCCESS! Video 2 saved at {FINAL_MP4} ({size_mb:.2f} MB)")
