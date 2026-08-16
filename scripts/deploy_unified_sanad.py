import os
import json
import requests

SUPABASE_URL = "https://idokyspokenbmzoegahq.supabase.co"
BASE_API = f"{SUPABASE_URL}/rest/v1"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c"

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=minimal"
}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LINKS_DIR = os.path.join(BASE_DIR, "data", "links")

CORE_9 = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "darimi", "ahmad"]

def deploy_unified_sanad():
    print("=" * 60)
    print("HADEETH.ID -- Deploy Unified Sanad to Supabase")
    print("=" * 60)

    # 1. Clear existing hadith_rijal table
    print("[*] Clearing existing hadith_rijal rows in Supabase...")
    r = requests.delete(f"{BASE_API}/hadith_rijal?id=gt.0", headers=HEADERS)
    if r.status_code not in (200, 204):
        print(f"[!] Warning: Delete returned {r.status_code}")

    junction_rows = []

    # 2. Iterate over all books
    for book in CORE_9:
        link_path = os.path.join(LINKS_DIR, f"{book}.json")
        if not os.path.exists(link_path):
            continue
            
        with open(link_path, 'r', encoding='utf-8') as f:
            links_data = json.load(f)
            
        lidwa_to_fawaz = links_data.get('lidwa_to_fawaz', {})
        unified_sanad = links_data.get('unified_sanad', {})
        
        print(f"[*] Extracting chains for {book}...")
        for lidwa_id, chain in unified_sanad.items():
            fawaz_id = lidwa_to_fawaz.get(str(lidwa_id))
            if not fawaz_id:
                # Fallback to assuming lidwa_id is fawaz_id if no map exists
                fawaz_id = lidwa_id
                
            hid = f"{book}_{fawaz_id}"
            
            # Chain is ordered Collector -> Prophet in Lidwa
            # Reverse it so position 1 = Prophet/Companion (like Kaggle expected)
            reversed_chain = list(reversed(chain))
            
            pos = 1
            for rawi in reversed_chain:
                sid = rawi.get('sid')
                if sid:
                    junction_rows.append({
                        "hadith_id": hid,
                        "rawi_id": sid,
                        "position": pos,
                        "transmission_verb": "عَنْ",
                        "transmission_en": "from",
                        "is_direct": (pos == 1)
                    })
                    pos += 1
                    
    print(f"[*] Total potential junction rows: {len(junction_rows)}")

    # 2.5 Fetch valid rijal IDs from Supabase to prevent Foreign Key constraint violations
    print("[*] Fetching valid rijal IDs from Supabase...")
    valid_rijal_ids = set()
    offset = 0
    while True:
        resp = requests.get(f"{BASE_API}/rijal?select=id&limit=1000&offset={offset}", headers=HEADERS)
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        for row in data:
            valid_rijal_ids.add(str(row['id']))
        offset += 1000
    print(f"[*] Found {len(valid_rijal_ids)} valid rijal IDs in Supabase")
    print(f"[*] Sample valid_rijal_ids: {list(valid_rijal_ids)[:5]}")
    if junction_rows:
        print(f"[*] Sample junction_row rawi_id: {junction_rows[0]['rawi_id']} (type: {type(junction_rows[0]['rawi_id'])})")

    # Filter junction rows
    valid_junction_rows = []
    for row in junction_rows:
        if row['rawi_id'] in valid_rijal_ids:
            valid_junction_rows.append(row)
            
    print(f"[*] Filtered down to {len(valid_junction_rows)} valid junction rows to insert")

    # 3. Batch insert
    batch_size = 500
    inserted = 0
    for i in range(0, len(valid_junction_rows), batch_size):
        batch = valid_junction_rows[i:i+batch_size]
        resp = requests.post(f"{BASE_API}/hadith_rijal", headers=HEADERS, json=batch)
        if resp.status_code in (200, 201):
            inserted += len(batch)
        else:
            print(f"[!] Batch {i} error: {resp.status_code} {resp.text[:100]}")

    print(f"\n[+] Successfully deployed {inserted} unified sanad junction rows to Supabase!")

if __name__ == "__main__":
    deploy_unified_sanad()
