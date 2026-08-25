# -*- coding: utf-8 -*-
import json

search1 = u'يَحْيَى بْنِ يَعْمَرَ'
search2 = u'أَبَا الْأَسْوَدِ'

with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        for t in obj['translations'].get('ar', []):
            if search1 in t['text'] and search2 in t['text']:
                print("Found in ID: " + str(obj['id']) + " | Lidwa ID: " + str(obj.get('lidwa_id')))