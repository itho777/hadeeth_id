import json
with open("../data/sources/lidwa/muslim.json", "r") as f:
    data = json.load(f)
for h in data:
    if h['id'] == 4672:
        print(h['id'], h['arab'][:100])