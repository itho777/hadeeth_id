import sqlite3

db_path = r"G:\AntigravityPortable\.gemini\antigravity\scratch\hadeeth_id\scratch\lidwa_plaintext.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

tables_to_check = [
    'buku',
    'had_agregat',
    'kumpulan_marfu'
]

print("SCHEMA:")
for t in tables_to_check:
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,))
    res = cur.fetchone()
    if res and res[0]:
        print(res[0])
        print("---")
        cur.execute(f"SELECT * FROM {t} LIMIT 1")
        print("Data:", cur.fetchone())
        print("===")
