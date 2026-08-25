import json
with open("../data/meta/fawaz_editions.json", "r") as f:
    d = json.load(f)
    print("bukhari keys:", d["bukhari"].keys())
    print("bukhari eng:", d["bukhari"]["eng"][0])