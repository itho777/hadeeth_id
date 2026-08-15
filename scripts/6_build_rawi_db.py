import os
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "sqlite", "hadith.db")
RAWIS_DIR = os.path.join(BASE_DIR, "data", "rawis")

def build_rawi_db():
    if not os.path.exists(RAWIS_DIR):
        os.makedirs(RAWIS_DIR)
        
    print("[*] Building Rawi index from SQLite...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if table exists first
    try:
        cursor.execute("SELECT * FROM narrators")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        print("[!] 'narrators' table not found in hadith.db!")
        return

    scholars = {}
    for r in rows:
        scholars[str(r['id'])] = {
            "name_ar": r['name_ar'],
            "name_en": r['name_en'],
            "grade": r['grade'],
            "birth_year": r['birth_year'],
            "death_year": r['death_year']
        }
        
    out_path = os.path.join(RAWIS_DIR, "scholars_index.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(scholars, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Successfully exported {len(scholars)} narrators to {out_path}.")
    
    conn.close()

if __name__ == "__main__":
    build_rawi_db()
