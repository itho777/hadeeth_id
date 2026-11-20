import asyncio
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8765"
PAGES = [
    ("topic-abudawud", "/topic-hadiths.html?topic=1&book=abudawud"),
    ("kitab-muntaqa", "/kitab.html?book=muntaqa"),
    ("kitab-tabarani", "/kitab.html?book=tabarani"),
    ("sanad-tabarani", "/sanad.html?book=tabarani&id=1"),
    ("hadith-bukhari", "/hadith.html?book=bukhari&id=1"),
    ("scholars", "/scholars.html"),
]

CHECKS = {
    "topic-abudawud": ["Terjemahan EN:", "English translation unavailable."],
    "kitab-muntaqa": ["turath:", "المتقى"],
    "kitab-tabarani": ["(294", "Kitab "],
    "sanad-tabarani": ["Sanad belum tersedia", "Imam al-Bukhari"],
    "hadith-bukhari": ["Source: unified", "Ã", "&bull;"],
    "scholars": ["Abu Hurairah", "data/rawis/active_rawis.min.json"],
}


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append("console:" + m.text) if m.type == "error" else None)
        for name, path in PAGES:
            errors.clear()
            await page.goto(BASE + path, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(12000)
            text = await page.locator("body").inner_text()
            counts = {s: text.count(s) for s in CHECKS[name]}
            overflow = await page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            print(f"{name}: overflow={overflow} errors={len(errors)} counts={counts}")
            for e in errors[:3]:
                print("   ", e[:200])
        await browser.close()


asyncio.run(main())
