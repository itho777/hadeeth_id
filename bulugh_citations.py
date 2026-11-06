"""Bulugh al-Maram carries Al-Albani's editorial apparatus inline.

Row shapes observed (441 of 1767 rows fail a plain text match):
  1. Variant / cross-reference rows that are NOT standalone hadiths:
       "وَهُوَ طَرَفٌ مِنْ الْحَدِيثِ الطَّوِيلِ الْمُتَقَدِّمِ ..."  -> points at an
       earlier hadith; the right answer is a POINTER, not a source link.
  2. Rows whose matn sits inside { ... } with the isnad/commentary outside.
  3. Rows that DO cite their source explicitly:
       "رواه أبو داود (775) ، والنسائي (2/132) ، والترمذي (242) ، وابن ماجه (804)"
       "وَلِمُسْلِمٍ عَنْهَا :"                -> Muslim
       "وَفِي رِوَايَةٍ لِلْبُخَارِيِّ :"        -> Bukhari
       "وَمِثْلُهُ عِنْدَ ابْنِ خُزَيْمَةَ"
     These give book + often the hadith NUMBER IN PARENS.

STRATEGY (strict priority, no guessing):
  a) Explicit numeric citation  "رواه X (NNN)"  -> link book X to hadith NNN, then
     VERIFY the number's Arabic text actually overlaps our matn. A number in a
     citation is a claim; we confirm it against text before accepting.
  b) Explicit book mention with no number -> search THAT book only, using the
     {braced} matn as the query.
  c) Cross-reference rows -> emit a `points_to` reference, no source link.
  d) Otherwise leave unmapped. Never invent.

Writes: bulugh_links.json (upgraded: adds resolved citations + points_to)
"""
import json, os, re, sys, unicodedata
from collections import Counter

ROOT = 'G:/hadeeth_id'
SRC = os.path.join(ROOT, 'data', 'sources')

BIDI = re.compile(r'[\u200B-\u200F\u202A-\u202E\u2066-\u2069\uFEFF]')
DIAC = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')
AR_PUNCT = re.compile(r'[^\w\s\u0600-\u06FF]', re.UNICODE)
AR_EXTRA = re.compile(r'[\u060C\u061B\u061F]')
HTML = re.compile(r'<[^>]+>')

# editorial apparatus that must be stripped from the matn
EDITORIAL = re.compile(
    r'\b(?:\d+\s*\.\s*\d+\s*-\s*|ضعيف|صحيح|حسن|لا يصح|قلت|انظر|رقم|البخاري برقم)'
)

BOOK_HINTS = {
    'bukhari': ['البخاري', 'البخارى', 'للشيخين', 'متفق عليه'],
    'muslim': ['مسلم', 'للشيخين', 'متفق عليه'],
    'abudawud': ['أبو داود', 'ابو داود', 'أبي داود'],
    'tirmidhi': ['الترمذي', 'الترمذى'],
    'nasai': ['النسائي', 'النسائى', 'النساي'],
    'ibnmajah': ['ابن ماجه', 'ابن ماجة'],
    'malik': ['مالك', 'الموطأ'],
    'ahmad': ['أحمد', 'أحمد بن حنبل'],
    'darimi': ['الدارمي'],
    'daruquthni': ['الدارقطني'],
    'ibnkhuzaimah': ['ابن خزيمة'],
    'ibnhibban': ['ابن حبان'],
    'hakim': ['الحاكم'],
    'khamsah': ['الخمسة', 'الخمسه', 'الأربعة'],
}


def norm_ar(s):
    if not s:
        return ''
    s = HTML.sub(' ', s)
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


def extract_braced(raw):
    """The actual matn of a variant row usually sits inside { ... }."""
    m = re.findall(r'\{([^{}]{10,})\}', raw or '')
    return max(m, key=len) if m else ''


CITE_RE = re.compile(
    r'(?:رواه|رواة|عند|لِل|في رواية ل|وفي رواية ل|أخرجه)?\s*'
    r'(البخاري|مسلم|أبو داود|ابو داود|الترمذي|النسائي|النسائى|ابن ماجه|ابن ماجة|'
    r'مالك|أحمد|الدارمي)\s*\(?(\d{1,5})?\)?'
)


def parse_citations(raw):
    """Return [(book, number|None), ...] from an explicit citation."""
    out = []
    n = norm_ar(raw)
    for m in CITE_RE.finditer(n):
        raw_book = m.group(1)
        num = m.group(2)
        book = None
        for b, hints in BOOK_HINTS.items():
            if any(norm_ar(h) in norm_ar(raw_book) for h in hints):
                book = b
                break
        if book:
            out.append((book, int(num) if num else None))
    # dedupe preserving order
    seen, res = set(), []
    for b, n2 in out:
        if (b, n2) in seen:
            continue
        seen.add((b, n2))
        res.append((b, n2))
    return res


CROSSREF_RE = re.compile(r'(?:طرف من الحديث|الحديث المتقدم|الحديث السابق|'
                         r'تقدم|سبق|انظر الحديث|رقم \(\s*\d+\)|الحديث رقم)')


def main():
    path = os.path.join(ROOT, 'bulugh_links.json')
    data = json.load(open(path, encoding='utf-8'))

    # load lidwa books by number for verification
    books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah',
             'malik', 'ahmad', 'darimi']
    lidwa = {}
    for b in books:
        p = os.path.join(SRC, 'lidwa', f'{b}.ndjson')
        if not os.path.exists(p):
            continue
        lidwa[b] = {}
        for line in open(p, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            lidwa[b][r.get('hadith_number')] = r

    stat = Counter()
    for rec in data:
        raw = rec.get('ar') or ''
        if rec.get('sources'):
            stat['already_linked'] += 1
            continue
        nraw = norm_ar(raw)
        cites = parse_citations(raw)

        # (c) pure cross-reference row
        if CROSSREF_RE.search(nraw) and not cites:
            rec['points_to'] = {'kind': 'cross_reference',
                                'note': 'Bulugh row references another hadith, not a new one'}
            stat['crossref'] += 1
            continue

        query = norm_ar(extract_braced(raw)) or nraw
        qt = set(toks(query)[i] for i in range(min(len(toks(query)), 12)))

        resolved = []
        # A NUMBERED citation is authoritative. 'متفق عليه' / 'للخمسة' expand to
        # book lists but carry no number, so they must not generate extra links
        # when a numbered citation already identifies the hadith. Observed: Bulugh
        # #1564 numbers Tirmidhi 3428 (matn 8/9 tokens present) while the generic
        # 'متفق عليه' also produced Bukhari 2736, a different hadith -> false conflict.
        numbered = [(b, n) for b, n in cites if n is not None]
        unnumbered = [(b, n) for b, n in cites if n is None]
        use = numbered if numbered else unnumbered
        for b, num in use:
            if b == 'khamsah':
                stat['khamsah_unresolved'] += 1
                continue
            if b not in lidwa:
                stat['cited_book_not_in_lidwa'] += 1
                continue
            if num is None:
                # (b) book known, number unknown -> text search within that book only
                best = None
                for no, r in lidwa[b].items():
                    rn = norm_ar(r.get('text_ar') or '')
                    if not rn:
                        continue
                    overlap = len(qt & set(toks(rn)))
                    if overlap >= max(3, int(len(qt) * 0.6)):
                        if best is None or overlap > best[0]:
                            best = (overlap, no)
                if best:
                    resolved.append({'book': b, 'lidwa_no': best[1],
                                     'method': 'cited_book_text_search',
                                     'overlap': best[0], 'tier': 'probable'})
                    stat['cited_book_textsearch'] += 1
                continue
            # (a) explicit number -> VERIFY by text, but against the MATN only.
            # Bulugh wraps the actual matn in { ... }; the surrounding isnad and
            # commentary are Albani's, not the source's, so including them dilutes
            # the overlap and produces false "unverified" verdicts (observed: a
            # 2-token matn like "في الإثم" can never pass a percentage-of-query test).
            r = lidwa[b].get(num)
            if not r:
                stat['cited_number_missing'] += 1
                continue
            rn = norm_ar(r.get('text_ar') or '')
            rtoks = set(toks(rn))
            braced = norm_ar(extract_braced(raw))
            if braced:
                # A braced matn IS the hadith text. Never slice it — the earlier
                # 'drop narrator preamble' rule assumed an isnad inside the query
                # and silently deleted the matn itself (Tirmidhi 3428 scored 0
                # against a row whose matn is verbatim present).
                core_tokens = toks(braced)
            else:
                mj = toks(query)
                core_tokens = mj[3:] if len(mj) > 8 else mj
            core = set(core_tokens)
            overlap = len(core & rtoks)
            if len(core_tokens) < 3:
                verdict = 'short_matn_citation_trusted'
                ok = None
            else:
                need = max(2, int(len(core) * (0.5 if len(core) <= 8 else 0.4)))
                ok = overlap >= need
                verdict = 'verified' if ok else 'number_conflict'
            tier = 'confirmed' if ok else ('probable' if ok is None else 'review')
            if ok is False:
                # The cited number does NOT carry this matn. Two possibilities we
                # cannot distinguish from here: (a) Bulugh's number refers to a
                # different edition/own-numbering, (b) the matn is abbreviated past
                # recognition. Either way the numeric claim is UNPROVEN, so it is
                # recorded as provenance only and never as a source link.
                rec.setdefault('citation_unverified', []).append({
                    'book': b, 'cited_no': num, 'overlap': overlap,
                    'core_tokens': len(core),
                    'reason': 'cited number does not contain this matn'})
                stat['cited_number_recorded_unverified'] += 1
                continue
            resolved.append({'book': b, 'lidwa_no': num,
                             'method': 'cited_number',
                             'overlap': overlap, 'core_tokens': len(core),
                             'tier': tier, 'text_verified': ok,
                             'verdict': verdict})
            stat['cited_number_' + verdict] += 1

        if resolved:
            rec['sources'] = resolved
            rec['best'] = sorted(resolved, key=lambda x: -x['overlap'])[0]
            rec['method'] = 'citation'
            stat['citation_linked'] += 1
        else:
            stat['still_unmapped'] += 1

    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('bulugh_links.json upgraded')
    for k, v in stat.most_common():
        print(f'  {k}: {v}')
    linked = sum(1 for x in data if x.get('sources'))
    print(f'\nlinked now: {linked}/{len(data)} ({100*linked/len(data):.1f}%)')


if __name__ == '__main__':
    main()