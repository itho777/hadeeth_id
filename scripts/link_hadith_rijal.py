"""
Phase 5: Parse Isnads from DB Hadiths & Populate hadith_rijal junction table
Matches narrator names in text_ar and text_en to rijal records in Supabase.
"""

import requests
import json
import re
import sys
from pathlib import Path

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
    r = requests.get(f"{BASE_API}/rijal?select=id,name_en,kunya_en,name_ar,name_variants", headers=HEADERS)
    return r.json()

def link_hadiths_to_rijal():
    print("=" * 60)
    print("HADEETH.ID -- Hadith-Rijal Linking Pipeline")
    print("=" * 60)

    rijal = fetch_all_rijal()
    print(f"Loaded {len(rijal)} narrators from database.")

    # Build name lookup map
    lookup = {}
    for rawi in rijal:
        rid = rawi["id"]
        names = []
        if rawi.get("name_en"):
            names.append(rawi["name_en"].lower())
        if rawi.get("kunya_en"):
            names.append(rawi["kunya_en"].lower())
        if rawi.get("name_variants"):
            for v in rawi["name_variants"]:
                names.append(v.lower())
        
        for n in names:
            clean_n = re.sub(r"['\u2018\u2019\u02bc\u02be\u02bf`]", "", n).strip()
            lookup[clean_n] = rid

    # Fetch hadiths
    offset = 0
    page_size = 1000
    junction_rows = []

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
            
            # Match "Narrated X:" pattern
            m = re.match(r'^Narrated\s+([^:]+):', en)
            if m:
                raw_name = m.group(1).strip()
                clean_name = re.sub(r'\s*\(.*\)', '', raw_name).strip()
                norm_name = re.sub(r"['\u2018\u2019\u02bc\u02be\u02bf`]", "", clean_name.lower()).strip()
                
                matched_id = lookup.get(norm_name)
                if matched_id:
                    junction_rows.append({
                        "hadith_id": hid,
                        "rawi_id": matched_id,
                        "position": 1,
                        "transmission_verb": "عَنْ",
                        "transmission_en": "narrated",
                        "is_direct": True
                    })

        offset += page_size
        print(f"  Processed {offset} hadiths, found {len(junction_rows)} narrator links...")
        if len(hadiths) < page_size:
            break

    print(f"\nTotal junction rows to insert: {len(junction_rows)}")

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

    print(f"✅ Inserted {inserted} hadith_rijal junction records successfully!")

if __name__ == "__main__":
    link_hadiths_to_rijal()
