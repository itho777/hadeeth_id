import json
with open("../data/lidwa-chapters/muslim.json", "r") as f:
    data = json.load(f)
    if isinstance(data, dict):
        print("keys:", data.keys()[:5])
        print("Chap 1:", data.get("1"))
        print("Chap 2:", data.get("2"))
    else:
        print("Type:", type(data))