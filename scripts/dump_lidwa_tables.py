import sqlite3

con = sqlite3.connect('scratch/lidwa_imported.db')
tables = [t[0] for t in con.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
print("Tables:", tables)
con.close()
