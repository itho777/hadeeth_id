import json
with open("../data/api/muslim.ndjson", "r") as f:
    for i, line in enumerate(f):
        if 95 <= i <= 100:
            obj = json.loads(line)
            print("ID:", obj['id'], "lidwa:", obj.get('lidwa_id'), "EN:", obj['translations'].get('en', [{}])[0].get('text', '')[:100])