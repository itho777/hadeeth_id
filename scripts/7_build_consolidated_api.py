import os
import json
import re
import shutil
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAWAZ_DIR = os.path.join(DATA_DIR, "editions")
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
    "nawawi": "forties/nawawi40.json",
    "qudsi": "forties/qudsi40.json",
    "shah": "forties/shahwaliullah40.json"
}

def strip_tashkeel(text):
    if not text:
        return ""
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\uFEFF]', '', text)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    return text

def build_api():
    print("[*] Starting Consolidated API Builder (Tafseer Model)...")
    
    if os.path.exists(API_OUT_DIR):
        shutil.rmtree(API_OUT_DIR)
    os.makedirs(API_OUT_DIR)
    
    with open(os.path.join(DATA_DIR, 'books_v2.json'), 'r', encoding='utf-8') as f:
        books = json.load(f)
        
    with open(os.path.join(LINKS_DIR, 'master_link.json'), 'r', encoding='utf-8') as f:
        master_link = json.load(f)
        
    cross_links_path = os.path.join(LINKS_DIR, 'cross_links.json')
    cross_links = {}
    if os.path.exists(cross_links_path):
        with open(cross_links_path, 'r', encoding='utf-8') as f:
            cross_links = json.load(f)

    # Pre-load Lidwa Sanad
    lidwa_sanad_map = {}
    lidwa_sanad_path = os.path.join(DATA_DIR, "supabase", "hadith_rijal_lidwa.csv")
    
    # Load rawis dictionary to embed names in the API response
    rawis_dict_path = os.path.join(DATA_DIR, "rawis", "active_rawis.min.json")
    rawis_dict = {}
    if os.path.exists(rawis_dict_path):
        with open(rawis_dict_path, 'r', encoding='utf-8') as f:
            rawis_dict = json.load(f)
            
    if os.path.exists(lidwa_sanad_path):
        import csv
        with open(lidwa_sanad_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Group by hadith_id
            from collections import defaultdict
            temp_map = defaultdict(list)
            for row in reader:
                temp_map[row['hadith_id']].append((int(row['chain_position']), row['rawi_id']))
            for h_id, rawis in temp_map.items():
                if ':' in h_id:
                    b_id, h_num = h_id.split(':')
                    if b_id not in lidwa_sanad_map:
                        lidwa_sanad_map[b_id] = {}
                    # Sort by position
                    rawis.sort(key=lambda x: x[0])
                    
                    # Instead of just strings, build enriched objects
                    enriched_rawis = []
                    for r in rawis:
                        r_id = r[1]
                        r_data = rawis_dict.get(r_id, {})
                        enriched_rawis.append({
                            "id": r_id,
                            "name_en": r_data.get("en", r_id),
                            "name_id": r_data.get("id", r_id),
                            "ar": r_data.get("ar", "")
                        })
                    
                    lidwa_sanad_map[b_id][h_num] = enriched_rawis

    total_hadiths_built = 0

    for b in books:
        book_id = b['id']
        print(f" -> Building Consolidated API for {book_id}...")
        
        book_out_dir = os.path.join(API_OUT_DIR, book_id)
        os.makedirs(book_out_dir, exist_ok=True)
        
        ml_book = master_link.get(book_id, {})
        
        ab_to_anchor = {}
        lidwa_to_anchor = {}
        for anchor_id, links in ml_book.items():
            if links.get('ahmedbaset_id'):
                ab_to_anchor[str(links['ahmedbaset_id'])] = anchor_id
            if links.get('lidwa_id'):
                lidwa_to_anchor[str(links['lidwa_id'])] = anchor_id
        
        fawaz_book_id = 'riyad' if book_id == 'riyad_arab' else book_id
        
        fawaz_data = []
        is_fawaz_anchor = False
        fawaz_path = os.path.join(FAWAZ_DIR, f"ara-{fawaz_book_id}.json")
        if os.path.exists(fawaz_path):
            with open(fawaz_path, 'r', encoding='utf-8') as f:
                fd = json.load(f)
                fawaz_data = fd.get('hadiths', []) if isinstance(fd, dict) else fd
                is_fawaz_anchor = True
                
        fawaz_map = {}
        for idx, h in enumerate(fawaz_data):
            hid = str(idx + 1)
            fawaz_map[hid] = h
                
        ab_data = []
        ab_rel = AB_PATHS.get(book_id)
        if ab_rel:
            ab_path = os.path.join(AHMEDBASET_DIR, ab_rel)
            if os.path.exists(ab_path):
                with open(ab_path, 'r', encoding='utf-8') as f:
                    ad = json.load(f)
                    ab_data = ad.get('hadiths', []) if isinstance(ad, dict) else ad
                    
        ab_map = {}
        for h in ab_data:
            hid = str(h.get('idInBook', h.get('id')))
            ab_map[hid] = h

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

        eng_native_map = {}
        eng_path = os.path.join(FAWAZ_DIR, f"eng-{fawaz_book_id}.json")
        if os.path.exists(eng_path):
            with open(eng_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
                for i, h in enumerate(d.get('hadiths', []) if isinstance(d, dict) else d):
                    eng_native_map[str(i+1)] = h.get('text', '')
                    
        ind_native_map = {}
        ind_path = os.path.join(FAWAZ_DIR, f"ind-{fawaz_book_id}.json")
        if os.path.exists(ind_path):
            with open(ind_path, 'r', encoding='utf-8') as f:
                d = json.load(f)
                for i, h in enumerate(d.get('hadiths', []) if isinstance(d, dict) else d):
                    ind_native_map[str(i+1)] = h.get('text', '')
                
        urd_native_map = {}
        urd_path = os.path.join(FAWAZ_DIR, f"urd-{fawaz_book_id}.json")
        if os.path.exists(urd_path):
            with open(urd_path, 'r', encoding='utf-8') as f:
                idat = json.load(f)
                ih = idat.get('hadiths', []) if isinstance(idat, dict) else idat
                for h in ih: urd_native_map[str(h.get('hadithnumber', ''))] = h.get('text', '')

        lidwa_metadata_map = {}
        meta_path = os.path.join(DATA_DIR, "api", book_id, "lidwa_metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                lidwa_metadata_map = json.load(f)

        lidwa_native_chapter_map = {}
        try:
            conn = sqlite3.connect(os.path.join(BASE_DIR, "scratch", "lidwa_plaintext.db"))
            c = conn.cursor()
            c.execute(f"SELECT NoHdt, ID_Kitab FROM tema_{book_id}")
            for r in c.fetchall():
                lidwa_native_chapter_map[str(r[0])] = str(r[1])
            conn.close()
        except Exception as e:
            pass

        def construct_payload(base_id, ds_type):
            anchor_id = None
            if ds_type == 'fawaz': anchor_id = base_id
            elif ds_type == 'ab': anchor_id = ab_to_anchor.get(base_id)
            elif ds_type == 'lidwa': anchor_id = lidwa_to_anchor.get(base_id)
            
            ml_entry = ml_book.get(anchor_id, {}) if anchor_id else {}
            
            text_ar, text_en, text_id, text_ur, rawis, syarah = "", "", "", "", [], ""
            ch_num, in_book_num = 1, base_id
            grade_str, grade_by = "Sahih", ""
            
            if ds_type == 'fawaz' and base_id in fawaz_map:
                h = fawaz_map[base_id]
                text_ar = h.get('text', '')
                ref = h.get("reference", {})
                in_book_num = ref.get("hadith", 0)
                ch_num = ref.get("book", 0)
                if h.get('grades'):
                    grade_str = h['grades'][0].get('grade', 'Sahih')
                    grade_by = h['grades'][0].get('name', '')
                    
            elif ds_type == 'ab' and base_id in ab_map:
                h = ab_map[base_id]
                text_ar = h.get('arabic', '')
                ch_num = h.get("chapterId", 1)
                eng_obj = h.get('english')
                if isinstance(eng_obj, dict):
                    text_en = f"{eng_obj.get('narrator', '')} {eng_obj.get('text', '')}".strip()
                else:
                    text_en = str(eng_obj or "")
                    
            elif ds_type == 'lidwa' and base_id in lidwa_map:
                h = lidwa_map[base_id]
                text_ar = h.get('text_ar', '')
                text_id = h.get('text_id', '')

            if anchor_id:
                anchor_row = fawaz_map.get(anchor_id)
                if anchor_row and ds_type == 'lidwa':
                    # First fallback is Fawaz chapter
                    ch_num = str(anchor_row.get('reference', {}).get('book', '1'))
                    in_book_num = str(anchor_row.get('reference', {}).get('hadith', base_id))
                elif not anchor_row and anchor_id in ab_map and ds_type == 'lidwa':
                    ch_num = str(ab_map[anchor_id].get('chapterId', '1'))
                    in_book_num = str(ab_map[anchor_id].get('idInBook', base_id))
                    
            if ds_type == 'lidwa' and str(base_id) in lidwa_native_chapter_map:
                # If Lidwa native chapter exists, it overrides everything!
                ch_num = lidwa_native_chapter_map[str(base_id)]
                
            if anchor_id:
                lidwa_id = ml_entry.get("lidwa_id")
                ab_id = ml_entry.get("ahmedbaset_id")
                
                rawis = ml_entry.get("kaggle_narrators", [])
                lidwa_id_str = str(lidwa_id) if lidwa_id else ""
                
                if lidwa_id_str and lidwa_id_str in lidwa_sanad_map.get(book_id, {}):
                    rawis = lidwa_sanad_map[book_id][lidwa_id_str]
                elif ds_type == 'lidwa' and str(base_id) in lidwa_sanad_map.get(book_id, {}):
                    rawis = lidwa_sanad_map[book_id][str(base_id)]
                    
                if ds_type == 'fawaz':
                    if anchor_id in urd_native_map:
                        text_ur = urd_native_map[anchor_id]
                    if anchor_id in eng_native_map:
                        text_en = eng_native_map[anchor_id]
                    if anchor_id in ind_native_map:
                        text_id = ind_native_map[anchor_id]
                    
                syarah_path = os.path.join(COMMENTARIES_DIR, f"{book_id}_{anchor_id}.json")
                if os.path.exists(syarah_path):
                    with open(syarah_path, 'r', encoding='utf-8') as f:
                        syarah = json.load(f).get('syarah_ar', '')

            # If no text_ar but we are importing fawaz directly, we still want to keep the record
            if not text_ar and ds_type != 'fawaz' and ds_type != 'ab' and ds_type != 'lidwa': return None

            lidwa_id_str = ""
            if anchor_id:
                lidwa_id_str = str(ml_entry.get("lidwa_id", ""))
            if not lidwa_id_str and ds_type == 'lidwa':
                lidwa_id_str = str(base_id)
                
            lmeta = lidwa_metadata_map.get(lidwa_id_str, {})

            return {
                "id": f"{book_id}_{ds_type}_{base_id}",
                "book_id": book_id,
                "dataset": ds_type,
                "chapter_id": f"{book_id}_c{ch_num}",
                "book_number": ch_num,
                "chapter_number": ch_num,
                "hadith_number": base_id,
                "in_book_number": in_book_num,
                "usc_msa_ref": f"Book {ch_num}, Hadith {in_book_num}" if in_book_num else "",
                "text_ar": text_ar,
                "text_ar_search": strip_tashkeel(text_ar),
                "text_en": text_en,
                "text_id": text_id,
                "text_ur": text_ur,
                "grade": grade_str,
                "grade_by": grade_by,
                "grade_id": lmeta.get("grade_id", ""),
                "is_qudsi": lmeta.get("is_qudsi", False),
                "is_mutawatir": lmeta.get("is_mutawatir", False),
                "is_marfu": lmeta.get("is_marfu", False),
                "is_mauquf": lmeta.get("is_mauquf", False),
                "is_maqthu": lmeta.get("is_maqthu", False),
                "is_mursal": lmeta.get("is_mursal", False),
                "is_munqathi": lmeta.get("is_munqathi", False),
                "is_muallaq": lmeta.get("is_muallaq", False),
                "rawis": rawis,
                "syarah": syarah,
                "cross_references": cross_links.get(book_id, {}).get(str(base_id), [])
            }

        fawaz_out = {}
        for idx, h in enumerate(fawaz_data):
            hid = str(idx + 1)
            payload = construct_payload(hid, 'fawaz')
            if payload:
                fawaz_out[hid] = payload
                total_hadiths_built += 1
                
        if fawaz_out:
            with open(os.path.join(book_out_dir, "fawaz.json"), "w", encoding="utf-8") as f:
                json.dump(fawaz_out, f, ensure_ascii=False)

        ab_out = {}
        for h in ab_data:
            hid = str(h.get('idInBook', h.get('id')))
            payload = construct_payload(hid, 'ab')
            if payload:
                ab_out[hid] = payload
                total_hadiths_built += 1
                
        if ab_out:
            with open(os.path.join(book_out_dir, "ab.json"), "w", encoding="utf-8") as f:
                json.dump(ab_out, f, ensure_ascii=False)

        lidwa_out = {}
        for h in lidwa_data:
            hid = str(h.get('hadith_number', h.get('id')))
            payload = construct_payload(hid, 'lidwa')
            if payload:
                lidwa_out[hid] = payload
                total_hadiths_built += 1
                
        if lidwa_out:
            with open(os.path.join(book_out_dir, "lidwa.json"), "w", encoding="utf-8") as f:
                json.dump(lidwa_out, f, ensure_ascii=False)

    print(f"\n[+] API Compilation Complete! Successfully generated {total_hadiths_built} Reciprocal JSON endpoints in consolidated format.")

if __name__ == "__main__":
    build_api()
