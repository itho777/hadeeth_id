# -*- coding: utf-8 -*-
import json, codecs
with codecs.open('check_eng_93.txt', 'w', 'utf-8') as out:
    with open("../data/raw_baseline/eng-muslim.json", "r") as f:
        data = json.load(f)
        for h in data['hadiths']:
            if h['hadithnumber'] == 93:
                out.write("eng-muslim 93: " + h['text'][:100] + "\n")
            if u'Yahya b. Ya\'mur' in h['text']:
                out.write("Yahya is at: " + str(h['hadithnumber']) + " | " + h['text'][:100] + "\n")