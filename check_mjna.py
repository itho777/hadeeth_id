import json, os

mjna_books = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni']
for b in mjna_books:
    ch_file = f'data/lidwa-chapters/{b}.json'
    ndjson_file = f'data/sources/mjna/{b}.ndjson'
    
    ch_exists = os.path.exists(ch_file)
    ndjson_exists = os.path.exists(ndjson_file)
    
    print(f"=== {b} ===")
    print(f"  chapter index: {ch_exists}")
    print(f"  mjna ndjson:   {ndjson_exists}")
    
    if ch_exists:
        with open(ch_file, 'r', encoding='utf-8') as f:
            d = json.load(f)
        chs = d.get('chapters', [])
        print(f"  id_source: {d.get('title_id_source', '???')}")
        print(f"  en_source: {d.get('title_en_source', '???')}")
        print(f"  chapters:  {len(chs)}")
        if chs:
            c0 = chs[0]
            print(f"  first ch title_ar: {c0.get('title_ar','')}")
            print(f"  first ch hadith_start: {c0.get('hadith_start','')}")
    
    if ndjson_exists:
        with open(ndjson_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
        try:
            row = json.loads(first_line)
            print(f"  ndjson keys: {list(row.keys())[:8]}")
        except:
            print("  ndjson first line parse error")
    print()
