import os
import sqlite3
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "sqlite", "hadith.db")
OUT_DIR = os.path.join(BASE_DIR, "data", "commentaries")

def export_syarah():
    print("[*] Exporting Syarah native data from SQLite...")
    
    if not os.path.exists(DB_PATH):
        print("[!] hadith.db not found. Cannot export Syarah.")
        return
        
    os.makedirs(OUT_DIR, exist_ok=True)
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM syarah")
    rows = cursor.fetchall()
    
    count = 0
    for row in rows:
        data = dict(row)
        
        # Deserialize JSON arrays if they exist as strings
        for field in ['benefits_en', 'benefits_id']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except Exception:
                    data[field] = []
        
        # Add a combined hadith_id field for UI convenience
        book_id = data.get('book_id')
        hadith_number = data.get('hadith_number')
        hadith_id = f"{book_id}_{hadith_number}"
        data['hadith_id'] = hadith_id
        
        # Export as native JSON
        out_path = os.path.join(OUT_DIR, f"{hadith_id}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        count += 1
            
    print(f"[+] Successfully exported {count} Syarah JSON files.")
    conn.close()

if __name__ == "__main__":
    export_syarah()
