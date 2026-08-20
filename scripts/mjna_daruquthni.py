import aiohttp
import asyncio
import json
import os
from bs4 import BeautifulSoup

async def fetch_hadith(session, hadith_number):
    url = f"https://www.mjna.or.id/daruquthni/hadits/{hadith_number}"
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            arabic_p = soup.find('p', class_='arabic2')
            latin_p = soup.find('p', class_='latin')
            
            if not arabic_p or not latin_p:
                return None
                
            return {
                'hadith_number': hadith_number,
                'id': str(hadith_number),
                'chapter_id': "1",
                'text_ar': arabic_p.text.strip(),
                'text_id': latin_p.text.strip(),
                'text_en': ""
            }
    except Exception as e:
        print(f"Error on {hadith_number}: {e}")
        return None

async def scrape_all():
    os.makedirs('data/sources/mjna', exist_ok=True)
    out_file = 'data/sources/mjna/daruquthni.ndjson'
    
    async with aiohttp.ClientSession() as session:
        # Batch size of 100 to avoid overwhelming
        with open(out_file, 'w', encoding='utf-8') as f:
            for i in range(1, 4791, 50):
                tasks = []
                for j in range(i, min(i+50, 4791)):
                    tasks.append(fetch_hadith(session, j))
                
                results = await asyncio.gather(*tasks)
                for r in results:
                    if r:
                        f.write(json.dumps(r, ensure_ascii=False) + '\n')
                print(f"Done up to {min(i+49, 4790)}/4790")

if __name__ == '__main__':
    asyncio.run(scrape_all())
