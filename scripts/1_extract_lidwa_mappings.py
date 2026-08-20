import sqlite3
import json
import os

con = sqlite3.connect('scratch/lidwa_imported.db')
con.row_factory = sqlite3.Row

out_dir = 'data/lidwa_extracts'
os.makedirs(out_dir, exist_ok=True)

books = ['abudaud', 'ahmad', 'bukhari', 'darimi', 'ibnumajah', 'malik', 'muslim', 'nasai', 'tirmidzi']

print("Extracting mapping tables...")
for book in books:
    table = f'mapping_{book}'
    try:
        rows = [dict(row) for row in con.execute(f"SELECT * FROM {table}")]
        with open(f'{out_dir}/mapping_{book}.json', 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    except sqlite3.OperationalError:
        print(f"Table {table} not found.")

print("Extracting ind_list (Topic Tags)...")
try:
    rows = [dict(row) for row in con.execute("SELECT * FROM ind_list")]
    with open(f'{out_dir}/ind_list.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
except sqlite3.OperationalError:
    print("Table ind_list not found.")

print("Extracting ind_(1-14)...")
for i in range(1, 15):
    table = f'ind_{i}'
    try:
        rows = [dict(row) for row in con.execute(f"SELECT * FROM {table}")]
        with open(f'{out_dir}/{table}.json', 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    except sqlite3.OperationalError:
        print(f"Table {table} not found.")

print("Extracting biografi_imam...")
try:
    rows = [dict(row) for row in con.execute("SELECT * FROM biografi_imam")]
    with open(f'{out_dir}/biografi_imam.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
except sqlite3.OperationalError:
    print("Table biografi_imam not found.")

con.close()
print("Done.")
