import json

with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        for t in obj['translations'].get('ar', []):
            if u'يَحْيَى بْنِ يَعْمَرَ' in t['text'] and u'أَبَا الْأَسْوَدِ' in t['text']:
                print("Found in ID: " + str(obj['id']) + " | Lidwa ID: " + str(obj.get('lidwa_id')))