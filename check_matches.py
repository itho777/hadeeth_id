import json

f = json.load(open('data/editions/ara-muslim.json', encoding='utf-8'))
l = json.load(open('data/sources/lidwa/muslim.json', encoding='utf-8'))

l_3942 = next((h for h in l if str(h['hadith_number']) == '3942'), None)
f_2883 = next((h for h in f['hadiths'] if str(h['hadithnumber']) == '2883'), None)

with open('scratch_matches.txt', 'w', encoding='utf-8') as out:
    out.write(f"Lidwa 3942 text snippet: {l_3942['text_ar'][:50]}\n")

    # Find which fawaz hadith matches Lidwa 3942's first 50 chars
    found_f = []
    for h in f['hadiths']:
        if l_3942['text_ar'][:50] in h['text']:
            found_f.append(h['hadithnumber'])

    out.write(f"Fawaz IDs matching Lidwa 3942's start: {found_f}\n")

    # Find which lidwa hadith matches Fawaz 2883's first 50 chars
    found_l = []
    for h in l:
        if f_2883['text'][:50] in h.get('text_ar', ''):
            found_l.append(h['hadith_number'])

    out.write(f"Lidwa IDs matching Fawaz 2883's start: {found_l}\n")
