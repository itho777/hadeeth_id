# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_api_chap2.txt", "w", "utf-8") as out:
    with open("../data/chapters/muslim.json", "r") as f:
        chapters = json.load(f)
        
    for ch in chapters[:2]:
        out.write(json.dumps(ch, indent=2) + "\n")