import json
with open("../data/api/muslim.ndjson", "r") as f:
    fawaz_only = 0
    ahmed_only = 0
    for line in f:
        obj = json.loads(line)
        en_srcs = [t.get('source') for t in obj['translations'].get('en', [])]
        if 'fawazahmed' in en_srcs and 'ahmedbaset' not in en_srcs:
            fawaz_only += 1
        elif 'ahmedbaset' in en_srcs:
            ahmed_only += 1
    print("Fawaz only:", fawaz_only)
    print("Ahmedbaset:", ahmed_only)