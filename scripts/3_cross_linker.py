import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
FAWAZ_DIR = os.path.join(BASE_DIR, "data", "editions")
AHMEDBASET_DIR = os.path.join(BASE_DIR, "data", "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
BOOKS_V2 = os.path.join(BASE_DIR, "data", "books_v2.json")

# Ahmedbaset relative paths mapping
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
    "nawawi": "forties/nawawi.json"
}

def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'[ة]', 'ه', text)
    text = re.sub(r'[ى]', 'ي', text)
    text = re.sub(r'[\W_]+', '', text)
    return text

def build_graph():
    os.makedirs(LINKS_DIR, exist_ok=True)

    print("[*] Starting Enhanced Cross-Linker (Dynamic Tripartite Graph)...")
    
    with open(BOOKS_V2, 'r', encoding='utf-8') as f:
        books_registry = json.load(f)

    for book_obj in books_registry:
        book = book_obj['id']
        print(f" -> Processing {book}...")
        
        lidwa_path = os.path.join(LIDWA_DIR, f"{book}.json")
        fawaz_path = os.path.join(FAWAZ_DIR, f"ara-{book}.json")
        
        ab_rel_path = AB_PATHS.get(book)
        ab_path = os.path.join(AHMEDBASET_DIR, ab_rel_path) if ab_rel_path else None

        fawaz_data = []
        if os.path.exists(fawaz_path):
            with open(fawaz_path, 'r', encoding='utf-8') as f:
                fd = json.load(f)
                fawaz_data = fd.get('hadiths', []) if isinstance(fd, dict) else fd
                
        ab_data = []
        if ab_path and os.path.exists(ab_path):
            with open(ab_path, 'r', encoding='utf-8') as f:
                ad = json.load(f)
                ab_data = ad.get('hadiths', []) if isinstance(ad, dict) else ad
                
        lidwa_data = []
        if os.path.exists(lidwa_path):
            with open(lidwa_path, 'r', encoding='utf-8') as f:
                lidwa_data = json.load(f)
                
        # Determine anchor
        if len(fawaz_data) > 0:
            print(f"    Anchor: Fawazahmed0 ({len(fawaz_data)} hadiths)")
            anchor_data = fawaz_data
            anchor_source = 'fawaz'
            
            def get_ar(row): return row.get('text')
            def get_id(row): return str(row.get('hadithnumber', row.get('id')))
            
        elif len(ab_data) > 0:
            print(f"    Anchor: AhmedBaset ({len(ab_data)} hadiths)")
            anchor_data = ab_data
            anchor_source = 'ab'
            
            def get_ar(row): return row.get('arabic')
            def get_id(row): return str(row.get('idInBook', row.get('id')))
        else:
            print(f"    No Anchor found for {book}, skipping.")
            continue
            
        # Build Anchor Hashes
        anchor_prefix = {}
        anchor_suffix = {}
        for h in anchor_data:
            ar_text = normalize_arabic(get_ar(h))
            if not ar_text: continue
            hid = get_id(h)
            if len(ar_text) >= 40:
                anchor_prefix[ar_text[:40]] = hid
                anchor_suffix[ar_text[-40:]] = hid
            else:
                anchor_prefix[ar_text] = hid

        book_graph = {}
        
        def map_to_anchor(target_data, get_target_ar, get_target_id, target_name):
            anchor_to_target = {}
            target_to_anchor = {}
            for t_row in target_data:
                t_id = get_target_id(t_row)
                t_text = normalize_arabic(get_target_ar(t_row))
                if not t_text: continue
                
                matched_a_id = anchor_prefix.get(t_text[:40]) if len(t_text) >= 40 else anchor_prefix.get(t_text)
                if not matched_a_id and len(t_text) >= 40:
                    matched_a_id = anchor_suffix.get(t_text[-40:])
                    
                if matched_a_id:
                    anchor_to_target[matched_a_id] = t_id
                    target_to_anchor[t_id] = matched_a_id
                    
            book_graph[f"{anchor_source}_to_{target_name}"] = anchor_to_target
            book_graph[f"{target_name}_to_{anchor_source}"] = target_to_anchor
            print(f"    {target_name.capitalize()} mapped: {len(anchor_to_target)}")

        # 1. Map Lidwa
        if lidwa_data:
            map_to_anchor(
                lidwa_data,
                lambda row: row.get('text_ar'),
                lambda row: str(row.get('hadith_number', row.get('id'))),
                'lidwa'
            )
            
        # 2. Map other if anchor is Fawaz
        if anchor_source == 'fawaz' and ab_data:
            map_to_anchor(
                ab_data,
                lambda row: row.get('arabic'),
                lambda row: str(row.get('idInBook', row.get('id'))),
                'ab'
            )
            
        out_path = os.path.join(LINKS_DIR, f"{book}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(book_graph, f, indent=2)

    print(f"[+] Link Engine finished! Saved dynamic graphs to {LINKS_DIR}")

if __name__ == "__main__":
    build_graph()
