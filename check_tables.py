import sqlite3
conn = sqlite3.connect('scratch/lidwa_plaintext.db')
print([row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
