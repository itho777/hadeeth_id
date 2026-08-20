import os
import json
import re
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
COMMENTARIES_DIR = os.path.join(DATA_DIR, "commentaries")
AHMEDBASET_DIR = os.path.join(DATA_DIR, "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(DATA_DIR, "links")

CONFIDENCE_THRESHOLD = 0.4

def normalize_arabic(text):
    if not text:
        return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_ahmedbaset(book_id):
    local_path = os.path.join(AHMEDBASET_DIR, "the_9_books", f"{book_id}.json")
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print(f"  [!] Ahmedbaset file not found: {local_path}")
        return []
    return data.get('hadiths', []) if isinstance(data, dict) else data

def load_commentaries(book_id):
    pattern = os.path.join(COMMENTARIES_DIR, f"{book_id}_*.json")
    files = glob.glob(pattern)
    commentaries = []
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                data['filename'] = os.path.basename(fpath)
                commentaries.append(data)
            except Exception as e:
                pass
    return commentaries

def link_syarah(book_id):
    print(f"\n[*] Linking Syarah for {book_id}...")
    ab_data = load_ahmedbaset(book_id)
    if not ab_data:
        return

    ab_docs, ab_map = [], []
    for h in ab_data:
        hnum = str(h.get('idInBook', h.get('id')))
        if not hnum:
            continue
        norm_ar = normalize_arabic(h.get('arabic', ''))
        if not norm_ar:
            continue
        ab_docs.append(norm_ar)
        ab_map.append(hnum)
        
    print(f"  Loaded {len(ab_docs)} AhmedBaset anchors.")

    com_data = load_commentaries(book_id)
    if not com_data:
        print("  [!] No commentaries found.")
        return
        
    com_docs, com_map = [], []
    for c in com_data:
        norm_ar = normalize_arabic(c.get('hadith_ar', ''))
        if not norm_ar:
            continue
        com_docs.append(norm_ar)
        com_map.append(c['filename'])
        
    print(f"  Loaded {len(com_docs)} commentaries.")

    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=1)
    ab_matrix = vectorizer.fit_transform(ab_docs)
    com_matrix = vectorizer.transform(com_docs)
    sims = cosine_similarity(com_matrix, ab_matrix)

    syarah_links = {}
    matched = 0
    
    for i, c_file in enumerate(com_map):
        best_idx = sims[i].argmax()
        score = float(sims[i][best_idx])
        if score >= CONFIDENCE_THRESHOLD:
            ab_id = ab_map[best_idx]
            if ab_id not in syarah_links:
                syarah_links[ab_id] = []
            syarah_links[ab_id].append(c_file)
            matched += 1

    print(f"  Matched {matched}/{len(com_map)} commentaries to AhmedBaset anchors.")

    out_file = os.path.join(LINKS_DIR, f"syarah_link_{book_id}.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(syarah_links, f, ensure_ascii=False, indent=2)
    print(f"  Saved syarah links to {out_file}")

if __name__ == '__main__':
    link_syarah("bukhari")
