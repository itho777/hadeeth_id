import re
import io

SQL_FILE = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql'

count = 0
with io.open(SQL_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if 'INSERT INTO "tema_ahmad"' in line:
            tuples = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            for t in tuples:
                print(t)
                count += 1
                if count >= 20:
                    break
        if count >= 20:
            break
