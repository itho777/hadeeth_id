# -*- coding: utf-8 -*-
import json
import os
import re
import codecs
import time

def get_ngrams(text, n=3):
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = text.replace(u'\u0671', u'\u0627')
    text = text.replace(' ', '')
    if not text: return set()
    return set([text[i:i+n] for i in range(len(text)-n+1)])

def jaccard(set1, set2):
    if not set1 or not set2: return 0.0
    return float(len(set1.intersection(set2))) / float(len(set1.union(set2)))

def run():
    print("Loading Lidwa Muslim...")
    l_data = []
    with codecs.open("../data/sources/lidwa/muslim.ndjson", 'r', 'utf-8') as f:
        for line in f:
            l_data.append(json.loads(line))
            
    print("Loading Fawazahmed Muslim...")
    f_data = []
    with codecs.open("../data/sources/fawaz_api/editions/ara-muslim.json", 'r', 'utf-8') as f:
        f_data = json.load(f).get('hadiths', [])
        
    print("Computing ngrams...")
    l_ngrams = [get_ngrams(h.get('text_ar', '')) for h in l_data]
    f_ngrams = [get_ngrams(h.get('text', '')) for h in f_data]
    
    links = {}
    print("Matching (this may take a minute)...")
    start = time.time()
    for i, ln in enumerate(l_ngrams):
        best_score = 0
        best_idx = -1
        
        # Heuristic: search in a window to speed up
        # We expect Lidwa i to be roughly near Fawaz i (but offset by up to 300)
        start_idx = max(0, i - 1000)
        end_idx = min(len(f_ngrams), i + 1000)
        
        for j in range(start_idx, end_idx):
            score = jaccard(ln, f_ngrams[j])
            if score > best_score:
                best_score = score
                best_idx = j
                
        if best_score > 0.1:
            links[str(l_data[i]['id'])] = f_data[best_idx]['hadithnumber']
            
        if i % 1000 == 0:
            print("Processed %d / %d in %.1fs" % (i, len(l_ngrams), time.time() - start))
            
    with open("links_muslim.json", "w") as f:
        json.dump(links, f)
        
    print("Done! Links saved.")

if __name__ == '__main__':
    run()