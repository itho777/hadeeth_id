import json
with open("../data/api/muslim.ndjson", "r") as f:
    for line in f:
        obj = json.loads(line)
        if obj['id'] == 93:
            print(obj['translations'].get('en', []))