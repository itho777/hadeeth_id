# -*- coding: utf-8 -*-
import json

with open("../data/raw_baseline/ara-muslim.json", "r") as f:
    ara_data = json.load(f)

empty_ara = [h['hadithnumber'] for h in ara_data['hadiths'] if not h.get('text', '').strip()]
print("Max empty:", max(empty_ara))
empty_outside_muqaddimah = [x for x in empty_ara if x > 92]
print("Empty outside Muqaddimah:", len(empty_outside_muqaddimah))
if empty_outside_muqaddimah:
    print("Examples:", empty_outside_muqaddimah[:10])