# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_api_jibril.txt", "w", "utf-8") as out:
    with open("../data/api/muslim.ndjson", "rb") as f:
        for line in f:
            obj = json.loads(line.decode('utf-8'))
            hid = obj.get('id')
            if hid in [1, 2, 8, 9]:
                out.write("ID: " + str(hid) + " | Lidwa: " + str(obj.get('lidwa_id')) + "\n")
                if 'en' in obj.get('translations', {}):
                    out.write("EN (First): " + obj['translations']['en'][0]['text'][:100].replace('\n', ' ') + "\n")