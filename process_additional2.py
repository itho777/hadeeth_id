import json
import re
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

def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&#39;', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Load Syafii
syafii_data = []
with open('scratch/parsed_syafii.ndjson', 'r', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        if d['id']: syafii_data.append(d)

for d in syafii_data: d['terjemah'] = clean_html(d['terjemah'])

syafii_ara = []
syafii_ind = []
syafii_api = []
for d in syafii_data:
    hid = int(d['id'])
    syafii_ara.append({"hadithnumber": hid, "text": d['arab']})
    syafii_ind.append({"hadithnumber": hid, "text": d['terjemah']})
    syafii_api.append({
        "id": hid,
        "hadith_number": hid,
        "text_ar": d['arab'],
        "text_en": "",
        "text_id": d['terjemah'],
        "translations": {
            "id": [{"text": d['terjemah'], "source": "irsyadulibad", "source_name": "IrsyadulIbad"}],
            "ar": [{"text": d['arab'], "source": "irsyadulibad", "source_name": "IrsyadulIbad"}]
        }
    })

with open("data/editions/ara-syafii.ndjson", "w", encoding="utf-8") as f:
    for a in syafii_ara: f.write(json.dumps(a, ensure_ascii=False) + '\n')
with open("data/editions/ind-syafii.ndjson", "w", encoding="utf-8") as f:
    for a in syafii_ind: f.write(json.dumps(a, ensure_ascii=False) + '\n')
with open("data/api/syafii.ndjson", "w", encoding="utf-8") as f:
    for a in syafii_api: f.write(json.dumps(a, ensure_ascii=False) + '\n')

print(f"Wrote Syafii files ({len(syafii_api)} records).")

# Load Riyad
riyad_data = []
with open('scratch/parsed_riyad.ndjson', 'r', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        if d['id']: riyad_data.append(d)

for d in riyad_data: d['terjemah'] = clean_html(d['terjemah'])

fawaz_riyad = []
with open("data/editions/ara-riyad.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        fawaz_riyad.append(json.loads(line))

fawaz_docs = [normalize_arabic(h['text']) for h in fawaz_riyad]
fawaz_ids = [h['hadithnumber'] for h in fawaz_riyad]

sql_docs = [normalize_arabic(d['arab']) for d in riyad_data]
sql_ids = [int(d['id']) for d in riyad_data]

vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=1)
fawaz_matrix = vectorizer.fit_transform(fawaz_docs)
sql_matrix = vectorizer.transform(sql_docs)
sims = cosine_similarity(sql_matrix, fawaz_matrix)

matched = 0
sql_to_fawaz = {}
for i, sql_id in enumerate(sql_ids):
    best_idx = sims[i].argmax()
    score = float(sims[i][best_idx])
    if score >= 0.2:  # very low threshold because text might differ slightly
        sql_to_fawaz[sql_id] = fawaz_ids[best_idx]
        matched += 1

print(f"Matched {matched} out of {len(sql_ids)} Riyad hadiths to Fawazahmed")

ind_riyad_fawaz = []
api_riyad = []
with open("data/api/riyad.ndjson", "r", encoding="utf-8") as f:
    for line in f:
        api_riyad.append(json.loads(line))

sql_id_to_terjemah = {int(d['id']): d['terjemah'] for d in riyad_data}

for f_id in fawaz_ids:
    matched_sql_ids = [s for s, f in sql_to_fawaz.items() if f == f_id]
    if matched_sql_ids:
        terjemah = sql_id_to_terjemah[matched_sql_ids[0]]
        ind_riyad_fawaz.append({"hadithnumber": f_id, "text": terjemah})
        
        for r in api_riyad:
            if r['id'] == f_id or str(r['id']) == str(f_id):
                if 'translations' not in r: r['translations'] = {}
                if 'id' not in r['translations']: r['translations']['id'] = []
                if not any(t.get('source') == 'irsyadulibad' for t in r['translations']['id']):
                    r['translations']['id'].append({"text": terjemah, "source": "irsyadulibad", "source_name": "IrsyadulIbad"})
                r['text_id'] = terjemah
                break

with open("data/editions/ind-riyad.ndjson", "w", encoding="utf-8") as f:
    for a in ind_riyad_fawaz: f.write(json.dumps(a, ensure_ascii=False) + '\n')
    
with open("data/api/riyad.ndjson", "w", encoding="utf-8") as f:
    for a in api_riyad: f.write(json.dumps(a, ensure_ascii=False) + '\n')

print(f"Wrote ind-riyad.ndjson with {len(ind_riyad_fawaz)} translations, and updated data/api/riyad.ndjson")
