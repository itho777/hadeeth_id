import sqlite3
import json

with open('data/rawis/active_rawis.min.json', 'r', encoding='utf-8') as f:
    rawis = json.load(f)

conn = sqlite3.connect('scratch/lidwa_plaintext.db')
cursor = conn.cursor()

# Get counts
cursor.execute("SELECT rawi_id, COUNT(hadith_id) FROM sanad GROUP BY rawi_id")
counts = dict(cursor.fetchall())

updated = 0
for k, v in rawis.items():
    if k.startswith("lidwa_"):
        rawi_id = int(k.split("_")[1])
        c = counts.get(rawi_id, 0)
        v['counts'] = str(c)
        updated += 1

with open('data/rawis/active_rawis.min.json', 'w', encoding='utf-8') as f:
    json.dump(rawis, f, ensure_ascii=False, separators=(',', ':'))

print(f"Updated {updated} rawis with accurate counts.")
