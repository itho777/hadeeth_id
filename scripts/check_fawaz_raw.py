import json
with open("../data/sources/fawazahmed/eng-muslim.json", "r") as f:
    data = json.load(f)
    print("Fawaz eng-muslim total:", len(data['hadiths']))
    for h in data['hadiths']:
        if h['hadithnumber'] in [8, 93]:
            print("ID:", h['hadithnumber'], "| Text:", h['text'][:100].replace('\n', ' '))