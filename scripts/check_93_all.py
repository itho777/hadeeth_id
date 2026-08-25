# -*- coding: utf-8 -*-
import json, codecs

languages = ['ara', 'eng', 'fra', 'urd', 'ben', 'rus', 'tam', 'tur']
output = []

for lang in languages:
    path = "../data/raw_baseline/" + lang + "-muslim.json"
    try:
        with open(path, "r") as f:
            data = json.load(f)
        h_93 = next((h.get('text', '') for h in data.get('hadiths', []) if h.get('hadithnumber') == 93), "")
        output.append((lang.upper(), h_93.strip().replace('\n', ' ')))
    except Exception as e:
        output.append((lang.upper(), "ERROR: " + str(e)))

with codecs.open("check_93_all.txt", "w", "utf-8") as out:
    for lang, text in output:
        out.write(lang + ": " + text[:150] + "\n")