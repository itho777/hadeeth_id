# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_269.txt", "w", "utf-8") as out:
    with open("../data/raw_baseline/eng-muslim.json", "r") as f:
        eng_data = json.load(f)
        for h in eng_data['hadiths']:
            if h.get('hadithnumber') in [269, 270, 271]:
                out.write("Eng " + str(h.get('hadithnumber')) + ": " + h.get('text')[:200].replace('\n', ' ') + "\n")
                
    with open("../data/api/muslim.ndjson", "rb") as f:
        for line in f:
            obj = json.loads(line.decode('utf-8'))
            if obj['id'] == 93:
                out.write("API Eng 93: " + obj['translations'].get('en', [{}])[0].get('text', '')[:200].replace('\n', ' ') + "\n")