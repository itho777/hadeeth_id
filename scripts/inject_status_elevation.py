import os
import json
import sqlite3

def inject_status_elevation():
    db_path = 'data/sources/lidwa/lidwa.new.db'
    if not os.path.exists(db_path):
        print("DB not found.")
        return

    conn = sqlite3.connect(db_path)
    
    book_mapping = {
        'bukhari': 'sanad_bukhari',
        'muslim': 'sanad_muslim',
        'tirmidhi': 'sanad_tirmidzi',
        'abudawud': 'sanad_abudaud',
        'nasai': 'sanad_nasai',
        'ibnmajah': 'sanad_ibnumajah',
        'darimi': 'sanad_darimi',
        'malik': 'sanad_malik',
        'ahmad': 'sanad_ahmad'
    }

    for book, table in book_mapping.items():
        ndjson_path = f'data/api/{book}.ndjson'
        if not os.path.exists(ndjson_path):
            continue
            
        print(f"Processing {book}...")
        
        # Build dictionary from DB for this book
        # We'll use NoUrut = 1 to get the primary sanad path
        cursor = conn.execute(f"SELECT NoHdt, Skema, Kedudukan FROM {table} WHERE NoUrut = 1")
        db_data = {}
        for row in cursor.fetchall():
            no_hdt, skema, kedudukan = row
            db_data[no_hdt] = {
                'status': skema.strip() if skema else None,
                'elevation': kedudukan.strip() if kedudukan else None
            }
            
        # Update NDJSON
        updated_lines = []
        with open(ndjson_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                h = json.loads(line)
                lidwa_id = h.get('lidwa_id')
                if lidwa_id and lidwa_id in db_data:
                    info = db_data[lidwa_id]
                    if info['status']:
                        h['status'] = info['status']
                    if info['elevation']:
                        h['elevation'] = info['elevation']
                updated_lines.append(json.dumps(h, ensure_ascii=False))
                
        # Write back
        with open(ndjson_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines) + '\n')

if __name__ == '__main__':
    inject_status_elevation()
