import re
import io

SQL_FILE = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql'

with io.open(SQL_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if 'INSERT INTO "datakitab_ahmad"' in line:
            # Find the ID
            matches = re.findall(r'\((\d+),\s*\'(.*?)\',\s*\'(.*?)\',\s*(.*?)\)', line)
            print("Matched Kitab IDs:", [m[0] for m in matches])
