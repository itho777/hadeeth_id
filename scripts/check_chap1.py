import json
start_iman = None
with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        if obj.get('chapter') == 1:
            print("Chapter 1 start:", obj.get('lidwa_id'))
            break