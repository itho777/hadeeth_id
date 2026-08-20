import json
import os
import re
import sys

HF_DIR = r"h:\Itho\2026\Project\Hadeeth\data source\Atif"
HF_BOOKS = {
    "bukhari": "Sahih%20al-Bukhari.json",
    "muslim": "Sahih%20Muslim.json",
    "abudawud": "Sunan%20Abi%20Dawud.json",
    "tirmidhi": "Jami%60%20at-Tirmidhi.json",
    "nasai": "Sunan%20an-Nasa%27i.json",
    "ibnmajah": "Sunan%20Ibn%20Majah.json"
}

AB_DIR = "data/sources/ahmedbaset/by_book/the_9_books"
OUT_DIR = "data/sources/ahmedbaset_graded/by_book/the_9_books"

os.makedirs(OUT_DIR, exist_ok=True)

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\uFEFF]', '', text)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text) # strip tashkeel
    text = re.sub(r'[^\w\s]', '', text) # strip punctuation
    text = re.sub(r'\s+', '', text) # strip whitespace
    return text[:40] # first 40 chars is plenty for alignment

for key, hf_filename in HF_BOOKS.items():
    print(f"Processing {key}...")
    
    # Load AhmedBaset
    ab_path = os.path.join(AB_DIR, f"{key}.json")
    with open(ab_path, 'r', encoding='utf-8') as f:
        ab_data = json.load(f)
        
    hadiths = ab_data.get('hadiths', ab_data) if isinstance(ab_data, dict) else ab_data
    
    # Load HF
    hf_path = os.path.join(HF_DIR, hf_filename)
    try:
        with open(hf_path, 'r', encoding='utf-8') as f:
            hf_data = json.load(f)
    except Exception as e:
        print(f"Skipping {key}, HF file not found or error: {e}")
        continue
        
    counts_match = len(hadiths) == len(hf_data)
    
    mapped_count = 0
    if counts_match:
        print(f"  -> Rigid 1:1 mapping by index for {key}")
        for i in range(len(hadiths)):
            grade = hf_data[i].get('Grade', '').strip()
            if grade:
                hadiths[i]['grade_en'] = grade
                mapped_count += 1
    else:
        print(f"  -> Fuzzy mapping by Arabic text for {key} (Lengths: AB={len(hadiths)}, HF={len(hf_data)})")
        # Build dictionary of HF hadiths by normalized arabic
        hf_map = {}
        for h in hf_data:
            norm = normalize_arabic(h.get('Arabic_Text', ''))
            if norm:
                hf_map[norm] = h.get('Grade', '').strip()
                
        for i in range(len(hadiths)):
            norm_ab = normalize_arabic(hadiths[i].get('arabic', ''))
            grade = hf_map.get(norm_ab, '')
            if grade:
                hadiths[i]['grade_en'] = grade
                mapped_count += 1
            else:
                # Try a slightly shorter match if 40 chars failed
                short_ab = norm_ab[:25]
                for k, v in hf_map.items():
                    if k.startswith(short_ab):
                        hadiths[i]['grade_en'] = v
                        mapped_count += 1
                        break
                        
    print(f"  -> Successfully mapped grades for {mapped_count}/{len(hadiths)} hadiths.")
    
    # Save new JSON
    out_path = os.path.join(OUT_DIR, f"{key}.json")
    
    # Reconstruct original structure if it was a dict
    if isinstance(ab_data, dict) and 'hadiths' in ab_data:
        ab_data['hadiths'] = hadiths
        out_payload = ab_data
    else:
        out_payload = hadiths
        
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out_payload, f, ensure_ascii=False, indent=2)

print("\nAll done! New graded AhmedBaset files saved to:", OUT_DIR)
