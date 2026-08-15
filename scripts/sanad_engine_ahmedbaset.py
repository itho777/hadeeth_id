import os
import json
import sys
from sanad_engine import build_scholar_index, extract_isnad, extract_names_from_isnad, normalize_arabic

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AB_BOOKS_DIR = os.path.join(BASE_DIR, "data", "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")

ADDITIONAL_BOOKS = {
    "qudsi": "forties/qudsi40.json",
    "shah": "forties/shahwaliullah40.json",
    "adab": "other_books/aladab_almufrad.json",
    "bulugh": "other_books/bulugh_almaram.json",
    "mishkat": "other_books/mishkat_almasabih.json",
    "riyad": "other_books/riyad_assalihin.json",
    "shamail": "other_books/shamail_muhammadiyah.json"
}

def process_ahmedbaset_sanad():
    print("[*] Loading Scholar Index...")
    scholar_index = build_scholar_index()
    print(f"[+] Loaded {len(scholar_index)} searchable name variations.")
    
    for book_id, ab_path in ADDITIONAL_BOOKS.items():
        print(f"[*] Processing Sanad for {book_id}...")
        
        link_path = os.path.join(LINKS_DIR, f"{book_id}.json")
        if not os.path.exists(link_path):
            continue
            
        with open(link_path, 'r', encoding='utf-8') as f:
            links = json.load(f)
            
        ab_full_path = os.path.join(AB_BOOKS_DIR, ab_path)
        with open(ab_full_path, 'r', encoding='utf-8') as f:
            ab_data = json.load(f)
            
        matched_count = 0
        for row in ab_data.get('hadiths', []):
            hid = str(row['idInBook'])
            text_ar = row.get('arabic', '')
            
            narrators = []
            if text_ar:
                isnad = extract_isnad(text_ar)
                raw_names = extract_names_from_isnad(isnad)
                
                for name in raw_names:
                    norm_name = name.replace('رضي الله عنه', '').replace('رحمه الله', '').strip()
                    sid = scholar_index.get(norm_name)
                    if not sid:
                        words = norm_name.split()
                        if len(words) >= 3:
                            sid = scholar_index.get(" ".join(words[:3]))
                        if not sid and len(words) >= 2:
                            sid = scholar_index.get(" ".join(words[:2]))
                    if sid:
                        narrators.append(sid)
                        
            if narrators:
                matched_count += 1
                
            if hid in links:
                links[hid]['kaggle_narrators'] = narrators
                
        with open(link_path, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
            
        print(f"[+] {book_id}: Found Sanad links for {matched_count} hadiths.")

if __name__ == "__main__":
    process_ahmedbaset_sanad()
