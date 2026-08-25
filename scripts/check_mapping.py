import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("SELECT * FROM mapping_muslim WHERE NoHdt IN (1, 92, 93, 135) ORDER BY NoHdt")
for row in c.fetchall():
    print("NoHdt:", row[0], "NoMapping:", row[1])