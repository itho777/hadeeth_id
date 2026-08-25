# -*- coding: utf-8 -*-
import json
with open("../data/chapters/muslim.json", "r") as f:
    chapters = json.load(f)
total = sum([ch.get('hadith_count', 0) for ch in chapters])
print("Total count in chapters API: " + str(total))