import json

with open("../data/sources/fawaz_api/editions/ara-muslim.json", "r", encoding="utf-8") as f:
    ara = json.load(f)
with open("../data/sources/fawaz_api/editions/eng-muslim.json", "r", encoding="utf-8") as f:
    eng = json.load(f)

for h in ara['hadiths']:
    if h['hadithnumber'] == 93:
        print("ARA ID 93:", h.get('text', '')[:100].encode('ascii', 'ignore').decode('ascii'))

for h in eng['hadiths']:
    if h['hadithnumber'] == 93:
        print("ENG ID 93:", h.get('text', '')[:100].encode('ascii', 'ignore').decode('ascii'))