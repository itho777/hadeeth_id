# -*- coding: utf-8 -*-
import json

with open("../data/raw_baseline/ara-muslim.json", "r") as f:
    ara_data = json.load(f)

empty_ara = [h['hadithnumber'] for h in ara_data['hadiths'] if not h.get('text', '').strip()]

with open("../data/raw_baseline/eng-muslim.json", "r") as f:
    eng_data = json.load(f)

empty_eng = [h['hadithnumber'] for h in eng_data['hadiths'] if not h.get('text', '').strip()]

print("Empty in Ara:", len(empty_ara))
print("Empty in Eng:", len(empty_eng))
print("Are they exactly the same gaps?", empty_ara == empty_eng)
if len(empty_ara) > 0:
    print("Example empty Ara:", empty_ara[:20])