import json
with open("../data/api/chapters/muslim.json", "r") as f:
    ch = json.load(f)
    print("Chap 0:", ch[0])
    print("Chap 1:", ch[1])