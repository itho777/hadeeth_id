import json
with open("../data/raw_baseline/ara-muslim.json", "r") as f:
    data = json.load(f)
    print("Total hadiths:", len(data["hadiths"]))
    # Let's count how many have hadithnumber < 8
    # Actually just print the first 10 hadiths
    for h in data["hadiths"][:10]:
        print("Hadith:", h["hadithnumber"])