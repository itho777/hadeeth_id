import sqlite3
import re
import json
import os

with open('scratch/irsyadulibad_db/riyadhus-shalihin.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# Strip all MySQL specific comments and settings
sql = re.sub(r'/\*!.*?\*/;', '', sql, flags=re.DOTALL)
sql = re.sub(r'SET .*?;', '', sql)
sql = re.sub(r'ALTER TABLE .*?;', '', sql, flags=re.DOTALL)
sql = sql.replace('START TRANSACTION;', 'BEGIN TRANSACTION;')

sql = sql.replace('COLLATE utf8_unicode_ci', '')
sql = sql.replace('COLLATE=utf8_unicode_ci', '')
sql = sql.replace('ENGINE=InnoDB DEFAULT CHARSET=utf8', '')
sql = re.sub(r'AUTO_INCREMENT=\d+', '', sql)
sql = sql.replace('bigint(20)', 'INTEGER')
sql = sql.replace('varchar(200)', 'TEXT')
sql = sql.replace('longtext', 'TEXT')

# SQLite string literal fixes:
sql = sql.replace('\\\'', '\'\'')
sql = sql.replace('\\n', '\n')
sql = sql.replace('\\r', '\r')
sql = sql.replace('\\"', '"')
sql = sql.replace('\\\\', '\\')

conn = sqlite3.connect(':memory:')
try:
    conn.executescript(sql)
    c = conn.cursor()
    c.execute('SELECT id, arab, terjemah FROM riyadhus_shalihin')
    rows = c.fetchall()
    
    out_dir = 'data/api/riyad'
    os.makedirs(out_dir, exist_ok=True)
    
    out_data = {}
    for r in rows:
        hid = str(r[0])
        payload = {
            'id': f'riyad_lidwa_{hid}',
            'book_id': 'riyad',
            'dataset': 'lidwa',
            'hadith_number': hid,
            'text_ar': r[1],
            'text_id': r[2],
            'chapter_id': 'riyad_c1',
            'chapter_number': 1,
            'in_book_number': hid
        }
        out_data[hid] = payload
        
    with open(os.path.join(out_dir, 'lidwa.json'), 'w', encoding='utf-8') as f:
        json.dump(out_data, f, ensure_ascii=False)
    print('Generated lidwa.json for riyad with', len(out_data), 'hadiths.')
except Exception as e:
    print('SQL Error:', e)
