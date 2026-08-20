import re

# Update js/app.js
text = open('js/app.js', encoding='utf-8').read()
text = text.replace('AR/ID: IrsyadulIbad / Lidwa SQL (1,800 entries)', 'AR/ID: IrsyadulIbad (1,800 entries)')
text = text.replace('AR/ID: SQL Lidwa / IrsyadulIbad (1.800 entri)', 'AR/ID: IrsyadulIbad (1.800 entri)')
open('js/app.js', 'w', encoding='utf-8').write(text)

# Update data/lidwa-chapters/syafii.json
import json
ch = json.load(open('data/lidwa-chapters/syafii.json', encoding='utf-8'))
ch['title_en_source'] = 'IrsyadulIbad'
ch['title_id_source'] = 'IrsyadulIbad'
json.dump(ch, open('data/lidwa-chapters/syafii.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
