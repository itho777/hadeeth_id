# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_api_chap.txt", "w", "utf-8") as out:
    with open("../data/chapters/muslim.json", "r") as f:
        chapters = json.load(f)
        
    for ch in chapters[:10]:
        out.write("Chap " + str(ch.get('id')) + ": " + ch.get('title_en', '') + " | Hadiths: " + str(ch.get('first_hadith_id')) + " to " + str(ch.get('last_hadith_id')) + "\n")