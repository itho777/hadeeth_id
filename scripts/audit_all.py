import json
import os
import glob

fawaz_github_repo = 'the_9_books' # We only have 9 books for fawaz locally but the script checks data/editions/
ab_github_repo = 'data/sources/ahmedbaset'
lidwa_local_repo = 'data/sources/lidwa'
lidwa_github_repo = 'scratch/irsyadulibad_db' # Just cloned

print("### Table 1: Fawaz (Local vs GitHub Source)")
print("| Book | Local Dataset (data/api) | GitHub Source | Match % |")
print("|---|---|---|---|")

books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad', 'nawawi', 'qudsi', 'shah', 'adab', 'bulugh', 'mishkat', 'riyad', 'riyad_arab', 'shamail', 'tabarani']

def get_fawaz_github_count(book):
    paths = {
        "bukhari": "data/editions/ara-bukhari.json",
        "muslim": "data/editions/ara-muslim.json",
        "abudawud": "data/editions/ara-abudawud.json",
        "tirmidhi": "data/editions/ara-tirmidhi.json",
        "nasai": "data/editions/ara-nasai.json",
        "ibnmajah": "data/editions/ara-ibnmajah.json",
        "malik": "data/editions/ara-malik.json",
        "nawawi": "data/editions/ara-nawawi.json",
        "qudsi": "data/editions/ara-qudsi.json",
        "shah": "data/editions/ara-shah.json"
    }
    if book not in paths: return 0
    path = paths[book]
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return len(data.get('hadiths', []))
    return 0

def get_ab_github_count(book):
    paths = {
        "bukhari": "data/sources/ahmedbaset/by_book/the_9_books/bukhari.json",
        "muslim": "data/sources/ahmedbaset/by_book/the_9_books/muslim.json",
        "abudawud": "data/sources/ahmedbaset/by_book/the_9_books/abudawud.json",
        "tirmidhi": "data/sources/ahmedbaset/by_book/the_9_books/tirmidhi.json",
        "nasai": "data/sources/ahmedbaset/by_book/the_9_books/nasai.json",
        "ibnmajah": "data/sources/ahmedbaset/by_book/the_9_books/ibnmajah.json",
        "malik": "data/sources/ahmedbaset/by_book/the_9_books/malik.json",
        "darimi": "data/sources/ahmedbaset/by_book/the_9_books/darimi.json",
        "ahmad": "data/sources/ahmedbaset/by_book/the_9_books/ahmed.json",
        "nawawi": "data/sources/ahmedbaset/by_book/forties/nawawi40.json",
        "qudsi": "data/sources/ahmedbaset/by_book/forties/qudsi40.json",
        "shah": "data/sources/ahmedbaset/by_book/forties/shahwaliullah40.json",
        "adab": "data/sources/ahmedbaset/by_book/other_books/aladab_almufrad.json",
        "bulugh": "data/sources/ahmedbaset/by_book/other_books/bulugh_almaram.json",
        "mishkat": "data/sources/ahmedbaset/by_book/other_books/mishkat_almasabih.json",
        "riyad": "data/sources/ahmedbaset/by_book/other_books/riyad_assalihin.json",
        "shamail": "data/sources/ahmedbaset/by_book/other_books/shamail_muhammadiyah.json"
    }
    if book not in paths: return 0
    path = paths[book]
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'hadiths' in data:
                return len(data['hadiths'])
            elif isinstance(data, list):
                return len(data)
    return 0

def get_lidwa_github_count(book):
    if book == 'bukhari': return 7008
    if book == 'muslim': return 5362
    if book == 'abudawud': return 4590
    if book == 'tirmidhi': return 3891
    if book == 'nasai': return 5662
    if book == 'ibnmajah': return 4331
    if book == 'malik': return 1594
    if book == 'ahmad': return 26363
    if book == 'darimi': return 3367
    if book == 'riyad': return 372
    if book == 'riyad_arab': return 850
    return 0

for b in books:
    local_path = f"data/api/{b}/fawaz.json"
    local_count = 0
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            local_count = len(json.load(f))
    git_count = get_fawaz_github_count(b)
    if local_count > 0 or git_count > 0:
        match = "100%" if local_count == git_count else f"{local_count/git_count*100:.1f}%" if git_count > 0 else "0%"
        print(f"| {b} | {local_count} | {git_count} | {match} |")

print("\n### Table 2: AhmedBaset (Local vs GitHub Source)")
print("| Book | Local Dataset (data/api) | GitHub Source | Match % |")
print("|---|---|---|---|")
for b in books:
    local_path = f"data/api/{b}/ab.json"
    local_count = 0
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            local_count = len(json.load(f))
    git_count = get_ab_github_count(b)
    if local_count > 0 or git_count > 0:
        match = "100%" if local_count == git_count else f"{local_count/git_count*100:.1f}%" if git_count > 0 else "0%"
        print(f"| {b} | {local_count} | {git_count} | {match} |")

print("\n### Table 3: Lidwa (Local vs GitHub Source)")
print("| Book | Local Dataset (data/api) | Local Lidwa Source (data/sources/lidwa) | GitHub Source (irsyadulibad/hadits-database) | Match % |")
print("|---|---|---|---|---|")
for b in books:
    if b == 'nawawi': continue
    local_path = f"data/api/{b}/lidwa.json"
    local_count = 0
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            local_count = len(json.load(f))
            
    source_path = f"data/sources/lidwa/{b}.json"
    source_count = 0
    if os.path.exists(source_path):
        with open(source_path, 'r', encoding='utf-8') as f:
            source_count = len(json.load(f))
            
    git_count = get_lidwa_github_count(b)
    
    if local_count > 0 or git_count > 0 or source_count > 0:
        match = "100%" if local_count == git_count else f"{local_count/git_count*100:.1f}%" if git_count > 0 else "0%"
        print(f"| {b} | {local_count} | {source_count} | {git_count} | {match} |")
