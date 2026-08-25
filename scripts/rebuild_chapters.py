import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LIDWA_CHAPS = os.path.join(BASE_DIR, "data", "lidwa-chapters")
CHAPTERS_OUT = os.path.join(BASE_DIR, "data", "chapters")
LIDWA_DB = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")

MAPPING_TABLES = {
    "bukhari": "mapping_bukhari", "muslim": "mapping_muslim", "abudawud": "mapping_abudaud",
    "tirmidhi": "mapping_tirmidzi", "nasai": "mapping_nasai", "ibnmajah": "mapping_ibnumajah",
    "malik": "mapping_malik", "darimi": "mapping_darimi"
}

def process_chapters(book):
    path = os.path.join(LIDWA_CHAPS, f"{book}.json")
    if not os.path.exists(path): return
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        chapters = data.get("chapters", [])
        
    table = MAPPING_TABLES.get(book)
    intl_map = {}
    if table:
        conn = sqlite3.connect(LIDWA_DB)
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT NoHdt, NoMapping FROM {table}")
            for row in cursor.fetchall():
                intl_map[row[0]] = row[1]
        except: pass
        conn.close()
        
    for c in chapters:
        start_lidwa = c.get("hadith_start")
        if start_lidwa and start_lidwa in intl_map:
            c["hadith_start"] = intl_map[start_lidwa]
        end_lidwa = c.get("hadith_end")
        if end_lidwa and end_lidwa in intl_map:
            c["hadith_end"] = intl_map[end_lidwa]
            
    out_path = os.path.join(CHAPTERS_OUT, f"{book}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)
    print(f"Updated chapters for {book}")

for b in ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]:
    process_chapters(b)