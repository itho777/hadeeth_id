"""Attach Lidwa scholarly data to a collection's linked sources:
  sanad chain (J1..J10 -> perawi_daftar), Skema (continuity), Kedudukan (marfu'),
  grade (derajat_*), and jarh wa ta'dil (komentar_imam).

KEY: the sanad tables are keyed by `NoHdt`, which is Lidwa's own sequential number
for that book. Our `lidwa_no` for the 9 books came straight from the Lidwa ndjson
`hadith_number`, which IS NoHdt (verified: mapping_bukhari.NoHdt runs 0..7008 and
the ndjson runs 1..7008). So the join key is (book -> table, lidwa_no -> NoHdt).
This is a keyed lookup on an integer within one book, NOT cross-source numbering
matching — the AR-text rule governs identifying WHICH hadith a source hadith is,
which is already done upstream.

Usage: python attach_lidwa_scholarly.py riyad
Writes: {stem}_full.json  (in place, adds scholarly blocks)  + report
"""
import json, os, sqlite3, sys
from collections import Counter

ROOT = 'G:/hadeeth_id'
LIDWA_DB = os.path.join(ROOT, 'data', 'sources', 'lidwa', 'lidwa.new.db')

# book -> lidwa table suffixes (note lidwa spells tirmidhi/ibnmajah differently)
SANAD_TBL = {
    'bukhari': 'sanad_bukhari', 'muslim': 'sanad_muslim',
    'abudawud': 'sanad_abudaud', 'tirmidhi': 'sanad_tirmidzi',
    'nasai': 'sanad_nasai', 'ibnmajah': 'sanad_ibnumajah',
    'ahmad': 'sanad_ahmad', 'malik': 'sanad_malik', 'darimi': 'sanad_darimi',
}
DERAJAT_TBL = {
    'bukhari': 'derajat_bukhari', 'muslim': 'derajat_muslim',
    'abudawud': 'derajat_abudaud', 'tirmidhi': 'derajat_tirmidzi',
    'nasai': 'derajat_nasai', 'ibnmajah': 'derajat_ibnumajah',
    'ahmad': 'derajat_ahmad', 'malik': 'derajat_malik', 'darimi': 'derajat_darimi',
}


def cols(cur, tbl):
    cur.execute(f'PRAGMA table_info({tbl})')
    return [r[1] for r in cur.fetchall()]


def main(stem):
    path = os.path.join(ROOT, f'{stem}_full.json')
    data = json.load(open(path, encoding='utf-8'))
    con = sqlite3.connect(f'file:{LIDWA_DB}?mode=ro', uri=True)
    cur = con.cursor()

    # ---- rawi master ----
    cur.execute('select Kode_Rawi,Nama,Quality,Kalangan,Nasab,Kuniyah,Laqob,'
                'Negeri_Hidup,Negeri_Wafat,Tahun_Wafat from perawi_daftar')
    rawi = {}
    for r in cur.fetchall():
        rawi[r[0]] = {
            'kode': r[0], 'nama': r[1], 'quality_code': r[2], 'kalangan': r[3],
            'nasab': r[4], 'kuniyah': r[5], 'laqob': r[6],
            'negeri_hidup': r[7], 'negeri_wafat': r[8], 'tahun_wafat': r[9],
        }

    # ---- jarh wa ta'dil per rawi ----
    cur.execute('select Kode_Rawi,Ulama,Koment from komentar_imam')
    komentar = {}
    for k, u, c in cur.fetchall():
        if not c or not c.strip():
            continue
        komentar.setdefault(k, []).append({'ulama': u, 'komentar': c})

    # ---- sanad cache per book ----
    sanad_cache = {}

    def sanad_for(book, no):
        tbl = SANAD_TBL.get(book)
        if not tbl:
            return []
        if tbl not in sanad_cache:
            try:
                cur.execute(f'select NoHdt,NoUrut,J1,J2,J3,J4,J5,J6,J7,J8,J9,J10,'
                            f'Skema,Kedudukan from {tbl}')
                m = {}
                for row in cur.fetchall():
                    m.setdefault(row[0], []).append({
                        'no_urut': row[1],
                        'chain': [x for x in row[2:12] if x],
                        'skema': row[12], 'kedudukan': row[13],
                    })
                sanad_cache[tbl] = m
            except sqlite3.Error as e:
                print('  sanad skip', tbl, e)
                sanad_cache[tbl] = {}
        return sanad_cache[tbl].get(no, [])

    grade_cache = {}

    def grades_for(book, no):
        tbl = DERAJAT_TBL.get(book)
        if not tbl:
            return []
        if tbl not in grade_cache:
            try:
                c = cols(cur, tbl)
                # column names vary; find number + text + source columns
                num_c = next((x for x in c if x.lower() in ('nohdt', 'no_hdt', 'hadith_number')), None)
                txt_c = next((x for x in c if x.lower() in ('derajat', 'derajat_hadits', 'teks')), None)
                src_c = next((x for x in c if x.lower() in ('idsumber', 'id_sumber', 'sumber')), None)
                ulama_c = next((x for x in c if x.lower() in ('ulama', 'nama')), None)
                sel = ','.join(x for x in (num_c, txt_c, src_c, ulama_c) if x)
                cur.execute(f'select {sel} from {tbl}')
                m = {}
                for row in cur.fetchall():
                    m.setdefault(row[0], []).append(
                        {'derajat': row[1] if len(row) > 1 else None,
                         'sumber': row[2] if len(row) > 2 else None,
                         'ulama': row[3] if len(row) > 3 else None})
                grade_cache[tbl] = m
            except sqlite3.Error as e:
                print('  grade skip', tbl, e)
                grade_cache[tbl] = {}
        return grade_cache[tbl].get(no, [])

    stat = Counter()
    for rec in data:
        for s in rec.get('sources') or []:
            book, no = s['book'], s['lidwa_no']
            chains = sanad_for(book, no)
            if chains:
                stat['with_sanad'] += 1
                resolved = []
                for ch in chains:
                    names = []
                    for kode in ch['chain']:
                        r = rawi.get(kode)
                        if r:
                            rr = dict(r)
                            rr['komentar'] = komentar.get(kode, [])
                            names.append(rr)
                        else:
                            names.append({'kode': kode, 'nama': None})
                    resolved.append({'no_urut': ch['no_urut'], 'rawi': names,
                                     'skema': ch['skema'], 'kedudukan': ch['kedudukan']})
                s['sanad'] = resolved
                s['sanad_count'] = len(resolved)
                # chain-level metadata, taking the first chain
                s['sanad_type'] = chains[0]['skema']
                s['hadith_type'] = chains[0]['kedudukan']
                if any(r.get('komentar') for ch in resolved for r in ch['rawi']):
                    stat['with_jarh'] += 1
            else:
                stat['no_sanad'] += 1
                s['sanad'] = []
                s['sanad_count'] = 0

            g = grades_for(book, no)
            if g:
                stat['with_grade'] += 1
                s['grades'] = g
                s['grade'] = '; '.join(x['derajat'] for x in g if x.get('derajat')) or s.get('grade')
            else:
                s['grades'] = []

    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'updated {path}')
    total = sum(1 for rec in data for _ in rec.get('sources') or [])
    print(f'source links: {total}')
    for k in ('with_sanad', 'no_sanad', 'with_jarh', 'with_grade'):
        print(f'  {k}: {stat[k]} ({100*stat[k]/max(1,total):.0f}%)')
    con.close()


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'riyad')