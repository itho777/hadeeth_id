import sqlite3
conn = sqlite3.connect('../data/sqlite/lidwa.new.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(c.fetchall())