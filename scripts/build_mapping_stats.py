"""Emit the exact mapping statistics consumed by docs.html.

Single source of truth: docs must never state a number that isn't computed here.
Writes ../data/mapping-stats.json (served by the CDN alongside the rest of data/).
"""
import json, os
from collections import Counter

ROOT = 'G:/hadeeth_id'
OUT = os.path.join(ROOT, 'data', 'mapping-stats.json')

COLLECTIONS = [
    ('riyad', 'Riyad as-Salihin', 'رياض الصالحين', 'Imam an-Nawawi',
     'AhmedBaset `/other_books/riyad_assalihin.json`'),
    ('nawawi', 'Nawawi 40', 'الأربعون النووية', 'Imam an-Nawawi',
     'Lidwa `nawawi.ndjson`'),
    ('bulugh', 'Bulugh al-Maram', 'بلوغ المرام', 'al-Hafiz Ibn Hajar',
     'AhmedBaset `/other_books/bulugh_almaram.json`'),
    ('mishkat', 'Mishkat al-Masabih', 'مشكاة المصابيح', 'al-Khatib at-Tibrizi',
     'AhmedBaset `/other_books/mishkat_almasabih.json`'),
    ('shamail', 'Shamail Muhammadiyah', 'الشمائل المحمدية', 'Imam at-Tirmidhi',
     'AhmedBaset `/other_books/shamail_muhammadiyah.json`'),
    ('aladab', 'Al-Adab al-Mufrad', 'الأدب المفرد', 'Imam al-Bukhari',
     'AhmedBaset `/other_books/aladab_almufrad.json`'),
    ('qudsi', 'Hadith Qudsi 40', 'الأربعون القدسية', '—',
     'Fawaz `ara-qudsi`'),
    ('dehlawi', 'Dehlawi 40 (Shah Waliullah)', 'أربعون الدهلوي', 'Shah Waliullah al-Dehlawi',
     'Fawaz `ara-dehlawi`'),
    ('ibnuhibban', 'Sahih Ibn Hibban', 'صحيح ابن حبان', 'Ibn Hibban',
     'MJNA `ibnuhibban.ndjson`'),
    ('ibnukhuzaimah', 'Sahih Ibn Khuzaimah', 'صحيح ابن خزيمة', 'Ibn Khuzaimah',
     'MJNA `ibnukhuzaimah.ndjson`'),
    ('mustadrak', 'Mustadrak al-Hakim', 'المستدرك على الصحيحين', 'al-Hakim an-Naysaburi',
     'MJNA `mustadrak.ndjson`'),
    ('daruquthni', 'Sunan Daruquthni', 'سنن الدارقطني', 'al-Daraqutni',
     'MJNA `daruquthni.ndjson`'),
    ('syafii', 'Musnad Syafii', 'مسند الشافعي', 'Imam asy-Syafii',
     'Irsyadulibad `syafii.ndjson`'),
]

# duplicate sources that share text with another collection
DUPLICATES = [{
    'a': 'Dehlawi 40 (Fawaz `ara-dehlawi`)',
    'b': 'Shah Waliullah 40 (AhmedBaset `forties/shahwaliullah40`)',
    'finding': 'Identical Arabic in all 40/40 rows; metadata author is '
               '“الشاه ولي الدين الدهلوي”. Same book, two files. Counted once.',
}]


def main():
    rows, total, total_links, T = [], 0, 0, 0
    tiers_sum = Counter()
    for stem, name, name_ar, author, anchor in COLLECTIONS:
        p = os.path.join(ROOT, f'{stem}_links.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        linked = sum(1 for x in d if x.get('sources'))
        links = sum(len(x.get('sources') or []) for x in d)
        t = Counter((x.get('best') or {}).get('tier', 'none') for x in d)
        meth = Counter(x.get('method', 'fingerprint') for x in d if x.get('sources'))
        conf, prob = t.get('confirmed', 0), t.get('probable', 0)
        reviews = sum(1 for x in d for s in (x.get('sources') or [])
                      if s.get('tier') == 'review')
        cu = sum(len(x.get('citation_unverified') or []) for x in d)
        rows.append({
            'id': stem, 'name': name, 'name_ar': name_ar, 'author': author,
            'anchor': anchor, 'total': len(d), 'linked': linked,
            'unmapped': len(d) - linked,
            'pct': round(100 * linked / max(1, len(d)), 1),
            'links': links, 'confirmed': conf, 'probable': prob,
            'review_links': reviews,
            'conf_pct': round(100 * conf / max(1, linked), 1),
            'methods': dict(meth),
            'citation_unverified': cu,
        })
        total += len(d)
        total_links += links
        tiers_sum['confirmed'] += conf
        tiers_sum['probable'] += prob
        T += linked

    payload = {
        'generated_by': 'scripts/build_mapping_stats.py',
        'verified_on': '2026-11-05',
        'method': 'Arabic-text matching (never hadith numbering)',
        'totals': {
            'collections': len(rows),
            'hadiths': total,
            'linked': T,
            'unmapped': total - T,
            'pct': round(100 * T / max(1, total), 1),
            'source_links': total_links,
            'confirmed': tiers_sum['confirmed'],
            'probable': tiers_sum['probable'],
            'conf_pct': round(100 * tiers_sum['confirmed'] / max(1, T), 1),
        },
        'collections': rows,
        'duplicates': DUPLICATES,
    }
    json.dump(payload, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'wrote {OUT}')
    print(json.dumps(payload['totals'], indent=1))
    for r in rows:
        print(f"  {r['name']:<32}{r['total']:>6}{r['linked']:>7}{r['pct']:>6}%"
              f"{r['links']:>7}  conf {r['conf_pct']:>5}%")


if __name__ == '__main__':
    main()