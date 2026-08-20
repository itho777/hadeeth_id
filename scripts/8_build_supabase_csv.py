import os
import json
import csv
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
API_DIR = os.path.join(BASE_DIR, "data", "api")
RAWIS_PATH = os.path.join(BASE_DIR, "data", "rawis", "active_rawis.min.json")
OUT_DIR = os.path.join(BASE_DIR, "data", "supabase")

def clean_text(text):
    if not text:
        return ""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove newlines and extra spaces
    text = ' '.join(text.split())
    return text

def build_supabase_dumps():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    print("[*] Generating Supabase CSV Dumps...")
    
    # 1. Generate Rawis CSV
    print(" -> Generating rawis.csv...")
    with open(RAWIS_PATH, 'r', encoding='utf-8') as f:
        rawis_data = json.load(f)
        
    with open(os.path.join(OUT_DIR, "rawis.csv"), 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['rawi_id', 'name_en', 'name_ar', 'grade', 'residence', 'death_ah'])
        for rid, row in rawis_data.items():
            en_name = row.get('en', '').split('\u0627')[0].strip() # Split off Arabic if mixed
            ar_name = row.get('ar', '').split(' ')[-1] # Very rough fallback, usually Kaggle has mixed
            if '\u0627' in row.get('ar', ''):
                ar_name = row.get('ar', '')[row.get('ar', '').find('\u0627'):].strip()
            
            writer.writerow([
                rid,
                clean_text(en_name),
                clean_text(ar_name),
                row.get('grade', ''),
                row.get('residence', ''),
                row.get('death_ah', '')
            ])
            
    # 2. Generate Search Index and Junction Table
    print(" -> Generating search_index.csv and hadith_rijal.csv...")
    
    with open(os.path.join(OUT_DIR, "search_index.csv"), 'w', encoding='utf-8', newline='') as fs, \
         open(os.path.join(OUT_DIR, "hadith_rijal.csv"), 'w', encoding='utf-8', newline='') as fr:
             
        s_writer = csv.writer(fs)
        s_writer.writerow(['id', 'book_id', 'chapter_number', 'hadith_number', 'grade', 'text_ar_search', 'text_en_search', 'text_id_search'])
        
        r_writer = csv.writer(fr)
        r_writer.writerow(['hadith_id', 'rawi_id', 'chain_position'])
        
        for book in os.listdir(API_DIR):
            book_dir = os.path.join(API_DIR, book)
            if not os.path.isdir(book_dir): continue
            
            for ds in ['fawaz.json', 'ab.json', 'lidwa.json']:
                path = os.path.join(book_dir, ds)
                if not os.path.exists(path): continue
                
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for hid, row in data.items():
                    # Write to Search Index
                    s_writer.writerow([
                        row['id'],
                        row['book_id'],
                        row['chapter_number'],
                        row['hadith_number'],
                        row.get('grade', ''),
                        clean_text(row.get('text_ar_search', '')),
                        clean_text(row.get('text_en', '')),
                        clean_text(row.get('text_id', ''))
                    ])
                    
                    # Write to Junction Table
                    rawis = row.get('rawis', [])
                    for i, rid in enumerate(rawis):
                        r_writer.writerow([
                            row['id'],
                            rid,
                            i
                        ])
                        
    print(f"[+] Successfully generated CSV dumps in {OUT_DIR}")

if __name__ == "__main__":
    build_supabase_dumps()
