import json
import os

in_file = 'data/sources/lidwa/syafii.ndjson'
out_file = 'data/api/syafii.ndjson'

with open(in_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(out_file, 'w', encoding='utf-8') as f:
    for line in lines:
        data = json.loads(line)
        data['id'] = str(data['hadith_number'])
        data['chapter_id'] = "1"
        if 'text_en' not in data:
            data['text_en'] = ""
        f.write(json.dumps(data, ensure_ascii=False) + '\n')
