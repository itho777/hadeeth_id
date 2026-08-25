import json
with open("../data/links/muslim.json", "r") as f:
    data = json.load(f)
    print("Links count:", len(data))
    print("Link for 8:", data.get('8'))
    print("Link for 93:", data.get('93'))