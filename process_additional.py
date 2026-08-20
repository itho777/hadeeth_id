import re
import json
import os
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def normalize_arabic(text):
    if not text: return ""
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)   # strip tashkeel
    text = re.sub(r'\u0640', '', text)                          # strip tatweel
    text = re.sub(r'[\u0625\u0623\u0622\u0627]', '\u0627', text)  # normalize alef
    text = re.sub(r'[\u064A\u0649]', '\u064A', text)             # normalize yaa
    text = re.sub(r'[\u0629\u0647]', '\u0647', text)             # normalize taa marbuta
    text = re.sub(r'\u0624', '\u0648', text)                     # normalize hamza-waw
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_mysql_dump(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We will just find all occurrences of `(\d+), '(.*?)', '(.*?)', '(.*?)'` ?
    # That's hard because arab and terjemah contain single quotes.
    # Better: use sqlparse or just manually split by `),\n(`
    
    match = re.search(r'INSERT INTO `[^`]+` \([^)]+\) VALUES\s*(.+);', content, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
        
    values_str = match.group(1).strip()
    if values_str.startswith('(') and values_str.endswith(')'):
        values_str = values_str[1:-1]
        
    # Split by `),(` or `),\n(`
    # But wait, text might contain `),(`
    # Let's write a simple state machine to parse MySQL tuples
    records = []
    state = 'VAL'
    curr_tuple = []
    curr_str = ""
    in_str = False
    escape = False
    
    for c in values_str:
        if state == 'VAL':
            if in_str:
                if escape:
                    curr_str += c
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == "'":
                    in_str = False
                else:
                    curr_str += c
            else:
                if c == "'":
                    in_str = True
                elif c == ',':
                    curr_tuple.append(curr_str.strip())
                    curr_str = ""
                elif c == ')':
                    curr_tuple.append(curr_str.strip())
                    records.append(curr_tuple)
                    curr_tuple = []
                    curr_str = ""
                    state = 'WAIT_NEXT'
                elif c.isdigit():
                    curr_str += c
        elif state == 'WAIT_NEXT':
            if c == '(':
                state = 'VAL'

    parsed = []
    for r in records:
        if len(r) >= 4:
            parsed.append({
                "id": int(r[0]),
                "arab": r[2].replace('\\r', '\r').replace('\\n', '\n'),
                "terjemah": r[3].replace('\\r', '\r').replace('\\n', '\n')
            })
    return parsed

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator='\n').strip()

print("Parsing Syafii...")
syafii_data = parse_mysql_dump("scratch/hadits-database/musnad-syafii.sql")
print(f"Parsed {len(syafii_data)} from Syafii")

print("Parsing Riyad...")
riyad_data = parse_mysql_dump("scratch/hadits-database/riyadhus-shalihin.sql")
print(f"Parsed {len(riyad_data)} from Riyad")

# Clean HTML
for d in syafii_data: d['terjemah'] = clean_html(d['terjemah'])
for d in riyad_data: d['terjemah'] = clean_html(d['terjemah'])

# 1. Process Syafii (No Fawazahmed equivalent, so we make it standalone)
syafii_ara = []
syafii_ind = []
syafii_api = []
for d in syafii_data:
    hid = d['id']
    syafii_ara.append({"hadithnumber": hid, "text": d['arab']})
    syafii_ind.append({"hadithnumber": hid, "text": d['terjemah']})
    syafii_api.append({
        "id": hid,
        "hadith_number": hid,
        "text_ar": d['arab'],
        "text_en": "",
        "text_id": d['terjemah'],
        "translations": {
            "id": [{"text": d['terjemah'], "source": "irsyadulibad"}],
            "ar": [{"text": d['arab'], "source": "irsyadulibad"}]
        }
    })

with open("data/editions/ara-syafii.ndjson", "w", encoding="utf-8") as f:
    for a in syafii_ara: f.write(json.dumps(a, ensure_ascii=False) + '\n')
with open("data/editions/ind-syafii.ndjson", "w", encoding="utf-8") as f:
    for a in syafii_ind: f.write(json.dumps(a, ensure_ascii=False) + '\n')
with open("data/api/syafii.ndjson", "w", encoding="utf-8") as f:
    for a in syafii_api: f.write(json.dumps(a, ensure_ascii=False) + '\n')

print("Wrote Syafii files.")

# 2. Process Riyad (Match to Fawazahmed)
fawaz_riyad = []
with open("data/editions/ara-riyad.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        fawaz_riyad.append(json.loads(line))

fawaz_docs = [normalize_arabic(h['text']) for h in fawaz_riyad]
fawaz_ids = [h['hadithnumber'] for h in fawaz_riyad]

sql_docs = [normalize_arabic(d['arab']) for d in riyad_data]
sql_ids = [d['id'] for d in riyad_data]

vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=1)
fawaz_matrix = vectorizer.fit_transform(fawaz_docs)
sql_matrix = vectorizer.transform(sql_docs)
sims = cosine_similarity(sql_matrix, fawaz_matrix)

matched = 0
sql_to_fawaz = {}
for i, sql_id in enumerate(sql_ids):
    best_idx = sims[i].argmax()
    score = float(sims[i][best_idx])
    if score >= 0.4:  # threshold
        sql_to_fawaz[sql_id] = fawaz_ids[best_idx]
        matched += 1

print(f"Matched {matched} out of {len(sql_ids)} Riyad hadiths to Fawazahmed")

# Now inject the Indonesian translations into data/editions/ind-riyad.ndjson
# using the Fawazahmed numbering!
ind_riyad_fawaz = []
# Also update data/api/riyad.ndjson
api_riyad = []
with open("data/api/riyad.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        api_riyad.append(json.loads(line))

# Map sql id to terjemah
sql_id_to_terjemah = {d['id']: d['terjemah'] for d in riyad_data}

# For every fawaz id, if we have a match, output the terjemah
for f_id in fawaz_ids:
    # find sql_id that matched this f_id
    # note: there could be multiple sql_ids matching same f_id, take first
    matched_sql_ids = [s for s, f in sql_to_fawaz.items() if f == f_id]
    if matched_sql_ids:
        terjemah = sql_id_to_terjemah[matched_sql_ids[0]]
        ind_riyad_fawaz.append({"hadithnumber": f_id, "text": terjemah})
        
        # update API
        for r in api_riyad:
            if r['id'] == f_id or str(r['id']) == str(f_id):
                if 'translations' not in r: r['translations'] = {}
                if 'id' not in r['translations']: r['translations']['id'] = []
                # Check if irsyadulibad is already there
                if not any(t.get('source') == 'irsyadulibad' for t in r['translations']['id']):
                    r['translations']['id'].append({"text": terjemah, "source": "irsyadulibad", "source_name": "IrsyadulIbad"})
                r['text_id'] = terjemah
                break

with open("data/editions/ind-riyad.ndjson", "w", encoding="utf-8") as f:
    for a in ind_riyad_fawaz: f.write(json.dumps(a, ensure_ascii=False) + '\n')
    
with open("data/api/riyad.ndjson", "w", encoding="utf-8") as f:
    for a in api_riyad: f.write(json.dumps(a, ensure_ascii=False) + '\n')

print(f"Wrote ind-riyad.ndjson with {len(ind_riyad_fawaz)} translations, and updated data/api/riyad.ndjson")
