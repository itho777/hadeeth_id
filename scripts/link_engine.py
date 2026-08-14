import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")

CORE_9 = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]
ADDITIONAL_8 = ["forties/nawawi", "forties/qudsi", "forties/shah", "other_books/adab", "other_books/bulugh", "other_books/mishkat", "other_books/riyad", "other_books/shamail"]

def normalize_arabic(text):
    if not text:
        return ""
    # Remove all diacritics (tashkeel)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    # Normalize alef
    text = re.sub(r'[إأآا]', 'ا', text)
    # Remove tatweel, spaces, punctuation for dense matching
    text = re.sub(r'[\W_]+', '', text)
    return text

def build_links():
    os.makedirs(LINKS_DIR, exist_ok=True)
    master_link = {}

    print("[*] Starting Link Engine...")

    # 1. Process Core 9 (Lidwa as Anchor)
    for book in CORE_9:
        print(f"  -> Processing Core 9 Book: {book}")
        master_link[book] = {}
        
        lidwa_path = os.path.join(SOURCES_DIR, "lidwa", f"{book}.json")
        ab_path = os.path.join(SOURCES_DIR, "ahmedbaset", "by_book", "the_9_books", f"{book}.json")
        
        if not os.path.exists(lidwa_path):
            continue
            
        with open(lidwa_path, 'r', encoding='utf-8') as f:
            lidwa_data = json.load(f)
            
        ab_data = []
        if os.path.exists(ab_path):
            with open(ab_path, 'r', encoding='utf-8') as f:
                ab_data = json.load(f).get('hadiths', [])
                
        # Build searchable O(1) index for AhmedBaset using Prefix and Suffix hashes
        ab_prefix = {}
        ab_suffix = {}
        for h in ab_data:
            if h.get('arabic'):
                ab_ar = normalize_arabic(h['arabic'])
                if len(ab_ar) >= 30:
                    ab_prefix[ab_ar[:30]] = h['idInBook']
                    ab_suffix[ab_ar[-30:]] = h['idInBook']
                else:
                    ab_prefix[ab_ar] = h['idInBook']

        for row in lidwa_data:
            h_num = str(row.get('hadith_number'))
            dar_num = str(row.get('darussalam_number'))
            anchor_id = h_num if h_num else dar_num
            
            if not anchor_id:
                continue
                
            lidwa_ar = normalize_arabic(row.get('text_ar', ''))
            
            matched_ab_id = None
            if lidwa_ar:
                # Try prefix
                if len(lidwa_ar) >= 30:
                    matched_ab_id = ab_prefix.get(lidwa_ar[:30])
                    # Try suffix if prefix fails
                    if not matched_ab_id:
                        matched_ab_id = ab_suffix.get(lidwa_ar[-30:])
                else:
                    matched_ab_id = ab_prefix.get(lidwa_ar)
            
            
            master_link[book][anchor_id] = {
                "anchor_source": "lidwa",
                "lidwa_id": row.get('id'), # internal sql id
                "lidwa_hnum": h_num,
                "ahmedbaset_id": matched_ab_id
            }

    # 2. Process Additional 8 (AhmedBaset as Anchor)
    for book_path in ADDITIONAL_8:
        book = book_path.split("/")[-1]
        print(f"  -> Processing Additional 8 Book: {book}")
        master_link[book] = {}
        
        ab_path = os.path.join(SOURCES_DIR, "ahmedbaset", "by_book", book_path + ".json")
        if not os.path.exists(ab_path):
            continue
            
        with open(ab_path, 'r', encoding='utf-8') as f:
            ab_data = json.load(f).get('hadiths', [])
            
        for row in ab_data:
            anchor_id = str(row.get('idInBook'))
            master_link[book][anchor_id] = {
                "anchor_source": "ahmedbaset",
                "lidwa_id": None, # Lidwa doesn't have these
                "ahmedbaset_id": anchor_id
            }

    out_path = os.path.join(LINKS_DIR, "master_link.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(master_link, f, indent=2)
        
    print(f"[+] Link Engine finished! Master links written to {out_path}")

if __name__ == "__main__":
    build_links()
