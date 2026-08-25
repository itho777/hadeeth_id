import sqlite3
db_path = "../scratch/lidwa_plaintext.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM muslim WHERE id = 4672")
row = cursor.fetchone()
print(row[3][:100]) # EN or ID