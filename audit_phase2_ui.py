import os, time
from playwright.sync_api import sync_playwright

os.makedirs("audit_screenshots", exist_ok=True)
console_errors = []
page_errors = []

def handle_console(msg):
    if msg.type in ["error", "warning"]:
        console_errors.append(f"[{msg.type.upper()}] {msg.text}")

def handle_page_error(exc):
    page_errors.append(str(exc))

print("=== STARTING PHASE 2: COMPREHENSIVE UI & BROWSER AUDIT ===")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.on("console", handle_console)
    page.on("pageerror", handle_page_error)

    # 1. Dashboard
    print("Navigating to Dashboard...")
    page.goto("http://localhost:41731", wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path="audit_screenshots/01_dashboard.png", full_page=True)
    print(" - Captured 01_dashboard.png")

    # 2. Investigations List
    print("Navigating to Investigations...")
    page.click("text=Investigations")
    time.sleep(1)
    page.screenshot(path="audit_screenshots/02_investigations.png", full_page=True)
    print(" - Captured 02_investigations.png")

    # 3. New Investigation / Ingestion View
    print("Navigating to New Investigation...")
    page.click("text=New Investigation")
    time.sleep(1)
    page.screenshot(path="audit_screenshots/03_new_investigation.png", full_page=True)
    print(" - Captured 03_new_investigation.png")

    # 4. Open Investigation Workspace
    print("Navigating to Investigation Workspace...")
    page.click("text=Investigations")
    time.sleep(1)
    # Click the first investigation in the table
    first_row = page.locator("tbody tr").first
    if first_row.count() > 0:
        first_row.click()
        time.sleep(2)
        page.screenshot(path="audit_screenshots/04_workspace_overview.png", full_page=True)
        print(" - Captured 04_workspace_overview.png")

        # Check tabs/sections in Workspace
        for tab_name, filename in [
            ("5 Whys", "05_workspace_whys.png"),
            ("Fishbone", "06_workspace_fishbone.png"),
            ("Findings", "07_workspace_findings.png"),
            ("CAPA", "08_workspace_capa.png"),
        ]:
            tab = page.locator(f"button:has-text('{tab_name}')")
            if tab.count() > 0:
                tab.first.click()
                time.sleep(1)
                page.screenshot(path=f"audit_screenshots/{filename}", full_page=True)
                print(f" - Captured {filename}")

    # 5. CAPA Management
    print("Navigating to CAPA Management...")
    page.click("text=CAPA Management")
    time.sleep(1)
    page.screenshot(path="audit_screenshots/09_capa_management.png", full_page=True)
    print(" - Captured 09_capa_management.png")

    # 6. Evidence Library
    print("Navigating to Evidence Library...")
    page.click("text=Evidence Library")
    time.sleep(1)
    page.screenshot(path="audit_screenshots/10_evidence_library.png", full_page=True)
    print(" - Captured 10_evidence_library.png")

    # 7. Audit Trail
    print("Navigating to Audit Trail...")
    page.click("text=Audit Trail")
    time.sleep(1)
    page.screenshot(path="audit_screenshots/11_audit_trail.png", full_page=True)
    print(" - Captured 11_audit_trail.png")

    # 8. Settings
    print("Navigating to Settings...")
    page.click("text=Settings")
    time.sleep(1)
    page.screenshot(path="audit_screenshots/12_settings.png", full_page=True)
    print(" - Captured 12_settings.png")

    browser.close()

print("\n=== PHASE 2 AUDIT RESULTS ===")
print(f"Total Console Warnings/Errors: {len(console_errors)}")
for err in console_errors[:10]:
    print(" ", err)
print(f"Total Page Runtime Exceptions: {len(page_errors)}")
for err in page_errors:
    print(" ", err)

