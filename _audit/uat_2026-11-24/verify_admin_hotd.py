from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))

    page.goto(f"{BASE}/index.html", wait_until="domcontentloaded")
    page.wait_for_timeout(16000)
    label = page.locator("#hotd-book-label").inner_text() if page.locator("#hotd-book-label").count() else ""
    arabic = page.locator("#hotd-arabic").inner_text() if page.locator("#hotd-arabic").count() else ""
    print("HOTD label:", label)
    print("HOTD arabic chars:", len(arabic), "placeholder" if "belum dapat dimuat" in arabic else "ok")

    page.goto(f"{BASE}/admin.html", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    gate = page.locator("#gate").is_visible()
    dash = page.locator("#dash").is_visible()
    print("admin gate visible:", gate, "dash visible:", dash)
    print("admin title:", page.title())
    print("page errors:", errors)
    browser.close()

assert "Ibn Hibban" in label, label
assert "placeholder" not in arabic, "HOTD did not render"
assert gate and not dash, "admin gate state wrong"
print("PASS")
