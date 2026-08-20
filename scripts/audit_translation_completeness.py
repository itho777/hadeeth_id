import json
import os

books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad', 'syafii', 'nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'riyad_arab', 'shamail', 'tabarani']

def get_completeness(path):
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not data: return None
    
    total = len(data)
    ar_count, en_count, id_count = 0, 0, 0
    for r in data.values():
        if r.get('text_ar', '').strip(): ar_count += 1
        if r.get('text_en', '').strip(): en_count += 1
        if r.get('text_id', '').strip(): id_count += 1
        
    return {
        'total': total,
        'ar': f"{(ar_count/total)*100:.1f}%" if total > 0 else "0%",
        'en': f"{(en_count/total)*100:.1f}%" if total > 0 else "0%",
        'id': f"{(id_count/total)*100:.1f}%" if total > 0 else "0%"
    }

print("\n### Table 1: Fawaz API Completeness")
print("| Book | AR | EN | ID |")
print("|---|---|---|---|")
for b in books:
    if b in ['darimi', 'ahmad', 'adab', 'bulugh', 'mishkat', 'riyad', 'riyad_arab', 'shamail', 'tabarani']: continue
    path = f"data/api/{b}/fawaz.json"
    stats = get_completeness(path)
    if stats:
        print(f"| {b} | {stats['ar']} | {stats['en']} | {stats['id']} |")

print("\n### Table 2: AhmedBaset API Completeness")
print("| Book | AR | EN | ID |")
print("|---|---|---|---|")
for b in books:
    if b == 'riyad_arab': continue
    path = f"data/api/{b}/ab.json"
    stats = get_completeness(path)
    if stats:
        print(f"| {b} | {stats['ar']} | {stats['en']} | {stats['id']} |")

print("\n### Table 3: Lidwa API Completeness")
print("| Book | AR | EN | ID |")
print("|---|---|---|---|")
for b in books:
    if b in ['adab', 'bulugh', 'mishkat', 'shamail', 'tabarani', 'qudsi', 'shah', 'nawawi']: continue
    path = f"data/api/{b}/lidwa.json"
    stats = get_completeness(path)
    if stats:
        print(f"| {b} | {stats['ar']} | {stats['en']} | {stats['id']} |")
