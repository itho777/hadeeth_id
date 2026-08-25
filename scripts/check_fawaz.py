import json
with open("../data/sources/fawaz_api/editions/eng-muslim.json", "r") as f:
    data = json.load(f)
    print("Total:", len(data['hadiths']))
    for h in data['hadiths'][:100]:
        if "Yahya b. Ya'mur" in h['text']:
            print("Found Yahya b. Ya'mur at ID:", h['hadithnumber'])