import json
import os
import zipfile

books_to_process = {
    'qudsi': 'db/by_book/forties/qudsi40.json',
    'shah': 'db/by_book/forties/shahwaliullah40.json',
    'adab': 'db/by_book/other_books/aladab_almufrad.json',
    'bulugh': 'db/by_book/other_books/bulugh_almaram.json',
    'mishkat': 'db/by_book/other_books/mishkat_almasabih.json',
    'riyad': 'db/by_book/other_books/riyad_assalihin.json',
    'shamail': 'db/by_book/other_books/shamail_muhammadiyah.json'
}

zip_path = 'scratch/hadith-json.zip'
base_prefix = 'hadith-json-main/'

os.makedirs('data/chapters', exist_ok=True)
os.makedirs('data/editions', exist_ok=True)

with zipfile.ZipFile(zip_path, 'r') as z:
    for book_id, json_path in books_to_process.items():
        print(f"Processing {book_id}...")
        full_path = base_prefix + json_path
        data = json.loads(z.read(full_path).decode('utf-8'))
        
        # Build chapters
        chapters_map = {}
        ara_hadiths = []
        eng_hadiths = []
        
        for h in data.get('hadiths', []):
            ch_id = h.get('chapterId')
            if ch_id is None:
                ch_id = 1
                
            hadith_num = h.get('idInBook') or h.get('id')
            
            # Update chapter info
            if ch_id not in chapters_map:
                chapters_map[ch_id] = {
                    "id": f"{book_id}_c{ch_id}",
                    "book_id": book_id,
                    "chapter_number": ch_id,
                    "title_en": f"Chapter {ch_id}",
                    "title_ar": f"باب {ch_id}",
                    "title_id": f"Bab {ch_id}",
                    "hadith_start": hadith_num,
                    "hadith_end": hadith_num,
                    "hadith_count": 0
                }
            
            ch = chapters_map[ch_id]
            ch["hadith_end"] = max(ch["hadith_end"], hadith_num)
            ch["hadith_count"] += 1
            
            # Format ara and eng
            ara_text = h.get('arabic', '')
            eng_obj = h.get('english') or {}
            
            eng_text = ""
            if isinstance(eng_obj, dict):
                narrator = eng_obj.get('narrator', '')
                text = eng_obj.get('text', '')
                eng_text = f"{narrator} {text}".strip()
            elif isinstance(eng_obj, str):
                eng_text = eng_obj
                
            ara_hadiths.append({
                "hadithnumber": hadith_num,
                "text": ara_text
            })
            
            eng_hadiths.append({
                "hadithnumber": hadith_num,
                "text": eng_text
            })
            
        # Write chapters
        chapters_list = list(chapters_map.values())
        chapters_list.sort(key=lambda x: x['chapter_number'])
        
        with open(f'data/chapters/{book_id}.json', 'w', encoding='utf-8') as f:
            json.dump(chapters_list, f, ensure_ascii=False, indent=2)
            
        # Write editions
        with open(f'data/editions/ara-{book_id}.json', 'w', encoding='utf-8') as f:
            json.dump({"metadata": {}, "hadiths": ara_hadiths}, f, ensure_ascii=False, indent=2)
            
        with open(f'data/editions/eng-{book_id}.json', 'w', encoding='utf-8') as f:
            json.dump({"metadata": {}, "hadiths": eng_hadiths}, f, ensure_ascii=False, indent=2)

print("Done processing all 7 secondary books!")
