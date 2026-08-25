import sqlite3
import os

db_path = "../data/sources/lidwa/lidwa.new.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM mapping_muslim WHERE NoHdt IN (9, 10, 135, 5362)")
print("Mappings:", cursor.fetchall())