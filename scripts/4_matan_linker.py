import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
FAWAZ_DIR = os.path.join(BASE_DIR, "data", "editions")
AHMEDBASET_DIR = os.path.join(BASE_DIR, "data", "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
BOOKS_V2 = os.path.join(BASE_DIR, "data", "books_v2.json")
MASTER_LINK = os.path.join(LINKS_DIR, "master_link.json")

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
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\uFEFF]', '', text)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[\u0625\u0623\u0622\u0627]', '\u0627', text)
    text = re.sub(r'[\u0629]', '\u0647', text)
    text = re.sub(r'[\u0649]', '\u064A', text)
    text = re.sub(r'[\W_]+', '', text)
    return text

def extract_matan(text):
    norm = normalize_arabic(text)
    if not norm: return ""
    markers = ["\u0642\u0627\u0644\u0631\u0633\u0648\u0644\u0627\u0644\u0644\u0647", "\u0633\u0645\u0639\u062a\u0631\u0633\u0648\u0644\u0627\u0644\u0644\u0647", "\u0639\u0646\u0627\u0644\u0646\u0628\u0649", "\u064a\u0642\u0648\u0644\u0631\u0633\u0648\u0644\u0627\u0644\u0644\u0647", "\u0627\u0646\u0631\u0633\u0648\u0644\u0627\u0644\u0644\u0647", "\u0639\u0646\u0631\u0633\u0648\u0644\u0627\u0644\u0644\u0647", "\u0642\u0627\u0644\u0627\u0644\u0646\u0628\u0649", "\u0633\u0645\u0639\u062a\u0627\u0644\u0646\u0628\u0649"]
    min_idx = len(norm)
    for m in markers:
        idx = norm.find(m)
        if idx != -1 and idx < min_idx:
            min_idx = idx
            
    if min_idx == len(norm):
        return norm # Fallback, return whole text
    return norm[min_idx:]

def build_graph():
    print("[*] Starting Matan Secondary Cross-Linker...")
    
    with open(BOOKS_V2, 'r', encoding='utf-8') as f:
        books_registry = json.load(f)
        
    with open(MASTER_LINK, 'r', encoding='utf-8') as f:
        master_link = json.load(f)

    for book_obj in books_registry:
        book = book_obj['id']
        print(f"\n -> Processing {book}...")
        
        if book not in master_link:
            continue
            
        link_path = os.path.join(LINKS_DIR, f"{book}.json")
        if not os.path.exists(link_path):
            continue
            
        with open(link_path, 'r', encoding='utf-8') as f:
            book_graph = json.load(f)
            
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
                
        anchor_data = fawaz_data if len(fawaz_data) > 0 else ab_data
        anchor_source = 'fawaz' if len(fawaz_data) > 0 else 'ab'
        if not anchor_data:
            continue

        def get_fawaz_ar(row): return row.get('text')
        def get_fawaz_id(row): return str(row.get('hadithnumber', row.get('id')))
        def get_ab_ar(row): return row.get('arabic')
        def get_ab_id(row): return str(row.get('idInBook', row.get('id')))
        def get_lidwa_ar(row): return row.get('text_ar')
        def get_lidwa_id(row): return str(row.get('hadith_number', row.get('id')))

        get_anchor_ar = get_fawaz_ar if anchor_source == 'fawaz' else get_ab_ar
        get_anchor_id = get_fawaz_id if anchor_source == 'fawaz' else get_ab_id
        
        # Build Matan index for Unlinked Anchors
        anchor_matan_prefix = {}
        unlinked_anchor_count = 0
        
        for h in anchor_data:
            a_id = get_anchor_id(h)
            ml_data = master_link[book].get(a_id, {})
            # Is it unlinked for Lidwa? Or unlinked for AB?
            has_lidwa = ml_data.get('lidwa_id') is not None
            has_ab = ml_data.get('ahmedbaset_id') is not None
            
            # If it's missing either, we will index its Matan
            if (lidwa_data and not has_lidwa) or (ab_data and not has_ab):
                matan = extract_matan(get_anchor_ar(h))
                if matan:
                    if len(matan) >= 40:
                        anchor_matan_prefix[matan[:40]] = a_id
                    else:
                        anchor_matan_prefix[matan] = a_id
                    unlinked_anchor_count += 1
                    
        print(f"    Indexed {unlinked_anchor_count} unlinked Anchor Matans.")
        
        def patch_graph(target_data, get_target_ar, get_target_id, target_name):
            linked_target_ids = set()
            for key in [f"{anchor_source}_to_{target_name}", f"{target_name}_to_{anchor_source}"]:
                if key not in book_graph:
                    book_graph[key] = {}
            
            # Find which target IDs are already linked
            for a_id, t_id in book_graph[f"{anchor_source}_to_{target_name}"].items():
                linked_target_ids.add(str(t_id))
                
            rescued = 0
            for t_row in target_data:
                t_id = get_target_id(t_row)
                if t_id in linked_target_ids:
                    continue
                    
                t_matan = extract_matan(get_target_ar(t_row))
                if not t_matan: continue
                
                matched_a_id = anchor_matan_prefix.get(t_matan[:40]) if len(t_matan) >= 40 else anchor_matan_prefix.get(t_matan)
                
                if matched_a_id and matched_a_id not in book_graph[f"{anchor_source}_to_{target_name}"]:
                    book_graph[f"{anchor_source}_to_{target_name}"][matched_a_id] = t_id
                    book_graph[f"{target_name}_to_{anchor_source}"][t_id] = matched_a_id
                    rescued += 1
                    
            print(f"    {target_name.capitalize()} rescued via Matan: {rescued}")
            
        if lidwa_data:
            patch_graph(lidwa_data, get_lidwa_ar, get_lidwa_id, 'lidwa')
            
        if anchor_source == 'fawaz' and ab_data:
            patch_graph(ab_data, get_ab_ar, get_ab_id, 'ab')
            
        with open(link_path, 'w', encoding='utf-8') as f:
            json.dump(book_graph, f, indent=2)

    print("\n[+] Matan Link Engine finished!")

if __name__ == "__main__":
    build_graph()
