# -*- coding: utf-8 -*-
import json, codecs
with codecs.open('check_jabir.txt', 'w', 'utf-8') as out:
    with open("../data/api/muslim.ndjson", "rb") as f:
        for line in f:
            obj = json.loads(line.decode('utf-8'))
            for t in obj['translations'].get('ar', []):
                if u'الْمُوجِبَتَانِ' in t['text']:
                    out.write(u"ID: " + unicode(obj['id']) + u"\n")
                    out.write(u"ARABIC: " + unicode(t['text'][:100]) + u"\n")
                    if 'en' in obj['translations']:
                        out.write(u"ENGLISH: " + unicode(obj['translations']['en'][0]['text'][:100]) + u"\n")
                    break