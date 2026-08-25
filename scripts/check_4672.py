import sqlite3
import os

db_path = "../data/sources/lidwa/lidwa.new.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM derajat_muslim WHERE NoHdt = 4672")
print("Lidwa 4672:", cursor.fetchone())