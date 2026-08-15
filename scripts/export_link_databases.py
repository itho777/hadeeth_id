import os
import json
import csv
import glob

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LINKS_DIR = os.path.join(DATA_DIR, 'links')
COMMENTARIES_DIR = os.path.join(DATA_DIR, 'commentaries')
EXPORTS_DIR = os.path.join(DATA_DIR, 'exports')

# Ensure exports directory exists
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Load master link data
master_link_path = os.path.join(LINKS_DIR, 'master_link.json')
print(f"Loading {master_link_path}...")
try:
    with open(master_link_path, 'r', encoding='utf-8') as f:
        master_link = json.load(f)
except Exception as e:
    print(f"Failed to load master_link.json: {e}")
    master_link = {}

# 1. Translation Links (Lidwa)
# 2. Sanad Links (Kaggle Narrators)
translation_csv_path = os.path.join(EXPORTS_DIR, 'translation_links.csv')
sanad_csv_path = os.path.join(EXPORTS_DIR, 'sanad_links.csv')

print("Exporting Translation and Sanad links...")
with open(translation_csv_path, 'w', newline='', encoding='utf-8') as f_trans, \
     open(sanad_csv_path, 'w', newline='', encoding='utf-8') as f_sanad:
     
    trans_writer = csv.writer(f_trans)
    trans_writer.writerow(['book_id', 'anchor_id', 'lidwa_id', 'lidwa_hnum'])
    
    sanad_writer = csv.writer(f_sanad)
    sanad_writer.writerow(['book_id', 'anchor_id', 'narrator_id'])
    
    for book_id, hadiths in master_link.items():
        if not isinstance(hadiths, dict):
            continue
        for anchor_id, data in hadiths.items():
            # Translation (Lidwa)
            lidwa_id = data.get('lidwa_id')
            lidwa_hnum = data.get('lidwa_hnum')
            if lidwa_id:
                trans_writer.writerow([book_id, anchor_id, lidwa_id, lidwa_hnum])
                
            # Sanad (Kaggle Narrators)
            narrators = data.get('kaggle_narrators', [])
            if isinstance(narrators, list):
                for n_id in narrators:
                    sanad_writer.writerow([book_id, anchor_id, n_id])

# 3. Syarah Links
syarah_csv_path = os.path.join(EXPORTS_DIR, 'syarah_links.csv')
print("Exporting Syarah links...")
with open(syarah_csv_path, 'w', newline='', encoding='utf-8') as f_syarah:
    syarah_writer = csv.writer(f_syarah)
    syarah_writer.writerow(['book_id', 'anchor_id', 'commentary_filename'])
    
    # Iterate over files in data/commentaries/
    search_pattern = os.path.join(COMMENTARIES_DIR, '*.json')
    for filepath in glob.glob(search_pattern):
        filename = os.path.basename(filepath)
        name_no_ext = os.path.splitext(filename)[0]
        # format: book_id_hadithNumber[_optionalPart]
        parts = name_no_ext.split('_')
        if len(parts) >= 2:
            book_id = parts[0]
            anchor_id = parts[1]
            syarah_writer.writerow([book_id, anchor_id, filename])

print(f"Export Complete! Files saved in: {EXPORTS_DIR}")
