# -*- coding: utf-8 -*-
import json

languages = ['ara', 'eng', 'fra', 'urd', 'ben', 'rus', 'tam', 'tur']

for lang in languages:
    path = "../data/raw_baseline/" + lang + "-muslim.json"
    try:
        with open(path, "r") as f:
            data = json.load(f)
            
        hadiths = data.get('hadiths', [])
        total = len(hadiths)
        
        # Count completely empty ones
        empty_count = sum(1 for h in hadiths if not h.get('text', '').strip())
        
        # Check hadith #93 (Jibril in Fawaz) and #269 (Jabir in Fawaz)
        h_93 = next((h.get('text') for h in hadiths if h.get('hadithnumber') == 93), "NOT FOUND")
        h_269 = next((h.get('text') for h in hadiths if h.get('hadithnumber') == 269), "NOT FOUND")
        
        print(lang.upper() + ": Total=" + str(total) + ", Empty=" + str(empty_count))
        # print("  #93 (Jibril expected): " + str(bool(h_93.strip())))
        # print("  #269 (Jabir expected): " + str(bool(h_269.strip())))
    except Exception as e:
        print(lang.upper() + ": Error - " + str(e))