import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AB_BOOKS_DIR = os.path.join(BASE_DIR, "data", "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")

# Map of UI Book ID -> Native AhmedBaset File path
ADDITIONAL_BOOKS = {
    "qudsi": "forties/qudsi40.json",
    "shah": "forties/shahwaliullah40.json",
    "adab": "other_books/aladab_almufrad.json",
    "bulugh": "other_books/bulugh_almaram.json",
    "mishkat": "other_books/mishkat_almasabih.json",
    "riyad": "other_books/riyad_assalihin.json",
    "shamail": "other_books/shamail_muhammadiyah.json"
}

def generate_links():
    os.makedirs(LINKS_DIR, exist_ok=True)
    
    for book_id, ab_path in ADDITIONAL_BOOKS.items():
        print(f"[*] Processing {book_id}...")
        full_path = os.path.join(AB_BOOKS_DIR, ab_path)
        if not os.path.exists(full_path):
            print(f"[!] File not found: {full_path}")
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            ab_data = json.load(f)
            
        links = {}
        for row in ab_data.get('hadiths', []):
            hid = str(row['idInBook'])
            links[hid] = {
                "anchor_source": "ahmedbaset",
                "ahmedbaset_id": int(hid),
                "kaggle_narrators": [],
                "has_syarah": False
            }
            
        out_path = os.path.join(LINKS_DIR, f"{book_id}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
            
        print(f"[+] {book_id}: Generated {len(links)} links.")

if __name__ == "__main__":
    generate_links()
