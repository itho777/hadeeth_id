import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load AhmedBaset reference
print("Loading AhmedBaset reference...")
url = 'https://raw.githubusercontent.com/AhmedBaset/hadith-json/main/db/by_book/the_9_books/muslim.json'
with urllib.request.urlopen(url) as r:
    ref = json.load(r)

# We want to patch hadithnumber 9 to 92 in our dataset
# In our dataset, Chapter 1 (Iman) starts at hadithnumber 8.
# In AhmedBaset, Chapter 1 (Iman) starts at idInBook 1.
# So our_id = their_id + 7.
# We need their_id 2 to 85 to patch our_id 9 to 92.

ref_map = {}
for h in ref['hadiths']:
    if h['chapterId'] == 1 and 2 <= h['idInBook'] <= 85:
        our_id = h['idInBook'] + 7
        ref_map[our_id] = h

# Load our datasets
with open('data/editions/ara-muslim.json', encoding='utf-8') as f:
    ara = json.load(f)

with open('data/editions/eng-muslim.json', encoding='utf-8') as f:
    eng = json.load(f)

# Patch ara-muslim
for h in ara['hadiths']:
    if 9 <= h['hadithnumber'] <= 92:
        h['text'] = ref_map[h['hadithnumber']]['arabic']

# Patch eng-muslim
for h in eng['hadiths']:
    if 9 <= h['hadithnumber'] <= 92:
        h['text'] = ref_map[h['hadithnumber']]['english']

# Save back
with open('data/editions/ara-muslim.json', 'w', encoding='utf-8') as f:
    json.dump(ara, f, ensure_ascii=False, indent=2)

with open('data/editions/eng-muslim.json', 'w', encoding='utf-8') as f:
    json.dump(eng, f, ensure_ascii=False, indent=2)

print("Successfully patched ara-muslim.json and eng-muslim.json for hadiths 9-92.")
