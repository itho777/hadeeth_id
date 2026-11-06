"""Nawawi 40 -> source hadith(s) via RARE-PHRASE ANCHORING (not whole-text similarity).

WHY the earlier approaches failed (measured, not assumed):
  * Whole-text LCS / shingle containment / run-length: Nawawi ABRIDGES and
    HARMONISES. He merges several narrations, drops sanad, rewrites connectives.
    Any global similarity metric is dominated by the parts that differ.
  * Ground-truth probe: Nawawi #2 (Jibril) genuinely appears in Muslim #9
    ('شديد بياض الثياب'), with parallels in Bukhari/Nasai/Ahmad. Whole-text
    scoring sent it to Abu Dawud #4075 because a long unmatched span outvoted
    a short exact one.

METHOD — rare-phrase anchoring:
  1. Take the Nawawi matn tokens.
  2. Generate its k-grams (k=5). Keep only grams that are RARE across the whole
     Lidwa corpus (document frequency low) — these are the fingerprints.
     Common phrases like 'رسول الله صلي الله عليه وسلم' carry no signal and are
     dropped by df, which is exactly what broke the earlier scorers.
  3. For each book, count how many of those rare grams appear in each row.
  4. score = matched_rare_grams / total_rare_grams of the Nawawi text.
  A true source contains nearly all of them; a wrong row catches one or two.

Tiers (1:N — compilation books legitimately have several sources):
  confirmed : >= 0.60 of rare grams found
  probable  : 0.40 - 0.60
  review    : 0.25 - 0.40
  unmapped  : < 0.25
"""
import json, os, re, sys, unicodedata
from collections import defaultdict, Counter

ROOT = 'G:/hadeeth_id'
SRC = os.path.join(ROOT, 'data', 'sources')

DIACRITICS = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
AR_EXTRA_PUNCT = re.compile(r'[\u060C\u061B\u061F]')
AR_PUNCT = re.compile(r'[^\w\s\u0600-\u06FF]', re.UNICODE)

ATTR_MARKERS = ['رواه اماما المحدثين', 'رواه الامامان', 'رواه الشيخان',
                'متفق عليه', 'رواه البخاري', 'رواه مسلم', 'رواه ابو داود',
                'رواه الترمذي', 'رواه النسايي', 'رواه ابن ماجه', 'رواه احمد',
                'رواه مالك', 'رواه الدارمي', 'اخرجه اماما', 'اخرجه']

BOOK_PATTERNS = {
    'bukhari': ['البخاري', 'صحيحيهما', 'الشيخان'],
    'muslim': ['مسلم بن الحجاج', 'النيسابوري', 'صحيحيهما', 'الشيخان'],
    'abudawud': ['ابو داود', 'ابي داود'],
    'tirmidhi': ['الترمذي'],
    'nasai': ['النسايي', 'النساي'],
    'ibnmajah': ['ابن ماجه'],
    'malik': ['مالك بن انس', 'الموطا'],
    'ahmad': ['احمد بن حنبل', 'المسند'],
    'darimi': ['الدارمي'],
}

K = 5
# Two-stage fingerprinting. A gram is a fingerprint only if it is rare ACROSS THE
# WHOLE CORPUS (all books combined), computed in pass 1. Per-book rarity is not
# enough: 'لا اله الا الله' is rare in Malik but ubiquitous overall.
GLOBAL_DF_CAP = 150      # total occurrences across all books to count as rare
MIN_EVIDENCE = 4         # fewer matched fingerprints than this proves nothing
MIN_NAV_GRAMS = 6        # a nawawi text yielding <6 fingerprints cannot be scored


def norm_ar(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKC', s)
    s = DIACRITICS.sub('', s)
    s = (s.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ء', '')
           .replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و').replace('ة', 'ه'))
    s = AR_EXTRA_PUNCT.sub(' ', s)
    s = AR_PUNCT.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def toks(n):
    return [t for t in n.split(' ') if t]


def grams(t, k=K):
    if len(t) < k:
        return [' '.join(t)] if t else []
    return [' '.join(t[i:i + k]) for i in range(len(t) - k + 1)]


def split_matn_attr(raw_ar):
    if not raw_ar:
        return [], []
    n = norm_ar(raw_ar)
    cut = len(n)
    for mk in ATTR_MARKERS:
        i = n.find(mk)
        if i != -1 and i < cut:
            cut = i
            break
    matn, attr = (n[:cut].strip(), n[cut:].strip()) if cut < len(n) else (n, '')
    return toks(matn), toks(attr)


def cited_books(attr_tokens):
    if not attr_tokens:
        return []
    a = ' '.join(attr_tokens)
    out = []
    for book, pats in BOOK_PATTERNS.items():
        if any(norm_ar(p) in a for p in pats):
            out.append(book)
    return out


def load_lidwa(book):
    p = os.path.join(SRC, 'lidwa', f'{book}.ndjson')
    if not os.path.exists(p):
        return []
    rows = []
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_book_index(rows, global_df):
    """gram -> set(row_idx). Keep only grams rare across the WHOLE corpus."""
    rows_g = []
    for r in rows:
        n = norm_ar(r.get('text_ar') or '')
        t = toks(n) if n else []
        rows_g.append({'tok': t, 'norm': n, 'no': r.get('hadith_number'), 'id': r.get('id'),
                       'g': set(grams(t))})
    inv = defaultdict(set)
    for i, rg in enumerate(rows_g):
        for g in rg['g']:
            if global_df[g] <= GLOBAL_DF_CAP:
                inv[g].add(i)
    return rows_g, inv


def phrase_anchor(nav_tok, raw_books, min_phrase=3):
    """Short-matn fallback: locate the hadith by its content phrase, verbatim.

    A 27-token matn is mostly narrator preamble ("عن أبي سعيد … قال"). Strip that,
    and the remainder ("لا ضرر ولا ضرار") is a distinctive, unambiguous phrase.
    We require the phrase to appear in the source AND the phrase to be at least
    `min_phrase` tokens, so we never anchor on a bare particle.
    """
    # drop narrator preamble: leading 'عن …' up to and including 'قال'
    toks = list(nav_tok)
    cut = 0
    for i, t in enumerate(toks):
        if t in ('قال', 'يقول', 'انه'):
            cut = i + 1
            break
    core = toks[cut:] if cut else toks
    # trim trailing grading chatter
    STOP = ('حديث', 'حسن', 'صحيح', 'رواه')
    while core and core[-1] in STOP:
        core.pop()
    if len(core) < min_phrase:
        return None

    phrase = ' '.join(core)
    found = []
    for b, rows in raw_books.items():
        for r in rows:
            if phrase in r['norm']:
                found.append({
                    'book': b, 'lidwa_no': r['no'], 'lidwa_id': r['id'],
                    'rare_grams': len(core), 'matched': len(core),
                    'score': 1.0, 'cited': False, 'tier': 'confirmed',
                    'phrase': phrase,
                })
    # prefer cited books first
    return found


def main():
    naw = load_lidwa('nawawi')
    print(f'nawawi rows: {len(naw)}')

    books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi']

    # ---- PASS 1: global document frequency across every book ----
    global_df = Counter()
    loaded = {}
    for b in books:
        rows = load_lidwa(b)
        if not rows:
            continue
        loaded[b] = rows
        for r in rows:
            n = norm_ar(r.get('text_ar') or '')
            if not n:
                continue
            for g in set(grams(toks(n))):
                global_df[g] += 1
        print(f'  df-scan {b}: {len(rows)} rows')
    print(f'  global grams: {len(global_df)}  rare(<={GLOBAL_DF_CAP}): {sum(1 for v in global_df.values() if v <= GLOBAL_DF_CAP)}')

    # ---- PASS 2: per-book rare-gram index ----
    idx = {}
    idx_raw = {}
    for b, rows in loaded.items():
        rows_g, inv = build_book_index(rows, global_df)
        idx[b] = (rows_g, inv)
        idx_raw[b] = rows_g
        print(f'  {b}: rows={len(rows_g)} rare_grams={len(inv)}')

    out = []
    for n in naw:
        nno = n.get('hadith_number')
        nav_tok, attr_tok = split_matn_attr(n.get('text_ar') or '')
        cited = cited_books(attr_tok)
        if not nav_tok:
            out.append({'nawawi_no': nno, 'status': 'empty'})
            continue
        nav_grams = grams(nav_tok)
        if len(nav_grams) < MIN_NAV_GRAMS:
            # Short matn (e.g. "لا ضرر ولا ضرار"). Fingerprints are too few to
            # score, so anchor on the DISTINCTIVE CONTENT PHRASE instead: strip the
            # narrator preamble (عن … قال) and search the remaining matn verbatim.
            anchored = phrase_anchor(nav_tok, idx_raw)
            if anchored:
                out.append({
                    'nawawi_no': nno, 'matn_toks': len(nav_tok), 'attr_toks': len(attr_tok),
                    'cited': cited, 'nav_grams': len(nav_grams),
                    'sources': anchored[:6], 'best': anchored[0],
                    'method': 'phrase_anchor', 'matn_ar': ' '.join(nav_tok),
                })
            else:
                out.append({'nawawi_no': nno, 'status': 'too_short_for_fingerprint',
                            'nav_grams': len(nav_grams), 'matn_ar': ' '.join(nav_tok),
                            'cited': cited, 'best': None, 'sources': []})
            continue

        results = []
        for b, (rows_g, inv) in idx.items():
            rare = [g for g in nav_grams if g in inv]
            if len(rare) < MIN_EVIDENCE:
                continue
            hits = Counter()
            for g in rare:
                for i in inv[g]:
                    hits[i] += 1
            for i, cnt in hits.items():
                if cnt < MIN_EVIDENCE:
                    continue          # absolute floor: 2 grams proves nothing
                rg = rows_g[i]
                score = cnt / len(rare)
                results.append({
                    'book': b, 'lidwa_no': rg['no'], 'lidwa_id': rg['id'],
                    'rare_grams': len(rare), 'matched': cnt,
                    'score': round(score, 4),
                    'cited': b in cited,
                })
        # Rank by ABSOLUTE evidence, not ratio. A 4/4 row is not a better match
        # than a 148/148 row; ratio ranks noise above signal. Ratio only breaks ties.
        results.sort(key=lambda r: (-r['matched'], -r['score']))
        seen, uniq = set(), []
        for r in results:
            key = (r['book'], r['lidwa_no'])
            if key in seen:
                continue
            seen.add(key)
            uniq.append(r)

        # Drop weak tails: once a strong match exists, keep only rows that carry a
        # meaningful share of the best evidence (compilation parallels).
        if uniq:
            best_n = uniq[0]['matched']
            uniq = [r for r in uniq if r['matched'] >= max(MIN_EVIDENCE, best_n * 0.5)]

        def tier_of(s, matched):
            # tier on evidence volume AND share; a 6/6 is not "confirmed"
            if matched < MIN_EVIDENCE:
                return 'unmapped'
            if s >= 0.60 and matched >= 8:
                return 'confirmed'
            if s >= 0.40 and matched >= MIN_EVIDENCE:
                return 'probable'
            if s >= 0.25:
                return 'review'
            return 'unmapped'

        for r in uniq:
            r['tier'] = tier_of(r['score'], r['matched'])
        keep = [r for r in uniq if r['tier'] in ('confirmed', 'probable')] or uniq[:1]
        method = 'fingerprint'
        if not keep or keep[0]['tier'] not in ('confirmed', 'probable'):
            # Fingerprinting found nothing usable (short/dense matn, heavy
            # harmonisation). Fall back to verbatim content-phrase anchoring.
            anchored = phrase_anchor(nav_tok, idx_raw)
            if anchored:
                keep = sorted(anchored, key=lambda r: (not r['cited'], r['book']))[:6]
                method = 'phrase_anchor'

        out.append({
            'nawawi_no': nno, 'matn_toks': len(nav_tok), 'attr_toks': len(attr_tok),
            'cited': cited, 'nav_grams': len(nav_grams), 'method': method,
            'sources': keep[:6], 'best': keep[0] if keep else None,
            'matn_ar': ' '.join(nav_tok),
        })

    dst = os.path.join(ROOT, 'nawawi_links.json')
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\nwrote {dst}')

    tiers = Counter(l['best']['tier'] if l.get('best') else l.get('status', 'none') for l in out)
    print('primary tiers:', dict(tiers))
    print('hadiths with >1 source:', sum(1 for l in out if len(l.get('sources') or []) > 1))
    print('\n--- per hadith ---')
    for l in sorted(out, key=lambda x: x['nawawi_no']):
        b = l.get('best')
        if not b:
            print(f"  #{l['nawawi_no']:>2}: none"); continue
        ex = ', '.join(f"{s['book']}#{s['lidwa_no']}({s['score']:.2f})"
                       for s in (l.get('sources') or [])[1:])
        print(f"  #{l['nawawi_no']:>2} ({l['matn_toks']:>3}t) -> {b['book']:<9}"
              f"#{b['lidwa_no']:<6} {b['matched']}/{b['rare_grams']} "
              f"score={b['score']:.3f} {b['tier']:<10}{'*' if b['cited'] else ' '}"
              f"{('  +' + ex) if ex else ''}")


if __name__ == '__main__':
    main()