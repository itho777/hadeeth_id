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

with codecs.open("full_table.md", "w", "utf-8") as out:
    out.write("| Book Title (Lidwa) | Book Title (Fawazahmed/API) | Lidwa System (Indonesian) | Fawazahmed (Current UI Nav) | True International (Fuat Abdul Baqi/API) |\n")
    out.write("| :--- | :--- | :--- | :--- | :--- |\n")
    
    for i in range(len(lidwa_chaps)):
        lidwa = lidwa_chaps[i]
        fawaz = fawaz_chaps[i] if i < len(fawaz_chaps) else {}
        
        l_title = lidwa.get('title_id', '')
        f_title = fawaz.get('title_en', '')
        
        l_start = str(lidwa.get('hadith_start', ''))
        l_count = str(lidwa.get('hadith_count', ''))
        
        f_start = str(fawaz.get('hadith_start', ''))
        f_count = str(fawaz.get('hadith_count', ''))
        
        # Calculate true intl start
        true_start = lidwa_to_intl.get(l_start, "?")
        
        # Calculate true intl count (approximate by looking at next chapter's start, or just leave blank to avoid confusion, or calculate exactly)
        if i + 1 < len(lidwa_chaps):
            next_l_start = str(lidwa_chaps[i+1].get('hadith_start', ''))
            next_true_start = lidwa_to_intl.get(next_l_start, "?")
        else:
            next_true_start = "?"
            
        out.write("| " + l_title + " | " + f_title + " | **Count:** " + l_count + "<br>**Starts:** #" + l_start + " | **Count:** " + f_count + "<br>**Starts:** #" + f_start + " | **Starts:** #" + true_start + " |\n")