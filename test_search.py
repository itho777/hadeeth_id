import json
import os

ndjson_path = r"g:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id\data\api\bukhari.ndjson"
all_hadiths = []
with open(ndjson_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            all_hadiths.append(json.loads(line))

h1 = all_hadiths[0]

def check_match(h, q):
    en = h.get("text_en") or (h.get("translations", {}).get("en", [{}])[0].get("text") if h.get("translations", {}).get("en") else "") or ""
    id_txt = h.get("text_id") or (h.get("translations", {}).get("id", [{}])[0].get("text") if h.get("translations", {}).get("id") else "") or ""
    ar = h.get("text_ar") or (h.get("translations", {}).get("ar", [{}])[0].get("text") if h.get("translations", {}).get("ar") else "") or ""
    num = str(h.get("id") or h.get("hadith_number") or "")
    q = q.lower()
    return (q in en.lower()) or (q in id_txt.lower()) or (q in ar) or (q in num)

print(f"Does Bukhari #1 match 'haji'?: {check_match(h1, 'haji')}")
print(f"Bukhari #1 tags: {h1.get('tags')}")

# Topics metadata
meta_path = r"g:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id\data\api\topics_metadata.ndjson"
if os.path.exists(meta_path):
    topics = []
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                topics.append(json.loads(line))
    print(f"Total topics: {len(topics)}")
    for t in topics:
        print(f"  Topic {t.get('id')}: {t.get('name_en')} | {t.get('name_id')}")

# Check which hadiths under topic "Acts of Worship" or "Hajj" match "haji"
for t in topics:
    name_en = t.get("name_en")
    topic_hadiths = [h for h in all_hadiths if h.get("tags") and name_en in h.get("tags")]
    matches = [h for h in topic_hadiths if check_match(h, "haji")]
    print(f"Topic '{name_en}': {len(topic_hadiths)} hadiths in Bukhari, {len(matches)} match 'haji'")
    if matches:
        print(f"  First 3 matching hadith IDs: {[m.get('id') for m in matches[:3]]}")
