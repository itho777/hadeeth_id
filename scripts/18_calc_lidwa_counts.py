import json
import csv
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "supabase", "hadith_rijal_lidwa.csv")
RAWIS_JSON = os.path.join(BASE_DIR, "data", "rawis", "active_rawis.min.json")

def main():
    print("[*] Calculating Lidwa Hadith Counts...")
    
    # Track unique hadiths per rawi to avoid double counting if a rawi appears twice in different paths of the same hadith
    rawi_hadiths = defaultdict(set)
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            if len(row) < 3: continue
            hadith_id, rawi_id, chain_pos = row
            rawi_hadiths[rawi_id].add(hadith_id)
            
    print(f"[*] Found counts for {len(rawi_hadiths)} unique rawis.")
    
    with open(RAWIS_JSON, 'r', encoding='utf-8') as f:
        rawis_data = json.load(f)
        
    updated = 0
    for rawi_id, hadiths in rawi_hadiths.items():
        if rawi_id in rawis_data:
            # Format count string
            rawis_data[rawi_id]['counts'] = str(len(hadiths))
            updated += 1
            
    with open(RAWIS_JSON, 'w', encoding='utf-8') as f:
        json.dump(rawis_data, f, ensure_ascii=False, separators=(',', ':'))
        
    print(f"[+] Successfully injected precise hadith counts into {updated} Lidwa profiles.")

if __name__ == '__main__':
    main()
