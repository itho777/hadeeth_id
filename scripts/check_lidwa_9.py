import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("SELECT NoHdt, NoMapping FROM mapping_muslim WHERE NoHdt IN (8, 9)")
for row in c.fetchall():
    print("NoHdt (Lidwa):", row[0], "NoMapping (Intl):", row[1])