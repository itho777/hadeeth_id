import json
import re

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
    text = re.sub(r'[Ø¥Ø£Ø¢Ø§]', 'Ø§', text)
    text = re.sub(r'[\W_]+', '', text)
    return text

f = json.load(open('data/editions/ara-muslim.json', encoding='utf-8'))
f_h = next((h for h in f['hadiths'] if str(h['hadithnumber']) == '2883'), None)

l = json.load(open('data/sources/lidwa/muslim.json', encoding='utf-8'))

f_norm = normalize_arabic(f_h['text'])
suffix = f_norm[-80:]

with open('scratch_suffix.txt', 'w', encoding='utf-8') as out:
    out.write(f"Searching for Fawaz 2883 Suffix: {suffix}\n")

    found = []
    for h in l:
        l_norm = normalize_arabic(h.get('text_ar', ''))
        if suffix in l_norm:
            found.append(h['hadith_number'])
            
    out.write(f"Matched Lidwa IDs using 80-char Suffix: {found}\n")
