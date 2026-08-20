import json
import re

def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&quot;', '\"').replace('&#39;', '\'')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

syafii_data = []
with open('scratch/parsed_syafii.ndjson', 'r', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        if d['id']: syafii_data.append(d)
print("Syafii valid records:", len(syafii_data))

riyad_data = []
with open('scratch/parsed_riyad.ndjson', 'r', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        if d['id']: riyad_data.append(d)
print("Riyad valid records:", len(riyad_data))
