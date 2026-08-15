"""
Phase 5: Parse Full Isnads from DB Hadiths & Populate hadith_rijal junction table
Matches narrator names in text_ar and text_en to rijal records in Supabase.
"""

import requests
import json
import re
import sys

SUPABASE_URL = "https://idokyspokenbmzoegahq.supabase.co"
BASE_API = f"{SUPABASE_URL}/rest/v1"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c"

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=minimal"
}

def fetch_all_rijal():
    """Fetch all rawi_id, name_en, kunya_en, name_ar from DB for matching."""
    r = requests.get(f"{BASE_API}/rijal?select=id,name_en,kunya_en,name_ar,name_variants,kunya", headers=HEADERS)
    return r.json()

def parse_isnad_tokens(text_ar):
    if not text_ar:
        return []

    # Separate Isnad from Matn
    matn_split_pattern = r'["«”"“「»\u201d\u201c\u200f]|أَنَّ\s+هِرَقْلَ|أَنَّ\s+رَسُولَ|أَنَّ\s+النَّبِيَّ|فَقَالَ\s+|قَالَ\s+رَسُولُ|قَالَتْ\s+'
    parts = re.split(matn_split_pattern, text_ar, maxsplit=1)
    isnad_part = parts[0] or text_ar

    m = re.search(r'(?:عَنِ?\s+النَّبِيِّ|رَسُولِ?\s+اللَّهِ).*?(?:قَالَ|قَالَتْ|يَقُولُ)\s+', isnad_part)
    if m:
        isnad_part = isnad_part[:m.end()]

    clean = re.sub(
        r'رَسُولُ?\s+اللَّهِ|رَسُولِ?\s+اللَّهِ|صَلَّى\s+اللَّهُ\s+عَلَيْهِ\s+وَسَلَّمَ|صلى\s+الله\s+عليه\s+وسلم|رَضِيَ?\s+اللَّهُ\s+عَنْهُ?مَا?|رضى\s+الله\s+عنه|أُمِّ?\s+الْمُؤْمِنِينَ|عَنِ?\s+النَّبِيِّ|النَّبِيِّ|أَنَّهَا?\s+قَالَتْ|أَنَّهُ\s+قَالَ|قَالَ|قَالَتْ|سَمِعْتُ|عَلَى|الْمِنْبَرِ|يَقُولُ|نَحْوَهُ',
        ' ',
        isnad_part
    )

    clean_no_tashkeel = re.sub(r'[\u064B-\u0652]', '', clean)
    clean_alpha = re.sub(r'[^\u0621-\u064A\s]', ' ', clean_no_tashkeel)
    clean_alpha = re.sub(r'\s+', ' ', clean_alpha).strip()

    tokens = [t.strip() for t in re.split(r'حدثنا|حدثني|أخبرنا|أخبرني|عن|أخبره|حدثه|سمع', clean_alpha) if t.strip()]

    valid = []
    stop_words = {'رسول الله', 'صلى الله', 'النبي', 'الإيمان', 'شعبة', 'صلاة', 'وضوء', 'فترة الوحى', 'حديثه', 'هرقل'}
    for t in tokens:
        t_clean = re.sub(r'^[ـ\s]+|[ـ\s]+$', '', t).strip()
        if len(t_clean) > 3 and not any(sw in t_clean for sw in stop_words):
            valid.append(t_clean)

    return valid

def link_hadiths_to_rijal():
    print("=" * 60)
    print("HADEETH.ID -- Hadith-Rijal Full Isnad Linking Pipeline")
    print("=" * 60)

    rijal = fetch_all_rijal()
    print(f"Loaded {len(rijal)} narrators from database.")

    # Build name lookup maps (English normalized + Arabic normalized)
    lookup_en = {}
    lookup_ar = {}

    for rawi in rijal:
        rid = rawi["id"]
        # English keys
        en_names = []
        if rawi.get("name_en"):
            en_names.append(rawi["name_en"].lower())
        if rawi.get("kunya_en"):
            en_names.append(rawi["kunya_en"].lower())
        if rawi.get("name_variants"):
            for v in rawi["name_variants"]:
                en_names.append(v.lower())
        for n in en_names:
            clean_n = re.sub(r"['\u2018\u2019\u02bc\u02be\u02bf`]", "", n).strip()
            lookup_en[clean_n] = rid

        # Arabic keys
        ar_names = []
        if rawi.get("name_ar"):
            ar_names.append(rawi["name_ar"])
        if rawi.get("kunya"):
            ar_names.append(rawi["kunya"])
        for n in ar_names:
            clean_ar = re.sub(r'[\u064B-\u0652]', '', n).strip()
            lookup_ar[clean_ar] = rid

    # Fetch all hadiths
    offset = 0
    page_size = 1000
    junction_rows = []
    seen_keys = set()

    while True:
        r = requests.get(
            f"{BASE_API}/hadiths?select=id,text_en,text_ar&limit={page_size}&offset={offset}",
            headers=HEADERS
        )
        hadiths = r.json()
        if not hadiths:
            break

        for h in hadiths:
            hid = h["id"]
            en = h.get("text_en", "")
            ar = h.get("text_ar", "")
            
            matched_narrators = []

            # Step A: Parse Arabic isnad tokens (Reverse: Companion -> Sheikh)
            ar_tokens = parse_isnad_tokens(ar)
            # Reverse so position 1 = closest to Prophet (Companion)
            ar_tokens_reversed = list(reversed(ar_tokens))

            pos = 1
            for tok in ar_tokens_reversed:
                matched_id = None
                # Check Arabic lookup
                for ar_key, rid in lookup_ar.items():
                    if ar_key in tok or tok in ar_key:
                        matched_id = rid
                        break

                if matched_id:
                    key = (hid, matched_id, pos)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        matched_narrators.append({
                            "hadith_id": hid,
                            "rawi_id": matched_id,
                            "position": pos,
                            "transmission_verb": "عَنْ",
                            "transmission_en": "from",
                            "is_direct": (pos == 1)
                        })
                        pos += 1

            # Step B: Fallback companion from English if position 1 missed
            if not any(m["position"] == 1 for m in matched_narrators) and en.startswith("Narrated "):
                m = re.match(r'^Narrated\s+([^:]+):', en)
                if m:
                    raw_name = m.group(1).strip()
                    clean_name = re.sub(r'\s*\(.*\)', '', raw_name).strip()
                    norm_name = re.sub(r"['\u2018\u2019\u02bc\u02be\u02bf`]", "", clean_name.lower()).strip()
                    matched_id = lookup_en.get(norm_name)
                    if matched_id:
                        key = (hid, matched_id, 1)
                        if key not in seen_keys:
                            seen_keys.add(key)
                            matched_narrators.insert(0, {
                                "hadith_id": hid,
                                "rawi_id": matched_id,
                                "position": 1,
                                "transmission_verb": "عَنْ",
                                "transmission_en": "narrated",
                                "is_direct": True
                            })

            junction_rows.extend(matched_narrators)

        offset += page_size
        print(f"  Processed {offset} hadiths, found {len(junction_rows)} narrator links...")
        if len(hadiths) < page_size:
            break

    print(f"\nTotal junction rows to insert: {len(junction_rows)}")

    # Clear existing hadith_rijal links before re-inserting full chains
    print("Clearing old hadith_rijal rows...")
    requests.delete(f"{BASE_API}/hadith_rijal?id=gt.0", headers=HEADERS)

    # Insert into hadith_rijal in batches
    batch_size = 100
    inserted = 0
    for i in range(0, len(junction_rows), batch_size):
        batch = junction_rows[i:i+batch_size]
        resp = requests.post(f"{BASE_API}/hadith_rijal", headers=HEADERS, json=batch)
        if resp.status_code in (200, 201):
            inserted += len(batch)
        else:
            print(f"Batch {i} error: {resp.status_code} {resp.text[:100]}")

    print(f"✅ Successfully inserted {inserted} full-chain hadith_rijal records into Supabase!")

if __name__ == "__main__":
    link_hadiths_to_rijal()
