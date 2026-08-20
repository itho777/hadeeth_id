import glob, json
from difflib import SequenceMatcher
import sqlite3

conn = sqlite3.connect('scratch/lidwa_plaintext.db')
cursor = conn.cursor()
cursor.execute('SELECT Kode_Rawi, Nama, bukhari, muslim, abudaud, tirmidzi, nasai, ibnumajah, ahmad, malik, darimi FROM perawi_daftar')
all_rawis = cursor.fetchall()

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

matches = {}
for f in glob.glob('data/rawis/profiles/rawi_*.json'):
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
    name_id = data.get('name_id', '').lower()
    name_en = data.get('name_en', '').lower()
    
    # Simple heuristic for top companions
    if 'hurairah' in name_en: best_match = [r for r in all_rawis if r[0]==4396][0]
    elif 'aisyah' in name_id or 'aishah' in name_en: best_match = [r for r in all_rawis if r[0]==4049][0]
    elif 'anas' in name_en and 'malik' in name_en: best_match = [r for r in all_rawis if r[0]==720][0]
    elif 'umar' in name_en and 'khat' in name_en: best_match = [r for r in all_rawis if r[0]==4967][0]
    elif 'abbas' in name_en and 'mutt' in name_en: best_match = [r for r in all_rawis if r[0]==4883][0]
    else:
        # Score based
        best_r = None
        best_score = 0
        for r in all_rawis:
            db_name = r[1].lower()
            sc = max(similar(name_id, db_name), similar(name_en, db_name))
            if sc > best_score:
                best_score = sc
                best_r = r
        best_match = best_r

    matches[data['id']] = {
        'json_name': name_en,
        'db_name': best_match[1],
        'counts': {
            'bukhari': best_match[2],
            'muslim': best_match[3],
            'abudaud': best_match[4],
            'tirmidzi': best_match[5],
            'nasai': best_match[6],
            'ibnumajah': best_match[7],
            'ahmad': best_match[8],
            'malik': best_match[9],
            'darimi': best_match[10]
        }
    }
    print("{} ({}) => {} (Score)".format(data['id'], name_en, best_match[1]))
    
    # Update JSON
    data['book_counts'] = matches[data['id']]['counts']
    with open(f, 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=2)

print('Updated all profiles.')
