#!/usr/bin/env python3
"""Verify no page reads site data from the same-origin CDN."""
import asyncio, json
from urllib.parse import urlparse
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8765"
PAGES = [
    "/index.html",
    "/books.html",
    "/topics.html",
    "/topics-in-kitab.html?topic=1",
    "/topic-hadiths.html?topic=1&book=abudawud",
    "/hadith.html?book=bukhari&id=1",
    "/hadith.html?book=abudawud&id=1",
    "/kitab.html?book=bukhari",
    "/kitab.html?book=muntaqa",
    "/scholars.html",
    "/profile-detail.html?id=19944",
    "/glossary.html",
    "/master-link-viewer.html",
    "/node_diagram.html",
]

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=r"C:/Program Files/Google/Chrome/Application/chrome.exe", headless=True)
        for path in PAGES:
            ctx = await browser.new_context()
            page = await ctx.new_page()
            reqs, bad, errors = [], [], []
            page.on("request", lambda r: reqs.append(r.url))
            page.on("response", lambda r: bad.append((r.status, r.url)) if r.status >= 400 and ("/data" in r.url or "r2.dev" in r.url) else None)
            page.on("pageerror", lambda e: errors.append(str(e)[:160]))
            await page.goto(BASE + path, wait_until="domcontentloaded", timeout=60000)
            try:
                await page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass
            cdn = [u for u in reqs if "/data" in urlparse(u).path and urlparse(u).netloc in ("127.0.0.1:8765", "hadeeth.id")]
            json_urls = [u for u in reqs if u.split("?")[0].endswith(".json") and ("data" in u or "r2.dev" in u)]
            body = await page.locator("body").inner_text()
            print(json.dumps({
                "page": path,
                "cdn_data_requests": cdn[:5],
                "json_requests": json_urls[:5],
                "bad_responses": bad[:5],
                "pageerrors": errors[:3],
                "body_chars": len(body),
                "sample": body[:90].replace("\n", " "),
            }, ensure_ascii=False))
            await ctx.close()
        await browser.close()

asyncio.run(main())
