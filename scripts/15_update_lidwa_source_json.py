import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")
LIDWA_OUT_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")

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

def update_lidwa_json():
    os.makedirs(LIDWA_OUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Preload Rawi dictionary for Sanad building
    print("Preloading Rawi dictionary...")
    perawi_dict = {}
    for row in conn.execute("SELECT * FROM perawi_daftar"):
        perawi_dict[row['Kode_Rawi']] = dict(row)
    
    for lidwa_imam, internal_id in LIDWA_BOOKS.items():
        print(f"[*] Extracting {lidwa_imam} -> {internal_id}.json")
        try:
            # Preload sanad for this book
            try:
                lidwa_sanad = {row['NoHdt']: dict(row) for row in conn.execute(f"SELECT * FROM sanad_{lidwa_imam}")}
            except:
                lidwa_sanad = {}
                
            cursor.execute("SELECT NoHdt, Isi_Arab, Isi_Indonesia, Isi_English FROM had_agregat WHERE imam = ? ORDER BY NoHdt", (lidwa_imam,))
            rows = cursor.fetchall()
            
            out_path = os.path.join(LIDWA_OUT_DIR, f"{internal_id}.json")
            output_data = []
            for row in rows:
                nohdt = row['NoHdt']
                isi_arab = row['Isi_Arab']
                isi_id = row['Isi_Indonesia']
                isi_en = row['Isi_English']
                
                record = {
                    "id": nohdt,
                    "hadith_number": nohdt,
                    "text_ar": isi_arab or "",
                    "text_id": isi_id or ""
                }
                if isi_en and isi_en.strip():
                    record["text_en"] = isi_en.strip()
                    
                # Add sanad
                if nohdt in lidwa_sanad:
                    sn = lidwa_sanad[nohdt]
                    chain = []
                    for j in range(1, 20):
                        j_key = f'J{j}'
                        if j_key in sn and sn[j_key] > 0:
                            rawi_id = sn[j_key]
                            rawi_info = perawi_dict.get(rawi_id, {})
                            name = rawi_info.get('Nama', str(rawi_id))
                            chain.append({"name": name, "id": f"lidwa_{rawi_id}"})
                    if chain:
                        record['rawis'] = chain
                        
                output_data.append(record)
                
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
                
            print(f"    Saved {len(rows)} records to {out_path}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    update_lidwa_json()
