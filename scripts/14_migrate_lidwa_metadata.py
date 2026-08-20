import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")

LIDWA_BOOKS = {
    "abudaud": "abudawud",
    "ahmad": "ahmad",
    "bukhari": "bukhari",
    "darimi": "darimi",
    "ibnumajah": "ibnmajah",
    "malik": "malik",
    "muslim": "muslim",
    "nasai": "nasai",
    "tirmidzi": "tirmidhi"
}

KUMPULAN_TYPES = [
    ("kumpulan_qudsi", "is_qudsi"),
    ("kumpulan_mutawatir", "is_mutawatir"),
    ("kumpulan_marfu", "is_marfu"),
    ("kumpulan_mauquf", "is_mauquf"),
    ("kumpulan_maqthu", "is_maqthu"),
    ("kumpulan_mursal", "is_mursal"),
    ("kumpulan_munqathi", "is_munqathi"),
    ("kumpulan_muallaq", "is_muallaq")
]

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Store metadata by book -> hadith_id
    metadata_map = {b: {} for b in LIDWA_BOOKS.values()}
    
    # 1. Fetch Derajat (Grades)
    for lidwa_suffix, internal_id in LIDWA_BOOKS.items():
        table_name = f"derajat_{lidwa_suffix}"
        try:
            cursor.execute(f"SELECT NoHdt, Derajat FROM {table_name}")
            rows = cursor.fetchall()
            for nohdt, derajat in rows:
                if nohdt not in metadata_map[internal_id]:
                    metadata_map[internal_id][nohdt] = {}
                metadata_map[internal_id][nohdt]["grade_id"] = derajat
        except sqlite3.OperationalError:
            pass

    # 2. Fetch Kumpulan (Flags)
    for table_name, flag_name in KUMPULAN_TYPES:
        try:
            cursor.execute(f"SELECT Sumber, NoHdt FROM {table_name}")
            rows = cursor.fetchall()
            for sumber, nohdt in rows:
                if sumber in LIDWA_BOOKS:
                    internal_id = LIDWA_BOOKS[sumber]
                    if nohdt not in metadata_map[internal_id]:
                        metadata_map[internal_id][nohdt] = {}
                    metadata_map[internal_id][nohdt][flag_name] = True
        except sqlite3.OperationalError:
            pass

    # 3. Write out to data/api/{book}/lidwa_metadata.json
    for internal_id, data in metadata_map.items():
        out_path = os.path.join(BASE_DIR, "data", "api", internal_id, "lidwa_metadata.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"[+] Wrote {len(data)} metadata entries for {internal_id}")

if __name__ == "__main__":
    migrate()
