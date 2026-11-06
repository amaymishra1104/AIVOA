"""
Script: record_video1_product_demo.py
Records the full Northline RCA Product Demonstration video at 1920x1080 30FPS MP4.
Target duration: ~6m 45s (5-8 min range).
Demonstrates real UI, real input formats, live AI analysis, 5 Whys, Fishbone,
Evidence Gaps, CAPAs, human confirmation, Supabase persistence, and Audit Trail.
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
SCRATCH_DIR = r"C:\Users\Amay\OneDrive\Pictures\OneDrive\Desktop\northline-rca\scratch_video1"
os.makedirs(SCRATCH_DIR, exist_ok=True)

FINAL_MP4 = os.path.join(OUTPUT_DIR, "Northline_RCA_Product_Demonstration.mp4")
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def human_scroll(page, target_y, duration=1.5, steps=25):
    """Smooth scroll page to target_y over duration."""
    current_y = page.evaluate("window.scrollY")
    diff = target_y - current_y
    if abs(diff) < 5:
        return
    step_time = duration / steps
    for i in range(1, steps + 1):
        progress = i / steps
        ease = progress * progress * (3 - 2 * progress) # smoothstep
        y = current_y + diff * ease
        page.evaluate(f"window.scrollTo(0, {y})")
        time.sleep(step_time)

def move_mouse_smooth(page, target_x, target_y, duration=0.8, steps=20):
    """Move cursor smoothly with visual feedback."""
    page.mouse.move(target_x, target_y, steps=steps)
    time.sleep(duration * 0.2)

def inject_cursor(page):
    """Inject glowing mouse pointer for presentation visibility."""
    page.evaluate("""
        () => {
            if (document.getElementById('demo-cursor')) return;
            const dot = document.createElement('div');
            dot.id = 'demo-cursor';
            dot.style = 'position:fixed;top:0;left:0;width:20px;height:20px;background:rgba(220,38,38,0.85);border:2px solid #ffffff;border-radius:50%;pointer-events:none;z-index:9999999;box-shadow:0 0 12px rgba(220,38,38,0.8);transition:transform 0.08s ease;transform:translate(-50%,-50%);';
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

print("=== STARTING PRODUCT DEMONSTRATION RECORDING (1920x1080 30FPS) ===")
start_time = time.time()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=SCRATCH_DIR,
        record_video_size={"width": 1920, "height": 1080}
    )
    page = context.new_page()

    # -------------------------------------------------------------
    # 0:00 - 0:40 (40s): INTRODUCTION & EXECUTIVE QUALITY DASHBOARD
    # -------------------------------------------------------------
    print("[0:00 - 0:40] Dashboard Walkthrough...")
    page.goto("http://localhost:41731/", wait_until="networkidle")
    inject_cursor(page)
    time.sleep(2)

    # Hover header & status badges
    move_mouse_smooth(page, 200, 30, duration=1.0)
    time.sleep(2)
    move_mouse_smooth(page, 960, 30, duration=1.0) # Groq / DB badges
    time.sleep(3)

    # Move across KPI cards
    kpi_positions = [(280, 160), (560, 160), (840, 160), (1120, 160), (1400, 160), (1680, 160)]
    for x, y in kpi_positions:
        move_mouse_smooth(page, x, y, duration=0.8)
        time.sleep(1.2)

    # Scroll down to analytics charts
    human_scroll(page, 380, duration=2.0)
    time.sleep(4)

    # Scroll down to Recent Investigations
    human_scroll(page, 700, duration=2.0)
    time.sleep(4)

    # Hover table row
    move_mouse_smooth(page, 500, 820, duration=1.0)
    time.sleep(3)

    # Scroll back to top
    human_scroll(page, 0, duration=1.5)
    time.sleep(2)

    # -------------------------------------------------------------
    # 0:40 - 1:40 (60s): MULTI-FORMAT INPUT METHODS (TXT, EML, PDF)
    # -------------------------------------------------------------
    print("[0:40 - 1:40] Demonstrating Input Methods on Ingest Studio...")
    move_mouse_smooth(page, 1720, 30, duration=1.0)
    # Navigate to Ingest
    page.goto("http://localhost:41731/ingest", wait_until="networkidle")
    inject_cursor(page)
    time.sleep(3)

    # Show dropzone and header
    move_mouse_smooth(page, 500, 260, duration=1.0)
    time.sleep(4)

    # 1. Metformin TXT Shift Note
    print(" -> Selecting Metformin TXT shift note...")
    move_mouse_smooth(page, 720, 190, duration=1.0)
    page.get_by_text("Shift note").click()
    time.sleep(2)
    # Highlight textarea with shift note content
    human_scroll(page, 350, duration=1.5)
    move_mouse_smooth(page, 650, 480, duration=1.0)
    time.sleep(8) # Read shift note details (LOD 0.42%, TD-12, MFH-26-2033)

    # 2. Omeprazole EML Near Miss Email
    print(" -> Selecting Omeprazole EML near-miss email...")
    human_scroll(page, 150, duration=1.0)
    move_mouse_smooth(page, 850, 190, duration=1.0)
    page.get_by_text("QA email").click()
    time.sleep(2)
    human_scroll(page, 320, duration=1.5)
    move_mouse_smooth(page, 550, 420, duration=1.0)
    time.sleep(8) # Read near-miss email details (Methanol vs Ethanol barcode override)

    # 3. Atorvastatin Calcium PDF Deviation Report (Primary Scenario)
    print(" -> Selecting Atorvastatin PDF deviation report...")
    human_scroll(page, 150, duration=1.0)
    move_mouse_smooth(page, 580, 190, duration=1.0)
    page.get_by_text("Deviation PDF").click()
    time.sleep(2)
    human_scroll(page, 320, duration=1.5)
    move_mouse_smooth(page, 500, 420, duration=1.0)
    time.sleep(6) # Show PDF attached and description

    # -------------------------------------------------------------
    # 1:40 - 2:40 (60s+): AI EXTRACTION & FORM POPULATION
    # -------------------------------------------------------------
    print("[1:40 - 2:40] Executing Live AI Graph Analysis...")
    analyze_btn = page.get_by_role("button", name="Analyze with AI Engine")
    move_mouse_smooth(page, 960, 520, duration=1.0)
    analyze_btn.click()
    print(" -> AI Analysis submitted. Monitoring streaming phases...")

    # Wait for completion (watching the live phases animate)
    page.wait_for_selector("text=EXTRACTION COMPLETED", timeout=180000)
    print(" -> AI Analysis completed!")
    time.sleep(3)

    # Review Extracted Entities Verification Panel
    human_scroll(page, 450, duration=1.5)
    move_mouse_smooth(page, 400, 600, duration=1.0)
    time.sleep(4) # Product: Atorvastatin calcium
    move_mouse_smooth(page, 750, 600, duration=1.0)
    time.sleep(3) # Batch: ATV-CA-26-0142
    move_mouse_smooth(page, 1100, 600, duration=1.0)
    time.sleep(3) # Severity: Major

    # Click Open in Investigation Workspace
    print(" -> Transitioning to Investigation Workspace...")
    open_btn = page.get_by_role("button", name="Open in Investigation Workspace →")
    move_mouse_smooth(page, 1600, 480, duration=1.0)
    open_btn.click()
    page.wait_for_load_state("networkidle")
    inject_cursor(page)
    time.sleep(4)

    # -------------------------------------------------------------
    # 2:40 - 3:50 (70s): AI-ASSISTED INVESTIGATION (5 WHYS & FISHBONE)
    # -------------------------------------------------------------
    print("[2:40 - 3:50] Walking through 5 Whys and Fishbone...")
    # Scroll through Identity and Event
    human_scroll(page, 200, duration=1.5)
    time.sleep(3)

    # Navigate to Section: Investigation via section-nav
    page.locator(".section-nav button").filter(has_text="Investigation").click()
    time.sleep(2)
    human_scroll(page, 750, duration=1.5)
    time.sleep(3)

    # Step through 5 Whys
    whys_cards = page.locator(".stack .card, .grid-3")
    count = whys_cards.count()
    print(f" -> Found {count} why / team items in UI")
    for i in range(min(count, 4)):
        box = whys_cards.nth(i).bounding_box()
        if box:
            move_mouse_smooth(page, box["x"] + 200, box["y"] + 40, duration=0.8)
            time.sleep(2.5)

    # Scroll down to Fishbone
    human_scroll(page, 1300, duration=1.5)
    time.sleep(4)
    # Move across Fishbone SVG / category branches
    move_mouse_smooth(page, 600, 500, duration=1.0) # Machine
    time.sleep(4)
    move_mouse_smooth(page, 950, 500, duration=1.0) # Method
    time.sleep(4)

    # -------------------------------------------------------------
    # 3:50 - 4:40 (50s): EVIDENCE GAPS IDENTIFICATION
    # -------------------------------------------------------------
    print("[3:50 - 4:40] Demonstrating Evidence Gaps...")
    page.locator(".section-nav button").filter(has_text="Gaps").click()
    time.sleep(2)
    human_scroll(page, 1800, duration=1.5)
    time.sleep(3)

    # Highlight gaps list
    gap_cards = page.locator("#gaps article.card")
    g_count = gap_cards.count()
    print(f" -> Found {g_count} evidence gaps in #gaps")
    for i in range(min(g_count, 3)):
        box = gap_cards.nth(i).bounding_box()
        if box:
            move_mouse_smooth(page, box["x"] + 150, box["y"] + 30, duration=0.8)
            time.sleep(3.0)

    # Confirm addressed on Gap 1
    confirm_gap_btn = page.locator("#gaps button:has-text('Confirm addressed')").first
    if confirm_gap_btn.count() > 0:
        box = confirm_gap_btn.bounding_box()
        if box:
            move_mouse_smooth(page, box["x"] + 20, box["y"] + 10, duration=0.8)
            confirm_gap_btn.click()
            time.sleep(3)

    # -------------------------------------------------------------
    # 4:40 - 5:40 (60s): CAPA RECOMMENDATIONS & MANAGEMENT
    # -------------------------------------------------------------
    print("[4:40 - 5:40] Demonstrating CAPA Management...")
    page.locator(".section-nav button").filter(has_text="CAPA").click()
    time.sleep(2)
    human_scroll(page, 2300, duration=1.5)
    time.sleep(3)

    # Walk through generated CAPAs
    capa_cards = page.locator("#capa article.card")
    c_count = capa_cards.count()
    print(f" -> Found {c_count} CAPA items in #capa")
    for i in range(min(c_count, 3)):
        box = capa_cards.nth(i).bounding_box()
        if box:
            move_mouse_smooth(page, box["x"] + 200, box["y"] + 30, duration=0.8)
            time.sleep(3.0)

    # Accept first CAPA
    accept_capa_btn = page.locator("#capa button:has-text('Accept CAPA')").first
    if accept_capa_btn.count() > 0:
        box = accept_capa_btn.bounding_box()
        if box:
            move_mouse_smooth(page, box["x"] + 20, box["y"] + 10, duration=0.8)
            accept_capa_btn.click()
            time.sleep(2)

    # Open CAPA Management Hub from navbar
    print(" -> Opening global CAPA Management Hub...")
    page.goto("http://localhost:41731/capa", wait_until="networkidle")
    inject_cursor(page)
    time.sleep(3)
    human_scroll(page, 300, duration=1.5)
    time.sleep(6) # Show cross-investigation CAPA register
    human_scroll(page, 0, duration=1.0)
    time.sleep(2)

    # Return to Workspace
    page.goto("http://localhost:41731/workspace", wait_until="networkidle")
    inject_cursor(page)
    time.sleep(3)

    # -------------------------------------------------------------
    # 5:40 - 6:45 (65s): HUMAN CONFIRMATION, PERSISTENCE & CLOSE
    # -------------------------------------------------------------
    print("[5:40 - 6:45] Demonstrating Confirmation, Saving & Persistence...")
    # Scroll to Causes / Confirmation
    page.locator(".section-nav button").filter(has_text="Causes").click()
    time.sleep(2)
    human_scroll(page, 1500, duration=1.5)
    time.sleep(2)

    # Confirm root cause hypothesis
    confirm_cause_btn = page.locator("#causes button:has-text('Confirm this cause')").first
    if confirm_cause_btn.count() > 0:
        box = confirm_cause_btn.bounding_box()
        if box:
            move_mouse_smooth(page, box["x"] + 30, box["y"] + 10, duration=0.8)
            confirm_cause_btn.click()
            time.sleep(3)

    # Save Investigation (Top bar Save button or Ctrl+S)
    print(" -> Saving Investigation to Supabase PostgreSQL...")
    page.keyboard.press("Control+s")
    time.sleep(4)

    # Browser Refresh to demonstrate persistence
    print(" -> Refreshing browser to verify cloud persistence...")
    page.reload(wait_until="networkidle")
    inject_cursor(page)
    time.sleep(4)
    # Show reloaded investigation data intact
    human_scroll(page, 500, duration=1.5)
    time.sleep(4)

    # Open Audit Trail View
    print(" -> Opening 21 CFR Part 11 compliant Audit Trail...")
    page.goto("http://localhost:41731/audit", wait_until="networkidle")
    inject_cursor(page)
    time.sleep(3)
    human_scroll(page, 300, duration=1.5)
    time.sleep(5) # Show audit trail events with diffs

    # Return to Executive Dashboard to close
    print(" -> Returning to Dashboard for conclusion...")
    page.goto("http://localhost:41731/", wait_until="networkidle")
    inject_cursor(page)
    time.sleep(2)
    human_scroll(page, 200, duration=1.5)
    time.sleep(5)

    # Finish recording
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
print(f"SUCCESS! Video 1 saved at {FINAL_MP4} ({size_mb:.2f} MB)")
