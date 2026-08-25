import json
with open("../data/sources/fawaz_api/editions/eng-muslim.json", "r") as f:
    data = json.load(f)
    print("Fawaz 7563:", data['hadiths'][7562]['text'][:100].replace('\n', ' '))