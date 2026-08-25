import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("PRAGMA table_info(datakitab_muslim)")
print("Kitab columns:", [r[1] for r in c.fetchall()])
c.execute("PRAGMA table_info(databab_muslim)")
print("Bab columns:", [r[1] for r in c.fetchall()])