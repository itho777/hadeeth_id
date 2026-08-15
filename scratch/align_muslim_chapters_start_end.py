import json, sys, urllib.request, re
sys.stdout.reconfigure(encoding='utf-8')

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text) # Remove diacritics
    text = re.sub(r'[^ء-ي ]', '', text) # Keep only Arabic letters and spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("Loading reference...")
url = 'https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books/muslim.json'
with urllib.request.urlopen(url) as r:
    ref = json.load(r)

print("Loading our dataset...")
with open('data/editions/ara-muslim.json', encoding='utf-8') as f:
    ours = json.load(f)['hadiths']

our_texts = [normalize_arabic(h['text']) for h in ours]

def find_best_match(ref_text, expected_id, search_radius=400):
    start_idx = max(0, expected_id - search_radius)
    end_idx = min(len(our_texts), expected_id + search_radius)
    
    # Use a solid chunk of the matn (last 200 chars)
    search_chunk = ref_text[-200:]
    if len(search_chunk) < 50: search_chunk = ref_text
    
    best_match_id = -1
    highest_score = 0
    
    # 1. Exact substring match
    for i in range(start_idx, end_idx):
        if search_chunk in our_texts[i]:
            return ours[i]['hadithnumber']
            
    # 2. Fuzzy match fallback
    words = set(search_chunk.split()[-20:])
    for i in range(start_idx, end_idx):
        our_words = set(our_texts[i].split())
        overlap = len(words & our_words)
        if overlap > highest_score and overlap > 5:
            highest_score = overlap
            best_match_id = ours[i]['hadithnumber']
            
    return best_match_id

# Group reference hadiths by chapter
ref_chapters = {}
for ch in ref['chapters']:
    ref_chapters[ch['id']] = {
        'title_en': ch['english'],
        'title_ar': ch['arabic'],
        'hadiths': []
    }
for h in ref['hadiths']:
    ref_chapters[h['chapterId']]['hadiths'].append(h)

mapped_chapters = []

for ch_id in range(1, 57):
    if not ref_chapters[ch_id]['hadiths']:
        continue
        
    first_h = ref_chapters[ch_id]['hadiths'][0]
    last_h = ref_chapters[ch_id]['hadiths'][-1]
    
    start_num = find_best_match(normalize_arabic(first_h['arabic']), first_h['idInBook'])
    end_num = find_best_match(normalize_arabic(last_h['arabic']), last_h['idInBook'])
    
    if start_num != -1 and end_num != -1:
        # Guarantee start is before end
        if start_num > end_num:
            start_num, end_num = end_num, start_num
            
        mapped_chapters.append({
            "id": f"muslim_c{ch_id}",
            "book_id": "muslim",
            "chapter_number": ch_id,
            "title_en": ref_chapters[ch_id]['title_en'],
            "title_ar": ref_chapters[ch_id]['title_ar'],
            "title_id": "", # Will map from existing if possible
            "hadith_start": start_num,
            "hadith_end": end_num,
            "hadith_count": end_num - start_num + 1
        })
        print(f"Ch {ch_id:02d}: {start_num:4d} - {end_num:4d} (Count: {end_num-start_num+1:3d}) | {ref_chapters[ch_id]['title_en'][:30]}")
    else:
        print(f"Ch {ch_id:02d}: FAILED TO MATCH")

# Handle Muqaddimah (0) which is always 1-7 in Darussalam 7563
mapped_chapters.append({
    "id": "muslim_c0",
    "book_id": "muslim",
    "chapter_number": 0,
    "title_en": "Introduction",
    "title_ar": "المقدمة",
    "title_id": "Muqaddimah",
    "hadith_start": 1,
    "hadith_end": 7,
    "hadith_count": 7
})

# Sort by the start number since the order of books differs!
mapped_chapters.sort(key=lambda x: x['hadith_start'])

# Re-number the chapters to be perfectly sequential for UI
for idx, ch in enumerate(mapped_chapters):
    if ch['chapter_number'] != 0:
        ch['chapter_number'] = idx
        ch['id'] = f"muslim_c{idx}"

# Restore Indonesian titles from the previous muslim.json if available
try:
    with open('data/chapters/muslim.json', 'r', encoding='utf-8') as f:
        old_chapters = json.load(f)
        id_map = {c['title_en']: c.get('title_id', '') for c in old_chapters}
        for ch in mapped_chapters:
            if ch['title_en'] in id_map:
                ch['title_id'] = id_map[ch['title_en']]
except:
    pass

# Patch gaps between chapters (ensure continuous coverage)
for i in range(len(mapped_chapters) - 1):
    curr_ch = mapped_chapters[i]
    next_ch = mapped_chapters[i+1]
    
    if curr_ch['hadith_end'] < next_ch['hadith_start'] - 1:
        # Extend current chapter to cover the gap
        curr_ch['hadith_end'] = next_ch['hadith_start'] - 1
        curr_ch['hadith_count'] = curr_ch['hadith_end'] - curr_ch['hadith_start'] + 1

# Ensure last chapter reaches 7563
if mapped_chapters[-1]['hadith_end'] < 7563:
    mapped_chapters[-1]['hadith_end'] = 7563
    mapped_chapters[-1]['hadith_count'] = mapped_chapters[-1]['hadith_end'] - mapped_chapters[-1]['hadith_start'] + 1

# Write to file
with open('data/chapters/muslim.json', 'w', encoding='utf-8') as f:
    json.dump(mapped_chapters, f, ensure_ascii=False, indent=2)

print("\nFinal bounded chapters written to data/chapters/muslim.json")
