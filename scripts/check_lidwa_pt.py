import sqlite3
import os

db_path = "../scratch/lidwa_plaintext.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables in lidwa_plaintext.db:", tables)
    
    if "muslim" in tables:
        cursor.execute("PRAGMA table_info(muslim)")
        print("muslim cols:", [c[1] for c in cursor.fetchall()])
        cursor.execute("SELECT * FROM muslim LIMIT 1")
        print("muslim sample:", cursor.fetchone())