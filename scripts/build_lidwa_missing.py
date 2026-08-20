import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_DIR = os.path.join(BASE_DIR, "scratch", "irsyadulibad_db")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")

def extract_sql_to_json(sql_filename, book_id, table_name, has_indo=True):
    sql_path = os.path.join(SQL_DIR, sql_filename)
    if not os.path.exists(sql_path):
        print(f"[-] {sql_filename} not found.")
        return
        
    print(f"[*] Parsing {sql_filename} -> {book_id}.json")
    with open(sql_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The SQL format for Lidwa is usually: (id, 'table_name', 'arab', 'indo')
    # Or for arab only: (id, 'table_name', 'arab')
    
    # We will just parse the literal inserts
    # It looks like: (9, 'musnad_syafii', 'arab text...', 'indo text...')
    if has_indo:
        pattern = r"\(\s*'?(\d+)'?,\s*'(?:[^']+)',\s*'(.*?)',\s*'(.*?)'\)"
    else:
        # riyad_arab table format
        pattern = r"\(\s*'?(\d+)'?,\s*'(?:[^']+)',\s*'(.*?)'\)"
        
    matches = re.findall(pattern, content, re.DOTALL)
    
    hadiths = []
    for match in matches:
        h_id = int(match[0])
        ar_text = match[1].replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r')
        
        payload = {
            "hadith_number": h_id,
            "text_ar": ar_text
        }
        
        if has_indo:
            id_text = match[2].replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r')
            payload["text_id"] = id_text
            
        hadiths.append(payload)

    hadiths.sort(key=lambda x: x["hadith_number"])
    
    out_path = os.path.join(OUTPUT_DIR, f"{book_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(hadiths, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Extracted {len(hadiths)} hadiths into {book_id}.json")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    extract_sql_to_json("musnad-syafii.sql", "syafii", "musnad_syafii", has_indo=True)
    extract_sql_to_json("riyadhus-shalihin.sql", "riyad", "riyadhus_shalihin", has_indo=True)
    extract_sql_to_json("riyadhus-shalihin-arab.sql", "riyad_arab", "riyadhus_shalihin_arab", has_indo=False)
