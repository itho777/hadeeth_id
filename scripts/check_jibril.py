# -*- coding: utf-8 -*-
import json, codecs
with codecs.open('lidwa_jibril.txt', 'w', 'utf-8') as out:
    with open("../data/api/muslim.ndjson", "rb") as f:
        for line in f:
            obj = json.loads(line.decode('utf-8'))
            for t in obj['translations'].get('id', []):
                if u'Yahya bin Ya\'mar' in t['text'] or u'Yahya bin Ya`mar' in t['text'] or u'Yahya bin Ya\'mar' in t['text']:
                    out.write(u"ID: " + unicode(obj['id']) + u" | Lidwa ID: " + unicode(obj.get('lidwa_id')) + u" | Text: " + unicode(t['text'][:100].replace('\n', ' ')) + u"\n")