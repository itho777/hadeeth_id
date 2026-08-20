import sqlite3
import pprint

conn = sqlite3.connect('scratch/lidwa_plaintext.db')
cursor = conn.cursor()

def show_table(table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    print(f"\n--- {table_name} ---")
    print(f"Cols: {[r[1] for r in cursor.fetchall()]}")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    print(f"Row 1: {cursor.fetchone()}")

show_table('datakitab_ahmad')
show_table('databab_ahmad')
show_table('had_agregat')
