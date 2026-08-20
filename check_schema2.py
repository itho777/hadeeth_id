import sqlite3
import pprint

conn = sqlite3.connect('scratch/lidwa_plaintext.db')
cursor = conn.cursor()

def show_table(table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [r[1] for r in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    row = cursor.fetchone()
    return {"cols": cols, "row1": row}

output = {
    "datakitab_ahmad": show_table('datakitab_ahmad'),
    "databab_ahmad": show_table('databab_ahmad'),
    "had_agregat": show_table('had_agregat'),
    "mapping_ahmad": show_table('mapping_ahmad'),
    "tema_ahmad": show_table('tema_ahmad'),
}

with open('schema_out.txt', 'w', encoding='utf-8') as f:
    f.write(pprint.pformat(output))
