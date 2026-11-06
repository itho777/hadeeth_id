"""COMMIT: Lidwa perawi -> Kaggle narrators mapping (strong+medium only).

Writes:
  G:/hadeeth_id/data/sources/kaggle/narrators_ext.json  (+ .sqlite table for review)
  Adds column mapping: lidwa_kode (int|null), mapping_confidence (text|null)

Rules (religious-text integrity):
  * ONLY tiers 'strong' and 'medium' are written as matched (confidence set).
  * 'ambiguous'/'weak'/'rejected'/'conflict_death_year' -> lidwa_kode = null,
    confidence = null. No forced mapping, ever.
  * Every unmatched row stays in narrators_ext with nulls so the rawi profile
    page renders Lidwa fields always and the Kaggle bio block only on match.

Idempotent: rebuilds narrators_ext.json from source each run.
"""
import json, os, re, sqlite3, unicodedata, difflib, sys
from collections import Counter, defaultdict

REPO = 'G:/hadeeth_id'
LIDWA_DB = os.path.join(REPO, 'data', 'sources', 'lidwa', 'lidwa.new.db')
KAGGLE = os.path.join(REPO, 'data', 'sources', 'kaggle', 'narrators.json')
OUT_JSON = os.path.join(REPO, 'data', 'sources', 'kaggle', 'narrators_ext.json')
OUT_DB = os.path.join(REPO, 'mapping_rawi.db')

AR = re.compile(r'[\u0600-\u06FF]')
NONLATIN = re.compile(r'[^a-z ]')

TOKEN_MAP = {
    'ibn': 'bin', 'ibnu': 'bin', 'bn': 'bin', 'abin': 'bin', 'bin': 'bin',
    'aboo': 'abu', 'abi': 'abu', 'abu': 'abu',
    'abdul': 'abd', 'abd': 'abd',
    'mohammed': 'muhammad', 'mohammad': 'muhammad', 'muhammed': 'muhammad',
    'mohamed': 'muhammad', 'muhammad': 'muhammad',
    'ahmed': 'ahmad', 'ahmad': 'ahmad',
    'hicham': 'hisham', 'hishaam': 'hisham', 'hisham': 'hisham',
    'omar': 'umar', 'umar': 'umar',
    'bekr': 'bakr', 'bakr': 'bakr',
    'sad': 'saad', 'saad': 'saad',
    'yahia': 'yahya', 'yahya': 'yahya',
    'sulaiman': 'sulayman', 'sulayman': 'sulayman',
    'ismaeel': 'ismail', 'ismaail': 'ismail', 'ismail': 'ismail',
    'othman': 'uthman', 'uthman': 'uthman', 'usman': 'uthman',
    'ayyub': 'ayyub', 'ayub': 'ayyub',
    'ibraheem': 'ibrahim', 'ibrahim': 'ibrahim',
    'yusuf': 'yusuf', 'yousuf': 'yusuf', 'yousaf': 'yusuf',
    'al': '', 'el': '', 'as': '', 'ad': '', 'ath': '', 'az': '', 'at': '',
}


def norm_latin(s):
    if not s:
        return []
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace('’', "'").replace('‘', "'").replace('`', "'")
    s = s.replace("'", '').replace('-', ' ')
    s = NONLATIN.sub(' ', s)
    out = []
    for t in s.split(' '):
        if not t:
            continue
        t = TOKEN_MAP.get(t, t)
        for p in t.split(' '):
            if p:
                out.append(p)
    return out


def ism(tokens):
    i = 0
    while i < len(tokens) and tokens[i] in ('abu', 'umm'):
        i += 1
    return tokens[i] if i < len(tokens) else (tokens[0] if tokens else '')


def kaggle_latin_prefix(name_ar):
    if not name_ar:
        return ''
    return AR.sub(' ', name_ar.split('(')[0]).strip()


def coerce_year(v):
    """Lidwa 'Tahun_Wafat' = '8 H'; Kaggle = int."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    m = re.search(r'(-?\d+)', str(v).strip())
    return int(m.group(1)) if m else None


def ordered_contains(hay, needle):
    if not needle:
        return False
    it = iter(hay)
    return all(t in it for t in needle)


def main():
    lcon = sqlite3.connect(f'file:{LIDWA_DB}?mode=ro', uri=True)
    lcur = lcon.cursor()
    lcur.execute('select Kode_Rawi, Nama, Kalangan, Tahun_Wafat from perawi_daftar')
    lidwa = []
    for kode, nama, kal, wafat in lcur.fetchall():
        t = norm_latin(nama or '')
        if not t:
            continue
        lidwa.append({'kode': kode, 'raw': nama, 'tok': t, 'ism': ism(t),
                      'kal': kal, 'wafat': coerce_year(wafat)})
    print(f'lidwa perawi normalized: {len(lidwa)}')

    kag = json.load(open(KAGGLE, encoding='utf-8'))
    kn = []
    for r in kag:
        pre = kaggle_latin_prefix(r.get('name_ar') or '')
        t = norm_latin(pre)
        kn.append({'id': r['id'], 'raw': pre, 'tok': t,
                   'ism': ism(t) if t else '',
                   'death': coerce_year(r.get('death_year'))})
    print(f'kaggle rows: {len(kn)}')

    by_ism = defaultdict(list)
    for i, r in enumerate(kn):
        if r['ism']:
            by_ism[r['ism']].append(i)

    # per-kaggle-row assignment (a kaggle row claimed once; best sim wins)
    claims = defaultdict(list)   # kaggle_idx -> [(score, lidwa_kode, tier)]
    tiers = Counter()
    for L in lidwa:
        cands = by_ism.get(L['ism'], [])
        if not cands:
            tiers['no_candidate'] += 1
            continue
        best = second = None
        for i in cands:
            K = kn[i]
            sim = difflib.SequenceMatcher(None, L['tok'], K['tok']).ratio()
            m = difflib.SequenceMatcher(None, L['tok'], K['tok']).find_longest_match(
                0, len(L['tok']), 0, len(K['tok']))
            prefix = m.size
            a, b = (L['tok'], K['tok']) if len(L['tok']) <= len(K['tok']) else (K['tok'], L['tok'])
            contained = ordered_contains(b, a)
            yr_ok = None
            if L['wafat'] is not None and K['death'] is not None:
                yr_ok = abs(L['wafat'] - K['death']) <= 3
            score = sim + (0.10 if yr_ok is True else (-0.15 if yr_ok is False else 0.0))
            cand = (score, sim, yr_ok, i)
            if best is None or score > best[0]:
                second = best
                best = cand
            elif second is None or score > second[0]:
                second = cand
        if best is None:
            tiers['no_overlap'] += 1
            continue
        score, sim, yr_ok, idx = best
        runner = second[0] if second else 0.0
        if yr_ok is False and sim < 0.95:
            tier = 'conflict_death_year'
        elif sim >= 0.92 or (contained and prefix >= 3 and sim >= 0.75):
            tier = 'strong'
        elif sim >= 0.80:
            tier = 'medium'
        elif sim >= 0.65:
            tier = 'weak'
        else:
            tier = 'rejected'
        if tier in ('strong', 'medium') and (score - runner) < 0.05 and second is not None:
            tier = 'ambiguous'
        tiers[tier] += 1
        if tier in ('strong', 'medium'):
            claims[idx].append((score, L['kode'], tier))

    # resolve kaggle-row contention: highest score wins, losers dropped
    final = {}
    contested = 0
    for idx, lst in claims.items():
        lst.sort(reverse=True)
        if len(lst) > 1:
            contested += 1
            if abs(lst[0][0] - lst[1][0]) < 0.05:
                continue   # too close -> leave unmapped
        final[idx] = lst[0]

    # ensure lidwa kode not used twice
    used = defaultdict(list)
    for idx, (sc, kode, tier) in final.items():
        used[kode].append((sc, idx))
    dup_kode_dropped = 0
    for kode, lst in used.items():
        if len(lst) > 1:
            lst.sort(reverse=True)
            for _, idx in lst[1:]:
                final.pop(idx, None)
                dup_kode_dropped += 1

    print(f'contested kaggle rows resolved: {contested}, dup-kode dropped: {dup_kode_dropped}')

    # write narrators_ext
    kby = {r['id']: r for r in kag}
    ext = []
    matched = 0
    conf_count = Counter()
    for i, r in enumerate(kn):
        src = kby[r['id']]
        hit = final.get(i)
        ek = hit[1] if hit else None
        ec = hit[2] if hit else None
        if ek is not None:
            matched += 1
            conf_count[ec] += 1
        ext.append({**src, 'lidwa_kode': ek, 'mapping_confidence': ec})
    # kaggle rows with no usable latin still emitted, unmapped
    written_ids = {r['id'] for r in kn}
    for r in kag:
        if r['id'] not in written_ids:
            ext.append({**r, 'lidwa_kode': None, 'mapping_confidence': None})

    json.dump(ext, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'wrote {OUT_JSON}  rows={len(ext)}  matched={matched}  conf={dict(conf_count)}')

    # review sqlite
    if os.path.exists(OUT_DB):
        os.remove(OUT_DB)
    con = sqlite3.connect(OUT_DB)
    cur = con.cursor()
    cur.execute('''CREATE TABLE narrators_ext(
        kaggle_id INTEGER PRIMARY KEY, name_ar TEXT, name_en TEXT, grade TEXT,
        birth_year TEXT, death_year TEXT, biography TEXT,
        lidwa_kode INTEGER, mapping_confidence TEXT)''')
    for e in ext:
        cur.execute('INSERT OR REPLACE INTO narrators_ext VALUES (?,?,?,?,?,?,?,?,?)',
                    (e.get('id'), e.get('name_ar'), e.get('name_en'), e.get('grade'),
                     None if e.get('birth_year') is None else str(e.get('birth_year')),
                     None if e.get('death_year') is None else str(e.get('death_year')),
                     e.get('biography'), e.get('lidwa_kode'), e.get('mapping_confidence')))
    cur.execute('CREATE INDEX idx_lidwa ON narrators_ext(lidwa_kode)')
    cur.execute('CREATE INDEX idx_conf ON narrators_ext(mapping_confidence)')
    con.commit()
    for row in cur.execute("select mapping_confidence, count(*) from narrators_ext group by 1"):
        print('  ', row)
    con.close()
    lcon.close()
    print('wrote', OUT_DB)


if __name__ == '__main__':
    main()