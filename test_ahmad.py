import json
f = open('data/api/ahmad/lidwa.json', 'r', encoding='utf-8')
data = json.load(f)

for k, v in data.items():
    if v['chapter_id'] == 'ahmad_c5':
        print(v['id'])
        break
