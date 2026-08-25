import json
import os
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LIDWA_DIR = os.path.join(BASE_DIR, "data", "sources", "lidwa")
FAWAZ_DIR = os.path.join(BASE_DIR, "data", "sources", "fawaz_api", "editions")

def strip_tashkeel(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = text.replace('\u0671', '\u0627')
    return text

def align_book(book_name):
    print(f"Aligning {book_name}...")
    lidwa_path = os.path.join(LIDWA_DIR, f"{book_name}.ndjson")
    if not os.path.exists(lidwa_path): return
    
    l_data = []
    with open(lidwa_path, 'r', encoding='utf-8') as f:
        for line in f: l_data.append(json.loads(line))
            
    fawaz_ar_path = os.path.join(FAWAZ_DIR, f"ara-{book_name}.json")
    if not os.path.exists(fawaz_ar_path): return
    
    with open(fawaz_ar_path, 'r', encoding='utf-8') as f:
        f_data = json.load(f).get('hadiths', [])
        
    l_texts = [strip_tashkeel(h.get('text_ar', '')) for h in l_data]
    f_texts = [strip_tashkeel(h.get('text', '')) for h in f_data]
    
    vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4), min_df=1)
    vec.fit(l_texts + f_texts)
    l_tfidf = vec.transform(l_texts)
    f_tfidf = vec.transform(f_texts)
    
    sim = cosine_similarity(l_tfidf, f_tfidf)
    
    links = {}
    for i, p_row in enumerate(sim):
        best_idx = np.argmax(p_row)
        best_score = p_row[best_idx]
        if best_score > 0.1:
            links[str(l_data[i]['id'])] = f_data[best_idx]['hadithnumber']
            
    print(f"Mapped {len(links)} / {len(l_data)} for {book_name}")
    with open(f"links_{book_name}.json", "w", encoding='utf-8') as f:
        json.dump(links, f, indent=2)

for b in ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]:
    align_book(b)