# -*- coding: utf-8 -*-
import json, codecs
with codecs.open("out_ara.txt", "w", "utf-8") as out:
    with open("../data/raw_baseline/ara-muslim.json", "r") as f:
        data = json.load(f)
        for h in data["hadiths"][:10]:
            out.write(u"Hadith: " + unicode(h["hadithnumber"]) + u" | " + unicode(h["text"][:100].replace('\n', ' ')) + u"\n")
        out.write(u"\nChecking 92 and 93:\n")
        for h in data["hadiths"][90:95]:
            out.write(u"Hadith: " + unicode(h["hadithnumber"]) + u" | " + unicode(h["text"][:100].replace('\n', ' ')) + u"\n")