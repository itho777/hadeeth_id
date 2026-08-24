import sqlite3
import os

db_path = "../data/sources/lidwa/lidwa.new.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in lidwa.new.db:", [t[0] for t in tables])
    
    # Check what columns exist in a hadith table
    if ('datahadis_muslim',) in tables:
        cursor.execute("PRAGMA table_info(datahadis_muslim)")
        cols = cursor.fetchall()
        print("datahadis_muslim columns:", [c[1] for c in cols])
        
        cursor.execute("SELECT * FROM datahadis_muslim LIMIT 1")
        print("Sample:", cursor.fetchone())