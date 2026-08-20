import sqlite3
import os
import re

db_path = 'lidwa_new.db'
sql_file = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql'

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
c = conn.cursor()

import io
print("Reading SQL file...")
with io.open(sql_file, 'r', encoding='utf-8') as f:
    sql_script = f.read()

print("Executing SQL script...")
# sqlite3.executescript is fast and handles multiple statements
try:
    c.executescript(sql_script)
    conn.commit()
    print("Database built successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()

conn.close()
