import os
import sys
import json
import time
import cloudscraper
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

COMMENTARIES_DIR = os.path.join("data", "commentaries", "en")
os.makedirs(COMMENTARIES_DIR, exist_ok=True)

# Define the books and their URL parameters
BOOKS = {
    'bukhari': {
        'panel': 'panel-1',
        'param': 'page',
        'total_hadiths': 1356,
        'per_page': 15,
        'pages': 91
    },
    'muslim': {
        'panel': 'panel-2',
        'param': 'muslim-page',
        'total_hadiths': 558,
        'per_page': 15,
        'pages': 38
    },
    'abudawud': {
        'panel': 'panel-3',
        'param': 'AbuDawud-page',
        'total_hadiths': 67,
        'per_page': 15,
        'pages': 5
    },
    'tirmidhi': {
        'panel': 'panel-4',
        'param': 'Tirmidhi-page',
        'total_hadiths': 10,
        'per_page': 15,
        'pages': 1
    },
    'ibnmajah': {
        'panel': 'panel-5',
        'param': 'IbnMajah-page',
        'total_hadiths': 25,
        'per_page': 15,
        'pages': 2
    }
}

def scrape_book(scraper, book_id, info):
    print(f"\n[*] Scraping EN Syarah for {book_id}...")
    
    for page in range(1, info['pages'] + 1):
        url = f"https://dorar.net/en/ahadith?activeTab={info['panel']}&{info['param']}={page}"
        print(f"  -> Fetching page {page}/{info['pages']} ...")
        
        try:
            res = scraper.get(url, timeout=15)
            if res.status_code != 200:
                print(f"     [ERROR] Status {res.status_code}")
                time.sleep(5)
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            panel = soup.find('div', id=info['panel'])
            if not panel:
                print(f"     [ERROR] Could not find {info['panel']}")
                continue
                
            cards = panel.find_all('div', class_='card')
            
            for card in cards:
                # Find hadith number
                num_tag = card.find('div', class_='custom_number')
                if not num_tag: continue
                hadith_num = num_tag.get_text(strip=True)
                
                # Find text
                h5_tag = card.find('h5')
                hadith_text = h5_tag.get_text(strip=True) if h5_tag else ""
                
                # Find commentary
                p_tag = card.find('p', class_='card-text')
                syarah_text = ""
                if p_tag:
                    # Remove the "Commentary :" prefix
                    for strong in p_tag.find_all('strong'):
                        strong.decompose()
                    syarah_text = p_tag.get_text(strip=True)
                
                out_path = os.path.join(COMMENTARIES_DIR, f"{book_id}_{hadith_num}.json")
                payload = {
                    "book_id": book_id,
                    "hadith_num": hadith_num,
                    "hadith_en": hadith_text,
                    "syarah_en": syarah_text
                }
                
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                    
            # Gentle delay
            time.sleep(2)
            
        except Exception as e:
            print(f"     [ERROR] {e}")
            time.sleep(5)

def main():
    print("[*] Starting Dorar EN Scraper...")
    scraper = cloudscraper.create_scraper()
    for book_id, info in BOOKS.items():
        scrape_book(scraper, book_id, info)
    print("\n[*] Finished scraping all EN Syarah!")

if __name__ == "__main__":
    main()
