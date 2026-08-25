# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_ara_gaps.txt", "w", "utf-8") as out:
    with open("../data/raw_baseline/ara-muslim.json", "r") as f:
        data = json.load(f)
    
    for h in data.get('hadiths', [])[:25]:
        num = h.get('hadithnumber')
        text = h.get('text', '').strip()
        out.write(str(num) + ": " + ("EMPTY" if not text else "HAS TEXT (" + text[:30].replace('\n', ' ') + "...)") + "\n")