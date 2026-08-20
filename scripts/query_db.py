import sqlite3
import json

conn = sqlite3.connect('data/sources/lidwa/lidwa.new.db')
tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
print(tables)
if 'sanad_bukhari' in tables:
    print(conn.execute("SELECT * FROM sanad_bukhari LIMIT 1").fetchall())
    print([d[0] for d in conn.execute("SELECT * FROM sanad_bukhari LIMIT 0").description])
