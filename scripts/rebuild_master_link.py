import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")
EDITIONS_DIR = os.path.join(BASE_DIR, "data", "editions")

def rebuild_master_link():
    print("[*] Rebuilding master_link.json using largest dataset anchor...")
    
    # Load all books
    books_path = os.path.join(BASE_DIR, "data", "books_v2.json")
    with open(books_path, 'r', encoding='utf-8') as f:
        books_registry = json.load(f)
        
    master_link = {}
    
    # Additional 8 paths mapping
    AB_PATHS = {
        "qudsi": "forties/qudsi40.json",
        "shah": "forties/shahwaliullah40.json",
        "adab": "other_books/aladab_almufrad.json",
        "bulugh": "other_books/bulugh_almaram.json",
        "mishkat": "other_books/mishkat_almasabih.json",
        "riyad": "other_books/riyad_assalihin.json",
        "shamail": "other_books/shamail_muhammadiyah.json",
        "nawawi": "forties/nawawi.json"
    }

    for book_obj in books_registry:
        book_id = book_obj['id']
        master_link[book_id] = {}
        
        fawaz_path = os.path.join(EDITIONS_DIR, f"ara-{book_id}.json")
        link_path = os.path.join(LINKS_DIR, f"{book_id}.json")
        
        if os.path.exists(fawaz_path):
            print(f"  -> {book_id}: Using Fawazahmed0 as anchor")
            with open(fawaz_path, 'r', encoding='utf-8') as f:
                fawaz_data = json.load(f)
                if 'hadiths' in fawaz_data:
                    fawaz_data = fawaz_data['hadiths']
                    
            links_data = {}
            if os.path.exists(link_path):
                with open(link_path, 'r', encoding='utf-8') as f:
                    links_data = json.load(f)
                    
            f_to_l = links_data.get('fawaz_to_lidwa', {})
            f_to_ab = links_data.get('fawaz_to_ab', {})
            f_to_rawis = links_data.get('fawaz_to_rawis', {})
            
            # Load Lidwa to get hnum
            lidwa_hnums = {}
            lidwa_path = os.path.join(SOURCES_DIR, "lidwa", f"{book_id}.json")
            if os.path.exists(lidwa_path):
                with open(lidwa_path, 'r', encoding='utf-8') as f:
                    ld = json.load(f)
                    for r in ld:
                        lidwa_hnums[str(r.get('id', ''))] = str(r.get('hadith_number', r.get('id')))
                        
            for row in fawaz_data:
                fawaz_id = str(row.get('hadithnumber', row.get('id')))
                lidwa_id = f_to_l.get(fawaz_id)
                lidwa_hnum = lidwa_hnums.get(str(lidwa_id)) if lidwa_id else None
                ab_id = f_to_ab.get(fawaz_id)
                rawis = f_to_rawis.get(fawaz_id, [])
                
                master_link[book_id][fawaz_id] = {
                    "anchor_source": "fawazahmed0",
                    "fawaz_id": fawaz_id,
                    "lidwa_id": lidwa_id,
                    "lidwa_hnum": lidwa_hnum,
                    "ahmedbaset_id": ab_id,
                    "kaggle_narrators": rawis
                }
                
        else:
            # AhmedBaset anchor
            ab_rel = AB_PATHS.get(book_id)
            if not ab_rel:
                print(f"  -> {book_id}: No known anchor data found, skipping.")
                continue
                
            print(f"  -> {book_id}: Using AhmedBaset as anchor")
            ab_path = os.path.join(SOURCES_DIR, "ahmedbaset", "by_book", ab_rel)
            if not os.path.exists(ab_path):
                continue
                
            with open(ab_path, 'r', encoding='utf-8') as f:
                ab_data = json.load(f).get('hadiths', [])
                
            for row in ab_data:
                ab_id = str(row.get('idInBook'))
                master_link[book_id][ab_id] = {
                    "anchor_source": "ahmedbaset",
                    "fawaz_id": None,
                    "lidwa_id": None,
                    "lidwa_hnum": None,
                    "ahmedbaset_id": ab_id,
                    "kaggle_narrators": [] # Not currently extracted for Additional 8
                }

    out_path = os.path.join(LINKS_DIR, "master_link.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(master_link, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Rebuild complete. Master links written to {out_path}")

if __name__ == "__main__":
    rebuild_master_link()
