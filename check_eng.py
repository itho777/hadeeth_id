import json

f = json.load(open('data/editions/eng-muslim.json', encoding='utf-8'))
f_h = next((h for h in f['hadiths'] if str(h['hadithnumber']) == '2883'), None)

ab = json.load(open('data/sources/ahmedbaset/by_book/the_9_books/muslim.json', encoding='utf-8'))['hadiths']
ab_h = next((h for h in ab if str(h['idInBook']) == '3001'), None)

with open('scratch_eng.txt', 'w', encoding='utf-8') as out:
    out.write(f"FAWAZ 2883 ENG:\n{f_h['text'][:300] if f_h else 'Not Found'}\n\n")
    if ab_h and ab_h.get('english'):
        out.write(f"AB 3001 ENG:\n{ab_h['english']['text'][:300]}\n")
    else:
        out.write("AB 3001 ENG: Not Found\n")
