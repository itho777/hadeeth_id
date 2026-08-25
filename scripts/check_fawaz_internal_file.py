import json

with open("../data/sources/fawaz_api/editions/ara-muslim.json", "r", encoding="utf-8") as f:
    ara = json.load(f)
with open("../data/sources/fawaz_api/editions/eng-muslim.json", "r", encoding="utf-8") as f:
    eng = json.load(f)

with open("fawaz_test.txt", "w", encoding="utf-8") as out:
    for h in ara['hadiths']:
        if h['hadithnumber'] in [1, 93]:
            out.write(f"ARA {h['hadithnumber']}: {h.get('text', '')[:100]}\n")
            
    for h in eng['hadiths']:
        if h['hadithnumber'] in [1, 93]:
            out.write(f"ENG {h['hadithnumber']}: {h.get('text', '')[:100]}\n")