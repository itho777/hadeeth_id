import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
FAWAZ_DIR = os.path.join(BASE_DIR, "data", "raw_baseline")
AHMEDBASET_DIR = os.path.join(BASE_DIR, "data", "sources", "ahmedbaset", "by_book", "the_9_books")
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")

# Ahmedbaset mapping
AB_MAP = {
    "ahmad": "ahmed"
}

BOOKS = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik"]

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
    graph = {}

    print("[*] Starting Enhanced Cross-Linker (Tripartite Graph)...")

    for book in BOOKS:
        print(f" -> Processing {book}...")
        lidwa_path = os.path.join(LIDWA_DIR, f"{book}.json")
        fawaz_path = os.path.join(FAWAZ_DIR, f"ara-{book}.json")
        ab_book_name = AB_MAP.get(book, book)
        ab_path = os.path.join(AHMEDBASET_DIR, f"{ab_book_name}.json")

        if not os.path.exists(fawaz_path):
            print(f"    Missing Fawaz for {book}")
            continue
            
        with open(fawaz_path, 'r', encoding='utf-8') as f:
            fawaz_data = json.load(f).get('hadiths', [])

        fawaz_prefix = {}
        fawaz_suffix = {}
        for h in fawaz_data:
            if h.get('text'):
                ar_text = normalize_arabic(h['text'])
                hid = str(h.get('hadithnumber'))
                if len(ar_text) >= 40:
                    fawaz_prefix[ar_text[:40]] = hid
                    fawaz_suffix[ar_text[-40:]] = hid
                else:
                    fawaz_prefix[ar_text] = hid

        # 1. Map Fawaz <-> Lidwa
        fawaz_to_lidwa = {}
        lidwa_to_fawaz = {}
        if os.path.exists(lidwa_path):
            with open(lidwa_path, 'r', encoding='utf-8') as f:
                lidwa_data = json.load(f)
            for l_row in lidwa_data:
                l_id = str(l_row.get('hadith_number'))
                l_text = normalize_arabic(l_row.get('text_ar'))
                if not l_text: continue
                
                matched_f_id = fawaz_prefix.get(l_text[:40]) if len(l_text) >= 40 else fawaz_prefix.get(l_text)
                if not matched_f_id and len(l_text) >= 40:
                    matched_f_id = fawaz_suffix.get(l_text[-40:])

                if matched_f_id:
                    fawaz_to_lidwa[matched_f_id] = l_id
                    lidwa_to_fawaz[l_id] = matched_f_id
            print(f"    Lidwa mapped: {len(fawaz_to_lidwa)}")

        # 2. Map Fawaz <-> AhmedBaset
        fawaz_to_ab = {}
        ab_to_fawaz = {}
        if os.path.exists(ab_path):
            with open(ab_path, 'r', encoding='utf-8') as f:
                ab_data = json.load(f).get('hadiths', [])
            for a_row in ab_data:
                a_id = str(a_row.get('idInBook'))
                a_text = normalize_arabic(a_row.get('arabic'))
                if not a_text: continue

                matched_f_id = fawaz_prefix.get(a_text[:40]) if len(a_text) >= 40 else fawaz_prefix.get(a_text)
                if not matched_f_id and len(a_text) >= 40:
                    matched_f_id = fawaz_suffix.get(a_text[-40:])

                if matched_f_id:
                    fawaz_to_ab[matched_f_id] = a_id
                    ab_to_fawaz[a_id] = matched_f_id
            print(f"    AhmedBaset mapped: {len(fawaz_to_ab)}")

        book_graph = {
            "fawaz_to_lidwa": fawaz_to_lidwa,
            "lidwa_to_fawaz": lidwa_to_fawaz,
            "fawaz_to_ab": fawaz_to_ab,
            "ab_to_fawaz": ab_to_fawaz
        }
        
        out_path = os.path.join(LINKS_DIR, f"{book}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(book_graph, f, indent=2)

    print(f"[+] Link Engine finished! Saved split graphs to {LINKS_DIR}")

if __name__ == "__main__":
    build_graph()
