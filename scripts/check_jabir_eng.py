# -*- coding: utf-8 -*-
import json, codecs
with codecs.open('check_jabir_eng.txt', 'w', 'utf-8') as out:
    with open("../data/raw_baseline/eng-muslim.json", "r") as f:
        data = json.load(f)
        for h in data['hadiths']:
            if u'narrated on the authority of Jabir that a man came to the Apostle of Allah' in h['text']:
                out.write("Jabir hadith is at: " + str(h['hadithnumber']) + " | " + h['text'][:100] + "\n")