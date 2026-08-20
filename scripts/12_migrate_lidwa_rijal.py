import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")
OUT_PATH = os.path.join(BASE_DIR, "supabase", "seeds", "lidwa_rijal.sql")

def escape_sql(val):
    if val is None or str(val).strip() == '':
        return "NULL"
    val_str = str(val).replace("'", "''")
    return f"'{val_str}'"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Extract Rijal
    cursor.execute("""
        SELECT Kode_Rawi, Nama, Quality, Kalangan, Nasab, Kuniyah, Laqob, 
               Negeri_Hidup, Negeri_Wafat, Tahun_Wafat
        FROM perawi_daftar
    """)
    rows = cursor.fetchall()
    
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("-- Auto-generated from lidwa_plaintext.db\n\n")
        f.write("BEGIN;\n\n")
        
        batch_size = 500
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            
            f.write("INSERT INTO public.rijal (id, name_en, name_ar, name_id, quality_id, kalangan_id, nasab_id, kuniyah_id, laqob_id, negeri_hidup_id, negeri_wafat_id, tahun_wafat_id)\nVALUES\n")
            
            values = []
            for row in batch:
                (kode, nama, quality, kalangan, nasab, kuniyah, laqob, hidup, wafat, thn_wafat) = row
                rid = f"'lidwa_{kode}'"
                
                # We put nama as name_id, and also name_en to satisfy NOT NULL constraint
                name_en = escape_sql(nama)
                name_id = escape_sql(nama)
                name_ar = escape_sql("") # We might not have Arabic name in Lidwa
                
                quality_val = str(quality) if quality else "NULL"
                
                v = f"({rid}, {name_en}, {name_ar}, {name_id}, {quality_val}, {escape_sql(kalangan)}, {escape_sql(nasab)}, {escape_sql(kuniyah)}, {escape_sql(laqob)}, {escape_sql(hidup)}, {escape_sql(wafat)}, {escape_sql(thn_wafat)})"
                values.append(v)
                
            f.write(",\n".join(values))
            f.write("\nON CONFLICT (id) DO UPDATE SET\n")
            f.write("  name_id = EXCLUDED.name_id,\n")
            f.write("  quality_id = EXCLUDED.quality_id,\n")
            f.write("  kalangan_id = EXCLUDED.kalangan_id,\n")
            f.write("  nasab_id = EXCLUDED.nasab_id,\n")
            f.write("  kuniyah_id = EXCLUDED.kuniyah_id,\n")
            f.write("  laqob_id = EXCLUDED.laqob_id,\n")
            f.write("  negeri_hidup_id = EXCLUDED.negeri_hidup_id,\n")
            f.write("  negeri_wafat_id = EXCLUDED.negeri_wafat_id,\n")
            f.write("  tahun_wafat_id = EXCLUDED.tahun_wafat_id;\n\n")

        f.write("COMMIT;\n")
        
    print(f"[+] Exported {len(rows)} Lidwa Rijal to {OUT_PATH}")

if __name__ == "__main__":
    migrate()
