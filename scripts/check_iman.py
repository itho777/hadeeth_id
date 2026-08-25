import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("SELECT MIN(NoHdt), MAX(NoHdt) FROM mapping_muslim WHERE NoHdt IN (SELECT NoHdt FROM ind_2 WHERE Kitab='Iman')")
print("Iman range in Lidwa:", c.fetchone())