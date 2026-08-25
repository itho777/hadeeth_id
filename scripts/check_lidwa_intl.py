import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("SELECT NoHdt, NoMapping FROM mapping_muslim WHERE NoHdt IN (1, 8, 9, 10, 92, 93)")
for row in c.fetchall():
    print("Lidwa:", row[0], "Intl:", row[1])