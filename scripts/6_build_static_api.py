import os
import json
import re
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAWAZ_DIR = os.path.join(DATA_DIR, "editions")
LIDWA_DIR = os.path.join(DATA_DIR, "sources", "lidwa")
AHMEDBASET_DIR = os.path.join(DATA_DIR, "sources", "ahmedbaset", "by_book")
LINKS_DIR = os.path.join(DATA_DIR, "links")
COMMENTARIES_DIR = os.path.join(DATA_DIR, "commentaries")
HADITHS_OUT_DIR = os.path.join(DATA_DIR, "hadiths")

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
    "nawawi": "forties/nawawi.json"
}

def strip_tashkeel(text):
    if not text:
        return ""
    text = re.sub(r'[\u200e\u200f\u202a-\u202e\u200b\u200c\u200d\uFEFF]', '', text)
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    return text

def build_api():
    print("[*] Starting Reciprocal API Builder...")
    
    # Wipe old API directory to prevent stale files
    if os.path.exists(HADITHS_OUT_DIR):
        shutil.rmtree(HADITHS_OUT_DIR)
    os.makedirs(HADITHS_OUT_DIR)
    
    with open(os.path.join(DATA_DIR, 'books_v2.json'), 'r', encoding='utf-8') as f:
        books = json.load(f)
        
    with open(os.path.join(LINKS_DIR, 'master_link.json'), 'r', encoding='utf-8') as f:
        master_link = json.load(f)

    total_hadiths_built = 0

    for b in books:
        book_id = b['id']
        print(f" -> Building Static API for {book_id}...")
        
        book_out_dir = os.path.join(HADITHS_OUT_DIR, book_id)
        os.makedirs(os.path.join(book_out_dir, "fawaz"), exist_ok=True)
        os.makedirs(os.path.join(book_out_dir, "ab"), exist_ok=True)
        os.makedirs(os.path.join(book_out_dir, "lidwa"), exist_ok=True)
        
        ml_book = master_link.get(book_id, {})
        
        # Build Reverse Maps
        ab_to_anchor = {}
        lidwa_to_anchor = {}
        for anchor_id, links in ml_book.items():
            if links.get('ahmedbaset_id'):
                ab_to_anchor[str(links['ahmedbaset_id'])] = anchor_id
            if links.get('lidwa_id'):
                lidwa_to_anchor[str(links['lidwa_id'])] = anchor_id
        
        # Load Fawaz Data
        fawaz_data = []
        is_fawaz_anchor = False
        fawaz_path = os.path.join(FAWAZ_DIR, f"ara-{book_id}.json")
        if os.path.exists(fawaz_path):
            with open(fawaz_path, 'r', encoding='utf-8') as f:
                fd = json.load(f)
                fawaz_data = fd.get('hadiths', []) if isinstance(fd, dict) else fd
                is_fawaz_anchor = True
                
        fawaz_map = {}
        for h in fawaz_data:
            hid = str(h.get('hadithnumber', h.get('id')))
            fawaz_map[hid] = h
                
        # Load AB Data
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

        # Load Lidwa Data
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

        # Load Native Translations
        eng_native_map = {}
        eng_path = os.path.join(FAWAZ_DIR, f"eng-{book_id}.json")
        if os.path.exists(eng_path):
            with open(eng_path, 'r', encoding='utf-8') as f:
                ed = json.load(f)
                eh = ed.get('hadiths', []) if isinstance(ed, dict) else ed
                for h in eh: eng_native_map[str(h.get('hadithnumber', ''))] = h.get('text', '')
                    
        ind_native_map = {}
        ind_path = os.path.join(FAWAZ_DIR, f"ind-{book_id}.json")
        if os.path.exists(ind_path):
            with open(ind_path, 'r', encoding='utf-8') as f:
                idat = json.load(f)
                ih = idat.get('hadiths', []) if isinstance(idat, dict) else idat
                for h in ih: ind_native_map[str(h.get('hadithnumber', ''))] = h.get('text', '')
                
        urd_native_map = {}
        urd_path = os.path.join(FAWAZ_DIR, f"urd-{book_id}.json")
        if os.path.exists(urd_path):
            with open(urd_path, 'r', encoding='utf-8') as f:
                idat = json.load(f)
                ih = idat.get('hadiths', []) if isinstance(idat, dict) else idat
                for h in ih: urd_native_map[str(h.get('hadithnumber', ''))] = h.get('text', '')

        def construct_payload(base_id, ds_type):
            anchor_id = None
            if ds_type == 'fawaz': anchor_id = base_id
            elif ds_type == 'ab': anchor_id = ab_to_anchor.get(base_id)
            elif ds_type == 'lidwa': anchor_id = lidwa_to_anchor.get(base_id)
            
            ml_entry = ml_book.get(anchor_id, {}) if anchor_id else {}
            
            text_ar, text_en, text_id, text_ur, rawis, syarah = "", "", "", "", [], ""
            ch_num, in_book_num = 1, base_id
            grade_str, grade_by = "Sahih", ""
            
            # 1. Fill from Base Dataset
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

            # 2. Enrich via Anchor Graph
            if anchor_id:
                lidwa_id = ml_entry.get("lidwa_id")
                ab_id = ml_entry.get("ahmedbaset_id")
                
                # Fetch missing from Lidwa
                if not text_id and lidwa_id and str(lidwa_id) in lidwa_map:
                    text_id = lidwa_map[str(lidwa_id)].get('text_id', '')
                
                # Fetch Sanad from Anchor Graph (always sourced from Lidwa originally)
                rawis = ml_entry.get("kaggle_narrators", [])
                
                # Fetch missing from AB
                if not text_en and ab_id and str(ab_id) in ab_map:
                    eng_obj = ab_map[str(ab_id)].get('english')
                    if isinstance(eng_obj, dict):
                        text_en = f"{eng_obj.get('narrator', '')} {eng_obj.get('text', '')}".strip()
                    else:
                        text_en = str(eng_obj or "")
                        
                # Fetch missing from Fawaz (Urdu + Fallbacks)
                if anchor_id in urd_native_map:
                    text_ur = urd_native_map[anchor_id]
                if not text_en and anchor_id in eng_native_map:
                    text_en = eng_native_map[anchor_id]
                if not text_id and anchor_id in ind_native_map:
                    text_id = ind_native_map[anchor_id]
                if not text_ar and anchor_id in fawaz_map:
                    text_ar = fawaz_map[anchor_id].get('text', '')
                    
                # Fetch Syarah
                syarah_path = os.path.join(COMMENTARIES_DIR, f"{book_id}_{anchor_id}.json")
                if os.path.exists(syarah_path):
                    with open(syarah_path, 'r', encoding='utf-8') as f:
                        syarah = json.load(f).get('syarah_ar', '')

            # If STILL no AR, skip (dead hadith)
            if not text_ar: return None

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
                "rawis": rawis,
                "syarah": syarah
            }

        # Generate Fawaz
        for h in fawaz_data:
            hid = str(h.get('hadithnumber', h.get('id')))
            payload = construct_payload(hid, 'fawaz')
            if payload:
                with open(os.path.join(book_out_dir, "fawaz", f"{hid}.json"), "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
                total_hadiths_built += 1
                
        # Generate AhmedBaset
        for h in ab_data:
            hid = str(h.get('idInBook', h.get('id')))
            payload = construct_payload(hid, 'ab')
            if payload:
                with open(os.path.join(book_out_dir, "ab", f"{hid}.json"), "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
                total_hadiths_built += 1
                
        # Generate Lidwa
        for h in lidwa_data:
            hid = str(h.get('hadith_number', h.get('id')))
            payload = construct_payload(hid, 'lidwa')
            if payload:
                with open(os.path.join(book_out_dir, "lidwa", f"{hid}.json"), "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
                total_hadiths_built += 1

    print(f"\n[+] API Compilation Complete! Successfully generated {total_hadiths_built} Reciprocal JSON endpoints.")

if __name__ == "__main__":
    build_api()
