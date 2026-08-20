import sqlite3
import json
import os
import re

OUT_DIR = 'data/api'
os.makedirs(OUT_DIR, exist_ok=True)

# Load Topic Tags
with open('data/lidwa_extracts/topic_tags.json', 'r', encoding='utf-8') as f:
    topic_tags = {str(item['tag_id']): item['name_en'] for item in json.load(f)}

# Preload Ind mappings
print("Preloading Ind (Tags) mappings...", flush=True)
ind_maps = {}  # (book, no_hdt) -> list of tags
for i in range(1, 15):
    try:
        with open(f'data/lidwa_extracts/ind_{i}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            tag_name = topic_tags.get(str(i), str(i))
            for row in data:
                key = (str(row['Sumber']).lower(), str(row['NoHdt']))
                if key not in ind_maps:
                    ind_maps[key] = []
                ind_maps[key].append(tag_name)
    except Exception as e:
        pass

# Book mappings
books = {
    'bukhari': {'fawaz': 'bukhari', 'atif': 'Sahih al-Bukhari', 'usm': 'bukhari'},
    'muslim': {'fawaz': 'muslim', 'atif': 'Sahih Muslim', 'usm': 'muslim'},
    'abudaud': {'fawaz': 'abudawud', 'atif': 'Sunan Abi Dawud', 'usm': 'abudaud'},
    'tirmidzi': {'fawaz': 'tirmidhi', 'atif': 'Jami` at-Tirmidhi', 'usm': 'tirmidzi'},
    'nasai': {'fawaz': 'nasai', 'atif': "Sunan an-Nasa'i", 'usm': 'nasai'},
    'ibnumajah': {'fawaz': 'ibnmajah', 'atif': 'Sunan Ibn Majah', 'usm': 'ibnumajah'},
    'malik': {'fawaz': 'malik', 'atif': None, 'usm': None},
    'ahmad': {'fawaz': 'ahmad', 'atif': None, 'usm': 'ahmad'},
    'darimi': {'fawaz': 'darimi', 'atif': None, 'usm': None}
}

con = sqlite3.connect('scratch/lidwa_imported.db')
con.row_factory = sqlite3.Row

# Preload Rawi dictionary for Sanad building
print("Preloading Rawi dictionary...")
perawi_dict = {}
for row in con.execute("SELECT * FROM perawi_daftar"):
    perawi_dict[row['Kode_Rawi']] = dict(row)

for lidwa_book, meta in books.items():
    print(f"\n--- Processing {lidwa_book} ---")
    fawaz_slug = meta['fawaz']
    
    # Load mapping
    int_to_lidwa = {}
    try:
        with open(f'data/lidwa_extracts/mapping_{lidwa_book}.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            if not mapping: # Empty mapping
                print(f"Mapping for {lidwa_book} is empty. Using NoHdt as NoMapping.")
                # We need to query max hadith number from had_agregat
                max_lidwa = con.execute(f"SELECT max(NoHdt) FROM had_agregat WHERE imam='{lidwa_book}'").fetchone()[0] or 0
                for i in range(1, max_lidwa + 1):
                    int_to_lidwa[i] = [i]
            else:
                for m in mapping:
                    i_id = m['NoMapping']
                    l_id = m['NoHdt']
                    if i_id not in int_to_lidwa:
                        int_to_lidwa[i_id] = []
                    int_to_lidwa[i_id].append(l_id)
    except FileNotFoundError:
        print(f"Mapping not found for {lidwa_book}. Skipping.")
        continue
        
    max_id = max(int_to_lidwa.keys()) if int_to_lidwa else 0
    
    # Load Fawazahmed
    fawaz_data = {}
    try:
        with open(f'data/sources/fawaz_combined_v2/{fawaz_slug}.json', 'r', encoding='utf-8') as f:
            fd = json.load(f)
            for h in fd:
                try:
                    hnum = int(float(h['hadithnumber']))
                    fawaz_data[hnum] = h
                except:
                    pass
            max_id = max(max_id, max(fawaz_data.keys()) if fawaz_data else 0)
    except Exception as e:
        print(f"Fawazahmed data not found for {fawaz_slug}: {e}")
        
    # Load Atif
    atif_data = {}
    atif_filename = meta['atif']
    if atif_filename:
        try:
            with open(f'data/sources/atif_hf/{atif_filename}.json', 'r', encoding='utf-8') as f:
                ad = json.load(f)
                for h in ad:
                    ref = h.get('Reference', '')
                    match = re.search(r':(\d+)', ref)
                    if match:
                        hnum = int(match.group(1))
                        atif_data[hnum] = h
                        max_id = max(max_id, hnum)
        except Exception as e:
            print(f"Atif data not found for {atif_filename}: {e}")
            
    # Load Usm
    usm_data = {}
    usm_slug = meta['usm']
    if usm_slug:
        try:
            with open(f'data/sources/usm_parsed/{usm_slug}.json', 'r', encoding='utf-8') as f:
                usm_data = {int(k): v for k, v in json.load(f).items()}
        except Exception as e:
            pass
            
    ab_data = {}
    ab_slug = {'ahmad': 'ahmed'}.get(lidwa_book, lidwa_book)
    try:
        with open(f'data/sources/ahmedbaset/by_book/the_9_books/{ab_slug}.json', 'r', encoding='utf-8') as f:
            for h in json.load(f)['hadiths']:
                if 'idInBook' in h:
                    ab_data[h['idInBook']] = h
    except Exception as e:
        pass

    # Load Lidwa Data into memory for this book to avoid millions of small DB queries
    print("Loading Lidwa data into memory...")
    
    lidwa_texts = {row['NoHdt']: dict(row) for row in con.execute(f"SELECT * FROM had_agregat WHERE imam='{lidwa_book}'")}
    try:
        lidwa_grades = {row['NoHdt']: dict(row) for row in con.execute(f"SELECT * FROM derajat_{lidwa_book}")}
    except:
        lidwa_grades = {}
        
    lidwa_fawaid = {}
    for row in con.execute(f"SELECT * FROM fawaid WHERE imam='{lidwa_book}'"):
        l_id = row['NoHdt']
        if l_id not in lidwa_fawaid:
            lidwa_fawaid[l_id] = []
        lidwa_fawaid[l_id].append(row['fawaid'])
        
    lidwa_penguat = {}
    try:
        for row in con.execute(f"SELECT * FROM penguat_{lidwa_book}"):
            l_id = row['NoHdt']
            if l_id not in lidwa_penguat:
                lidwa_penguat[l_id] = []
            lidwa_penguat[l_id].append(row['IdPenguat']) # Just an example, maybe NoHdt2? We'll see if it throws error
    except:
        pass
        
    try:
        lidwa_sanad = {row['NoHdt']: dict(row) for row in con.execute(f"SELECT * FROM sanad_{lidwa_book}")}
    except:
        lidwa_sanad = {}
        
    ndjson_path = os.path.join(OUT_DIR, f"{fawaz_slug}.ndjson")
    index_path = os.path.join(OUT_DIR, f"{fawaz_slug}_ndjson_index.json")
    
    index_data = []
    
    with open(ndjson_path, 'w', encoding='utf-8') as f_out:
        for i in range(1, max_id + 1):
            lidwa_ids = int_to_lidwa.get(i, [])`n            record = {
                "id": i,
                "lidwa_id": lidwa_ids[0] if lidwa_ids else None,
                "book": fawaz_slug,
                "translations": {},
                "syarah": [],
                "gradings": [],
                "sanad": [],
                "tags": [],
                "fortifying": []
            }
            
            # --- 1. LIDWA DATA ---
            lidwa_ids = int_to_lidwa.get(i, [])
            
            # Translations
            for l_id in lidwa_ids:
                if l_id in lidwa_texts:
                    text = lidwa_texts[l_id]
                    if text['Isi_Arab']:
                        if 'ar' not in record['translations']: record['translations']['ar'] = []
                        record['translations']['ar'].append({"text": text['Isi_Arab'], "source": "lidwa"})
                    if text['Isi_Indonesia']:
                        if 'id' not in record['translations']: record['translations']['id'] = []
                        record['translations']['id'].append({"text": text['Isi_Indonesia'], "source": "lidwa"})
                    if text.get('Isi_English'):
                        if 'en' not in record['translations']: record['translations']['en'] = []
                        record['translations']['en'].append({"text": text['Isi_English'], "source": "lidwa"})
                        
                # Ahmedbaset Fallbacks
                if l_id in ab_data:
                    ab_hadith = ab_data[l_id]
                    if ab_hadith.get('arabic'):
                        if 'ar' not in record['translations']: record['translations']['ar'] = []
                        record['translations']['ar'].append({"text": ab_hadith['arabic'], "source": "ahmedbaset"})
                    if ab_hadith.get('english'):
                        en_text = ab_hadith['english']
                        if isinstance(en_text, dict):
                            en_text = (en_text.get('narrator', '') + ' ' + en_text.get('text', '')).strip()
                        if 'en' not in record['translations']: record['translations']['en'] = []
                        record['translations']['en'].append({"text": en_text, "source": "ahmedbaset"})

                # Gradings
                if l_id in lidwa_grades:
                    record['gradings'].append({"grade": lidwa_grades[l_id].get('Derajat', ''), "source": "lidwa"})
                    
                # Syarah
                if l_id in lidwa_fawaid:
                    for sy in lidwa_fawaid[l_id]:
                        record['syarah'].append({"text": sy, "source": "lidwa"})
                        
                # Tags
                lidwa_source_name = {
                    'abudaud': 'abu daud',
                    'ibnumajah': 'ibnu majah',
                    'nasai': "nasa'i",
                    'tirmidzi': 'tirmidzi',
                    'bukhari': 'bukhari',
                    'muslim': 'muslim',
                    'malik': 'malik',
                    'darimi': 'darimi',
                    'ahmad': 'ahmad'
                }.get(lidwa_book, lidwa_book)

                tags = ind_maps.get((lidwa_source_name, str(l_id)), [])
                for t in tags:
                    if t not in record['tags']:
                        record['tags'].append(t)
                        
                # Sanad
                if l_id in lidwa_sanad:
                    sn = lidwa_sanad[l_id]
                    chain = []
                    for j in range(1, 20):
                        j_key = f'J{j}'
                        if j_key in sn and sn[j_key] != 0:
                            rawi_id = sn[j_key]
                            rawi_info = perawi_dict.get(rawi_id, {})
                            name = rawi_info.get('Nama', str(rawi_id))
                            chain.append({"name": name, "id": rawi_id, "source": "lidwa"})
                    if chain:
                        record['sanad'] = chain # Lidwa is priority, so just assign
                        
            # --- 2. FAWAZ DATA ---
            if i in fawaz_data:
                fd = fawaz_data[i]
                for lang, code in [('text_ara', 'ar'), ('text_eng', 'en'), ('text_ind', 'id'), 
                                   ('text_urd', 'ur'), ('text_ben', 'bn'), ('text_fra', 'fr')]:
                    if fd.get(lang):
                        if code not in record['translations']: record['translations'][code] = []
                        # Only add if Lidwa didn't already satisfy it (we add as fallback, UI will pick first)
                        # Or we just add it to the array and UI filters. Let's add it.
                        record['translations'][code].append({"text": fd[lang], "source": "fawazahmed"})
                        
                # Gradings
                if fd.get('grades'):
                    for gr in fd['grades']:
                        record['gradings'].append({"grade": gr.get('grade', ''), "name": gr.get('name', ''), "source": "fawazahmed"})
                        
            # --- 3. ATIF DATA ---
            if i in atif_data:
                ad = atif_data[i]
                if ad.get('English_Text'):
                    if 'en' not in record['translations']: record['translations']['en'] = []
                    record['translations']['en'].append({"text": ad['English_Text'], "source": "atif"})
                if ad.get('Grade'):
                    record['gradings'].append({"grade": ad['Grade'], "source": "atif"})
                    
            # --- 4. USM DATA ---
            if i in usm_data:
                record['gradings'].append({"grade": usm_data[i], "source": "usm12345"})
                
            # Filter empty translations
            record['translations'] = {k: v for k, v in record['translations'].items() if v}
            
            # Write line and record index
            start_byte = f_out.tell()
            f_out.write(json.dumps(record, ensure_ascii=False) + '\n')
            end_byte = f_out.tell()
            
            index_data.append({
                "id": i,
                "start": start_byte,
                "end": end_byte
            })
            
    with open(index_path, 'w', encoding='utf-8') as f_idx:
        json.dump(index_data, f_idx, separators=(',', ':'))
        
    print(f"Successfully wrote {max_id} records to {ndjson_path}")

con.close()
print("All NDJSON databases built.")
