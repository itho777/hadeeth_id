import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
KAGGLE_NARRATORS = os.path.join(BASE_DIR, "data", "sources", "kaggle", "narrators.json")
OUT_PATH = os.path.join(BASE_DIR, "data", "rawis", "active_rawis.min.json")

print("[*] Loading Kaggle narrators...")
with open(KAGGLE_NARRATORS, 'r', encoding='utf-8') as f:
    kaggle_data = json.load(f)

kaggle_dict = {str(r['id']): r for r in kaggle_data}

print("[*] Analyzing active rawis and counting hadith appearances...")
unique_rawis = set()
rawi_counts = {}

for file in os.listdir(LINKS_DIR):
    if not file.endswith('.json'): continue
    
    with open(os.path.join(LINKS_DIR, file), 'r', encoding='utf-8') as f:
        data = json.load(f)
        if 'fawaz_to_rawis' in data:
            for narrators in data['fawaz_to_rawis'].values():
                for nr in narrators:
                    nr_str = str(nr)
                    unique_rawis.add(nr_str)
                    rawi_counts[nr_str] = rawi_counts.get(nr_str, 0) + 1

active_scholars = {}
for sid in unique_rawis:
    if sid in kaggle_dict:
        s = kaggle_dict[sid]
        
        # Parse Biography for Places
        places = "-"
        bio = s.get('biography', '') or ''
        for line in bio.split('\n'):
            if line.startswith('Places:'):
                places = line.replace('Places:', '').strip()
                if places == 'NA' or not places:
                    places = '-'
                break
                
        # Parse Death Year
        death = s.get('death_year')
        death_ah = f"{death} H" if death else "-"
        
        # Attempt to extract Kunyah from English Name
        kunyah = "-"
        en_name = s.get('name_en', '')
        # Simplistic extraction: If the name contains Abu/Umm/Ibn, we can try to extract it, but it's safer to just let the regex logic run.
        # Let's see if we can find it
        lower_name = en_name.lower()
        words = en_name.split()
        for i, w in enumerate(words):
            wl = w.lower()
            if wl in ['abu', 'umm']:
                if i + 1 < len(words):
                    kunyah = f"{w} {words[i+1]}"
                    break
        
        counts_str = f"{rawi_counts.get(sid, 0)} Hadiths"
        
        active_scholars[sid] = {
            "ar": s.get("name_ar", ""),
            "en": s.get("name_en", ""),
            "id": s.get("name_id", ""),
            "kunyah": kunyah,
            "residence": places,
            "death_ah": death_ah,
            "grade": s.get("grade", ""),
            "counts": counts_str
        }

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(active_scholars, f, ensure_ascii=False, separators=(',', ':'))

print(f"[+] Exported {len(active_scholars)} active rawis with fully enriched data to {OUT_PATH}")
