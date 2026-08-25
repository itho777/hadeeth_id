# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_jabir.txt", "w", "utf-8") as out:
    with open("../data/raw_baseline/eng-muslim.json", "r") as f:
        eng_data = json.load(f)
        for h in eng_data['hadiths']:
            if h.get('text') and "guarantee" in h.get('text').lower() and "jabir" in h.get('text').lower():
                out.write("Found at Fawaz: " + str(h.get('hadithnumber')) + "\n")
                out.write(h.get('text')[:200].replace('\n', ' ') + "\n")
                
    with open("../data/raw_baseline/ara-muslim.json", "r") as f:
        ara_data = json.load(f)
        for h in ara_data['hadiths']:
            if h.get('hadithnumber') == 269: # If it's 269
                out.write("Ara 269: " + h.get('text')[:200].replace('\n', ' ') + "\n")