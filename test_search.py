import sqlite3

conn = sqlite3.connect('scratch/lidwa_plaintext.db')
cursor = conn.cursor()

cursor.execute("SELECT imam, NoHdt FROM had_agregat WHERE Isi_Arab LIKE '%عثمان بن محمد%' LIMIT 10")
for r in cursor.fetchall():
    print(r)
