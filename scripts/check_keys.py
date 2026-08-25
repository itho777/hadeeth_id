import json
with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        if obj['id'] == 8:
            print("ID 8 keys:", obj.keys())
            print("ID 8:", obj)
            break