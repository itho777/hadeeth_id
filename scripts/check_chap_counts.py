# -*- coding: utf-8 -*-
import json, codecs
with codecs.open("check_chap_counts.txt", "w", "utf-8") as out:
    with open("../data/chapters/muslim.json", "r") as f:
        chapters = json.load(f)
    for ch in chapters[:15]:
        out.write(str(ch.get('chapter_number')) + " | " + ch.get('title_en', '') + " | count=" + str(ch.get('hadith_count')) + "\n")