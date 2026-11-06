"""Anchor-mapping engine v2: lidwa (anchor) -> source, by AR text similarity.

Confidence model (religious-text integrity: never force a match):
  tier 'exact'      -> confidence 'confirmed'  (normalized whole-text identical)
  tier 'exact_multi'-> ordinal-resolved, 'confirmed'
  else use full-text token LCS ratio with the best candidate:
      lcs >= 0.90 -> 'confirmed'
      0.75-0.90   -> 'probable'
      0.50-0.75   -> 'review'
      < 0.50      -> 'unmapped'  (id=None)

Monotonic-offset windowing bounds residual candidates by nearest exact neighbours,
so candidate sets stay tiny and fast.

Usage: python build_mapping.py <book> [targets]   targets=comma list, default fawaz,ahmedbaset,atif
"""
import json, re, unicodedata, os, sys, difflib
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'data', 'sources')

DIACRITICS = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
AR_EXTRA_PUNCT = re.compile(r'[\u060C\u061B\u061F]')
AR_PUNCT = re.compile(r'[^\w\s\u0600-\u06FF]', re.UNICODE)

ATIF_NAME = {'bukhari': 'Sahih al-Bukhari.json', 'muslim': 'Sahih Muslim.json',
             'tirmidhi': 'Jami` at-Tirmidhi.json', 'abudawud': 'Sunan Abi Dawud.json',
             'nasai': "Sunan an-Nasa'i.json", 'ibnmajah': 'Sunan Ibn Majah.json'}


def norm_ar(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKC', s)
    s = DIACRITICS.sub('', s)
    s = (s.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ء', '')
           .replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و').replace('ة', 'ه'))
    s = AR_EXTRA_PUNCT.sub(' ', s)
    s = AR_PUNCT.sub(' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def toks(n):
    return [t for t in n.split(' ') if t]


def cshingles(t, k=4):
    n = len(t)
    if n == 0:
        return frozenset()
    if n < k:
        return frozenset({' '.join(t)})
    return frozenset({' '.join(sorted(t[i:i + k])) for i in range(n - k + 1)})


def lcs_ratio(a, b):
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def load_lidwa(book):
    out = []
    with open(os.path.join(SRC, 'lidwa', f'{book}.ndjson'), encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_ahmedbaset(book):
    fn = 'ahmed.json' if book == 'ahmad' else f'{book}.json'
    p = os.path.join(SRC, 'ahmedbaset', 'by_book', 'the_9_books', fn)
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding='utf-8'))
    return d.get('hadiths', []) if isinstance(d, dict) else d


def load_fawaz(edition):
    p = os.path.join(SRC, 'fawaz_api', 'editions', f'{edition}.min.json')
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding='utf-8'))
    return d.get('hadiths', [])


def load_atif(book):
    fn = ATIF_NAME.get(book)
    if not fn:
        return []
    p = os.path.join(SRC, 'atif_hf', fn)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding='utf-8'))


def atif_number(row):
    r = row.get('In-book reference') or ''
    m = re.search(r'Hadith\s+(\d+)', r)
    return int(m.group(1)) if m else None


def _coerce_num(v):
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s.lstrip('-').isdigit():
            return int(s)
        try:
            f = float(s)
            return int(f) if f.is_integer() else f
        except ValueError:
            return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def prepare_target(rows, text_key, id_key, num_key):
    items = []
    exact = defaultdict(list)
    for r in rows:
        raw = r.get(text_key)
        if isinstance(raw, dict):
            raw = raw.get('text') or ''
        n = norm_ar(raw or '')
        if not n:
            continue
        iid = r.get(id_key)
        num = _coerce_num(r.get(num_key))
        idx = len(items)
        t = toks(n)
        items.append({'norm': n, 'id': iid, 'num': num, 'tok': t, 'sh': cshingles(t)})
        exact[n].append(idx)
    return items, exact


def score_shingle(anchor_tok, cand):
    a = cshingles(anchor_tok)
    if not a:
        return 0.0
    c = cand['sh']
    inter = len(a & c)
    if inter == 0:
        return 0.0
    contain = inter / len(a)
    cover = inter / max(1, len(c))
    return contain if len(cand['tok']) >= len(anchor_tok) else cover


def classify(lidwa_tok, best_tok, tier):
    if tier in ('exact', 'exact_multi') or (best_tok is None):
        return 'confirmed' if tier in ('exact', 'exact_multi') else 'unmapped'
    r = lcs_ratio(lidwa_tok, best_tok)
    if r >= 0.90:
        return 'confirmed'
    if r >= 0.75:
        return 'probable'
    if r >= 0.50:
        return 'review'
    return 'unmapped'


def _prev_mapped_num(res, i):
    for j in range(i - 1, -1, -1):
        r = res[j]
        if r and r.get('num') is not None:
            return r['num']
    return None


def _next_mapped_num(res, i):
    for j in range(i + 1, len(res)):
        r = res[j]
        if r and r.get('num') is not None:
            return r['num']
    return None


def _window_indices(items, lo, hi, pad=15):
    if lo is None and hi is None:
        return range(len(items))
    if lo is None:
        return [j for j, it in enumerate(items) if it['num'] is not None and it['num'] <= hi + pad]
    if hi is None:
        return [j for j, it in enumerate(items) if it['num'] is not None and it['num'] >= lo - pad]
    return [j for j, it in enumerate(items)
            if it['num'] is not None and lo - pad <= it['num'] <= hi + pad]


def map_target(lidwa, items, exact, min_contain=0.75, min_tokens=6, allow_containment=True):
    N = len(lidwa)
    res = [None] * N
    unmapped = []
    for i, h in enumerate(lidwa):
        n = norm_ar(h.get('text_ar') or '')
        hit = exact.get(n)
        if not hit:
            unmapped.append(i)
            continue
        if len(hit) == 1:
            it = items[hit[0]]
            res[i] = {'id': it['id'], 'num': it['num'], 'score': 1.0, 'tier': 'exact'}
        else:
            res[i] = {'multi': hit}
    for i in range(N):
        r = res[i]
        if r and 'multi' in r:
            lo = _prev_mapped_num(res, i)
            hi = _next_mapped_num(res, i)
            best = None
            for j in r['multi']:
                c = items[j]
                if c['num'] is None:
                    continue
                dlo = abs(c['num'] - lo) if lo is not None else 0
                dhi = abs(c['num'] - hi) if hi is not None else 0
                d = (dlo + dhi) if (lo is not None and hi is not None) else (dlo or dhi)
                if best is None or d < best[1]:
                    best = (c, d)
            if best is not None:
                res[i] = {'id': best[0]['id'], 'num': best[0]['num'],
                          'score': 1.0, 'tier': 'exact_multi'}
            else:
                res[i] = {'id': None, 'num': None, 'score': 1.0, 'tier': 'ambiguous_multi'}
    for i in unmapped:
        n = norm_ar(lidwa[i].get('text_ar') or '')
        t = toks(n)
        if not allow_containment or len(t) < min_tokens:
            res[i] = {'id': None, 'num': None, 'score': 0.0, 'tier': 'fragment_source'}
            continue
        lo = _prev_mapped_num(res, i)
        hi = _next_mapped_num(res, i)
        winset = _window_indices(items, lo, hi)
        best = None
        second = None
        for j in winset:
            c = items[j]
            s = score_shingle(t, c)
            if s <= 0:
                continue
            cand = (s, c)
            if best is None or s > best[0]:
                second = best
                best = cand
            elif second is None or s > second[0]:
                second = cand
        if best is None:
            res[i] = {'id': None, 'num': None, 'score': 0.0, 'tier': 'no_candidate'}
            continue
        amb = (best[0] < 1.0 and second is not None and (best[0] - second[0]) < 0.03)
        tier = 'ambiguous' if amb else ('containment' if best[0] >= min_contain else 'below_threshold')
        res[i] = {'id': best[1]['id'], 'num': best[1]['num'],
                  'score': round(best[0], 3), 'tier': tier, 'tok': best[1]['tok']}
    # final confidence pass
    for i in range(N):
        r = res[i]
        if r is None:
            continue
        lidwa_tok = toks(norm_ar(lidwa[i].get('text_ar') or ''))
        target_tok = r.get('tok')
        r['confidence'] = classify(lidwa_tok, target_tok, r['tier'])
        if r['confidence'] == 'unmapped':
            r['id'] = None
            r['num'] = None
    return res


CONF_OK = {'confirmed', 'probable'}


def run(book, targets=('fawaz', 'ahmedbaset', 'atif')):
    print(f'== {book} ==', flush=True)
    lidwa = load_lidwa(book)
    print(f'lidwa={len(lidwa)}', flush=True)
    combined = {'stats': {'book': book, 'lidwa': len(lidwa)}, 'rows': []}
    for tg in targets:
        if tg == 'ahmedbaset':
            rows = load_ahmedbaset(book)
            tk, ik, nk = 'arabic', 'id', 'idInBook'
        elif tg == 'atif':
            rows = load_atif(book)
            tk, ik, nk = 'Arabic_Text', None, None
        else:
            rows = load_fawaz(f'ara-{book}')
            tk, ik, nk = 'text', 'hadithnumber', 'arabicnumber'
        if not rows:
            print(f'  {tg}: no source', flush=True)
            continue
        # atif id = its own ordinal; number = parsed from In-book reference
        if tg == 'atif':
            items, exact = [], defaultdict(list)
            for idx, r in enumerate(rows):
                n = norm_ar(r.get('Arabic_Text') or '')
                if not n:
                    continue
                num = atif_number(r)
                t = toks(n)
                items.append({'norm': n, 'id': idx, 'num': num, 'tok': t, 'sh': cshingles(t)})
                exact[n].append(len(items) - 1)
        else:
            items, exact = prepare_target(rows, tk, ik, nk)
        print(f'  {tg}: rows={len(rows)} indexed={len(items)}', flush=True)
        res = map_target(lidwa, items, exact,
                         allow_containment=(book != 'ahmad'))
        conf = defaultdict(int)
        tiers = defaultdict(int)
        for r in res:
            tiers[r['tier']] += 1
            conf[r['confidence']] += 1
        mapped = sum(1 for r in res if r['confidence'] in CONF_OK)
        stats = {'target': tg, 'indexed': len(items),
                 'mapped_ok': mapped,
                 'coverage_pct': round(100 * mapped / max(1, len(lidwa)), 2),
                 'tiers': dict(tiers), 'confidence': dict(conf)}
        combined['stats'][tg] = stats
        combined['rows'].append({
            'target': tg,
            'data': [[lidwa[i].get('hadith_number'), lidwa[i].get('id'),
                      r['id'], r['num'], r['score'], r['tier'], r['confidence']]
                     for i, r in enumerate(res)],
        })
        print(f'    ok={mapped} cov={stats["coverage_pct"]}% conf={dict(conf)}', flush=True)
    dst = os.path.join(ROOT, f'mapping_{book}.json')
    json.dump(combined, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    print('wrote', dst, flush=True)
    return combined


if __name__ == '__main__':
    book = sys.argv[1] if len(sys.argv) > 1 else 'bukhari'
    targets = tuple(sys.argv[2].split(',')) if len(sys.argv) > 2 else ('fawaz', 'ahmedbaset')
    run(book, targets)