import os
import json
import shutil
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASETS_DIR = os.path.join(DATA_DIR, "datasets")

# Ensure dataset directory exists
os.makedirs(DATASETS_DIR, exist_ok=True)

# Dataset specifications from the user
FAWAZ_BOOKS = {
    'bukhari': ['ara', 'ara1', 'ben', 'eng', 'fra', 'ind', 'rus', 'tam', 'tur', 'urd'],
    'muslim': ['ara', 'ara1', 'ben', 'eng', 'fra', 'ind', 'rus', 'tam', 'tur', 'urd'],
    'nasai': ['ara', 'ara1', 'ben', 'eng', 'fra', 'ind', 'tur', 'urd'],
    'abudawud': ['ara', 'ara1', 'ben', 'eng', 'fra', 'ind', 'rus', 'tur', 'urd'],
    'tirmidhi': ['ara', 'ara1', 'ben', 'eng', 'ind', 'tur', 'urd'],
    'ibnmajah': ['ara', 'ara1', 'ben', 'eng', 'fra', 'ind', 'tur', 'urd'],
    'malik': ['ara', 'ara1', 'ben', 'eng', 'fra', 'ind', 'tur', 'urd'],
    'dehlawi': ['ara', 'ara1', 'eng', 'fra'],
    'nawawi': ['ara', 'ara1', 'ben', 'eng', 'fra', 'tur'],
    'qudsi': ['ara', 'ara1', 'eng', 'fra']
}

print("Creating strict dataset structure...")

# 1. Fawaz
fawaz_dir = os.path.join(DATASETS_DIR, "fawaz")
os.makedirs(fawaz_dir, exist_ok=True)
fawaz_src_dir = os.path.join(DATA_DIR, "sources", "fawaz_api", "editions")

# Helper to create NDJSON format
def json_to_ndjson(src_json, dest_ndjson, metadata={}):
    if not os.path.exists(src_json):
        print(f"  [!] Missing source {src_json}")
        return False
        
    try:
        with open(src_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            if 'hadiths' in data:
                items = data['hadiths']
            else:
                items = [data]
                
        with open(dest_ndjson, 'w', encoding='utf-8') as f:
            for item in items:
                # Merge metadata if needed, though usually frontend just wants array
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        print(f"  [Error] Failed to process {src_json}: {e}")
        return False

# Rebuild Fawaz
print("Rebuilding Fawaz...")
for book, langs in FAWAZ_BOOKS.items():
    book_dir = os.path.join(fawaz_dir, book)
    os.makedirs(book_dir, exist_ok=True)
    
    for lang in langs:
        edition = f"{lang}-{book}"
        if lang == 'ara1':
            edition = f"ara-{book}1" # handle fawaz naming quirk if any, wait, fawaz uses ara-bukhari1
            
        src = os.path.join(fawaz_src_dir, edition, f"{edition}.min.json")
        if not os.path.exists(src):
            src = os.path.join(fawaz_src_dir, f"{edition}.min.json") # fallback
            
        dest = os.path.join(book_dir, f"{lang}.ndjson")
        if os.path.exists(src):
            json_to_ndjson(src, dest)
            print(f"  [+] Fawaz: {edition} -> {dest}")
        else:
            print(f"  [-] Fawaz: missing {edition}")

print("\nDone building isolated datasets.")
