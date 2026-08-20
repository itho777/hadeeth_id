import sqlite3
import json
import os

DB_PATH = 'scratch/lidwa_plaintext.db'
OUT_DIR = 'data/rawis/profiles'

def generate_profiles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Kode_Rawi, Nama, Quality, Kalangan, Nasab, Kuniyah, Laqob, 
               Negeri_Hidup, Negeri_Wafat, Tahun_Wafat, 
               bukhari, muslim, abudaud, tirmidzi, nasai, ibnumajah, ahmad, malik, darimi 
        FROM perawi_daftar
    ''')
    rows = cursor.fetchall()
    
    os.makedirs(OUT_DIR, exist_ok=True)
    
    for r in rows:
        kode, nama, quality, kalangan, nasab, kunyah, laqob, n_hidup, n_wafat, t_wafat, b, m, ad, t, n, im, ah, ma, d = r
        rawi_id = f"lidwa_{kode}"
        
        # Calculate sum
        total_counts = b + m + ad + t + n + im + ah + ma + d
        
        profile = {
            "id": rawi_id,
            "name_en": nama,
            "name_id": nama,
            "name_ar": "",
            "is_sahabi": "true" if (kalangan and ("Sahabat" in kalangan or "Shahabat" in kalangan)) else "false",
            "generation": kalangan if kalangan else "-",
            "grade": str(quality) if quality else "-",
            "died_ah": t_wafat if t_wafat else "-",
            "city_of_death": n_wafat if n_wafat else "-",
            "residence": n_hidup if n_hidup else "-",
            "kunyah": kunyah if kunyah else "-",
            "parents": nasab if nasab else "-",
            "nasab": nasab if nasab else "-",
            "laqob": laqob if laqob else "-",
            "hadith_count": str(total_counts),
            "book_counts": {
                "bukhari": b,
                "muslim": m,
                "abudaud": ad,
                "tirmidzi": t,
                "nasai": n,
                "ibnumajah": im,
                "ahmad": ah,
                "malik": ma,
                "darimi": d
            }
        }
        
        filepath = os.path.join(OUT_DIR, f"{rawi_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
            
    print(f"Successfully generated {len(rows)} lidwa profile JSON files.")

if __name__ == '__main__':
    generate_profiles()
