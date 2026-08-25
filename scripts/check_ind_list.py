import sqlite3
db_path = "../scratch/lidwa_plaintext.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM ind_list")
print(cursor.fetchall())