import json

f = json.load(open('data/editions/eng-muslim.json', encoding='utf-8'))
f_h = next((h for h in f['hadiths'] if str(h['hadithnumber']) == '2883'), None)

ab = json.load(open('data/sources/ahmedbaset/by_book/the_9_books/muslim.json', encoding='utf-8'))['hadiths']

f_eng = f_h['text'].strip()[:100]

print(f"Searching for Fawaz ENG: {f_eng}")

found = []
for h in ab:
    if h.get('english') and h['english'].get('text') and f_eng in h['english']['text']:
        found.append(h['idInBook'])
        
print(f"Matched AB IDs using English text: {found}")
