import sqlite3
db_path = "../scratch/lidwa_plaintext.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(datakitab_muslim)")
print([c[1] for c in cursor.fetchall()])
cursor.execute("SELECT * FROM datakitab_muslim LIMIT 1")
print(cursor.fetchone())