import sqlite3
db_path = "../data/sources/lidwa/lidwa.new.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(ind_2)")
print([c[1] for c in cursor.fetchall()])
cursor.execute("SELECT * FROM ind_2 WHERE NoHdt = 4672")
row = cursor.fetchone()
print(row)