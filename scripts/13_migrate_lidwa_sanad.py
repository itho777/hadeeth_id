import sqlite3
import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")
OUT_PATH = os.path.join(BASE_DIR, "data", "supabase", "hadith_rijal_lidwa.csv")

# Map of Lidwa book suffix to our internal book IDs
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

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    
    total_written = 0
    with open(OUT_PATH, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['hadith_id', 'rawi_id', 'chain_position'])
        
        for lidwa_suffix, internal_id in LIDWA_BOOKS.items():
            table_name = f"sanad_{lidwa_suffix}"
            try:
                cursor.execute(f"SELECT NoHdt, J1, J2, J3, J4, J5, J6, J7, J8, J9, J10 FROM {table_name}")
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                print(f"[-] Table {table_name} missing, skipping.")
                continue
                
            for row in rows:
                nohdt = row[0]
                hadith_id = f"{internal_id}:{nohdt}"
                
                # Positions 1 to 10
                for pos, j_val in enumerate(row[1:]):
                    if j_val > 0:
                        rawi_id = f"lidwa_{j_val}"
                        writer.writerow([hadith_id, rawi_id, pos])
                        total_written += 1
                        
    print(f"[+] Exported {total_written} sanad relationships to {OUT_PATH}")

if __name__ == "__main__":
    migrate()
