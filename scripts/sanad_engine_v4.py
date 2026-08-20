import os
import json
import re
import difflib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LINKS_DIR = os.path.join(BASE_DIR, "data", "links", "relinked")
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")
RAWIS_PATH = os.path.join(BASE_DIR, "data", "rawis", "active_rawis.min.json")

CORE_9 = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]

def normalize(name):
    name = name.lower()
    name = re.sub(r'\b(bin|ibn|binti|b.|b)\b', ' ', name)
    name = re.sub(r'\b(al-|az-|ar-|as-|at-|an-|ad-|ash-|ak-)\b', '', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    return ' '.join(name.split())

def build_kaggle_index():
    with open(RAWIS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    kaggle_names = {}
    for rid, r in data.items():
        en = r.get('en', '')
        kunyah = r.get('kunyah', '')
        if en: kaggle_names[normalize(en)] = rid
        if kunyah and kunyah != '-': kaggle_names[normalize(kunyah)] = rid
    return kaggle_names

def extract_lidwa_brackets(text_id):
    if not text_id:
        return []
    matches = re.findall(r'\[(.*?)\]', text_id)
    return [m for m in matches if len(m) > 2]

def find_match(lidwa_name, kaggle_names):
    norm_lidwa = normalize(lidwa_name)
    matches = difflib.get_close_matches(norm_lidwa, kaggle_names.keys(), n=1, cutoff=0.7)
    if matches:
        return kaggle_names[matches[0]]
    
    for k_name in kaggle_names.keys():
        if norm_lidwa in k_name.split() or k_name in norm_lidwa.split():
            return kaggle_names[k_name]
    return None

def process_sanad():
    print("[*] Building Kaggle Index...")
    kaggle_names = build_kaggle_index()
    print(f"[+] Indexed {len(kaggle_names)} name variations from active_rawis.")
    
    for book in CORE_9:
        link_path = os.path.join(LINKS_DIR, f"{book}.json")
        lidwa_path = os.path.join(SOURCES_DIR, "lidwa", f"{book}.json")
        
        if not os.path.exists(link_path) or not os.path.exists(lidwa_path):
            continue
            
        print(f"[*] Processing Sanad for {book}...")
        with open(link_path, 'r', encoding='utf-8') as f:
            links = json.load(f)
        with open(lidwa_path, 'r', encoding='utf-8') as f:
            lidwa_data = json.load(f)
            
        lidwa_lookup = {str(row.get('hadith_number', row.get('id'))): row for row in lidwa_data}
        
        f_to_l = links.get('fawaz_to_lidwa', {})
        f_to_r = links.get('fawaz_to_rawis', {})
        if 'fawaz_to_rawis' not in links:
            links['fawaz_to_rawis'] = f_to_r
            
        matched_count = 0
        total_extracted = 0
        
        for anchor_id, lidwa_id in f_to_l.items():
            lidwa_id = str(lidwa_id)
            row = lidwa_lookup.get(lidwa_id)
            if row and row.get('text_id'):
                bracket_names = extract_lidwa_brackets(row['text_id'])
                if bracket_names:
                    total_extracted += 1
                    rawis = []
                    for name in bracket_names:
                        rid = find_match(name, kaggle_names)
                        if rid:
                            rawis.append(rid)
                    f_to_r[anchor_id] = rawis
                    if rawis:
                        matched_count += 1
                        
        with open(link_path, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2)
            
        print(f"[+] {book}: Extracted brackets from {total_extracted}, successfully mapped to Kaggle for {matched_count} hadiths.")

if __name__ == "__main__":
    process_sanad()
