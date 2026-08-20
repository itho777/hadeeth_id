import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")
RAWIS_MIN_JSON = os.path.join(BASE_DIR, "data", "rawis", "active_rawis.min.json")

def append_lidwa_rawis():
    print("[*] Loading existing active_rawis.min.json...")
    with open(RAWIS_MIN_JSON, 'r', encoding='utf-8') as f:
        active_rawis = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Kode_Rawi, Nama, Kalangan, Nasab, Kuniyah, Laqob, Negeri_Hidup, Negeri_Wafat, Tahun_Wafat FROM perawi_daftar")
    rows = cursor.fetchall()
    
    count = 0
    for row in rows:
        kode, nama, kalangan, nasab, kuniyah, laqob, negeri_hidup, negeri_wafat, tahun_wafat = row
        lidwa_id = f"lidwa_{kode}"
        
        # Format the grade / role
        roleId = f"Kalangan: {kalangan}" if kalangan else "Perawi"
        roleEn = roleId.replace('Kalangan: Sahabat', 'Companion').replace('Kalangan:', 'Level:')
        
        # We only have Indonesian info primarily, which serves both EN/ID when Lidwa edition is active.
        active_rawis[lidwa_id] = {
            "en": nama,
            "id": nama,
            "ar": nama,  # Lidwa 'Nama' is Indonesian, we don't have Ar unfortunately unless we map to Kaggle, but this prevents crashes
            "role": roleEn,
            "roleId": roleId,
            "kunyah": kuniyah if kuniyah else "-",
            "residence": negeri_hidup if negeri_hidup else "-",
            "death_ah": tahun_wafat if tahun_wafat else "-",
            "counts": "Lidwa Sanad"
        }
        count += 1
        
    with open(RAWIS_MIN_JSON, 'w', encoding='utf-8') as f:
        json.dump(active_rawis, f, ensure_ascii=False, separators=(',', ':'))
        
    print(f"[+] Injected {count} Lidwa narrators into active_rawis.min.json.")

if __name__ == "__main__":
    append_lidwa_rawis()
