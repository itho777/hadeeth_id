import json
with open("../data/meta/fawaz_editions.json", "r") as f:
    d = json.load(f)
    print("bukhari keys:", d["bukhari"].keys())
    print("bukhari collection length:", len(d["bukhari"]["collection"]))
    print("bukhari collection[0]:", d["bukhari"]["collection"][0])