import sqlite3
import os

sql_file = r"H:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.new.db.sql"
db_file = r"G:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id\scratch\lidwa_plaintext.db"

if os.path.exists(db_file):
    os.remove(db_file)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print(f"Reading {sql_file}...")
with open(sql_file, 'r', encoding='utf-8') as f:
    sql_script = f.read()

print("Executing SQL script...")
try:
    cursor.executescript(sql_script)
    conn.commit()
    print("Database created successfully!")
except Exception as e:
    print(f"Error during execution: {e}")
