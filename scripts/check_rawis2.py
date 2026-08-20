import json

data = json.load(open('data/rawis/active_rawis.min.json', encoding='utf-8'))
sample = list(data.values())[:1][0]
with open('temp.txt', 'w', encoding='utf-8') as f:
    f.write("KEYS: " + str(list(sample.keys())) + "\n")
    f.write("SAMPLE: " + json.dumps(sample, ensure_ascii=False)[:400] + "\n")
