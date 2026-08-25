import sqlite3
import os

db_path = "../data/sources/lidwa/lidwa.new.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(mapping_muslim)")
print("mapping_muslim cols:", [c[1] for c in cursor.fetchall()])

cursor.execute("SELECT * FROM mapping_muslim LIMIT 2")
print("mapping_muslim sample:", cursor.fetchall())