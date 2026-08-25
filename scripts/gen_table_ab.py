# -*- coding: utf-8 -*-
import json, codecs

with open("../data/lidwa-chapters/muslim.json", "r") as f:
    lidwa_chaps = json.load(f)['chapters']
with open("../data/chapters/muslim.json", "r") as f:
    fawaz_chaps = json.load(f)

lidwa_to_intl = {}
with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        if obj.get('lidwa_id') and obj.get('id'):
            lidwa_to_intl[str(obj['lidwa_id'])] = str(obj['id'])

ab_start_map = {}
with open("../data/sources/ahmedbaset/by_book/the_9_books/muslim.json", "r") as f:
    ab_raw = json.load(f)
    for h in ab_raw.get('hadiths', []):
        cid = h.get('chapterId')
        if cid is not None and cid not in ab_start_map:
            ab_start_map[cid] = h.get('idInBook')

with codecs.open("full_table_with_ab.md", "w", "utf-8") as out:
    out.write("| Kitab # (Lidwa) | Kitab Title (Lidwa) | Kitab # (Intl) | Kitab Title (English UI) | Lidwa System (Indonesian) | Fawazahmed (Current UI Nav) | True Darussalam (API) | Raw AhmedBaset Source |\n")
    out.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    
    for i in range(len(lidwa_chaps)):
        lidwa = lidwa_chaps[i]
        fawaz = fawaz_chaps[i] if i < len(fawaz_chaps) else {}
        
        l_num = str(lidwa.get('chapter_number', '?'))
        l_title = lidwa.get('title_id', '')
        
        f_num = str(fawaz.get('chapter_number', '?'))
        f_title = fawaz.get('title_en', '')
        
        l_start = str(lidwa.get('hadith_start', ''))
        l_count = str(lidwa.get('hadith_count', ''))
        
        f_start = str(fawaz.get('hadith_start', ''))
        f_count = str(fawaz.get('hadith_count', ''))
        
        true_start = lidwa_to_intl.get(l_start, "?")
        if true_start == "?" and "Tobat" in l_title:
            true_start = "~2744"
            
        ab_raw_start = str(ab_start_map.get(int(f_num) if f_num.isdigit() else 0, "?"))
        
        out.write("| **" + l_num + "** | " + l_title + " | **" + f_num + "** | " + f_title + " | **Count:** " + l_count + "<br>**Starts:** #" + l_start + " | **Count:** " + f_count + "<br>**Starts:** #" + f_start + " | **Starts:** #" + true_start + " | **Starts:** #" + ab_raw_start + " |\n")