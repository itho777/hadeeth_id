import json
import os

out_path = 'data/api/topics_metadata.json'

with open('data/lidwa_extracts/topic_tags.json', 'r', encoding='utf-8') as f:
    topics = json.load(f)

metadata = []
for t in topics:
    # Read the ind_{id}.json to get count of hadiths (rough estimate)
    count = 0
    try:
        with open(f"data/lidwa_extracts/ind_{t['tag_id']}.json", 'r', encoding='utf-8') as ind_f:
            count = len(json.load(ind_f))
    except:
        pass
        
    metadata.append({
        'id': t['tag_id'],
        'name_en': t['name_en'],
        'name_id': t['name_id'],
        'hadith_count': count
    })

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"Generated {out_path} with {len(metadata)} topics.")
