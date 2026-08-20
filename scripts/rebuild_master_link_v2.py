import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")

def rebuild_master_link():
    print("[*] Rebuilding master_link.json using AhmedBaset as the universal anchor...")
    
    books_path = os.path.join(BASE_DIR, "data", "books_v2.json")
    with open(books_path, 'r', encoding='utf-8') as f:
        books_registry = json.load(f)
        
    master_link = {}
    
    AB_PATHS = {
        "bukhari": "the_9_books/bukhari.json",
        "muslim": "the_9_books/muslim.json",
        "abudawud": "the_9_books/abudawud.json",
        "tirmidhi": "the_9_books/tirmidhi.json",
        "nasai": "the_9_books/nasai.json",
        "ibnmajah": "the_9_books/ibnmajah.json",
        "malik": "the_9_books/malik.json",
        "darimi": "the_9_books/darimi.json",
        "ahmad": "the_9_books/ahmed.json",
        "qudsi": "forties/qudsi40.json",
        "shah": "forties/shahwaliullah40.json",
        "adab": "other_books/aladab_almufrad.json",
        "bulugh": "other_books/bulugh_almaram.json",
        "mishkat": "other_books/mishkat_almasabih.json",
        "riyad": "other_books/riyad_assalihin.json",
        "shamail": "other_books/shamail_muhammadiyah.json",
        "nawawi": "forties/nawawi40.json"
    }

    for book_obj in books_registry:
        book_id = book_obj['id']
        master_link[book_id] = {}
        
        ab_rel = AB_PATHS.get(book_id)
        if not ab_rel:
            print(f"  -> {book_id}: No known AhmedBaset data found, skipping.")
            continue
            
        print(f"  -> {book_id}: Using AhmedBaset as anchor")
        ab_path = os.path.join(SOURCES_DIR, "ahmedbaset", "by_book", ab_rel)
        if not os.path.exists(ab_path):
            print(f"     [!] File not found: {ab_path}")
            continue
            
        with open(ab_path, 'r', encoding='utf-8') as f:
            ab_data = json.load(f).get('hadiths', [])
            
        # Load Lidwa links
        lidwa_links = {}
        # Core 9 books are in relinked_ab
        core_link_path = os.path.join(LINKS_DIR, "relinked_ab", f"{book_id}.json")
        # Other books are in links (created by Phase 2 cross linker)
        other_link_path = os.path.join(LINKS_DIR, f"{book_id}.json")
        
        if os.path.exists(core_link_path):
            with open(core_link_path, 'r', encoding='utf-8') as f:
                lidwa_links = json.load(f)
        elif os.path.exists(other_link_path):
            with open(other_link_path, 'r', encoding='utf-8') as f:
                # Other books links are in format {ahmedbaset_id: {lidwa_id: ...}}
                lidwa_links = json.load(f)
                
        # Load Lidwa to get hnum and rawis
        lidwa_hnums = {}
        lidwa_rawis = {}
        lidwa_path = os.path.join(SOURCES_DIR, "lidwa", f"{book_id}.json")
        if os.path.exists(lidwa_path):
            with open(lidwa_path, 'r', encoding='utf-8') as f:
                ld = json.load(f)
                for r in ld:
                    l_id = str(r.get('id', ''))
                    lidwa_hnums[l_id] = str(r.get('hadith_number', l_id))
                    lidwa_rawis[l_id] = r.get('kaggle_narrators', [])
                    
        for row in ab_data:
            ab_id = str(row.get('hadithnumber', row.get('idInBook', row.get('id', ''))))
            
            # Find the lidwa link
            link_obj = lidwa_links.get(ab_id, {})
            # It could be the obj itself has 'lidwa_id' or it is just lidwa_id string
            lidwa_id = None
            if isinstance(link_obj, dict):
                lidwa_id = str(link_obj.get('lidwa_id')) if link_obj.get('lidwa_id') else None
            elif isinstance(link_obj, str):
                lidwa_id = link_obj
            elif isinstance(link_obj, int):
                lidwa_id = str(link_obj)
                
            lidwa_hnum = lidwa_hnums.get(str(lidwa_id)) if lidwa_id else None
            rawis = lidwa_rawis.get(str(lidwa_id), []) if lidwa_id else []
            
            master_link[book_id][ab_id] = {
                "anchor_source": "ahmedbaset",
                "ahmedbaset_id": ab_id,
                "lidwa_id": lidwa_id,
                "lidwa_hnum": lidwa_hnum,
                "kaggle_narrators": rawis
            }

    out_path = os.path.join(LINKS_DIR, "master_link.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(master_link, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Rebuild complete. Master links written to {out_path}")

if __name__ == "__main__":
    rebuild_master_link()
