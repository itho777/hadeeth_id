import re
import json

def parse_sql(sql_file, out_file):
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the INSERT INTO statement
    # Format: INSERT INTO `table` (`id`, `kitab`, `arab`, `terjemah`) VALUES (1, '...', '...', '...'), (2, ...);
    
    match = re.search(r'INSERT INTO `[^`]+` \([^)]+\) VALUES\s*(.+);', content, re.DOTALL | re.IGNORECASE)
    if not match:
        print(f"No INSERT INTO found in {sql_file}")
        return

    values_str = match.group(1)
    
    # We need a robust parser for SQL values, because the strings contain escaped quotes
    import csv
    
    # Replace ( and ) with [ and ] to make it valid JSON array of arrays? No, single quotes.
    # Better: use a state machine to extract tuples
    
    records = []
    
    state = 'WAIT_TUPLE'
    current_tuple = []
    current_val = ""
    in_string = False
    escape = False
    
    for i, c in enumerate(values_str):
        if state == 'WAIT_TUPLE':
            if c == '(':
                state = 'IN_TUPLE'
                current_tuple = []
                current_val = ""
        elif state == 'IN_TUPLE':
            if in_string:
                if escape:
                    current_val += c
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == "'":
                    in_string = False
                else:
                    current_val += c
            else:
                if c == "'":
                    in_string = True
                elif c == ',':
                    current_tuple.append(current_val.strip())
                    current_val = ""
                elif c == ')':
                    current_tuple.append(current_val.strip())
                    records.append(current_tuple)
                    state = 'WAIT_TUPLE'
                elif c.isdigit() or c == '.' or c == '-':
                    current_val += c
                else:
                    pass # ignore whitespace
                    
    print(f"Parsed {len(records)} records from {sql_file}")
    
    with open(out_file, 'w', encoding='utf-8') as out:
        for r in records:
            if len(r) >= 4:
                obj = {
                    "id": r[0],
                    "kitab": r[1],
                    "arab": r[2].replace('\\r', '\r').replace('\\n', '\n'),
                    "terjemah": r[3].replace('\\r', '\r').replace('\\n', '\n')
                }
                out.write(json.dumps(obj, ensure_ascii=False) + "\n")

parse_sql("scratch/hadits-database/musnad-syafii.sql", "scratch/parsed_syafii.ndjson")
parse_sql("scratch/hadits-database/riyadhus-shalihin.sql", "scratch/parsed_riyad.ndjson")
