import json
with open("../data/sources/fawaz_api/editions/ara-muslim.json", "r", encoding="utf-8") as f:
    ara = json.load(f)
print("Fawaz AR 1:", ara['hadiths'][0]['text'])