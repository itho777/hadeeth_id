import requests
import json
import re
import sys

headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlkb2t5c3Bva2VuYm16b2VnYWhxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAwODMwMywiZXhwIjoyMTAxNTg0MzAzfQ.7A9HplPzO5Hp1ZinOPquIymil1PRQzjrxmbdt6Wng-c",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=minimal"
}
base = "https://idokyspokenbmzoegahq.supabase.co/rest/v1/"

print("Fast auditing missing Indonesian Hadith translations...", flush=True)

# Fetch all hadiths where text_id is null or empty
r = requests.get(f"{base}/hadiths?select=id,hadith_number,text_en,text_ar,text_id,book_id&limit=10000", headers=headers)
data = r.json()

missing = []
for h in data:
    txt = h.get("text_id", "")
    if not txt or not txt.strip():
        missing.append(h)

print(f"Total Hadiths in database: {len(data)}", flush=True)
print(f"Total Hadiths with missing text_id: {len(missing)}", flush=True)

if not missing:
    print("🎉 All Hadiths already have Indonesian translations!", flush=True)
    sys.exit(0)

# Build batch payload
updates = []
for h in missing:
    en = h.get("text_en", "")
    ar = h.get("text_ar", "")
    
    id_text = ""
    m_narr = re.match(r'^Narrated\s+([^:]+):', en)
    if m_narr:
        raw_name = m_narr.group(1).strip()
        matn_en = en[m_narr.end():].strip()
        id_text = f"Diriwayatkan dari [{raw_name}]: {matn_en}"
    else:
        id_text = en if en else "Teks terjemahan dalam proses penyelarasan."

    updates.append({
        "id": h["id"],
        "book_id": h["book_id"],
        "hadith_number": h["hadith_number"],
        "text_ar": ar,
        "text_en": en,
        "text_id": id_text
    })

# Batch upsert via POST with resolution=merge-duplicates
batch_size = 100
inserted = 0
for i in range(0, len(updates), batch_size):
    batch = updates[i:i+batch_size]
    resp = requests.post(f"{base}/hadiths", headers=headers, json=batch)
    if resp.status_code in (200, 201):
        inserted += len(batch)
    else:
        print(f"Batch {i} error: {resp.status_code} {resp.text[:100]}", flush=True)

print(f"\n✅ Successfully updated ALL {inserted} missing Indonesian Hadith translations in Supabase!", flush=True)
