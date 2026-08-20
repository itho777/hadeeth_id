import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(BASE_DIR, 'data', 'api')
EDITIONS_DIR = os.path.join(BASE_DIR, 'data', 'editions')

books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah']

def clean_arabic(text):
    import re
    # Just a simple strip
    return text.strip()

for book in books:
    api_file = os.path.join(API_DIR, f"{book}.ndjson")
    ara_file = os.path.join(EDITIONS_DIR, f"ara-{book}.ndjson")
    eng_file = os.path.join(EDITIONS_DIR, f"eng-{book}.ndjson")
    
    if not os.path.exists(api_file) or not os.path.exists(ara_file):
        continue
        
    # Read API
    api_hadiths = []
    api_ids = set()
    with open(api_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            h = json.loads(line)
            api_hadiths.append(h)
            api_ids.add(str(h.get('hadith_number', h.get('id'))))
            
    # Read Fawaz Ara
    ara_hadiths = {}
    with open(ara_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            h = json.loads(line)
            hid = str(h.get('hadithnumber', h.get('id')))
            ara_hadiths[hid] = h
            
    # Read Fawaz Eng
    eng_hadiths = {}
    if os.path.exists(eng_file):
        with open(eng_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                h = json.loads(line)
                hid = str(h.get('hadithnumber', h.get('id')))
                eng_hadiths[hid] = h
                
    missing_ids = []
    for hid in ara_hadiths.keys():
        if hid not in api_ids:
            missing_ids.append(hid)
            
    if not missing_ids:
        print(f"{book}: No missing hadiths.")
        continue
        
    print(f"{book}: Found {len(missing_ids)} missing hadiths from Fawazahmed. Injecting...")
    
    # Sort missing ids
    def try_int(x):
        try:
            return int(x)
        except:
            return 999999
    
    missing_ids.sort(key=try_int)
    
    # For each missing hadith, try to guess the chapter_id based on the closest previous hadith in API
    def get_closest_chapter(hid_str):
        hid_int = try_int(hid_str)
        closest_ch = "1"
        min_diff = 999999
        for api_h in api_hadiths:
            api_int = try_int(api_h.get('hadith_number'))
            if api_int <= hid_int:
                diff = hid_int - api_int
                if diff < min_diff:
                    min_diff = diff
                    closest_ch = str(api_h.get('chapter_id', '1'))
        return closest_ch
        
    for hid in missing_ids:
        ara_h = ara_hadiths[hid]
        eng_h = eng_hadiths.get(hid, {})
        
        ch_id = get_closest_chapter(hid)
        
        text_ar = ara_h.get('text', '')
        text_en = eng_h.get('text', '')
        
        new_h = {
            "id": int(hid) if hid.isdigit() else hid,
            "hadith_number": hid,
            "chapter_id": int(ch_id) if ch_id.isdigit() else ch_id,
            "text_ar": text_ar,
            "text_ar_plain": clean_arabic(text_ar),
            "text_en": text_en,
            "text_id": "",
            "syarah_ar": "",
            "syarah_en": "",
            "syarah_id": "",
            "syarah_source": "",
            "related": [],
            "grade_en": "Not graded",
            "grade_id": "Tidak ada derajat",
            "elevation": "",
            "lidwa_id": None,
            "grade": ""
        }
        api_hadiths.append(new_h)
        api_ids.add(hid)
        
    # Re-sort the entire API list
    api_hadiths.sort(key=lambda x: try_int(x.get('hadith_number')))
    
    # Save back to API
    with open(api_file, 'w', encoding='utf-8') as f:
        for h in api_hadiths:
            f.write(json.dumps(h, ensure_ascii=False) + '\n')
            
    print(f"{book}: Successfully injected {len(missing_ids)} hadiths.")
