import json
with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        if obj['id'] == 1:
            print("ID 1 Arabic:", obj['translations']['ar'][0]['text'][:100])
            print("ID 1 Lidwa:", obj.get('lidwa_id'))
            break