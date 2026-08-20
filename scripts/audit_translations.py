import json
import os

books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad', 'nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'riyad_arab', 'shamail', 'tabarani']

def get_translations(path):
    if not os.path.exists(path): return False, False, False
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not data: return False, False, False
    
    # Just check the first hadith to see if fields exist and are non-empty strings
    sample = next(iter(data.values()))
    ar = bool(sample.get('text_ar', '').strip())
    en = bool(sample.get('text_en', '').strip())
    id = bool(sample.get('text_id', '').strip())
    
    # Actually, let's scan all to be sure at least ONE hadith has it
    for r in data.values():
        if r.get('text_ar', '').strip(): ar = True
        if r.get('text_en', '').strip(): en = True
        if r.get('text_id', '').strip(): id = True
        if ar and en and id: break
        
    return ar, en, id

print("\n### Table 1: Fawaz")
print("| Book | AR | EN | ID |")
print("|---|---|---|---|")
for b in books:
    if b in ['darimi', 'ahmad', 'adab', 'bulugh', 'mishkat', 'riyad', 'riyad_arab', 'shamail', 'tabarani']: continue
    path = f"data/api/{b}/fawaz.json"
    ar, en, id = get_translations(path)
    print(f"| {b} | {'Yes' if ar else '-'} | {'Yes' if en else '-'} | {'Yes' if id else '-'} |")

print("\n### Table 2: AhmedBaset")
print("| Book | AR | EN | ID |")
print("|---|---|---|---|")
for b in books:
    if b == 'riyad_arab': continue
    path = f"data/api/{b}/ab.json"
    ar, en, id = get_translations(path)
    if ar or en or id:
        print(f"| {b} | {'Yes' if ar else '-'} | {'Yes' if en else '-'} | {'Yes' if id else '-'} |")

print("\n### Table 3: Lidwa")
print("| Book | AR | EN | ID |")
print("|---|---|---|---|")
for b in books:
    if b in ['adab', 'bulugh', 'mishkat', 'shamail', 'tabarani', 'qudsi', 'shah', 'nawawi']: continue
    path = f"data/api/{b}/lidwa.json"
    ar, en, id = get_translations(path)
    if ar or en or id:
        print(f"| {b} | {'✓' if ar else '-'} | {'✓' if en else '-'} | {'✓' if id else '-'} |")
