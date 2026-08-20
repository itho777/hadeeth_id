import json
import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAWAZ_DIR = os.path.join(DATA_DIR, "editions")
LIDWA_DIR = os.path.join(DATA_DIR, "sources", "lidwa")
AB_DIR = os.path.join(DATA_DIR, "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(DATA_DIR, "links")

AB_PATHS = {
    'bukhari': 'the_9_books/bukhari.json', 'muslim': 'the_9_books/muslim.json', 'abudawud': 'the_9_books/abudawud.json',
    'tirmidhi': 'the_9_books/tirmidhi.json', 'nasai': 'the_9_books/nasai.json', 'ibnmajah': 'the_9_books/ibnmajah.json',
    'malik': 'the_9_books/malik.json', 'darimi': 'the_9_books/darimi.json', 'ahmad': 'the_9_books/ahmed.json',
    'qudsi': 'forties/qudsi40.json', 'shah': 'forties/shahwaliullah40.json', 'adab': 'other_books/aladab_almufrad.json',
    'bulugh': 'other_books/bulugh_almaram.json', 'mishkat': 'other_books/mishkat_almasabih.json',
    'riyad': 'other_books/riyad_assalihin.json', 'shamail': 'other_books/shamail_muhammadiyah.json'
}

ANCHORS = {
    'bukhari': 'fawaz', 'muslim': 'fawaz', 'abudawud': 'ahmedbaset', 'tirmidhi': 'ahmedbaset',
    'nasai': 'ahmedbaset', 'ibnmajah': 'ahmedbaset', 'malik': 'ahmedbaset', 'darimi': 'ahmedbaset',
    'ahmad': 'fawaz', 'nawawi': 'fawaz', 'qudsi': 'fawaz', 'shah': 'fawaz', 'adab': 'fawaz',
    'bulugh': 'fawaz', 'mishkat': 'fawaz', 'riyad': 'fawaz', 'shamail': 'fawaz', 'tabarani': 'fawaz',
    'syafii': 'lidwa', 'riyad_arab': 'lidwa'
}

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\uFEFF]', '', text) 
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text) 
    text = re.sub(r'ة', 'ه', text) 
    text = re.sub(r'ي', 'ى', text)
    text = text.replace("ـ", "").replace(".", "").replace(",", "").replace("،", "").strip()
    return text

def extract_matan(text):
    text = normalize_arabic(text)
    markers = ["قال رسول الله", "سمعت رسول الله", "عن النبى", "يقول رسول الله", "ان رسول الله", "عن رسول الله"]
    min_idx = len(text)
    for m in markers:
        idx = text.find(m)
        if idx != -1 and idx < min_idx:
            min_idx = idx
    if min_idx == len(text):
        return text
    return text[min_idx:]

def load_fawaz(book_id):
    path = os.path.join(FAWAZ_DIR, f'ara-{book_id}.json')
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
        hadiths = d.get('hadiths', []) if isinstance(d, dict) else d
        return [{"id": str(i+1), "text": extract_matan(h.get('text', ''))} for i, h in enumerate(hadiths)]

def load_ahmedbaset(book_id):
    ab_rel = AB_PATHS.get(book_id)
    if not ab_rel: return []
    path = os.path.join(AB_DIR, ab_rel)
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
        hadiths = d.get('hadiths', []) if isinstance(d, dict) else d
        return [{"id": str(h.get('idInBook', h.get('id'))), "text": extract_matan(h.get('arabic', ''))} for h in hadiths]

def load_lidwa(book_id):
    path = os.path.join(LIDWA_DIR, f'{book_id}.json')
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
        if isinstance(d, dict): d = [v for k,v in d.items()]
        return [{"id": str(h.get('hadith_number', h.get('id'))), "text": extract_matan(h.get('text_ar', h.get('arab', '')))} for h in d]

def vectorized_match(primary_data, secondary_data, threshold=0.85):
    if not primary_data or not secondary_data: return {}
    
    primary_texts = [h['text'] for h in primary_data]
    secondary_texts = [h['text'] for h in secondary_data]
    
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4), min_df=1)
    # Fit on all texts to share vocabulary
    all_texts = primary_texts + secondary_texts
    try:
        vectorizer.fit(all_texts)
    except ValueError:
        return {} # Empty vocabulary
        
    primary_tfidf = vectorizer.transform(primary_texts)
    secondary_tfidf = vectorizer.transform(secondary_texts)
    
    # Calculate cosine similarity matrix (Primary X Secondary)
    sim_matrix = cosine_similarity(primary_tfidf, secondary_tfidf)
    
    mapping = {}
    for i, p_row in enumerate(sim_matrix):
        best_idx = np.argmax(p_row)
        best_score = p_row[best_idx]
        if best_score >= threshold:
            mapping[primary_data[i]['id']] = secondary_data[best_idx]['id']
            
    return mapping

def build_links_for_book(book_id):
    anchor = ANCHORS.get(book_id)
    if not anchor: return
    
    print(f"[*] Relinking {book_id} (Anchor: {anchor})...")
    
    fawaz_data = load_fawaz(book_id)
    ab_data = load_ahmedbaset(book_id)
    lidwa_data = load_lidwa(book_id)
    
    master_links = {}
    
    if anchor == 'fawaz':
        ab_matches = vectorized_match(fawaz_data, ab_data)
        lidwa_matches = vectorized_match(fawaz_data, lidwa_data)
        for h in fawaz_data:
            hid = h['id']
            links = {'fawaz_id': hid}
            if hid in ab_matches: links['ahmedbaset_id'] = ab_matches[hid]
            if hid in lidwa_matches: links['lidwa_id'] = lidwa_matches[hid]
            master_links[hid] = links
            
    elif anchor == 'ahmedbaset':
        f_matches = vectorized_match(ab_data, fawaz_data)
        lidwa_matches = vectorized_match(ab_data, lidwa_data)
        for h in ab_data:
            hid = h['id']
            links = {'ahmedbaset_id': hid}
            if hid in f_matches: links['fawaz_id'] = f_matches[hid]
            if hid in lidwa_matches: links['lidwa_id'] = lidwa_matches[hid]
            master_links[hid] = links
            
    elif anchor == 'lidwa':
        f_matches = vectorized_match(lidwa_data, fawaz_data)
        ab_matches = vectorized_match(lidwa_data, ab_data)
        for h in lidwa_data:
            hid = h['id']
            links = {'lidwa_id': hid}
            if hid in f_matches: links['fawaz_id'] = f_matches[hid]
            if hid in ab_matches: links['ahmedbaset_id'] = ab_matches[hid]
            master_links[hid] = links

    os.makedirs(LINKS_DIR, exist_ok=True)
    out_path = os.path.join(LINKS_DIR, f"{book_id}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(master_links, f, ensure_ascii=False, indent=2)
    print(f" [+] Generated {len(master_links)} links for {book_id}")

if __name__ == "__main__":
    for b in ANCHORS.keys():
        build_links_for_book(b)
