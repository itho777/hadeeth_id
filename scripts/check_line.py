import json
with open("../data/api/muslim.ndjson", "r") as f:
    for i, line in enumerate(f):
        obj = json.loads(line)
        if obj['id'] == 8:
            print("ID 8 is at line:", i+1)
        if obj['id'] == 93:
            print("ID 93 is at line:", i+1)