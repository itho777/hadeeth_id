import json
with open("../data/sources/fawaz_api/editions/ara-muslim.json", "r") as f:
    ara = json.load(f)
for h in ara['hadiths']:
    if h['hadithnumber'] == 93:
        print("ARA ID 93:", h['text'])