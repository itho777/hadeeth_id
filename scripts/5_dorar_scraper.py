import os
import json
import time
import urllib.parse
import logging
import cloudscraper
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAWAZ_DIR = os.path.join(DATA_DIR, "editions")
AHMEDBASET_DIR = os.path.join(DATA_DIR, "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(DATA_DIR, "links")
COMMENTARIES_DIR = os.path.join(DATA_DIR, "commentaries")

os.makedirs(COMMENTARIES_DIR, exist_ok=True)

AB_PATHS = {
    "qudsi": "forties/qudsi40.json",
    "shah": "forties/shahwaliullah40.json",
    "adab": "other_books/aladab_almufrad.json",
    "bulugh": "other_books/bulugh_almaram.json",
    "mishkat": "other_books/mishkat_almasabih.json",
    "riyad": "other_books/riyad_assalihin.json",
    "shamail": "other_books/shamail_muhammadiyah.json"
}

def search_dorar(scraper, text_ar):
    words = text_ar.split()
    # Try different slices of the text to bypass the sanad
    search_queries = [
        " ".join(words[:6]),
        " ".join(words[5:11]) if len(words) > 10 else None,
        " ".join(words[-6:]) if len(words) > 6 else None
    ]
    
    for query in search_queries:
        if not query: continue
        url = f"https://www.dorar.net/hadith/search?q={urllib.parse.quote(query)}"
        try:
            response = scraper.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            xplain_tag = soup.find('a', attrs={'xplain': True})
            if xplain_tag:
                return xplain_tag['xplain']
        except Exception as e:
            logging.error(f"Search failed: {e}")
    return None

def fetch_explanation(scraper, xplain_id):
    url = f"https://dorar.net/hadith/sharh/{xplain_id}"
    try:
        response = scraper.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "hadith_ar": "",
            "rawi": "",
            "muhaddith": "",
            "masdar": "",
            "grade": "",
            "takhrij": "",
            "syarah_ar": "Not Available"
        }
        
        sharh_content = soup.find('div', id='sharh-text-content')
        if sharh_content:
            first_div = sharh_content.find('div')
            if first_div:
                text_div = first_div.find('div')
                if text_div:
                    result["hadith_ar"] = text_div.get_text(strip=True)
                    
            for span in sharh_content.find_all('span'):
                classes = span.get('class', [])
                if '#ae8422' in classes or span.get('style', '') == 'color: #ae8422':
                    prev = span.previous_sibling
                    if prev and isinstance(prev, str):
                        if "الراوي" in prev: result["rawi"] = span.get_text(strip=True)
                        if "المحدث" in prev and "خلاصة" not in prev: result["muhaddith"] = span.get_text(strip=True)
                        if "المصدر" in prev: result["masdar"] = span.get_text(strip=True)
                        if "خلاصة" in prev: result["grade"] = span.get_text(strip=True)
                        
            takhrij_p = sharh_content.find('p')
            if takhrij_p and "التخريج" in takhrij_p.get_text():
                span = takhrij_p.find('span')
                if span:
                    result["takhrij"] = span.get_text(strip=True)
            
            if first_div:
                syarah_parts = []
                for sibling in first_div.next_siblings:
                    if sibling.name:
                        syarah_parts.append(sibling.get_text(separator='\n\n', strip=True))
                    elif str(sibling).strip():
                        syarah_parts.append(str(sibling).strip())
                result["syarah_ar"] = "\n\n".join(filter(None, syarah_parts))
                
            return result
        
        # Fallback to old logic
        tj = soup.find('div', class_='text-justify')
        if tj:
            ns = tj.find_next_sibling()
            if ns:
                full_text = ns.get_text(separator='\n\n', strip=True)
                parts = full_text.split('التخريج :')
                if len(parts) > 1:
                    lines = parts[-1].split('\n\n')
                    sharh_text = "\n\n".join(lines[1:]).strip()
                    if not sharh_text:
                        sharh_text = parts[-1].strip()
                    result["syarah_ar"] = sharh_text
                else:
                    result["syarah_ar"] = full_text
        return result
    except Exception as e:
        logging.error(f"Fetch explanation failed: {e}")
        return None

def scrape_syarah():
    print("[*] Starting Dorar Syarah JSON Scraper...")
    scraper = cloudscraper.create_scraper(browser='chrome')
    
    with open(os.path.join(DATA_DIR, 'books_v2.json'), 'r', encoding='utf-8') as f:
        books = json.load(f)
        
    for b in books:
        book_id = b['id']
        print(f"\n[*] Processing {book_id}...")
        
        # Determine if Anchor is Fawaz or AhmedBaset
        fawaz_path = os.path.join(FAWAZ_DIR, f"ara-{book_id}.json")
        anchor_data = []
        is_fawaz = False
        
        if os.path.exists(fawaz_path):
            with open(fawaz_path, 'r', encoding='utf-8') as f:
                fd = json.load(f)
                anchor_data = fd.get('hadiths', []) if isinstance(fd, dict) else fd
                is_fawaz = True
        elif book_id in AB_PATHS:
            ab_path = os.path.join(AHMEDBASET_DIR, AB_PATHS[book_id])
            if os.path.exists(ab_path):
                with open(ab_path, 'r', encoding='utf-8') as f:
                    ad = json.load(f)
                    anchor_data = ad.get('hadiths', []) if isinstance(ad, dict) else ad
                    
        if not anchor_data:
            continue
            
        for row in anchor_data:
            anchor_id = str(row.get('hadithnumber', row.get('id'))) if is_fawaz else str(row.get('idInBook', row.get('id')))
            text_ar = row.get('text', row.get('arabic', ''))
            
            if not text_ar: continue
            
            syarah_path = os.path.join(COMMENTARIES_DIR, f"{book_id}_{anchor_id}.json")
            if os.path.exists(syarah_path):
                continue # Skip if already downloaded!
                
            logging.info(f"Scraping Syarah for {book_id} - {anchor_id}")
            
            xplain_id = search_dorar(scraper, text_ar)
            extracted_data = None
            if xplain_id:
                extracted_data = fetch_explanation(scraper, xplain_id)
                    
            syarah_payload = {
                "book_id": book_id,
                "anchor_id": anchor_id,
                "source": "Dorar"
            }
            if extracted_data:
                syarah_payload.update(extracted_data)
            else:
                syarah_payload["syarah_ar"] = "Not Available"
            
            with open(syarah_path, 'w', encoding='utf-8') as f:
                json.dump(syarah_payload, f, ensure_ascii=False, indent=2)
                
            # Be nice to Dorar servers to prevent IP bans
            time.sleep(3)

if __name__ == "__main__":
    scrape_syarah()
