"""Consolidate all mapping_*.json into mapping.db (SQLite) + summary.

Tables:
  anchor_map(book, nohdt, fawaz_num, fawaz_score, fawaz_conf,
             ab_id, ab_score, ab_conf)          -- lidwa -> fawaz/ahmedbaset
  lidwa_internal(book, nohdt, nomapping, idsumber)  -- authoritative edition refs
  summary(book, lidwa_n, fawaz_mapped, fawaz_cov, ab_mapped, ab_cov, ...)
"""
import json, os, sqlite3, glob

ROOT = 'G:/hadeeth_id'
DB = os.path.join(ROOT, 'mapping.db')
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute('''CREATE TABLE anchor_map(
    book TEXT, nohdt INTEGER, fawaz_num TEXT, fawaz_score REAL, fawaz_conf TEXT,
    ab_id TEXT, ab_score REAL, ab_conf TEXT)''')
cur.execute('''CREATE TABLE lidwa_internal(
    book TEXT, nohdt INTEGER, nomapping INTEGER, idsumber INTEGER)''')
cur.execute('''CREATE TABLE summary(
    book TEXT, lidwa_n INTEGER,
    fawaz_ok INTEGER, fawaz_cov REAL, ab_ok INTEGER, ab_cov REAL)''')

books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah',
         'ahmad', 'malik', 'darimi']

# lidwa internal mappings
lcon = sqlite3.connect('file:G:/hadeeth_id/data/sources/lidwa/lidwa.new.db?mode=ro', uri=True)
lcur = lcon.cursor()

rows_out = []
for book in books:
    p = os.path.join(ROOT, f'mapping_{book}.json')
    if not os.path.exists(p):
        print('MISSING', book)
        continue
    m = json.load(open(p, encoding='utf-8'))
    lidwa_n = m['stats']['lidwa']
    fz = None
    ab = None
    for r in m['rows']:
        if r['target'] == 'fawaz':
            fz = r['data']
        elif r['target'] == 'ahmedbaset':
            ab = r['data']
    # fz/ab are lists of [lidwa_no, lidwa_id, src_id, src_num, score, tier, conf]
    fz_map = {el[0]: el for el in fz} if fz else {}
    ab_map = {el[0]: el for el in ab} if ab else {}
    fz_ok = sum(1 for e in fz_map.values() if e[6] in ('confirmed', 'probable'))
    ab_ok = sum(1 for e in ab_map.values() if e[6] in ('confirmed', 'probable'))
    for i in range(1, lidwa_n + 1):
        fe = fz_map.get(i)
        ae = ab_map.get(i)
        cur.execute('INSERT INTO anchor_map VALUES (?,?,?,?,?,?,?,?)',
                    (book, i,
                     fe[3] if fe else None, fe[4] if fe else None, fe[6] if fe else None,
                     ae[2] if ae else None, ae[4] if ae else None, ae[6] if ae else None))
    # internal mapping
    tbl = {'bukhari': 'mapping_bukhari', 'muslim': 'mapping_muslim',
           'abudawud': 'mapping_abudaud', 'tirmidhi': 'mapping_tirmidzi',
           'nasai': 'mapping_nasai', 'ibnmajah': 'mapping_ibnumajah',
           'ahmad': 'mapping_ahmad', 'malik': 'mapping_malik', 'darimi': 'mapping_darimi'}[book]
    try:
        lcur.execute(f'select NoHdt, NoMapping, IdSumber from {tbl}')
        for nohdt, nomap, idsum in lcur.fetchall():
            cur.execute('INSERT INTO lidwa_internal VALUES (?,?,?,?)',
                        (book, nohdt, nomap, idsum))
    except Exception as e:
        print('internal skip', book, e)
    cur.execute('INSERT INTO summary VALUES (?,?,?,?,?,?)',
                (book, lidwa_n, fz_ok, round(100*fz_ok/lidwa_n, 1), ab_ok, round(100*ab_ok/lidwa_n, 1)))
    print(f'{book}: lidwa={lidwa_n} fawaz_ok={fz_ok} ({round(100*fz_ok/lidwa_n,1)}%) ab_ok={ab_ok} ({round(100*ab_ok/lidwa_n,1)}%)')

con.commit()
print()
print('=== SUMMARY ===')
for r in cur.execute('select * from summary order by lidwa_n desc'):
    print('%-10s lidwa=%-6s fawaz=%-5s (%-5s%%) ahmedbaset=%-5s (%-5s%%)' % r)
con.close()
lcon.close()
print('wrote', DB)