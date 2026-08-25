import json
with open("../data/raw_baseline/eng-muslim.json", "r") as f:
    data = json.load(f)

for h in data["hadiths"][:5]:
    print("Hadith " + str(h.get('hadithnumber')) + ": " + h.get('text')[:100].replace('\n', ' '))
    
for h in data["hadiths"][90:95]:
    print("Hadith " + str(h.get('hadithnumber')) + ": " + h.get('text')[:100].replace('\n', ' '))