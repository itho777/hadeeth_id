import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
RAWIS_PATH = os.path.join(BASE_DIR, "data", "rawis", "scholars_index.json")
OUT_PATH = os.path.join(BASE_DIR, "data", "rawis", "active_rawis.min.json")

unique_rawis = set()

for file in os.listdir(LINKS_DIR):
    if not file.endswith('.json'): continue
    with open(os.path.join(LINKS_DIR, file), 'r', encoding='utf-8') as f:
        data = json.load(f)
        if 'fawaz_to_rawis' in data:
            for narrators in data['fawaz_to_rawis'].values():
                for nr in narrators:
                    unique_rawis.add(str(nr))

with open(RAWIS_PATH, 'r', encoding='utf-8') as f:
    scholars = json.load(f)

active_scholars = {}
for sid in unique_rawis:
    if sid in scholars:
        s = scholars[sid]
        # Keep only essential fields to minimize payload
        active_scholars[sid] = {
            "ar": s.get("name_ar", ""),
            "en": s.get("name_en", ""),
            "id": s.get("name_id", ""),
            "kunyah": s.get("kunyah", ""),
            "residence": s.get("residence", ""),
            "death_ah": s.get("death_ah", ""),
            "grade": s.get("grade", ""),
            "counts": s.get("counts", "")
        }

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(active_scholars, f, ensure_ascii=False, separators=(',', ':'))

print(f"Exported {len(active_scholars)} active rawis to {OUT_PATH}")
