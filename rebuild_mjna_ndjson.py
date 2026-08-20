"""
Rebuild MJNA books' API NDJSON files to have the proper translations structure
with source: 'mjna' — consistent with how the 9-core books store translations.

Before: { hadith_number, text_ar, text_id, ... }
After:  { hadith_number, text_ar, translations: { ar: [{source:'mjna', text:...}], id: [{source:'mjna', text:...}] } }
"""

import json
import os

MJNA_BOOKS = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni']

for book in MJNA_BOOKS:
    in_path = f'data/api/{book}.ndjson'
    out_path = f'data/api/{book}.ndjson'
    
    rows = []
    with open(in_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    
    rebuilt = []
    for row in rows:
        text_ar = row.get('text_ar', '')
        text_id = row.get('text_id', '')
        text_en = row.get('text_en', '')
        
        translations = {}
        if text_ar:
            translations['ar'] = [{'source': 'mjna', 'text': text_ar}]
        if text_id:
            translations['id'] = [{'source': 'mjna', 'text': text_id}]
        if text_en:
            translations['en'] = [{'source': 'mjna', 'text': text_en}]
        
        new_row = {
            'id': row.get('id') or row.get('hadith_number'),
            'hadith_number': row.get('hadith_number'),
            'chapter_id': row.get('chapter_id'),
            'text_ar': text_ar,
            'translations': translations
        }
        rebuilt.append(new_row)
    
    # Write back
    with open(out_path, 'w', encoding='utf-8') as f:
        for row in rebuilt:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    
    print(f"Rebuilt {book}: {len(rebuilt)} hadiths, sample translations keys: {list(rebuilt[0]['translations'].keys()) if rebuilt else 'none'}")

print("\nDone! All MJNA NDJSON files now use translations.id[source=mjna] structure.")
