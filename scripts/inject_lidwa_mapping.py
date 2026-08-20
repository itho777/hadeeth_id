import json
import re
import os

db_path = 'h:/Itho/2026/Project/Hadeeth/data source/lidwa/lidwa.new.db.sql'

books = {
    'bukhari': 'mapping_bukhari',
    'muslim': 'mapping_muslim',
    'abudawud': 'mapping_abudaud',
    'tirmidhi': 'mapping_tirmidzi',
    'nasai': 'mapping_nasai',
    'ibnmajah': 'mapping_ibnumajah',
    'malik': 'mapping_malik',
    'darimi': 'mapping_darimi',
    'ahmad': 'mapping_ahmad'
}

mappings = {b: {} for b in books}

print("Parsing SQL dump...")
with open(db_path, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.startswith("INSERT INTO \"mapping_"):
            continue
            
        for book_slug, table_name in books.items():
            if f'"{table_name}"' in line:
                m = re.search(r'VALUES \((.*?)\);', line)
                if m:
                    parts = m.group(1).split(',')
                    if len(parts) >= 2:
                        lidwa_id = parts[0].strip()
                        intl_id = parts[1].strip()
                        
                        if intl_id != '0' and lidwa_id != '0':
                            # fawaz_to_lidwa maps fawaz (intl) -> lidwa
                            mappings[book_slug][intl_id] = lidwa_id
                break

for book_slug, sql_map in mappings.items():
    link_path = f'data/links/{book_slug}.json'
    if not os.path.exists(link_path):
        graph = {'fawaz_to_lidwa': {}}
    else:
        with open(link_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)
            
    if 'fawaz_to_lidwa' not in graph:
        graph['fawaz_to_lidwa'] = {}
        
    old_count = len(graph['fawaz_to_lidwa'])
    
    # Merge! The SQL internal mapping takes precedence
    for intl_id, lidwa_id in sql_map.items():
        graph['fawaz_to_lidwa'][intl_id] = lidwa_id
        
    new_count = len(graph['fawaz_to_lidwa'])
    print(f"[{book_slug}] SQL provided {len(sql_map)} mappings. Total grew from {old_count} to {new_count}")
    
    with open(link_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

print("Done updating data/links/*.json")
