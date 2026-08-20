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

# The sql file has: INSERT INTO "mapping_bukhari" VALUES (1351,1442,1);
# NoHdt = Lidwa ID
# NoMapping = International ID
# So fawaz (International) -> Lidwa: fawaz_to_lidwa[international_id] = lidwa_id

fawaz_to_lidwa = {}

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
                        
                        # In the SQL, Darimi or others might be different, but assuming NoHdt, NoMapping
                        if intl_id != '0' and lidwa_id != '0':
                            key = f"{book_slug}_{intl_id}"
                            # If multiple International map to one Lidwa or vice-versa
                            # Usually 1 fawaz ID maps to 1 Lidwa ID.
                            fawaz_to_lidwa[key] = lidwa_id
                break

print(f"Extracted {len(fawaz_to_lidwa)} mappings from Lidwa SQL.")

# Load existing link_graph
graph_path = 'data/link_graph.json'
if os.path.exists(graph_path):
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)
else:
    graph = {'fawaz_to_lidwa': {}}

# The user wants both to be taken into account. The internal mapping should override text matching.
old_count = len(graph['fawaz_to_lidwa'])

# We merge them! 
for k, v in fawaz_to_lidwa.items():
    graph['fawaz_to_lidwa'][k] = v

new_count = len(graph['fawaz_to_lidwa'])
print(f"Merged! Link graph went from {old_count} to {new_count} entries.")

with open(graph_path, 'w', encoding='utf-8') as f:
    json.dump(graph, f)

print("Done updating data/link_graph.json")
