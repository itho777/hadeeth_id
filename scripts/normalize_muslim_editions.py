"""
Normalize Muslim edition JSON files to the standard format.

Standard format: {metadata: {...}, hadiths: [{hadithnumber: N, arabicnumber: N, text: "...", grades: [...]}]}

Issues found:
- ara-muslim.json: uses 'id' instead of 'hadithnumber'
- eng-muslim.json: uses 'id' instead of 'hadithnumber', many empty text entries
- ind-muslim.json: flat list [{id, terjemah, sanad}], NOT wrapped in {hadiths: [...]}
"""
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

editions_dir = 'data/editions'

# ── 1. ara-muslim.json ─────────────────────────────────────────────────────────
print("Processing ara-muslim.json ...")
with open(os.path.join(editions_dir, 'ara-muslim.json'), 'r', encoding='utf-8') as f:
    ara = json.load(f)

# It already has {metadata, hadiths} wrapper, but uses 'id' instead of 'hadithnumber'
for h in ara['hadiths']:
    if 'hadithnumber' not in h and 'id' in h:
        h['hadithnumber'] = h['id']

with open(os.path.join(editions_dir, 'ara-muslim.json'), 'w', encoding='utf-8') as f:
    json.dump(ara, f, ensure_ascii=False, separators=(',', ':'))

print(f"  -> {len(ara['hadiths'])} hadiths normalized. Sample: hadithnumber={ara['hadiths'][0]['hadithnumber']}")


# ── 2. eng-muslim.json ─────────────────────────────────────────────────────────
print("Processing eng-muslim.json ...")
with open(os.path.join(editions_dir, 'eng-muslim.json'), 'r', encoding='utf-8') as f:
    eng = json.load(f)

for h in eng['hadiths']:
    if 'hadithnumber' not in h and 'id' in h:
        h['hadithnumber'] = h['id']

with open(os.path.join(editions_dir, 'eng-muslim.json'), 'w', encoding='utf-8') as f:
    json.dump(eng, f, ensure_ascii=False, separators=(',', ':'))

print(f"  -> {len(eng['hadiths'])} hadiths normalized. Sample: hadithnumber={eng['hadiths'][0]['hadithnumber']}")


# ── 3. ind-muslim.json ─────────────────────────────────────────────────────────
print("Processing ind-muslim.json ...")
with open(os.path.join(editions_dir, 'ind-muslim.json'), 'r', encoding='utf-8') as f:
    ind_raw = json.load(f)

if isinstance(ind_raw, list):
    # Convert flat list to standard format
    normalized_hadiths = []
    for h in ind_raw:
        normalized_hadiths.append({
            'hadithnumber': h['id'],
            'arabicnumber': h.get('arabicnumber', h['id']),
            'text': h.get('terjemah', ''),
            'sanad': h.get('sanad', ''),
            'grades': h.get('grades', [])
        })
    
    ind_normalized = {
        'metadata': {
            'name': 'Sahih Muslim',
            'sections': {},
            'last_hadithnumber': normalized_hadiths[-1]['hadithnumber'] if normalized_hadiths else 0
        },
        'hadiths': normalized_hadiths
    }
    
    with open(os.path.join(editions_dir, 'ind-muslim.json'), 'w', encoding='utf-8') as f:
        json.dump(ind_normalized, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"  -> Converted list of {len(ind_raw)} entries to {{hadiths}} format.")
    print(f"     Sample: hadithnumber={normalized_hadiths[0]['hadithnumber']}, text={normalized_hadiths[0]['text'][:80]}")
else:
    # Already dict, just normalize id -> hadithnumber
    for h in ind_raw['hadiths']:
        if 'hadithnumber' not in h and 'id' in h:
            h['hadithnumber'] = h['id']
    with open(os.path.join(editions_dir, 'ind-muslim.json'), 'w', encoding='utf-8') as f:
        json.dump(ind_raw, f, ensure_ascii=False, separators=(',', ':'))
    print(f"  -> Already dict, normalized id->hadithnumber for {len(ind_raw['hadiths'])} entries.")


# ── 4. Verify all Muslim editions ──────────────────────────────────────────────
print()
print("Verification:")
for fname in ['ara-muslim.json', 'eng-muslim.json', 'ind-muslim.json']:
    fpath = os.path.join(editions_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    is_dict = isinstance(data, dict)
    has_hadiths = is_dict and 'hadiths' in data
    if has_hadiths:
        first = data['hadiths'][0]
        has_hadithnumber = 'hadithnumber' in first
        print(f"  {fname}: OK dict={is_dict}, has_hadiths={has_hadiths}, has_hadithnumber={has_hadithnumber}, count={len(data['hadiths'])}")
    else:
        print(f"  {fname}: PROBLEM! is_dict={is_dict}, has_hadiths={has_hadiths}")

print()
print("Done.")
