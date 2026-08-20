import sqlite3
conn = sqlite3.connect('scratch/lidwa_plaintext.db')
print([col[0] for col in conn.execute("SELECT DISTINCT Derajat FROM derajat_bukhari").fetchall()])
