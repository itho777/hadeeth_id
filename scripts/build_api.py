# -*- coding: utf-8 -*-
import json
import os
import sqlite3
import codecs

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
FAWAZ_DIR = os.path.join(BASE_DIR, "data", "sources", "fawaz_api", "editions")
LIDWA_DB = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")
API_OUT = os.path.join(BASE_DIR, "data", "api")

LANGS = ["eng", "ind", "urd", "fra", "ben", "rus", "tam", "tur"]

def build_book(book_name, fawaz_name, lidwa_map_table):
    print("Building API for " + book_name)
    
    # 1. Load links
    link_path = "links_" + book_name + ".json"
    if not os.path.exists(link_path):
        print("No links found.")
        return
    with open(link_path, "r") as f:
        links = json.load(f)
        
    # 2. Load Lidwa
    l_data = []
    with codecs.open(os.path.join(LIDWA_DIR, book_name + ".ndjson"), 'r', 'utf-8') as f:
        for line in f:
            l_data.append(json.loads(line))
            
    # 3. Load Mapping
    intl_map = {}
    conn = sqlite3.connect(LIDWA_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NoHdt, NoMapping FROM " + lidwa_map_table)
        for row in cursor.fetchall():
            intl_map[str(row[0])] = row[1]
    except Exception as e:
        pass
    conn.close()
    
    # 4. Load Fawaz Translations
    fawaz_trans = {} # lang -> id -> text
    for lang in LANGS:
        fawaz_trans[lang] = {}
        path = os.path.join(FAWAZ_DIR, lang + "-" + fawaz_name + ".json")
        if os.path.exists(path):
            with codecs.open(path, "r", "utf-8") as f:
                f_json = json.load(f)
                for h in f_json.get('hadiths', []):
                    fawaz_trans[lang][h['hadithnumber']] = h.get('text', '').strip()
                    
    # 5. Build Final
    out_path = os.path.join(API_OUT, book_name + ".ndjson")
    with codecs.open(out_path, "w", "utf-8") as f_out:
        for l_h in l_data:
            l_id = str(l_h['id'])
            intl_id = intl_map.get(l_id, l_h['id']) # fallback to lidwa native
            fawaz_id = links.get(l_id)
            
            # Start object
            out_obj = {
                "id": intl_id,
                "lidwa_id": l_h['id'],
                "book": book_name,
                "translations": {
                    "ar": [{"text": l_h.get('text_ar', ''), "source": "lidwa"}],
                    "id": [{"text": l_h.get('text_id', ''), "source": "lidwa"}]
                }
            }
            
            # Inject Fawaz
            if fawaz_id:
                for lang in LANGS:
                    if lang == "ind": continue # Use lidwa for ind
                    t = fawaz_trans[lang].get(fawaz_id)
                    if t and t.strip():
                        # Map lang code for output
                        l_code = "en" if lang == "eng" else lang
                        if l_code not in out_obj["translations"]:
                            out_obj["translations"][l_code] = []
                        out_obj["translations"][l_code].append({
                            "text": t,
                            "source": "fawazahmed"
                        })
                        
            f_out.write(json.dumps(out_obj) + "\n")
    print("Done building " + book_name)

if __name__ == '__main__':
    build_book("muslim", "muslim", "mapping_muslim")