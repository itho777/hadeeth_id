import json

idx = json.load(open('data/rawis/scholars_index.json', encoding='utf-8'))

# Check first few entries
for k in list(idx.keys())[:3]:
    entry = idx[k]
    with open('temp.txt', 'a', encoding='utf-8') as f:
        f.write(f"{k}: {json.dumps(entry, ensure_ascii=False)}\n")

# Also search for ibn umar by name
for k, v in idx.items():
    if isinstance(v, dict) and 'umar' in str(v.get('name', '')).lower():
        with open('temp.txt', 'a', encoding='utf-8') as f:
            f.write(f"MATCH id={k}: {json.dumps(v, ensure_ascii=False)[:200]}\n")
        break
