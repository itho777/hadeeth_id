import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("PRAGMA table_info(had_agregat)")
print([row[1] for row in c.fetchall()])
c.execute("SELECT NoHdt, KitabId FROM had_agregat WHERE SumberId=2 LIMIT 5")
print(c.fetchall())