import json
import re

html = open('scholars.html', 'r', encoding='utf-8').read()
scholars_in_html = re.findall(r"id:\s*'([^']+)',\s*name_en:\s*\"([^\"]+)\"", html)

rawis = json.load(open('data/rawis/active_rawis.min.json', 'r', encoding='utf-8'))
rawi_names_en = {v.get('name_en'): v.get('name_ar') for k, v in rawis.items() if v.get('name_en')}
rawi_names_en_lower = {k.lower(): v for k, v in rawi_names_en.items()}

missing = []
for scholar_id, name_en in scholars_in_html:
    ar_name = rawi_names_en.get(name_en) or rawi_names_en_lower.get(name_en.lower())
    if not ar_name:
        missing.append((scholar_id, name_en))

print("Missing in active_rawis:", missing)
