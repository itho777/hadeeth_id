import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'scratch', 'lidwa_plaintext.db')
LIDWA_CHAPTERS_DIR = os.path.join(BASE_DIR, 'data', 'lidwa-chapters')

os.makedirs(LIDWA_CHAPTERS_DIR, exist_ok=True)

books = [
    "abudaud",
    "ahmad",
    "bukhari",
    "darimi",
    "ibnumajah",
    "malik",
    "muslim",
    "nasai",
    "tirmidzi"
]

def build():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for book in books:
        # Load datakitab
        try:
            cursor.execute(f"SELECT ID_Kitab, Kitab_Indonesia, Kitab_Arab FROM datakitab_{book}")
            kitab_rows = cursor.fetchall()
        except sqlite3.OperationalError:
            print(f"Skipping {book}, no datakitab table.")
            continue
            
        kitab_map = {}
        for r in kitab_rows:
            kitab_map[r[0]] = {"id": r[1], "ar": r[2]}
            
        # Get hadith stats per kitab
        try:
            cursor.execute(f"SELECT ID_Kitab, MIN(NoHdt), MAX(NoHdt), COUNT(NoHdt) FROM tema_{book} GROUP BY ID_Kitab")
            stats_rows = cursor.fetchall()
        except sqlite3.OperationalError:
            print(f"Skipping {book}, no tema table.")
            continue
            
        stats_map = {}
        for r in stats_rows:
            stats_map[r[0]] = {
                "min": r[1],
                "max": r[2],
                "count": r[3]
            }

        chapters = []
        # Sort kitabs by ID to maintain order
        sorted_kitabs = sorted(list(kitab_map.keys()))
        for idx, k_id in enumerate(sorted_kitabs):
            k_info = kitab_map[k_id]
            stats = stats_map.get(k_id, {"min": 0, "max": 0, "count": 0})
            
            chapters.append({
                "id": f"{book}_c{k_id}",
                "book_id": book,
                "chapter_number": k_id,
                "title_en": k_info["id"], # We use ID as fallback for EN
                "title_ar": k_info["ar"],
                "title_id": k_info["id"],
                "hadith_start": stats["min"],
                "hadith_end": stats["max"],
                "hadith_count": stats["count"]
            })
            
        out_data = {
            "book_id": book,
            "title_id_source": "Native Lidwa Database",
            "title_en_source": "Native Lidwa Database (ID fallback)",
            "title_ar_source": "Native Lidwa Database",
            "chapters": chapters
        }
        
        out_path = os.path.join(LIDWA_CHAPTERS_DIR, f"{book}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out_data, f, ensure_ascii=False, indent=2)
            
        print(f"Built {out_path} with {len(chapters)} chapters.")

if __name__ == "__main__":
    build()
