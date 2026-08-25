import sqlite3
import os

db_path = "../data/sources/lidwa/lidwa.new.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM mapping_muslim WHERE NoHdt = 5362")
print("Lidwa 5362 maps to:", cursor.fetchall())

cursor.execute("SELECT * FROM mapping_muslim WHERE NoMapping > 3033 LIMIT 5")
print("High mappings:", cursor.fetchall())