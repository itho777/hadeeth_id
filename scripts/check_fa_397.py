import json
with open("../data/sources/fawaz_api/editions/eng-muslim.json", "r", encoding="utf-8") as f:
    eng = json.load(f)
print("Fawaz ENG 397:", eng['hadiths'][396]['text'][:200])