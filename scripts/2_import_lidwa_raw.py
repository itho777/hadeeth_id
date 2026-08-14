import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(BASE_DIR, "scratch", "irsyadulibad_db")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")

BOOK_MAPPING = {
    "shahih-bukhari.sql": "bukhari",
    "shahih-muslim.sql": "muslim",
    "sunan-abu-daud.sql": "abudawud",
    "sunan-tirmidzi.sql": "tirmidhi",
    "sunan-nasai.sql": "nasai",
    "sunan-ibnu-majah.sql": "ibnmajah",
    "muwatho_malik.sql": "malik",
    "musnad_darimi.sql": "darimi",
    "musnad-ahmad.sql": "ahmad"
}

def import_lidwa():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("[*] Starting Lidwa raw import from SQL dumps...")
    
    for sql_file, book_id in BOOK_MAPPING.items():
        sql_path = os.path.join(SQL_DIR, sql_file)
        if not os.path.exists(sql_path):
            print(f"[-] SQL file {sql_file} not found, skipping.")
            continue
            
        print(f"[*] Processing {sql_file} for {book_id}...")
        with open(sql_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # The SQL INSERT format is usually: (id, 'book_name', 'arabic_text', 'indo_text')
        # We need to handle optional quotes around the ID, because some files have them and some don't.
        # Format: (123, 'shahih_bukhari', 'Arabic...', 'Indo...')
        pattern = r"\(\s*'?(\d+)'?,\s*'(?:[^']+)',\s*'(.*?)',\s*'(.*?)'\)"
        matches = re.findall(pattern, content, re.DOTALL)
        
        hadiths = []
        for match in matches:
            h_id = int(match[0])
            ar_text = match[1].replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r')
            id_text = match[2].replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r')
            
            hadiths.append({
                "hadith_number": h_id,
                "text_ar": ar_text,
                "text_id": id_text
            })
            
        # Sort by hadith number to ensure consistency
        hadiths.sort(key=lambda x: x["hadith_number"])
        
        out_path = os.path.join(OUTPUT_DIR, f"{book_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(hadiths, f, ensure_ascii=False, indent=2)
            
        print(f"[+] Exported {len(hadiths)} hadiths to {book_id}.json")

if __name__ == "__main__":
    import_lidwa()
