import sqlite3
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
c.execute("SELECT MIN(NoHdt), MAX(NoHdt), COUNT(*) FROM databab_muslim WHERE KitabId=1")
print("Mukadimah (Kitab 1):", c.fetchone())
c.execute("SELECT MIN(NoHdt), MAX(NoHdt), COUNT(*) FROM databab_muslim WHERE KitabId=2")
print("Iman (Kitab 2):", c.fetchone())