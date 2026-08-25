# -*- coding: utf-8 -*-
import json, codecs

# Load the Lidwa chapters
with open("../data/lidwa-chapters/muslim.json", "r") as f:
    lidwa_chaps = json.load(f)['chapters']
    
# Load Fawazahmed chapters
with open("../data/chapters/muslim.json", "r") as f:
    fawaz_chaps = json.load(f)

# Load the API ndjson to map lidwa_id -> true intl id
lidwa_to_intl = {}
with open("../data/api/muslim.ndjson", "rb") as f:
    for line in f:
        obj = json.loads(line.decode('utf-8'))
        l_id = obj.get('lidwa_id')
        i_id = obj.get('id')
        if l_id and i_id:
            lidwa_to_intl[str(l_id)] = str(i_id)

with codecs.open("full_table_with_numbers.md", "w", "utf-8") as out:
    out.write("| Kitab # (Lidwa) | Kitab Title (Lidwa) | Kitab # (Intl) | Kitab Title (English UI) | Lidwa System (Indonesian) | Fawazahmed (Current UI Nav) | True Darussalam (API) |\n")
    out.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    
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
        
        # Calculate true intl start
        true_start = lidwa_to_intl.get(l_start, "?")
        if true_start == "?" and "Tobat" in l_title:
            true_start = "~2744"
            
        out.write("| **" + l_num + "** | " + l_title + " | **" + f_num + "** | " + f_title + " | **Count:** " + l_count + "<br>**Starts:** #" + l_start + " | **Count:** " + f_count + "<br>**Starts:** #" + f_start + " | **Starts:** #" + true_start + " |\n")