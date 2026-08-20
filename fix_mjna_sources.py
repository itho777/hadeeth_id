"""
Fix 3 issues in js/app.js:
1. Arabic titles for MJNA books' chapter cards (fix garbled title_ar in lidwa-chapters json too)
2. Replace "Lidwa Kitab" / "Lidwa Hadith" labels with correct source labels (MJNA.or.id for the 4 new books, Lidwa only for the 9 core books)
3. Fix hadith loading for MJNA books - load from data/sources/mjna/ not data/sources/lidwa/
"""

import json
import re

MJNA_BOOKS = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni']
MJNA_ARABIC = {
    'ibnukhuzaimah': 'صحيح ابن خزيمة',
    'ibnuhibban': 'صحيح ابن حبان',
    'mustadrak': 'مستدرك الحاكم',
    'daruquthni': 'سنن الدارقطني',
}
MJNA_TITLES_EN = {
    'ibnukhuzaimah': 'Shahih Ibnu Khuzaimah',
    'ibnuhibban': 'Shahih Ibnu Hibban',
    'mustadrak': 'Mustadrak Al-Hakim',
    'daruquthni': 'Sunan Daruquthni',
}
MJNA_TITLES_ID = {
    'ibnukhuzaimah': 'Shahih Ibnu Khuzaimah',
    'ibnuhibban': 'Shahih Ibnu Hibban',
    'mustadrak': 'Mustadrak Al-Hakim',
    'daruquthni': 'Sunan Daruquthni',
}

# Fix lidwa-chapters/<book>.json — correct the title_ar on the single chapter entry
for book in MJNA_BOOKS:
    path = f'data/lidwa-chapters/{book}.json'
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    d['title_id_source'] = 'MJNA.or.id'
    d['title_en_source'] = 'MJNA.or.id'
    for ch in d.get('chapters', []):
        ch['title_ar'] = MJNA_ARABIC[book]
        ch['title_en'] = MJNA_TITLES_EN[book]
        ch['title_id'] = MJNA_TITLES_ID[book]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"Fixed {path}")

print("\nChapter JSON files fixed. Now patching app.js...")

with open('js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# ---- FIX 1: In BRANCH C (kitab page chapter listing), 
#   replace "Lidwa ${hadithRange}..." with source-aware label
old_ch_label = '`Lidwa ${hadithRange}${hadithCount ? ` &bull; ${hadithCount} hadits` : \'\'}`'
# We need to make the label source-aware. The source info is already in lidwaIndex.
# Replace the entire span text in the chapter card (line 2706 area)
old_span = "                <span class=\"text-xs text-outline dark:text-gray-400 font-semibold\">Lidwa ${hadithRange}${hadithCount ? ` &bull; ${hadithCount} hadits` : ''}</span>"
new_span = "                <span class=\"text-xs text-outline dark:text-gray-400 font-semibold\">${idSource} ${hadithRange}${hadithCount ? ` &bull; ${hadithCount} hadits` : ''}</span>"
if old_span in code:
    code = code.replace(old_span, new_span)
    print("Fixed: chapter card source label (Lidwa -> idSource variable)")
else:
    print("WARNING: Could not find chapter card Lidwa span to fix")

# ---- FIX 2: In BRANCH C hadith-list loading, load from mjna path for MJNA books
# Currently: const lidwaAll = await window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId)
# We need to detect if it's an MJNA book and use 'sources/mjna' instead
old_lidwa_fetch = "      const lidwaAll = await window.HadeethAPI.fetchNdjsonFull('sources/lidwa', bookId).catch(() => null);"
new_lidwa_fetch = """      const mjnaBooks = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];
      const isMjnaBook = mjnaBooks.includes(bookId);
      const nativeSourceDir = isMjnaBook ? 'sources/mjna' : 'sources/lidwa';
      const nativeSourceLabel = isMjnaBook ? 'MJNA.or.id' : 'Lidwa';
      const lidwaAll = await window.HadeethAPI.fetchNdjsonFull(nativeSourceDir, bookId).catch(() => null);"""

if old_lidwa_fetch in code:
    code = code.replace(old_lidwa_fetch, new_lidwa_fetch)
    print("Fixed: MJNA books load from sources/mjna instead of sources/lidwa")
else:
    print("WARNING: Could not find lidwa fetch line to fix")

# ---- FIX 3: Replace hardcoded "Lidwa Kitab" / "Lidwa Hadith" labels in the hadith-list loading code
old_meta_en = '`Lidwa Kitab ${chapterId}`'
new_meta_en = '`${nativeSourceLabel} Kitab ${chapterId}`'
count = code.count(old_meta_en)
code = code.replace(old_meta_en, new_meta_en)
print(f"Fixed: {count}x 'Lidwa Kitab' -> '{new_meta_en}'")

old_count_en = '`Lidwa Hadith ${rangeStr} \u2022 ${total} Hadiths in ${bookName} Kitab ${chapterId}`'
new_count_en = '`${nativeSourceLabel} Hadith ${rangeStr} \u2022 ${total} Hadiths in ${bookName} Kitab ${chapterId}`'
code = code.replace(old_count_en, new_count_en)

old_count_id = '`Lidwa Hadits ${rangeStr} \u2022 ${total} Hadits dalam ${bookName} Kitab ${chapterId}`'
new_count_id = '`${nativeSourceLabel} Hadits ${rangeStr} \u2022 ${total} Hadits dalam ${bookName} Kitab ${chapterId}`'
code = code.replace(old_count_id, new_count_id)

old_count_fallback = '`${total} Hadits \u2014 Lidwa Kitab ${chapterId}`'
new_count_fallback = '`${total} Hadits \u2014 ${nativeSourceLabel} Kitab ${chapterId}`'
code = code.replace(old_count_fallback, new_count_fallback)
print("Fixed: Lidwa count labels -> nativeSourceLabel")

# ---- FIX 4: Fix the BRANCH C comment header to be more neutral
code = code.replace(
    '// BRANCH C \u2014 Lidwa / Irsyad (native ID + AR, EN from AhmedBaset where matched)\n  // Reads from data/lidwa-chapters/<book>.json (pre-built index)',
    '// BRANCH C \u2014 Native source loading (Lidwa for 9 books, MJNA.or.id for additional books)\n  // Reads from data/lidwa-chapters/<book>.json (pre-built index)'
)

# Also fix the comment in hadith-list loading
code = code.replace(
    '// BRANCH C \u2014 Lidwa / Irsyad native hadith loading',
    '// BRANCH C \u2014 Native source hadith loading (Lidwa / MJNA.or.id)'
)
code = code.replace(
    "// Fetch English + Arabic from fawazahmed0 CDN; Indonesian from Lidwa source directly",
    "// Fetch English + Arabic from fawazahmed0 CDN; Indonesian from source data (Lidwa / IrsyadulIbad / MJNA.or.id)"
)
code = code.replace(
    "// Load Indonesian live from Lidwa/Irsyad source data",
    "// Load Indonesian from native source data (Lidwa / IrsyadulIbad / MJNA.or.id / etc.)"
)
print("Fixed: Comments updated to reflect correct sources")

# ---- FIX 5: Fix the "Lidwa chapter data not available" error message
code = code.replace(
    '        <p>Lidwa chapter data not available for <strong>${bookId}</strong>.</p>',
    '        <p>Chapter data not available for <strong>${bookId}</strong>.</p>'
)

# ---- FIX 6: Fix "Lidwa chapter index fetch error" console warning
code = code.replace(
    "console.warn('Lidwa chapter index fetch error:', e);",
    "console.warn('Chapter index fetch error:', e);"
)

# Bump cache buster
code = code.replace('js/app.js?v=2026082001', 'js/app.js?v=2026082002')

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("\napp.js patched successfully!")
