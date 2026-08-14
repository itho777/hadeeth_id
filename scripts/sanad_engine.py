import os
import json
import re
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")
RAWIS_PATH = os.path.join(BASE_DIR, "data", "rawis", "scholars_index.json")

CORE_9 = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]
ADDITIONAL_8 = ["nawawi", "qudsi", "shah", "adab", "bulugh", "mishkat", "riyad", "shamail"]

def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\uFEFF]', '', text) # Remove invisible directional marks
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text) # Remove tashkeel
    text = re.sub(r'[إأآا]', 'ا', text) # Normalize alef
    text = re.sub(r'ة', 'ه', text) # Normalize taa marbuta
    text = re.sub(r'ي', 'ى', text) # Normalize yaa
    return text

def extract_isnad(text):
    text = normalize_arabic(text)
    # Split by Prophet's speech markers to isolate the chain
    markers = ["قال رسول الله", "سمعت رسول الله", "عن النبى", "يقول رسول الله", "ان رسول الله", "عن رسول الله"]
    min_idx = len(text)
    for m in markers:
        idx = text.find(m)
        if idx != -1 and idx < min_idx:
            min_idx = idx
            
    if min_idx == len(text):
        return text # If no marker found, return all (fallback)
    return text[:min_idx]

def extract_names_from_isnad(isnad):
    # Split by transmission keywords
    keywords = r'(حدثنا|حدثنى|اخبرنا|اخبرنى|انبانا|انبانى|عن|سمعت|قال|ح وحدثنا)'
    parts = re.split(keywords, isnad)
    names = []
    for p in parts:
        p = p.strip()
        if p and not re.match(keywords, p) and len(p) > 3:
            names.append(p)
    return names

def build_scholar_index():
    with open(RAWIS_PATH, 'r', encoding='utf-8') as f:
        scholars = json.load(f)
        
    index = {}
    for sid, data in scholars.items():
        raw_name = data.get('name_ar', '')
        # Extract Arabic characters
        ar_chars = re.findall(r'[\u0600-\u06FF\s]+', raw_name)
        if ar_chars:
            ar_name = " ".join(ar_chars).replace('رضي الله عنه', '').replace('رحمه الله', '').strip()
            name_ar = normalize_arabic(ar_name)
            if name_ar:
                index[name_ar] = sid
                # Index first 2 and 3 words for loose matching
                words = name_ar.split()
                if len(words) >= 2:
                    short_name2 = " ".join(words[:2])
                    if short_name2 not in index:
                        index[short_name2] = sid
                if len(words) >= 3:
                    short_name3 = " ".join(words[:3])
                    if short_name3 not in index:
                        index[short_name3] = sid
    return index

def process_sanad():
    print("[*] Loading Scholar Index...")
    scholar_index = build_scholar_index()
    print(f"[+] Loaded {len(scholar_index)} searchable name variations.")
    
    # Process Core 9
    for book in CORE_9:
        link_path = os.path.join(LINKS_DIR, f"{book}.json")
        source_path = os.path.join(SOURCES_DIR, "lidwa", f"{book}.json")
        
        if not os.path.exists(link_path) or not os.path.exists(source_path):
            continue
            
        print(f"[*] Processing Sanad for {book}...")
        with open(link_path, 'r', encoding='utf-8') as f:
            links = json.load(f)
        with open(source_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
            
        # O(1) source lookup
        source_lookup = {str(row['id']): row for row in source_data}
        
        matched_count = 0
        for anchor_id, l_data in links.items():
            lidwa_id = str(l_data.get('lidwa_id'))
            row = source_lookup.get(lidwa_id)
            narrators = []
            
            if row and row.get('text_ar'):
                isnad = extract_isnad(row['text_ar'])
                raw_names = extract_names_from_isnad(isnad)
                
                for name in raw_names:
                    norm_name = name.replace('رضي الله عنه', '').strip()
                    # Attempt exact match
                    sid = scholar_index.get(norm_name)
                    if not sid:
                        words = norm_name.split()
                        # Attempt 3 words
                        if len(words) >= 3:
                            sid = scholar_index.get(" ".join(words[:3]))
                        # Attempt 2 words
                        if not sid and len(words) >= 2:
                            sid = scholar_index.get(" ".join(words[:2]))
                            
                    if sid:
                        narrators.append(sid)
                        
            if narrators:
                matched_count += 1
            l_data['kaggle_narrators'] = narrators
            
        with open(link_path, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2)
            
        print(f"[+] {book}: Found Sanad links for {matched_count} hadiths.")

if __name__ == "__main__":
    process_sanad()
