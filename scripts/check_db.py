import sqlite3

db_path = r'c:\Users\waverider\Downloads\lidwa.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [x[0] for x in cursor.fetchall()]
print(f"Tables: {tables}\n")

for table in tables:
    print(f"=== Table: {table} ===")
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
    print(f"Schema: {cursor.fetchone()[0]}")
    
    cursor.execute(f"SELECT COUNT(*) FROM {table};")
    print(f"Count: {cursor.fetchone()[0]}")
    
    cursor.execute(f"SELECT * FROM {table} LIMIT 2;")
    rows = cursor.fetchall()
    print("Sample Data:")
    for row in rows:
        # truncate long strings for readability
        trunc_row = [str(x)[:100] + '...' if len(str(x)) > 100 else str(x) for x in row]
        print(trunc_row)
    print("\n")
