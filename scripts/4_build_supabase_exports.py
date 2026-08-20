import json
import csv
import os
import glob

api_dir = 'data/api'
out_csv = 'data/supabase_search.csv'

books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi']

with open(out_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['book', 'hadith_id', 'text_ar', 'text_en', 'text_id', 'tags'])
    
    for book in books:
        ndjson_file = os.path.join(api_dir, f"{book}.ndjson")
        if not os.path.exists(ndjson_file):
            continue
            
        print(f"Exporting {book} to CSV...")
        with open(ndjson_file, 'r', encoding='utf-8') as n_file:
            for line in n_file:
                record = json.loads(line)
                
                # Get the first text of each language
                text_ar = record['translations'].get('ar', [{'text': ''}])[0]['text'] if 'ar' in record['translations'] else ''
                text_en = record['translations'].get('en', [{'text': ''}])[0]['text'] if 'en' in record['translations'] else ''
                text_id = record['translations'].get('id', [{'text': ''}])[0]['text'] if 'id' in record['translations'] else ''
                
                tags = ", ".join(record.get('tags', []))
                
                writer.writerow([
                    book,
                    record['id'],
                    text_ar,
                    text_en,
                    text_id,
                    tags
                ])
                
print("Supabase CSV generated at data/supabase_search.csv")
