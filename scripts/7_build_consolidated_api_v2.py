import os
import json
import re
import shutil
import sqlite3

sys_stdout = open(1, 'w', encoding='utf-8', closefd=False)
import sys
sys.stdout = sys_stdout

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LIDWA_DIR = os.path.join(DATA_DIR, "sources", "lidwa")
AHMEDBASET_DIR = os.path.join(DATA_DIR, "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(DATA_DIR, "links")
COMMENTARIES_DIR = os.path.join(DATA_DIR, "commentaries")
API_OUT_DIR = os.path.join(DATA_DIR, "api")

AB_PATHS = {
    "bukhari": "the_9_books/bukhari.json",
    "muslim": "the_9_books/muslim.json",
    "abudawud": "the_9_books/abudawud.json",
    "tirmidhi": "the_9_books/tirmidhi.json",
    "nasai": "the_9_books/nasai.json",
    "ibnmajah": "the_9_books/ibnmajah.json",
    "malik": "the_9_books/malik.json",
    "darimi": "the_9_books/darimi.json",
    "ahmad": "the_9_books/ahmed.json",
    "qudsi": "forties/qudsi40.json",
    "shah": "forties/shahwaliullah40.json",
    "adab": "other_books/aladab_almufrad.json",
    "bulugh": "other_books/bulugh_almaram.json",
    "mishkat": "other_books/mishkat_almasabih.json",
    "riyad": "other_books/riyad_assalihin.json",
    "shamail": "other_books/shamail_muhammadiyah.json",
    "nawawi": "forties/nawawi40.json"
}

def strip_tashkeel(text):
    if not text:
        return ""
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\uFEFF]', '', text)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    return text

def build_api():
    print("[*] Starting Consolidated API Builder (AhmedBaset Anchor)...")
    
    if os.path.exists(API_OUT_DIR):
        shutil.rmtree(API_OUT_DIR, ignore_errors=True)
    os.makedirs(API_OUT_DIR, exist_ok=True)
    
    with open(os.path.join(DATA_DIR, 'books_v2.json'), 'r', encoding='utf-8') as f:
        books = json.load(f)
        
    with open(os.path.join(LINKS_DIR, 'master_link.json'), 'r', encoding='utf-8') as f:
        master_link = json.load(f)
        
    cross_links_path = os.path.join(LINKS_DIR, 'cross_links.json')
    cross_links = {}
    if os.path.exists(cross_links_path):
        with open(cross_links_path, 'r', encoding='utf-8') as f:
            cross_links = json.load(f)
            
    syarah_links = {}
    for f in os.listdir(LINKS_DIR):
        if f.startswith('syarah_link_') and f.endswith('.json'):
            b_id = f.replace('syarah_link_', '').replace('.json', '')
            with open(os.path.join(LINKS_DIR, f), 'r', encoding='utf-8') as sy:
                syarah_links[b_id] = json.load(sy)

    # Pre-load Lidwa Sanad
    lidwa_sanad_map = {}
    lidwa_sanad_path = os.path.join(DATA_DIR, "supabase", "hadith_rijal_lidwa.csv")
    
    rawis_dict_path = os.path.join(DATA_DIR, "rawis", "active_rawis.min.json")
    rawis_dict = {}
    if os.path.exists(rawis_dict_path):
        with open(rawis_dict_path, 'r', encoding='utf-8') as f:
            rawis_dict = json.load(f)
            
    if os.path.exists(lidwa_sanad_path):
        import csv
        with open(lidwa_sanad_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            from collections import defaultdict
            temp_map = defaultdict(list)
            for row in reader:
                temp_map[row['hadith_id']].append((int(row['chain_position']), row['rawi_id']))
            for h_id, rawis in temp_map.items():
                if ':' in h_id:
                    b_id, h_num = h_id.split(':')
                    if b_id not in lidwa_sanad_map:
                        lidwa_sanad_map[b_id] = {}
                    # Group rawis into separate paths based on chain_position resets
                    paths = []
                    current_path = []
                    last_pos = -1
                    for r in rawis: # original order from CSV preserves the branches sequentially
                        pos = r[0]
                        if pos <= last_pos:
                            paths.append(current_path)
                            current_path = []
                        current_path.append(r)
                        last_pos = pos
                    if current_path:
                        paths.append(current_path)
                    
                    enriched_paths = []
                    for path in paths:
                        enriched_path = []
                        for r in path:
                            r_id = r[1]
                            r_data = rawis_dict.get(r_id, {})
                            enriched_path.append({
                                "id": r_id,
                                "name_en": r_data.get("en", r_id),
                                "name_id": r_data.get("id", r_id),
                                "ar": r_data.get("ar", "")
                            })
                        enriched_paths.append(enriched_path)
                    
                    # Store multiple paths, and use the first path as the default 'rawis'
                    lidwa_sanad_map[b_id][h_num] = {
                        "rawis": enriched_paths[0] if enriched_paths else [],
                        "paths": enriched_paths
                    }

    # Pre-load Lidwa Grades and Elevations from lidwa_plaintext.db
    lidwa_grades_map = {}
    lidwa_elevation_map = {}
    lidwa_db_path = os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db")
    if os.path.exists(lidwa_db_path):
        conn = sqlite3.connect(lidwa_db_path)
        table_map = {
            "bukhari": "derajat_bukhari",
            "muslim": "derajat_muslim",
            "abudawud": "derajat_abudaud",
            "tirmidhi": "derajat_tirmidzi",
            "nasai": "derajat_nasai",
            "ibnmajah": "derajat_ibnumajah",
            "darimi": "derajat_darimi",
            "ahmad": "derajat_ahmad",
            "malik": "derajat_malik"
        }
        for b_id, table_name in table_map.items():
            lidwa_grades_map[b_id] = {}
            try:
                cursor = conn.execute(f"SELECT NoHdt, Derajat FROM {table_name}")
                for row in cursor.fetchall():
                    lidwa_grades_map[b_id][str(row[0])] = row[1].strip()
            except sqlite3.OperationalError:
                pass
                
        # Kumpulan for Elevation
        kumpulan_tables = {
            "kumpulan_marfu": "Marfu'",
            "kumpulan_mauquf": "Mauquf",
            "kumpulan_maqthu": "Maqthu'",
            "kumpulan_mursal": "Mursal",
            "kumpulan_muallaq": "Mu'allaq",
            "kumpulan_munqathi": "Munqathi'",
            "kumpulan_mutawatir": "Mutawatir",
            "kumpulan_qudsi": "Qudsi"
        }
        book_name_to_id = {
            "bukhari": "bukhari", "muslim": "muslim", "abudaud": "abudawud",
            "tirmidzi": "tirmidhi", "nasai": "nasai", "ibnumajah": "ibnmajah",
            "darimi": "darimi", "ahmad": "ahmad", "malik": "malik"
        }
        for table, label in kumpulan_tables.items():
            try:
                # Schema might be: (Id, Kitab, NoHdt)
                cursor = conn.execute(f"SELECT * FROM {table}")
                for row in cursor.fetchall():
                    b_name = row[1]
                    h_num = str(row[2])
                    b_id = book_name_to_id.get(b_name.lower(), b_name)
                    if b_id not in lidwa_elevation_map:
                        lidwa_elevation_map[b_id] = {}
                    
                    # If already has one, maybe join them? Usually a hadith is only one main type, but could be Qudsi and Marfu.
                    if h_num in lidwa_elevation_map[b_id]:
                        lidwa_elevation_map[b_id][h_num] += f", {label}"
                    else:
                        lidwa_elevation_map[b_id][h_num] = label
            except sqlite3.OperationalError:
                pass
                
        conn.close()

    total_hadiths_built = 0

    for b in books:
        book_id = b['id']
        print(f" -> Building Consolidated API for {book_id}...")
        
        book_out_dir = os.path.join(API_OUT_DIR, book_id)
        os.makedirs(book_out_dir, exist_ok=True)
        
        ml_book = master_link.get(book_id, {})
        
        ab_rel = AB_PATHS.get(book_id)
        if not ab_rel:
            print(f"    [!] No AhmedBaset mapping for {book_id}, skipping.")
            continue
            
        ab_data = []
        ab_path_graded = os.path.join(DATA_DIR, "sources", "ahmedbaset_graded", "by_book", ab_rel)
        ab_path_orig = os.path.join(AHMEDBASET_DIR, ab_rel)
        ab_path = ab_path_graded if os.path.exists(ab_path_graded) else ab_path_orig
        
        if os.path.exists(ab_path):
            with open(ab_path, 'r', encoding='utf-8') as f:
                ad = json.load(f)
                ab_data = ad.get('hadiths', []) if isinstance(ad, dict) else ad
        else:
            print(f"    [!] File not found {ab_path}, skipping.")
            continue
            
        lidwa_data = []
        lidwa_path = os.path.join(LIDWA_DIR, f"{book_id}.json")
        if os.path.exists(lidwa_path):
            with open(lidwa_path, 'r', encoding='utf-8') as f:
                lidwa_data = json.load(f)
                
        lidwa_map = {}
        for h in lidwa_data:
            hid = str(h.get('hadith_number', h.get('id')))
            lidwa_map[hid] = h
            lidwa_map[str(h.get('id'))] = h

        # Load Lidwa Syarah from DB if commentaries not sufficient
        # Actually Lidwa JSON might already contain 'syarah' in the new dumps.
        
        final_payload = []
        for h in ab_data:
            ab_id = str(h.get('idInBook', h.get('id')))
            
            ml_entry = ml_book.get(ab_id, {})
            lidwa_id = str(ml_entry.get('lidwa_id')) if ml_entry.get('lidwa_id') else None
            lidwa_hnum = str(ml_entry.get('lidwa_hnum')) if ml_entry.get('lidwa_hnum') else None
            
            text_ar = h.get('arabic', '')
            eng_obj = h.get('english')
            text_en = ""
            if isinstance(eng_obj, dict):
                narrator = eng_obj.get('narrator', '')
                text = eng_obj.get('text', '')
                text_en = f"{narrator} {text}" if narrator else text
            else:
                text_en = str(eng_obj or "")
                
            text_en = text_en.strip()
            
            ch_num = str(h.get("chapterId", 1))
            in_book_num = str(ab_id)
            grade_str = h.get('grade', 'Sahih') # fallback if ab doesn't have grade
            grade_en = h.get('grade_en', '')
            
            # Lidwa injection
            text_id = ""
            syarah_id = ""
            rawis = []
            grade_id = ""
            
            lidwa_h = None
            if lidwa_id and lidwa_id in lidwa_map:
                lidwa_h = lidwa_map[lidwa_id]
            elif lidwa_hnum and lidwa_hnum in lidwa_map:
                lidwa_h = lidwa_map[lidwa_hnum]
                
            if lidwa_h:
                text_id = lidwa_h.get('text_id', '')
                syarah_id = lidwa_h.get('syarah', '')
                # Extract lidwa grade by trying both identifiers
                b_grades = lidwa_grades_map.get(book_id, {})
                grade_id = b_grades.get(str(lidwa_h.get('hadith_number')), "")
                if not grade_id:
                    grade_id = b_grades.get(str(lidwa_h.get('id')), "")
                
            paths = []
            if lidwa_hnum and book_id in lidwa_sanad_map:
                sanad_data = lidwa_sanad_map[book_id].get(lidwa_hnum, {})
                rawis = sanad_data.get("rawis", [])
                paths = sanad_data.get("paths", [])
            
            # Cross Links
            cl_key = f"{book_id}:{in_book_num}"
            related = cross_links.get(cl_key, [])
            
            # Syarah Injection
            syarah_ar = ""
            syarah_source = ""
            s_links = syarah_links.get(book_id, {})
            c_files = s_links.get(in_book_num, [])
            for c_file in c_files:
                c_path = os.path.join(COMMENTARIES_DIR, c_file)
                if os.path.exists(c_path):
                    with open(c_path, 'r', encoding='utf-8') as cf:
                        cdat = json.load(cf)
                        s_ar = cdat.get('syarah_ar', '')
                        if s_ar:
                            syarah_ar += s_ar + "\n\n"
                        if not syarah_source:
                            syarah_source = cdat.get('source', '')
            syarah_ar = syarah_ar.strip()
            
            # Grade & Elevation
            grade_en = h.get('grade_en', '')
            grade_ar = h.get('grade', '') # keep if it actually existed in ahmedbaset
            
            elevation = ""
            if lidwa_h:
                b_elevs = lidwa_elevation_map.get(book_id, {})
                elevation = b_elevs.get(str(lidwa_h.get('hadith_number')), "")
                if not elevation:
                    elevation = b_elevs.get(str(lidwa_h.get('id')), "")
            
            # Standardize payload
            out_obj = {
                "id": in_book_num,
                "hadith_number": in_book_num,
                "chapter_id": ch_num,
                "text_ar": text_ar,
                "text_ar_plain": strip_tashkeel(text_ar),
                "text_en": text_en,
                "text_id": text_id,
                "text_ur": "", # AhmedBaset doesn't have Urdu
                "rawis": rawis,
                "paths": paths,
                "syarah_ar": syarah_ar,
                "syarah_en": "",
                "syarah_id": syarah_id,
                "syarah_source": syarah_source,
                "related": related,
                "grade_en": grade_en,
                "grade_id": grade_id,
                "elevation": elevation,
                "lidwa_id": lidwa_id
            }
            
            # Re-inject 'grade' backwards compatibility but leave empty instead of fake 'Sahih'
            out_obj["grade"] = grade_ar
            
            final_payload.append(out_obj)
            
        print(f"    -> Generated {len(final_payload)} hadiths")
        total_hadiths_built += len(final_payload)
        
        # Write paginated chunks
        chunk_size = 500
        for i in range(0, len(final_payload), chunk_size):
            chunk = final_payload[i:i+chunk_size]
            page_idx = (i // chunk_size) + 1
            chunk_path = os.path.join(book_out_dir, f"{page_idx}.json")
            with open(chunk_path, 'w', encoding='utf-8') as f:
                json.dump({"data": chunk, "total": len(final_payload), "page": page_idx}, f, ensure_ascii=False, indent=2)
                
        # Write complete file
        complete_path = os.path.join(API_OUT_DIR, f"{book_id}.json")
        with open(complete_path, 'w', encoding='utf-8') as f:
            json.dump(final_payload, f, ensure_ascii=False)
            
    print(f"\n[+] API Generation Complete! Processed {total_hadiths_built} hadiths.")

if __name__ == "__main__":
    build_api()
