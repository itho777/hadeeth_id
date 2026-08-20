import json
import os
import re
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
from scripts.relink_matan import load_fawaz, load_ahmedbaset, load_lidwa, vectorized_match, extract_matan, normalize_arabic, ANCHORS

DATA_DIR = os.path.join(BASE_DIR, "data")
LINKS_DIR = os.path.join(DATA_DIR, "links")

SECONDARY_BOOKS = ['nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'shamail', 'tabarani', 'syafii', 'riyad_arab']
NINE_BOOKS = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad']

def get_targets_from_text(text):
    targets = set()
    norm = normalize_arabic(text)
    if 'متفق عليه' in norm or ('بخارى' in norm and 'مسلم' in norm) or ('بشارى' in norm and 'مسلم' in norm):
        targets.add('bukhari')
        targets.add('muslim')
    if 'بخارى' in norm or 'بشارى' in norm: targets.add('bukhari')
    if 'مسلم' in norm: targets.add('muslim')
    if 'ابو داود' in norm: targets.add('abudawud')
    if 'ترمذى' in norm: targets.add('tirmidhi')
    if 'نسائى' in norm: targets.add('nasai')
    if 'ابن ماجه' in norm: targets.add('ibnmajah')
    if 'مالك' in norm: targets.add('malik')
    if 'دارمى' in norm: targets.add('darimi')
    if 'احمد' in norm: targets.add('ahmad')
    return list(targets)

def load_canonical_data():
    print("[*] Pre-loading all 9 Canonical Books...")
    canonical = {}
    for b in NINE_BOOKS:
        anchor = ANCHORS[b]
        if anchor == 'fawaz': canonical[b] = load_fawaz(b)
        elif anchor == 'ahmedbaset': canonical[b] = load_ahmedbaset(b)
        elif anchor == 'lidwa': canonical[b] = load_lidwa(b)
    return canonical

def run_phase_2():
    print("[*] Starting Phase 2 Cross-Collection NLP Matcher...")
    canonical = load_canonical_data()
    cross_links = {}
    
    for b in SECONDARY_BOOKS:
        print(f" -> Parsing {b}...")
        anchor = ANCHORS[b]
        if anchor == 'fawaz': data = load_fawaz(b)
        elif anchor == 'ahmedbaset': data = load_ahmedbaset(b)
        elif anchor == 'lidwa': data = load_lidwa(b)
        else: continue
            
        book_cross_links = {}
        
        # We process in batches grouped by target to vectorize matching
        target_groups = {cb: [] for cb in NINE_BOOKS}
        id_to_hadith = {}
        
        for h in data:
            hid = h['id']
            id_to_hadith[hid] = h
            targets = get_targets_from_text(h['text'])
            for t in targets:
                target_groups[t].append(h)
                
        for t, h_list in target_groups.items():
            if not h_list: continue
            print(f"    - Running NLP against {t} for {len(h_list)} hadiths...")
            # Use 0.85 threshold to be strictly prudent
            matches = vectorized_match(h_list, canonical[t], threshold=0.85)
            for hid, match_id in matches.items():
                if hid not in book_cross_links: book_cross_links[hid] = []
                book_cross_links[hid].append(f"{t}:{match_id}")
                
        if book_cross_links:
            cross_links[b] = book_cross_links
            print(f"    [+] Generated {sum(len(v) for v in book_cross_links.values())} cross-references for {b}")
            
    out_path = os.path.join(LINKS_DIR, "cross_links.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(cross_links, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Saved cross-references to {out_path}")

if __name__ == "__main__":
    run_phase_2()
