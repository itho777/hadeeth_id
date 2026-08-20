import json
import os
import glob

# For all books, read the link graph, read the Lidwa NDJSON, and create a baked ind-{book}.json
books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad']

for book in books:
    link_path = f"data/links/{book}.json"
    lidwa_path = f"data/sources/lidwa/{book}.ndjson"
    
    if not os.path.exists(link_path) or not os.path.exists(lidwa_path):
        continue
        
    print(f"Baking {book}...")
    with open(link_path, 'r', encoding='utf-8') as f:
        link_graph = json.load(f)
        
    fawaz_to_lidwa = link_graph.get('fawaz_to_lidwa', {})
    
    lidwa_map = {}
    with open(lidwa_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            d = json.loads(line)
            num = str(d.get('hadith_number') or d.get('hadithnumber') or d.get('id'))
            if d.get('text_id'):
                lidwa_map[num] = d.get('text_id')
                
    ara_path = f"data/raw_baseline/ara-{book}.json"
    if not os.path.exists(ara_path):
        continue
        
    with open(ara_path, 'r', encoding='utf-8') as f:
        ara_data = json.load(f)
        
    baked_hadiths = []
    for ah in ara_data.get('hadiths', []):
        fawaz_num = str(ah.get('hadithnumber') or ah.get('id'))
        
        target_lidwa = fawaz_to_lidwa.get(fawaz_num)
        ind_text = ""
        if target_lidwa and target_lidwa in lidwa_map:
            ind_text = lidwa_map[target_lidwa]
            
        baked_hadiths.append({
            "hadithnumber": int(fawaz_num) if fawaz_num.isdigit() else fawaz_num,
            "text": ind_text,
            "grades": ah.get('grades', []),
            "reference": ah.get('reference', {}),
            "_linked_from_lidwa": target_lidwa
        })
        
    baked_data = {
        "metadata": ara_data.get("metadata", {}),
        "hadiths": baked_hadiths
    }
    
    out_path = f"data/raw_baseline/ind-{book}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(baked_data, f, ensure_ascii=False, indent=2)
        
print("Done baking!")
