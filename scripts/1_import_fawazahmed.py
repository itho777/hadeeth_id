import json
import os
import urllib.request
import time

out_dir = 'data/sources/fawaz_combined_v2'
os.makedirs(out_dir, exist_ok=True)

langs = ['ara', 'eng', 'ind', 'urd', 'ben', 'fra']
books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi']

def fetch_json(url):
    print(f"Fetching {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error fetching {url}: {e}. Retrying...")
            time.sleep(2)
    return None

for book in books:
    print(f"\n--- Processing {book} ---")
    combined_map = {} # Key: (book, hadith_in_book)
    
    for lang in langs:
        url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{lang}-{book}.json"
        data = fetch_json(url)
        if not data:
            # Maybe the edition is named differently e.g. eng-bukhari1?
            # Let's try to just fall back if not found.
            continue
            
        hadiths = data.get('hadiths', [])
        
        for h in hadiths:
            ref = h.get('reference', {})
            b_num = ref.get('book')
            h_num = ref.get('hadith')
            global_num = h.get('hadithnumber')
            
            # Use tuple of (kitab, hadith_in_kitab) as primary key
            key = (str(b_num), str(h_num))
            if key not in combined_map:
                combined_map[key] = {
                    'reference': ref,
                    'hadithnumber': global_num,
                    'grades': h.get('grades', [])
                }
            
            # Overwrite global num and grades if it's arabic
            if lang == 'ara':
                combined_map[key]['hadithnumber'] = global_num
                combined_map[key]['grades'] = h.get('grades', [])
                
            combined_map[key][f'text_{lang}'] = h.get('text', '')

    # Convert to list and sort by global hadith number (fallback to reference)
    def sort_key(item):
        k, v = item
        try:
            return float(v['hadithnumber'])
        except:
            return 999999
            
    sorted_hadiths = [v for k, v in sorted(combined_map.items(), key=sort_key)]
    
    out_path = os.path.join(out_dir, f"{book}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_hadiths, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(sorted_hadiths)} hadiths for {book}.")
    
print("\nDone.")
