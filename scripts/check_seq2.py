# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_8_9_10.txt", "w", "utf-8") as out:
    with open("../data/api/muslim.ndjson", "rb") as f:
        for line in f:
            obj = json.loads(line.decode('utf-8'))
            if obj['id'] in [7, 8, 9, 10]:
                ar_text = obj['translations']['ar'][0]['text'][:200].replace('\n', ' ')
                en_text = obj['translations'].get('en', [{'text': ''}])[0]['text'][:200].replace('\n', ' ')
                id_text = obj['translations'].get('id', [{'text': ''}])[0]['text'][:200].replace('\n', ' ')
                
                out.write("ID: " + str(obj['id']) + " | Lidwa: " + str(obj.get('lidwa_id')) + "\n")
                out.write("AR: " + ar_text + "\n")
                out.write("EN: " + en_text + "\n")
                out.write("ID: " + id_text + "\n\n")