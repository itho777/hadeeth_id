import os
import re
import json
import difflib
import requests

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCES_DIR = os.path.join(DATA_DIR, "sources")
LIDWA_DIR = os.path.join(SOURCES_DIR, "lidwa")
LINKS_DIR = os.path.join(DATA_DIR, "links")

SUPABASE_URL = "https://idokyspokenbmzoegahq.supabase.co"
BASE_API = f"{SUPABASE_URL}/rest/v1"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c"

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

CORE_9 = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]
PRONOUNS = ['bapaknya', 'ayahnya', 'kakeknya', 'pamannya', 'bapakku', 'ayahku']

def load_lidwa(book):
    path = os.path.join(LIDWA_DIR, f"{book}.json")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {str(r.get('id', r.get('hadith_number'))): r for r in data}

def load_links(book):
    path = os.path.join(LINKS_DIR, f"{book}.json")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_lidwa_chain(text_id):
    if not text_id:
        return []
    isnad_part = re.split(r'beliau\s+bersabda\s*:|berfirman\s*:|berkata\s*:|tentang\s+firman\s+Allah|bahwa\s+Rasulullah', text_id, maxsplit=1)[0]
    brackets = re.findall(r'\[([^\]]+)\]', isnad_part)
    
    rawis = []
    for b in brackets:
        b_clean = re.sub(r'^(Telah menceritakan|telah menceritakan|Telah mengabarkan|telah mengabarkan|Telah menceritakan kepada kami|Telah menceritakan kepadaku)\s+', '', b, flags=re.IGNORECASE).strip()
        if len(b_clean) > 2:
            rawis.append(b_clean)
    return rawis

def resolve_relative(token, prev_name, prev_prev_name=None):
    token = token.lower()
    if token in ['bapaknya', 'ayahnya', 'bapakku', 'ayahku']:
        parts = re.split(r'\s+bin\s+|\s+binti\s+', prev_name, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            return parts[1].strip()
    elif token in ['kakeknya']:
        parts = re.split(r'\s+bin\s+|\s+binti\s+', prev_name, flags=re.IGNORECASE)
        if len(parts) >= 3:
            return parts[2].strip()
        if prev_prev_name:
            parts2 = re.split(r'\s+bin\s+|\s+binti\s+', prev_prev_name, maxsplit=1, flags=re.IGNORECASE)
            if len(parts2) == 2:
                return parts2[1].strip()
    return token

def normalize_indonesian_to_en(name):
    name = name.replace('sy', 'sh')
    name = name.replace('ts', 'th')
    name = name.replace('dz', 'dh')
    name = name.replace('dl', 'dh')
    name = name.replace('dj', 'j')
    name = name.replace('tj', 'c')
    name = name.replace('ch', 'kh')
    name = name.replace(' ais', ' aish')
    name = name.replace(' aisyah', ' aisha')
    name = name.replace('\'aisyah', 'aisha')
    name = name.replace('khattab', 'khattab')
    name = name.replace('khaththab', 'khattab')
    name = name.replace('hisyam', 'hisham')
    return name

def normalize_name(name, is_indo=False):
    name = re.sub(r'radliallahu \'anhu|radliallahu \'anha|radliallahu \'anhuma|radliyallahu \'anhu|radliyallahu \'anha', '', name, flags=re.IGNORECASE)
    name = name.replace('\'', '').replace('`', '').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip().lower()
    if is_indo:
        name = normalize_indonesian_to_en(name)
    return name

def fetch_supabase_rijal_index():
    print("[*] Fetching live Rijal slugs from Supabase...")
    index = {}
    offset = 0
    while True:
        r = requests.get(f"{BASE_API}/rijal?select=id,name_en,kunya_en,name_variants,kunya&limit=1000&offset={offset}", headers=HEADERS)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        for rawi in data:
            rid = rawi["id"]
            en_names = []
            if rawi.get("name_en"): en_names.append(rawi["name_en"])
            if rawi.get("kunya_en"): en_names.append(rawi["kunya_en"])
            if rawi.get("name_variants"): en_names.extend(rawi["name_variants"])
            
            for n in en_names:
                norm = normalize_name(n)
                if norm:
                    index[norm] = rid
                    words = norm.split()
                    if len(words) >= 3:
                        index[" ".join(words[:3])] = rid
                    if len(words) >= 2:
                        index[" ".join(words[:2])] = rid
        offset += 1000
    print(f"[+] Built global index with {len(index)} searchable name keys from Supabase")
    return index

def process_book(book, global_index):
    print(f"[*] Processing {book}...")
    lidwa_data = load_lidwa(book)
    links_data = load_links(book)
    
    if not lidwa_data or not links_data:
        print(f"[-] Missing data for {book}")
        return
        
    fawaz_to_lidwa = links_data.get('fawaz_to_lidwa', {})
    
    unified_sanad = {}
    
    for fawaz_id, lidwa_id in fawaz_to_lidwa.items():
        lidwa_row = lidwa_data.get(str(lidwa_id))
        if not lidwa_row:
            continue
            
        text_id = lidwa_row.get('text_id', '')
        lidwa_chain = extract_lidwa_chain(text_id)
            
        resolved_chain = []
        for i, name in enumerate(lidwa_chain):
            if name.lower() in PRONOUNS:
                prev1 = resolved_chain[i-1]['resolved_name'] if i > 0 else ""
                prev2 = resolved_chain[i-2]['resolved_name'] if i > 1 else ""
                resolved_name = resolve_relative(name, prev1, prev2)
            else:
                resolved_name = name
                
            norm_name = normalize_name(resolved_name, is_indo=True)
            matched_sid = None
            
            # Try global index
            matched_sid = global_index.get(norm_name)
            if not matched_sid:
                words = norm_name.split()
                if len(words) >= 3:
                    matched_sid = global_index.get(" ".join(words[:3]))
                if not matched_sid and len(words) >= 2:
                    matched_sid = global_index.get(" ".join(words[:2]))
                        
            resolved_chain.append({
                'original': name,
                'resolved_name': resolved_name,
                'sid': matched_sid
            })
            
        unified_sanad[str(lidwa_id)] = resolved_chain

    links_data['unified_sanad'] = unified_sanad
    
    links_path = os.path.join(LINKS_DIR, f"{book}.json")
    with open(links_path, 'w', encoding='utf-8') as f:
        json.dump(links_data, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Saved {len(unified_sanad)} unified sanad chains to {book}.json")

if __name__ == "__main__":
    global_index = fetch_supabase_rijal_index()
    for book in CORE_9:
        process_book(book, global_index)
