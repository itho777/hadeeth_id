import sqlite3
import sys
import json

def main():
    conn = sqlite3.connect('scratch/lidwa_plaintext.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT NoHdt, Isi_Indonesia, Isi_Arab FROM had_agregat WHERE imam='darimi' AND NoHdt=1638")
    hadith = cursor.fetchone()
    
    if not hadith:
        print("Hadith 1638 not found in had_agregat for darimi")
        return
        
    out = f"Lidwa ID for Darimi 1638: {hadith[0]}\n"
    out += f"Indo: {hadith[1][:100]}...\n"
    out += f"Arab: {hadith[2][:100]}...\n\n--- Sanad Data ---\n"
    
    try:
        cursor.execute("SELECT NoUrut, J1, J2, J3, J4, J5, J6, J7, J8, J9, J10, Skema, Kedudukan FROM sanad_darimi WHERE NoHdt=1638")
        sanad_rows = cursor.fetchall()
        
        for s in sanad_rows:
            no_urut = s[0]
            j_cols = s[1:11]
            skema = s[11]
            kedudukan = s[12]
            
            rawi_ids = [j for j in j_cols if j]
            out += f"\nJalur {no_urut}:\n"
            out += f"Skema: {skema}, Kedudukan: {kedudukan}\n"
            
            for i, rawi_id in enumerate(rawi_ids):
                cursor.execute("SELECT Nama, Kalangan FROM perawi_daftar WHERE Kode_Rawi=?", (rawi_id,))
                perawi = cursor.fetchone()
                if perawi:
                    out += f"  [{i+1}] ID {rawi_id}: {perawi[0]} ( {perawi[1]} )\n"
                else:
                    out += f"  [{i+1}] ID {rawi_id}: [Perawi Not Found]\n"
                
    except Exception as e:
        out += f"Error fetching sanad: {e}\n"
        
    with open('out_darimi.txt', 'w', encoding='utf-8') as f:
        f.write(out)

if __name__ == "__main__":
    main()
