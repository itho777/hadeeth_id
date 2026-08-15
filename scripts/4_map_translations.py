import os
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "sqlite", "hadith_final.db")
EDITIONS_DIR = os.path.join(BASE_DIR, "data", "editions")

def extract_translations():
    if not os.path.exists(EDITIONS_DIR):
        os.makedirs(EDITIONS_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all distinct book IDs
    cursor.execute("SELECT DISTINCT book_id FROM hadiths")
    books = [row['book_id'] for row in cursor.fetchall()]
    
    for book in books:
        print(f"[*] Processing translations for {book}...")
        
        cursor.execute("SELECT hadith_number, text_id, text_en FROM hadiths WHERE book_id = ? ORDER BY CAST(hadith_number AS INTEGER)", (book,))
        rows = cursor.fetchall()
        
        ind_hadiths = []
        eng_hadiths = []
        
        for r in rows:
            h_num = r['hadith_number']
            
            # ID
            if r['text_id']:
                ind_hadiths.append({
                    "hadithnumber": h_num,
                    "text": r['text_id']
                })
            
            # EN
            if r['text_en']:
                eng_hadiths.append({
                    "hadithnumber": h_num,
                    "text": r['text_en']
                })
                
        # Write IND edition
        ind_data = {
            "metadata": {"name": f"Indonesian Translation for {book}"},
            "hadiths": ind_hadiths
        }
        ind_path = os.path.join(EDITIONS_DIR, f"ind-{book}.json")
        with open(ind_path, 'w', encoding='utf-8') as f:
            json.dump(ind_data, f, ensure_ascii=False, indent=2)
            
        # Write ENG edition
        eng_data = {
            "metadata": {"name": f"English Translation for {book}"},
            "hadiths": eng_hadiths
        }
        eng_path = os.path.join(EDITIONS_DIR, f"eng-{book}.json")
        with open(eng_path, 'w', encoding='utf-8') as f:
            json.dump(eng_data, f, ensure_ascii=False, indent=2)
            
        print(f"[+] Saved {len(ind_hadiths)} ID, {len(eng_hadiths)} EN for {book}")
        
    conn.close()

if __name__ == "__main__":
    extract_translations()
