import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("PRAGMA table_info(databab_muslim)")
print([row[1] for row in c.fetchall()])