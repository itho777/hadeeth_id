"""Map a SHORT collection -> its source hadith(s) in Lidwa, then translations.

Generalises map_nawawi40.py. The hard part is per-collection ANCHOR selection:
collections differ wildly in structure, and picking the wrong file silently maps
chapter blobs instead of hadiths.

MEASURED STRUCTURE of Riyad as-Salihin in this repo:
  irsyadulibad/riyad.ndjson        372 rows  = CHAPTER blobs (one row bundles the
                                              whole باب incl. Qur'an verses and many
                                              hadiths; max row 44 KB). UNUSABLE.
  irsyadulibad/riyad_arab.ndjson   850 rows  = includes front-matter/intro.
  ahmedbaset/.../riyad_assalihin.json 1896 rows = TRUE hadith granularity,
                                              AR + EN, with (متفق عليه) notes. USE THIS.
  (The 1,896 count matches the canonical Riyad as-Salihin hadith total.)

Method (same as Nawawi — AR TEXT ONLY, never hadith numbering):
  1. Strip trailing source notes: (متفق عليه) / (رواه البخاري) / (رواه مسلم) etc.
  2. Rare-gram fingerprint (k=5, globally rare across the Lidwa corpus).
  3. Rank by ABSOLUTE matched grams; require MIN_EVIDENCE; share for tier.
  4. Short matn -> verbatim phrase anchor.
  5. Translations: resolve the linked hadith to ITS FAWAZ NUMBER BY ARABIC TEXT,
     then read every language at that fawaz number. Never join on Lidwa's number.
"""
import json, os, re, sys, unicodedata
from collections import defaultdict, Counter

ROOT = 'G:/hadeeth_id'
SRC = os.path.join(ROOT, 'data', 'sources')

DIACRITICS = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
AR_EXTRA_PUNCT = re.compile(r'[\u060C\u061B\u061F]')
AR_PUNCT = re.compile(r'[^\w\s\u0600-\u06FF]', re.UNICODE)
HTML_TAGS = re.compile(r'<[^>]+>')
# Invisible bidi/formatting marks. AhmedBaset wraps notes as
# "(\u200f\u200f(\u200fمتفق عليه\u200f)\u200f\u200f)" — without stripping these a
# plain '(' regex never matches and provenance is silently lost.
BIDI = re.compile(r'[\u200B-\u200F\u202A-\u202E\u2066-\u2069\uFEFF]')

# trailing provenance notes used by compilation books
NOTE_RE = re.compile(
    r'\(+\s*(?:متفق عليه|متفق علیه|رواه البخاري ومسلم|رواه مسلم|رواه البخاري|'
    r'رواه أبو داود|رواه الترمذي|رواه النسائي|رواه ابن ماجه|رواه مالك|'
    r'رواه أحمد|رواه الدارمي|رواه الدارقطني|رواه الحاكم|رواه ابن حبان|'
    r'رواه ابن خزيمة|رواه الطبراني|رواه البيهقي|رواه عبد الرزاق|'
    r'حديث حسن صحيح|حديث صحيح|حديث حسن|حديث ضعيف|صحيح|حسن|ضعيف)[^)]*\)+'
)

BOOK_PATTERNS = {
    'bukhari': ['البخاري', 'الشيخان', 'صحيحيهما'],
    'muslim': ['مسلم', 'الشيخان', 'صحيحيهما'],
    'abudawud': ['ابو داود', 'ابي داود'],
    'tirmidhi': ['الترمذي'],
    'nasai': ['النسائي', 'النساي'],
    'ibnmajah': ['ابن ماجه'],
    'malik': ['مالك', 'الموطا'],
    'ahmad': ['احمد', 'المسند'],
    'darimi': ['الدارمي'],
}

K = 5
GLOBAL_DF_CAP = 150
MIN_EVIDENCE = 4


def norm_ar(s):
    if not s:
        return ''
    s = HTML_TAGS.sub(' ', s)
    s = BIDI.sub('', s)
    s = unicodedata.normalize('NFKC', s)
    s = DIACRITICS.sub('', s)
    # Persian/Urdu orthography -> Arabic. Indo-Persian and Dehlawi-era texts use
    # ک (U+06A9) for ك, ی (U+06CC) for ي, ہ for ه, ے for ي. Without this folding a
    # phrase like 'الدنیا سجن المومن' matches ZERO rows while its hadith plainly
    # exists -- measured on fawaz ara-dehlawi.
    s = (s.replace('\u06A9', '\u0643')     # ک -> ك
           .replace('\u06CC', '\u064A')    # ی -> ي
           .replace('\u06C1', '\u0647')    # ہ -> ه
           .replace('\u06D2', '\u064A')    # ے -> ي
           .replace('\u06BE', '\u0647')    # ھ -> ه
           .replace('\u067E', '\u0628')    # پ -> ب
           .replace('\u0686', '\u062C')    # چ -> ج
           .replace('\u0698', '\u0632')    # ژ -> ز
           .replace('\u06AF', '\u0643'))   # گ -> ك
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


def strip_bidi(s):
    return BIDI.sub('', s) if s else s


def split_notes(raw):
    """Separate the hadith text from its trailing provenance note."""
    if not raw:
        return '', ''
    clean = strip_bidi(raw)
    m = NOTE_RE.search(clean)
    if not m:
        return clean, ''
    return clean[:m.start()] + clean[m.end():], m.group(0)


def cited_books(note):
    if not note:
        return []
    n = norm_ar(note)
    out = []
    for b, pats in BOOK_PATTERNS.items():
        if any(norm_ar(p) in n for p in pats):
            out.append(b)
    # 'متفق عليه' = agreed by Bukhari AND Muslim
    if (norm_ar('متفق عليه') in n or norm_ar('الشيخان') in n
            or norm_ar('صحيحيهما') in n):
        for b in ('bukhari', 'muslim'):
            if b not in out:
                out.append(b)
    return out


def load_lidwa(book):
    p = os.path.join(SRC, 'lidwa', f'{book}.ndjson')
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_anchor(kind, name):
    """Load the ANCHOR collection with hadith granularity."""
    if kind == 'ahmedbaset_other':
        p = os.path.join(SRC, 'ahmedbaset', 'by_book', 'other_books', f'{name}.json')
        if not os.path.exists(p):
            return []
        d = json.load(open(p, encoding='utf-8'))
        rows = []
        for h in d.get('hadiths', []):
            rows.append({
                'no': h.get('idInBook'),
                'ar': h.get('arabic') or '',
                'en': (h.get('english') or {}).get('text') if isinstance(h.get('english'), dict) else None,
                'en_narrator': (h.get('english') or {}).get('narrator') if isinstance(h.get('english'), dict) else None,
            })
        return rows
    if kind == 'ahmedbaset_forties':
        p = os.path.join(SRC, 'ahmedbaset', 'by_book', 'forties', f'{name}.json')
        if not os.path.exists(p):
            return []
        d = json.load(open(p, encoding='utf-8'))
        rows = []
        for h in d.get('hadiths', []):
            en = h.get('english')
            rows.append({
                'no': h.get('idInBook'),
                'ar': h.get('arabic') or '',
                'en': en.get('text') if isinstance(en, dict) else None,
                'en_narrator': en.get('narrator') if isinstance(en, dict) else None,
            })
        return rows
    if kind == 'fawaz':
        p = os.path.join(SRC, 'fawaz_api', 'editions', f'ara-{name}.min.json')
        if not os.path.exists(p):
            return []
        d = json.load(open(p, encoding='utf-8'))
        return [{'no': h.get('hadithnumber'), 'ar': h.get('text') or '', 'en': None}
                for h in d.get('hadiths', [])]
    if kind == 'mjna':
        p = os.path.join(SRC, 'mjna', f'{name}.ndjson')
        if not os.path.exists(p):
            return []
        out = []
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out.append({'no': r.get('hadith_number') or r.get('number'),
                        'ar': r.get('text_ar') or '', 'en': r.get('text_en') or None})
        return out
    if kind == 'irsyadulibad':
        # rows carry an inline numbering prefix ("مسند الشافعي 12: ...") that is
        # editorial, not part of the hadith — strip it or the matn never matches.
        p = os.path.join(SRC, 'irsyadulibad', f'{name}.ndjson')
        if not os.path.exists(p):
            return []
        out = []
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            ar = re.sub(r'^\s*[^\d:]{2,40}\s*\d+\s*:\s*', '', r.get('text_ar') or '')
            out.append({'no': r.get('hadith_number'), 'ar': ar,
                        'en': r.get('text_en') or None,
                        'id': r.get('text_id') or None})
        return out
    return []


def build_book_index(rows, global_df):
    items = []
    for r in rows:
        n = norm_ar(r.get('text_ar') or '')
        t = toks(n) if n else []
        items.append({'tok': t, 'norm': n, 'no': r.get('hadith_number'), 'id': r.get('id'),
                      'g': set(grams(t))})
    inv = defaultdict(set)
    for i, it in enumerate(items):
        for g in it['g']:
            if global_df[g] <= GLOBAL_DF_CAP:
                inv[g].add(i)
    return items, inv


def phrase_anchor(anchor_tok, raw_books, min_phrase=2):
    """Verbatim content-phrase anchoring.

    Needed for collections of MAXIMS (Dehlawi 40 is 2-3 tokens per hadith:
    'الحرب خدعة', 'المسلم مرآة المسلم'). Fingerprinting cannot work below ~6 grams
    and LCS is meaningless on 2 tokens, so the only honest method is: does this
    exact phrase occur inside a source hadith?
    Trim narrator preamble / grading chatter first, then require the remaining
    phrase to be at least `min_phrase` tokens so we never anchor on a bare particle.
    """
    t = list(anchor_tok)
    cut = 0
    for i, x in enumerate(t):
        if x in ('قال', 'يقول', 'انه', 'قالت'):
            cut = i + 1
            break
    core = t[cut:] if cut else t
    STOP = ('حديث', 'حسن', 'صحيح', 'رواه', 'متفق', 'عليه', 'متقن')
    while core and core[-1] in STOP:
        core.pop()
    if len(core) < min_phrase:
        return []
    phrase = ' '.join(core)
    # Try the full phrase, then progressively shorter prefixes so a source that
    # quotes only part of the maxim still links.
    variants = [phrase]
    if len(core) > 3:
        variants.append(' '.join(core[:len(core) - 1]))
    if len(core) > 4:
        variants.append(' '.join(core[:max(3, len(core) // 2)]))
    found = []
    for b, items in raw_books.items():
        for it in items:
            for v in variants:
                if v and v in it['norm']:
                    found.append({'book': b, 'lidwa_no': it['no'], 'lidwa_id': it['id'],
                                  'rare_grams': len(core), 'matched': len(v.split(' ')),
                                  'score': round(len(v.split(' ')) / len(core), 4),
                                  'cited': False, 'tier': 'confirmed' if v == phrase else 'probable',
                                  'phrase': v})
                    break
    # strongest first: full-phrase hits before partial ones
    found.sort(key=lambda r: (-r['matched'], r['book']))
    return found


def tier_of(score, matched):
    if matched < MIN_EVIDENCE:
        return 'unmapped'
    if score >= 0.60 and matched >= 8:
        return 'confirmed'
    if score >= 0.40:
        return 'probable'
    if score >= 0.25:
        return 'review'
    return 'unmapped'


def run(anchor_kind, anchor_name, out_stem):
    anchor = load_anchor(anchor_kind, anchor_name)
    print(f'anchor {anchor_kind}/{anchor_name}: {len(anchor)} hadiths')
    if not anchor:
        print('no anchor rows'); return

    books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah',
             'malik', 'ahmad', 'darimi']

    # PASS 1: global df
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
    print(f'global grams: {len(global_df)}')

    # PASS 2: index
    idx, idx_raw = {}, {}
    for b, rows in loaded.items():
        items, inv = build_book_index(rows, global_df)
        idx[b] = (items, inv)
        idx_raw[b] = items
        print(f'  {b}: {len(items)} rows')

    out = []
    for h in anchor:
        no = h['no']
        raw_ar = h['ar']
        body, note = split_notes(raw_ar)
        cited = cited_books(note)
        at = toks(norm_ar(body))
        if not at:
            out.append({'no': no, 'status': 'empty_after_note_strip'})
            continue
        ag = grams(at)
        results = []
        for b, (items, inv) in idx.items():
            rare = [g for g in ag if g in inv]
            if len(rare) < MIN_EVIDENCE:
                continue
            hits = Counter()
            for g in rare:
                for i in inv[g]:
                    hits[i] += 1
            for i, cnt in hits.items():
                if cnt < MIN_EVIDENCE:
                    continue
                it = items[i]
                results.append({
                    'book': b, 'lidwa_no': it['no'], 'lidwa_id': it['id'],
                    'rare_grams': len(rare), 'matched': cnt,
                    'score': round(cnt / len(rare), 4), 'cited': b in cited,
                })
        results.sort(key=lambda r: (-r['matched'], -r['score']))
        seen, uniq = set(), []
        for r in results:
            key = (r['book'], r['lidwa_no'])
            if key in seen:
                continue
            seen.add(key)
            uniq.append(r)
        if uniq:
            top_n = uniq[0]['matched']
            uniq = [r for r in uniq if r['matched'] >= max(MIN_EVIDENCE, top_n * 0.5)]
        for r in uniq:
            r['tier'] = tier_of(r['score'], r['matched'])
        keep = [r for r in uniq if r['tier'] in ('confirmed', 'probable')] or uniq[:1]
        method = 'fingerprint'
        if not keep or keep[0]['tier'] not in ('confirmed', 'probable'):
            anchored = phrase_anchor(at, idx_raw)
            if anchored:
                keep = sorted(anchored, key=lambda r: (not r['cited'], r['book']))[:6]
                method = 'phrase_anchor'

        out.append({
            'no': no, 'matn_toks': len(at), 'cited': cited, 'method': method,
            'sources': keep[:6], 'best': keep[0] if keep else None,
            'ar': body.strip(), 'en': h.get('en'), 'en_narrator': h.get('en_narrator'),
        })

    dst = os.path.join(ROOT, f'{out_stem}_links.json')
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\nwrote {dst}')
    tiers = Counter(x['best']['tier'] if x.get('best') else x.get('status', 'none') for x in out)
    print('tiers:', dict(tiers))
    print('linked:', sum(1 for x in out if x.get('sources')),
          ' multi:', sum(1 for x in out if len(x.get('sources') or []) > 1))
    return out


if __name__ == '__main__':
    kind = sys.argv[1] if len(sys.argv) > 1 else 'ahmedbaset_other'
    name = sys.argv[2] if len(sys.argv) > 2 else 'riyad_assalihin'
    stem = sys.argv[3] if len(sys.argv) > 3 else 'riyad'
    run(kind, name, stem)