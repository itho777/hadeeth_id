# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_chap_cmp.txt", "w", "utf-8") as out:
    try:
        with open("../data/lidwa-chapters/muslim.json", "r") as f:
            lidwa = json.load(f)
        out.write("--- LIDWA CHAPTERS ---\n")
        for ch in lidwa[:10]:
            out.write(str(ch.get('chapter_number')) + " | " + ch.get('title_id', '') + " | Count=" + str(ch.get('hadith_count')) + " (Start: " + str(ch.get('hadith_start')) + ")\n")
    except Exception as e:
        out.write("Lidwa error: " + str(e) + "\n")
        
    try:
        with open("../data/chapters/muslim.json", "r") as f:
            intl = json.load(f)
        out.write("\n--- INTERNATIONAL (Fawazahmed/API) CHAPTERS ---\n")
        for ch in intl[:10]:
            out.write(str(ch.get('chapter_number')) + " | " + ch.get('title_en', '') + " | Count=" + str(ch.get('hadith_count')) + " (Start: " + str(ch.get('hadith_start')) + ")\n")
    except Exception as e:
        pass