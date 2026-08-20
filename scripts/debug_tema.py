import re
import io

SQL_FILE = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql'

with io.open(SQL_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if 'INSERT INTO "tema_ahmad"' in line:
            print("tema_ahmad inserts:")
            # get all tuples
            tuples = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            print("First 10 tuples:", tuples[:10])
            break
