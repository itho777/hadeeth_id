"""Resolve each linked hadith to its FAWAZ number by Arabic text, then pull all
languages at THAT fawaz number.

WHY this indirection is mandatory (measured, see conversation):
  Lidwa's `hadith_number` and fawaz's `hadithnumber` are NOT the same space for
  every book. Lidwa Muslim #9 = hadith Jibril. fawaz urd-muslim #9 = the 'kadhib'
  proverb. fawaz ara-muslim #9 is EMPTY. Joining Lidwa -> fawaz by number therefore
  attaches a DIFFERENT hadith in translation — wrong religious text, forbidden.

  For books where the spaces do agree (bukhari 1..N verified identical) the number
  join happens to work, which is exactly why this bug is easy to miss.

METHOD:
  1. For each linked source row, take its Lidwa Arabic text.
  2. Find the fawaz ara-{book} row with the same Arabic (normalized exact, else
     high LCS). That yields the fawaz number.
  3. Use that fawaz number for every language edition of the book.
  If step 2 fails, NO translations are attached for that source. Absent is correct.

Writes: nawawi40_full.json (translations block rebuilt), fawaz_number_map.json
"""
import json, os, re, sys, unicodedata, difflib
from collections import defaultdict

ROOT = 'G:/hadeeth_id'
SRC = os.path.join(ROOT, 'data', 'sources')
LANGS = ['ara', 'eng', 'ind', 'urd', 'ben', 'fra', 'tur', 'rus', 'tam']
LIDWA_LANG_COL = {'ara': 'text_ar', 'eng': 'text_en', 'ind': 'text_id'}
BOOKS = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik']

DIAC = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
AR_PUNCT = re.compile(r'[^\w\s\u0600-\u06FF]', re.UNICODE)
AR_EXTRA = re.compile(r'[\u060C\u061B\u061F]')


def norm_ar(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKC', s)
    s = DIAC.sub('', s)
    s = (s.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ء', '')
           .replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و').replace('ة', 'ه'))
    s = AR_EXTRA.sub(' ', s)
    s = AR_PUNCT.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def toks(n):
    return [t for t in n.split(' ') if t]


def load_json(p, default=None):
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding='utf-8'))


def load_ndjson(p):
    rows = []
    if not os.path.exists(p):
        return rows
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    links = load_json(os.path.join(ROOT, 'nawawi_links.json'))
    if not links:
        print('run map_nawawi40.py first'); return
    naw_rows = {r['hadith_number']: r
                for r in load_ndjson(os.path.join(SRC, 'lidwa', 'nawawi.ndjson'))}

    # --- build fawaz arabic indexes per book ---
    fz_ar = {}
    for b in BOOKS:
        d = load_json(os.path.join(SRC, 'fawaz_api', 'editions', f'ara-{b}.min.json'))
        if not d:
            continue
        rows = []
        for h in d.get('hadiths', []):
            t = (h.get('text') or '').strip()
            if t:
                rows.append({'no': h.get('hadithnumber'), 'norm': norm_ar(t), 'tok': toks(norm_ar(t))})
        fz_ar[b] = rows
    print('fawaz arabic indexed:', {b: len(r) for b, r in fz_ar.items()})

    # shingle index for candidate generation
    sh_idx = {}
    for b, rows in fz_ar.items():
        inv = defaultdict(set)
        for i, r in enumerate(rows):
            t = r['tok']
            for j in range(max(0, len(t) - 4)):
                inv[' '.join(t[j:j + 4])].add(i)
        sh_idx[b] = inv

    def resolve_fawaz_no(book, lidwa_ar):
        """Find the fawaz hadithnumber whose Arabic equals this Lidwa text."""
        rows = fz_ar.get(book)
        if not rows or not lidwa_ar:
            return None, 0.0
        nt = toks(norm_ar(lidwa_ar))
        if not nt:
            return None, 0.0
        inv = sh_idx[book]
        votes = defaultdict(int)
        for j in range(max(0, len(nt) - 4)):
            for i in inv.get(' '.join(nt[j:j + 4]), ()):
                votes[i] += 1
        cands = sorted(votes.items(), key=lambda kv: -kv[1])[:60]
        best = (None, 0.0)
        for i, _ in cands:
            sm = difflib.SequenceMatcher(None, nt, rows[i]['tok'], autojunk=False)
            matched = sum(blk.size for blk in sm.get_matching_blocks())
            ratio = 2.0 * matched / (len(nt) + len(rows[i]['tok']))
            if ratio > best[1]:
                best = (rows[i]['no'], ratio)
        return best

    # edition coverage, for reporting only (NOT a correctness proof)
    coverage = {}
    for b in BOOKS:
        ar_n = {r['no'] for r in fz_ar.get(b, [])}
        if not ar_n:
            continue
        for lg in LANGS:
            if lg == 'ara':
                continue
            d = load_json(os.path.join(SRC, 'fawaz_api', 'editions', f'{lg}-{b}.min.json'))
            if not d:
                continue
            ln = {h.get('hadithnumber') for h in d.get('hadiths', [])
                  if (h.get('text') or '').strip()}
            coverage.setdefault(b, {})[lg] = round(len(ar_n & ln) / len(ar_n), 4)

    fz_cache = {}

    def fawaz(book, lang):
        key = (book, lang)
        if key not in fz_cache:
            d = load_json(os.path.join(SRC, 'fawaz_api', 'editions', f'{lang}-{book}.min.json'))
            fz_cache[key] = ({h.get('hadithnumber'): h.get('text')
                              for h in (d or {}).get('hadiths', [])} if d else None)
        return fz_cache[key]

    lidwa_cache = {}

    def lidwa(book):
        if book not in lidwa_cache:
            lidwa_cache[book] = {r['hadith_number']: r
                                 for r in load_ndjson(os.path.join(SRC, 'lidwa', f'{book}.ndjson'))}
        return lidwa_cache[book]

    out = []
    num_map = []
    resolved = unresolved = 0
    for l in sorted(links, key=lambda x: x['nawawi_no']):
        no = l['nawawi_no']
        nr = naw_rows.get(no, {})
        rec = {
            'nawawi_no': no,
            'anchor': {
                'source': 'lidwa', 'book_id': 'nawawi', 'hadith_number': no,
                'id': nr.get('id'),
                'text_ar': nr.get('text_ar'),
                'text_en': nr.get('text_en') or None,
                'text_id': nr.get('text_id') or None,
                'text_fr': nr.get('text_fr') or None,
                'text_ur': nr.get('text_ur') or None,
                'grade': nr.get('grade'), 'grade_by': nr.get('grade_by'),
                'missing_langs': [lg for lg, k in
                                  (('en', 'text_en'), ('id', 'text_id'),
                                   ('fr', 'text_fr'), ('ur', 'text_ur'))
                                  if not nr.get(k)],
            },
            'matn_toks': l.get('matn_toks'),
            'cited_in_nawawi_note': l.get('cited', []),
            'sources': [],
            'status': l.get('status') or ('linked' if l.get('sources') else 'unmapped'),
        }
        for s in (l.get('sources') or []):
            book = s['book']
            lr = lidwa(book).get(s['lidwa_no'], {})
            src = {
                'book': book, 'lidwa_no': s['lidwa_no'], 'lidwa_id': s.get('lidwa_id'),
                'tier': s.get('tier'), 'score': s.get('score'),
                'matched_grams': s.get('matched'), 'rare_grams': s.get('rare_grams'),
                'cited': s.get('cited'),
                'text_ar': lr.get('text_ar'),
                'text_id': lr.get('text_id') or None,
                'text_en': lr.get('text_en') or None,
                'grade': lr.get('grade'), 'grade_by': lr.get('grade_by'),
                'translations': {}, 'fawaz_no': None, 'fawaz_match': None,
            }
            fno, fratio = resolve_fawaz_no(book, lr.get('text_ar'))
            src['fawaz_no'] = fno
            src['fawaz_match'] = round(fratio, 4) if fno else None
            num_map.append({'book': book, 'lidwa_no': s['lidwa_no'],
                            'fawaz_no': fno, 'ratio': round(fratio, 4)})
            if fno is None:
                unresolved += 1
            else:
                resolved += 1

            for lg in LANGS:
                chosen = None
                if lg in LIDWA_LANG_COL:
                    lv = (lr.get(LIDWA_LANG_COL[lg]) or '').strip()
                    if lv:
                        chosen = {'text': lv, 'via': 'lidwa', 'number': s['lidwa_no']}
                if chosen is None and lg != 'ara' and fno is not None:
                    v = ((fawaz(book, lg) or {}).get(fno) or '').strip()
                    if v:
                        chosen = {'text': v, 'via': 'fawaz', 'number': fno,
                                  'edition_coverage': coverage.get(book, {}).get(lg)}
                if chosen is not None:
                    src['translations'][lg] = chosen
            src['missing_langs'] = [lg for lg in LANGS if lg not in src['translations']]
            rec['sources'].append(src)

        rec['source_count'] = len(rec['sources'])
        out.append(rec)

    json.dump(out, open(os.path.join(ROOT, 'nawawi40_full.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(num_map, open(os.path.join(ROOT, 'fawaz_number_map.json'), 'w', encoding='utf-8'), indent=1)

    print(f'\nwrote nawawi40_full.json ({len(out)} records)')
    print(f'fawaz-number resolved: {resolved}   unresolved: {unresolved}')
    from collections import Counter
    avail = Counter()
    tot = sum(len(r['sources']) for r in out)
    for r in out:
        for s in r['sources']:
            for lg in s['translations']:
                avail[lg] += 1
    print(f'\ntranslation availability across {tot} source-hadiths:')
    for lg in LANGS:
        print(f'  {lg}: {avail[lg]:>3}/{tot} ({100*avail[lg]/max(1,tot):.0f}%)')


if __name__ == '__main__':
    main()