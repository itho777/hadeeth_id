import re
import io

SQL_FILE = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql'

with io.open(SQL_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if 'INSERT INTO "tema_ahmad"' in line:
            print("Found tema_ahmad insert line. First 100 chars:")
            print(line[:100])
            tuples = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            print("Regex matched {} tuples in this line.".format(len(tuples)))
            if tuples:
                print("First 3 tuples:", tuples[:3])
            break
