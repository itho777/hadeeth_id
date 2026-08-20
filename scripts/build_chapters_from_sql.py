import os
import json
import io
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIDWA_CHAPTERS_DIR = os.path.join(BASE_DIR, 'data', 'lidwa-chapters')
SQL_FILE = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql'

books = [
    "abudaud", "ahmad", "bukhari", "darimi", "ibnumajah",
    "malik", "muslim", "nasai", "tirmidzi"
]

def parse_sql():
    if not os.path.exists(LIDWA_CHAPTERS_DIR):
        os.makedirs(LIDWA_CHAPTERS_DIR)
    
    # Store data
    kitab_maps = {book: {} for book in books}
    stats_maps = {book: {} for book in books}
    
    current_table = None
    
    print("Reading SQL file line by line...")
    with io.open(SQL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('INSERT INTO "datakitab_'):
                # Extract book name
                m = re.search(r'INSERT INTO "datakitab_([^"]+)"', line)
                if m:
                    book = m.group(1)
                    if book in books:
                        current_table = "datakitab_{}".format(book)
                    else:
                        current_table = None
            elif line.startswith('INSERT INTO "tema_'):
                m = re.search(r'INSERT INTO "tema_([^"]+)"', line)
                if m:
                    book = m.group(1)
                    if book == 'muslim_lama':
                        current_table = None
                        continue
                    if book == 'bukhari_old':
                        current_table = None
                        continue
                    if book in books:
                        current_table = "tema_{}".format(book)
                    else:
                        current_table = None
            elif line.startswith('INSERT INTO '):
                current_table = None
                
            if current_table:
                # Extract tuples from this line. It could be on the same line or next lines.
                # A simple regex to find (1, 'text', ...)
                # Actually, tema_ is just (id_kitab, id_bab, no_hadith)
                if current_table.startswith('tema_'):
                    book = current_table.split('_')[1]
                    # Find all tuples: (1,1,1)
                    tuples = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
                    for t in tuples:
                        k_id = int(t[1])
                        h_id = int(t[0])
                        if k_id not in stats_maps[book]:
                            stats_maps[book][k_id] = {'min': h_id, 'max': h_id, 'count': 0}
                        stats_maps[book][k_id]['min'] = min(stats_maps[book][k_id]['min'], h_id)
                        stats_maps[book][k_id]['max'] = max(stats_maps[book][k_id]['max'], h_id)
                        stats_maps[book][k_id]['count'] += 1
                        
                elif current_table.startswith('datakitab_'):
                    book = current_table.split('_')[1]
                    # Format: (1,'Indonesia','Arab','English')
                    # We can use a regex to match the id, and the next 3 strings.
                    # Because strings can contain commas, it's safer to use split or ast.literal_eval
                    # Let's use a simpler regex that matches (number, '...', '...', '...')
                    # or (number, '...', '...', NULL)
                    matches = re.findall(r'\((\d+),\s*\'(.*?)\',\s*\'(.*?)\',\s*(.*?)\)', line)
                    for m in matches:
                        k_id = int(m[0])
                        indo = m[1].replace("''", "'")
                        arab = m[2].replace("''", "'")
                        english_raw = m[3]
                        
                        english = indo # fallback
                        if english_raw.startswith("'") and english_raw.endswith("'"):
                            en = english_raw[1:-1].replace("''", "'")
                            if en.strip():
                                english = en
                                
                        kitab_maps[book][k_id] = {
                            "id": indo,
                            "ar": arab,
                            "en": english
                        }

    print("Writing JSON files...")
    for book in books:
        kitab_map = kitab_maps[book]
        stats_map = stats_maps[book]
        
        if not kitab_map:
            print("Skipping {}, no datakitab found.".format(book))
            continue
            
        chapters = []
        sorted_kitabs = sorted(list(kitab_map.keys()))
        for k_id in sorted_kitabs:
            k_info = kitab_map[k_id]
            stats = stats_map.get(k_id, {"min": 0, "max": 0, "count": 0})
            
            chapters.append({
                "id": "{}_c{}".format(book, k_id),
                "book_id": book,
                "chapter_number": k_id,
                "title_en": k_info["en"],
                "title_ar": k_info["ar"],
                "title_id": k_info["id"],
                "hadith_start": stats["min"],
                "hadith_end": stats["max"],
                "hadith_count": stats["count"]
            })
            
        out_data = {
            "book_id": book,
            "title_id_source": "Native Lidwa Database",
            "title_en_source": "Native Lidwa Database",
            "title_ar_source": "Native Lidwa Database",
            "chapters": chapters
        }
        
        out_path = os.path.join(LIDWA_CHAPTERS_DIR, "{}.json".format(book))
        with io.open(out_path, 'w', encoding='utf-8') as f:
            # json.dump kwargs for python 2/3 compat
            f.write(unicode(json.dumps(out_data, ensure_ascii=False, indent=2)))
            
        print("Built {}.json with {} chapters.".format(book, len(chapters)))

if __name__ == "__main__":
    parse_sql()
