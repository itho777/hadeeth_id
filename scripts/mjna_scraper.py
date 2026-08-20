import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import os
import re

BOOKS = {
    'ibnukhuzaimah': 1808,
    'ibnuhibban': 2769,
    'daruquthni': 4790,
    'mustadrak': 673
}

async def fetch_page(session, book, i, retries=3):
    # mjna pagination usually starts at 0 or 1. Let's try `index/i` where i is 0-indexed.
    url = f"https://www.mjna.or.id/{book}/index/{i}"
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    ar_elem = soup.find('p', class_='arabic2')
                    id_elem = soup.find('p', class_='latin')
                    
                    if ar_elem and id_elem:
                        ar_text = ar_elem.get_text().strip()
                        # Clean up formatting like leading zeros or exact book name
                        ar_text = re.sub(r'^\s*[\u0600-\u06FF\s]+\d+\s*:\s*', '', ar_text)
                        
                        id_text = id_elem.get_text().strip()
                        id_text = re.sub(r'^(Shahih|Sunan|Mustadrak)\s+.*?\d+\s*:\s*', '', id_text)
                        
                        return {
                            'hadith_number': str(i + 1),
                            'text_ar': ar_text,
                            'text_id': id_text
                        }
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed {url}: {e}")
            await asyncio.sleep(1)
    return None

async def scrape_book(book, count):
    print(f"Scraping {book} ({count} hadiths)...")
    out_file = f"data/sources/mjna/{book}.ndjson"
    os.makedirs('data/sources/mjna', exist_ok=True)
    
    # We will do batches to avoid killing the server
    batch_size = 50
    results = [None] * count
    
    async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            tasks = []
            for i in range(batch_start, batch_end):
                tasks.append(fetch_page(session, book, i))
            
            batch_results = await asyncio.gather(*tasks)
            for j, res in enumerate(batch_results):
                results[batch_start + j] = res
            print(f"{book}: {batch_end}/{count}")
            await asyncio.sleep(0.5)
            
    with open(out_file, 'w', encoding='utf-8') as f:
        valid = 0
        for res in results:
            if res:
                f.write(json.dumps(res, ensure_ascii=False) + '\n')
                valid += 1
    print(f"Done {book}, saved {valid}/{count} to {out_file}")

async def main():
    for book, count in BOOKS.items():
        await scrape_book(book, count)

if __name__ == '__main__':
    asyncio.run(main())
