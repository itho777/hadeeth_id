# -*- coding: utf-8 -*-
import json, codecs
with codecs.open('fawaz_93_ar.txt', 'w', 'utf-8') as out:
    with open("../data/api/muslim.ndjson", "rb") as f:
        for line in f:
            obj = json.loads(line.decode('utf-8'))
            if obj['id'] == 93:
                for t in obj['translations'].get('ar', []):
                    out.write(u"ARABIC (" + unicode(t['source']) + u"): " + unicode(t['text']) + u"\n")
                break