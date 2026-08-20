import json
f = json.load(open('data/editions/ara-muslim.json', encoding='utf-8'))
f_h = next((h for h in f['hadiths'] if str(h['hadithnumber']) == '2883'), None)
l = json.load(open('data/sources/lidwa/muslim.json', encoding='utf-8'))
l_h = next((h for h in l if str(h['hadith_number']) == '3942'), None)
with open('scratch_check.txt', 'w', encoding='utf-8') as out:
    out.write(f"FAWAZ 2883 MATAN:\n{f_h['text'][:200] if f_h else 'Not Found'}\n\n")
    out.write(f"LIDWA 3942 MATAN:\n{l_h['text_ar'][:200] if l_h else 'Not Found'}\n")
