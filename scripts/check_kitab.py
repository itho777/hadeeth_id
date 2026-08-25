import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("SELECT * FROM datakitab_muslim LIMIT 5")
for row in c.fetchall(): print(row)