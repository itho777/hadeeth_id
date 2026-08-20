import json

data = json.load(open('data/rawis/active_rawis.min.json', encoding='utf-8'))

# Check the 'counts' field structure for a few entries
for k, v in list(data.items())[:5]:
    counts = v.get('counts', '')
    with open('temp.txt', 'a', encoding='utf-8') as f:
        f.write(f"ID={k}: counts={counts!r}\n")
