import os
import json

COMMENTARIES_DIR = r"G:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id\data\commentaries"

if not os.path.exists(COMMENTARIES_DIR):
    print("No commentaries directory found.")
    exit(0)

count = 0
for f in os.listdir(COMMENTARIES_DIR):
    if f.endswith('.json'):
        path = os.path.join(COMMENTARIES_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            if "hadith_ar" not in data or data.get("syarah_ar") in ["", "Not Available"]:
                os.remove(path)
                count += 1
        except Exception as e:
            print(f"Error reading {f}: {e}")

print(f"Deleted {count} incomplete legacy files to allow re-scraping with new fields.")
