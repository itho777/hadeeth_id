import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
import re

async def scrape_chapters():
    url = "https://www.mjna.or.id/daruquthni/index/1"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            chapters = []
            
            for a in soup.find_all('a', href=True):
                if '/bab/' in a['href']:
                    href = a['href']
                    bab_id = re.search(r'/bab/(\d+)', href).group(1)
                    title = a.text.strip()
                    
                    chapters.append({
                        'chapter_id': str(bab_id),
                        'title_en': title,
                        'title_id': title,
                        'url': href,
                        'hadiths': []
                    })
                    
            print(f"Found {len(chapters)} chapters.")
            
            # Now fetch each chapter to get its hadiths
            for ch in chapters:
                async with session.get(ch['url']) as resp:
                    ch_html = await resp.text()
                    ch_soup = BeautifulSoup(ch_html, 'html.parser')
                    for a in ch_soup.find_all('a', href=True):
                        if '/hadits/' in a['href']:
                            match = re.search(r'/hadits/(\d+)', a['href'])
                            if match:
                                ch['hadiths'].append(int(match.group(1)))
                print(f"Chapter {ch['chapter_id']} has {len(ch['hadiths'])} hadiths.")
            
            with open('data/sources/mjna/daruquthni_chapters.json', 'w', encoding='utf-8') as f:
                json.dump(chapters, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    asyncio.run(scrape_chapters())
