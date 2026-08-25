import json
with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        if obj['id'] == 135:
            print("ID 135 Arabic:", obj['translations']['ar'][0]['text'][:100].replace('\n', ' '))
            print("ID 135 Lidwa:", obj.get('lidwa_id'))
            break