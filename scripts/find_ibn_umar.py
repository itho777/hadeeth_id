import json

data = json.load(open('data/rawis/active_rawis.min.json', encoding='utf-8'))

# Look for ibn umar (Abdullah ibn Umar) - he'd have id 19944 or similar
# Let's search by name
for k, v in data.items():
    en_name = v.get('en', '') or ''
    if 'Ibn' in en_name and 'Umar' in en_name and 'Abdullah' in en_name:
        with open('temp.txt', 'a', encoding='utf-8') as f:
            f.write(f"ID={k}: {json.dumps(v, ensure_ascii=False)[:300]}\n")
        break
