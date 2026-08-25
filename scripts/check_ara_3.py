# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_ara_3.txt", "w", "utf-8") as out:
    with open("../data/raw_baseline/ara-muslim.json", "r") as f:
        data = json.load(f)

    for h in data["hadiths"][:5]:
        out.write("Hadith " + str(h.get('hadithnumber')) + ": " + h.get('text')[:100].replace('\n', ' ') + "\n")