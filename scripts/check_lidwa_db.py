import sqlite3

db_path = r'H:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.db'
try:
    con = sqlite3.connect(db_path)
    tables = con.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    print("Tables found:")
    for t in tables:
        print(t[0])
    con.close()
except Exception as e:
    print(f"Error: {e}")
