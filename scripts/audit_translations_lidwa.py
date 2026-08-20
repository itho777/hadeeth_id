import json
import os

books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad', 'nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'riyad_arab', 'shamail', 'tabarani']

def get_translations(path):
    if not os.path.exists(path): return False, False, False
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not data: return False, False, False
    
    ar, en, id_lang = False, False, False
    for r in data.values():
        if r.get('text_ar', '').strip(): ar = True
        if r.get('text_en', '').strip(): en = True
        if r.get('text_id', '').strip(): id_lang = True
        if ar and en and id_lang: break
    return ar, en, id_lang

print('\n### Table 3: Lidwa')
print('| Book | AR | EN | ID |')
print('|---|---|---|---|')
for b in books:
    if b in ['adab', 'bulugh', 'mishkat', 'shamail', 'tabarani', 'qudsi', 'shah', 'nawawi']: continue
    path = f'data/api/{b}/lidwa.json'
    ar, en, id_lang = get_translations(path)
    if ar or en or id_lang:
        ar_str = "Yes" if ar else "-"
        en_str = "Yes" if en else "-"
        id_str = "Yes" if id_lang else "-"
        print(f'| {b} | {ar_str} | {en_str} | {id_str} |')
