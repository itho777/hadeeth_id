"""Enrich a *_{stem}_links.json collection with translations, keyed off FAWAZ Arabic.

CORE RULE (non-negotiable): hadith identity is established by ARABIC TEXT.
We never join translations on Lidwa's hadith number. For each linked source hadith
we first resolve WHICH fawaz row carries the same Arabic, and only then read every
language edition at that fawaz number. If the Arabic cannot be matched, no
translation is attached at all — absent is correct, adjacent is wrong text.

Usage: python enrich_collection.py riyad
Reads  : {stem}_links.json, lidwa/*.ndjson, fawaz editions
Writes : {stem}_full.json
"""
import json, os, re, sys, unicodedata, difflib
from collections import defaultdict

ROOT = 'G:/hadeeth_id'
SRC = os.path.join(ROOT, 'data', 'sources')
LANGS = ['ara', 'eng', 'ind', 'urd', 'ben', 'fra', 'tur', 'rus', 'tam']
LIDWA_LANG_COL = {'ara': 'text_ar', 'eng': 'text_en', 'ind': 'text_id'}
BOOKS = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik']
BIDI = re.compile(r'[\u200B-\u200F\u202A-\u202E\u2066-\u2069\uFEFF]')
DIAC = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
AR_PUNCT = re.compile(r'[^\w\s\u0600-\u06FF]', re.UNICODE)
AR_EXTRA = re.compile(r'[\u060C\u061B\u061F]')


def norm_ar(s):
    if not s:
        return ''
    s = BIDI.sub('', s)
    s = unicodedata.normalize('NFKC', s)
    s = DIAC.sub('', s)
    s = (s.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ء', '')
           .replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و').replace('ة', 'ه'))
    s = AR_EXTRA.sub(' ', s)
    s = AR_PUNCT.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def toks(n):
    return [t for t in n.split(' ') if t]


def load_json(p, d=None):
    if not os.path.exists(p):
        return d
    return json.load(open(p, encoding='utf-8'))


def load_ndjson(p):
    rows = []
    if not os.path.exists(p):
        return rows
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main(stem, anchor_name=None):
    links = load_json(os.path.join(ROOT, f'{stem}_links.json'))
    if not links:
        print(f'{stem}_links.json missing'); return

    # fawaz arabic index per book -> resolve Lidwa text to a fawaz number
    fz_ar, sh_idx = {}, {}
    for b in BOOKS:
        d = load_json(os.path.join(SRC, 'fawaz_api', 'editions', f'ara-{b}.min.json'))
        if not d:
            continue
        rows = []
        for h in d.get('hadiths', []):
            t = (h.get('text') or '').strip()
            if t:
                n = norm_ar(t)
                rows.append({'no': h.get('hadithnumber'), 'tok': toks(n)})
        fz_ar[b] = rows
        inv = defaultdict(set)
        for i, r in enumerate(rows):
            for j in range(max(0, len(r['tok']) - 4)):
                inv[' '.join(r['tok'][j:j + 4])].add(i)
        sh_idx[b] = inv
    print('fawaz arabic indexed:', {b: len(r) for b, r in fz_ar.items()})

    def resolve(book, ar_text):
        rows = fz_ar.get(book)
        if not rows or not ar_text:
            return None, 0.0
        nt = toks(norm_ar(ar_text))
        if not nt:
            return None, 0.0
        votes = defaultdict(int)
        inv = sh_idx[book]
        for j in range(max(0, len(nt) - 4)):
            for i in inv.get(' '.join(nt[j:j + 4]), ()):
                votes[i] += 1
        cands = sorted(votes.items(), key=lambda kv: -kv[1])[:60]
        best = (None, 0.0)
        for i, _ in cands:
            sm = difflib.SequenceMatcher(None, nt, rows[i]['tok'], autojunk=False)
            m = sum(blk.size for blk in sm.get_matching_blocks())
            ratio = 2.0 * m / (len(nt) + len(rows[i]['tok']))
            if ratio > best[1]:
                best = (rows[i]['no'], ratio)
        return best

    fz_cache, lidwa_cache = {}, {}

    def fawaz(book, lang):
        key = (book, lang)
        if key not in fz_cache:
            d = load_json(os.path.join(SRC, 'fawaz_api', 'editions', f'{lang}-{book}.min.json'))
            fz_cache[key] = ({h.get('hadithnumber'): h.get('text')
                              for h in (d or {}).get('hadiths', [])} if d else None)
        return fz_cache[key]

    def lidwa(book):
        if book not in lidwa_cache:
            lidwa_cache[book] = {r['hadith_number']: r
                                 for r in load_ndjson(os.path.join(SRC, 'lidwa', f'{book}.ndjson'))}
        return lidwa_cache[book]

    out = []
    resolved = unresolved = 0
    for rec in links:
        r = {
            'no': rec['no'], 'ar': rec.get('ar'), 'en': rec.get('en'),
            'en_narrator': rec.get('en_narrator'),
            'matn_toks': rec.get('matn_toks'), 'cited': rec.get('cited', []),
            'method': rec.get('method'), 'sources': [],
            'status': rec.get('status') or ('linked' if rec.get('sources') else 'unmapped'),
        }
        for s in (rec.get('sources') or []):
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
            fno, fr = resolve(book, lr.get('text_ar'))
            src['fawaz_no'] = fno
            src['fawaz_match'] = round(fr, 4) if fno else None
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
                        chosen = {'text': v, 'via': 'fawaz', 'number': fno}
                if chosen is not None:
                    src['translations'][lg] = chosen
            src['missing_langs'] = [lg for lg in LANGS if lg not in src['translations']]
            r['sources'].append(src)
        out.append(r)

    dst = os.path.join(ROOT, f'{stem}_full.json')
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\nwrote {dst} records={len(out)}')
    print(f'fawaz-number resolved {resolved}, unresolved {unresolved}')
    print('linked:', sum(1 for x in out if x['sources']),
          'multi:', sum(1 for x in out if len(x['sources']) > 1))
    from collections import Counter
    avail = Counter()
    tot = sum(len(x['sources']) for x in out)
    for x in out:
        for s in x['sources']:
            for lg in s['translations']:
                avail[lg] += 1
    print(f'translation availability across {tot} source hadiths:')
    for lg in LANGS:
        print(f'  {lg}: {avail[lg]:>4}/{tot} ({100*avail[lg]/max(1,tot):.0f}%)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'riyad')