import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
FAWAZ_DIR = os.path.join(BASE_DIR, "data", "sources", "fawaz_api", "editions")
LIDWA_DB = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")
API_OUT = os.path.join(BASE_DIR, "data", "api")
os.makedirs(API_OUT, exist_ok=True)

LANGS = ["eng", "ind", "urd", "fra", "ben", "rus", "tam", "tur"]
MAPPING_TABLES = {
    "bukhari": "mapping_bukhari", "muslim": "mapping_muslim", "abudawud": "mapping_abudaud",
    "tirmidhi": "mapping_tirmidzi", "nasai": "mapping_nasai", "ibnmajah": "mapping_ibnumajah",
    "malik": "mapping_malik", "darimi": "mapping_darimi"
}

def build_book(book_name):
    print(f"Building API for {book_name}...")
    link_path = f"links_{book_name}.json"
    if not os.path.exists(link_path): return
    with open(link_path, "r", encoding='utf-8') as f:
        links = json.load(f)
        
    l_data = []
    with open(os.path.join(LIDWA_DIR, f"{book_name}.ndjson"), 'r', encoding='utf-8') as f:
        for line in f: l_data.append(json.loads(line))
            
    intl_map = {}
    conn = sqlite3.connect(LIDWA_DB)
    cursor = conn.cursor()
    table = MAPPING_TABLES.get(book_name)
    if table:
        try:
            cursor.execute(f"SELECT NoHdt, NoMapping FROM {table}")
            for row in cursor.fetchall():
                intl_map[str(row[0])] = row[1]
        except Exception: pass
    conn.close()
    
    fawaz_trans = {lang: {} for lang in LANGS}
    for lang in LANGS:
        path = os.path.join(FAWAZ_DIR, f"{lang}-{book_name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for h in json.load(f).get('hadiths', []):
                    fawaz_trans[lang][h['hadithnumber']] = str(h.get('text', '')).strip()
                    
    grouped = {} # intl_id -> out_obj
    
    for l_h in l_data:
        l_id = str(l_h['id'])
        intl_id = intl_map.get(l_id, l_h['id'])
        fawaz_id = links.get(l_id)
        
        if intl_id not in grouped:
            grouped[intl_id] = {
                "id": intl_id,
                "lidwa_id": [],
                "book": book_name,
                "translations": {}
            }
            
        g = grouped[intl_id]
        g["lidwa_id"].append(l_h['id'])
        
        # Merge AR
        if "ar" not in g["translations"]: g["translations"]["ar"] = []
        g["translations"]["ar"].append({"text": l_h.get('text_ar', ''), "source": "lidwa", "id": l_h['id']})
        
        # Merge ID
        if "id" not in g["translations"]: g["translations"]["id"] = []
        g["translations"]["id"].append({"text": l_h.get('text_id', ''), "source": "lidwa", "id": l_h['id']})
        
        # Inject Fawaz
        if fawaz_id:
            for lang in LANGS:
                if lang == "ind": continue 
                t = fawaz_trans[lang].get(fawaz_id)
                if t and t.strip():
                    l_code = "en" if lang == "eng" else lang
                    if l_code not in g["translations"]:
                        g["translations"][l_code] = []
                    # Check for duplicates so we don't spam 3 identical English translations if Fawaz repeated it
                    if not any(x["text"] == t for x in g["translations"][l_code]):
                        g["translations"][l_code].append({
                            "text": t,
                            "source": "fawazahmed"
                        })
                        
    out_path = os.path.join(API_OUT, f"{book_name}.ndjson")
    with open(out_path, "w", encoding="utf-8") as f_out:
        # Sort by intl_id numerically if possible
        for i_id in sorted(grouped.keys(), key=lambda x: int(x) if str(x).isdigit() else x):
            f_out.write(json.dumps(grouped[i_id], ensure_ascii=False) + "\n")
            
    print(f"Done building {book_name}")

for b in ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]:
    build_book(b)