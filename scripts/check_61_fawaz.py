import json
with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        if obj['id'] == 61:
            print("ID 61 Lidwa:", obj.get('lidwa_id'))
            print("ID 61 Arabic:", obj['translations']['ar'][0]['text'][:50])
            break