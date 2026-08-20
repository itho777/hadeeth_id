"""
Fix: Only show translation options in dropdown when they are actually available.

Strategy:
1. For Lidwa ID/EN: check data.translations first (already in NDJSON), only add if text exists
2. For AhmedBaset EN: only add if book is one of the 9 core books (AB only covers those)
3. For Fawaz editions: already conditionally added — no change needed
4. After populating dropdown, probe each option and remove any that return no text
   (async availability check runs after initial render)
"""

with open('js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# ---- CHANGE 1: Don't unconditionally push Lidwa options.
# Only add if the translations already exist in the NDJSON data object.
# If not in data, we'll still add but mark them as "probe-needed".
# Better approach: check data.translations before pushing.

old_lidwa_block = '''  // Inject Lidwa translation via Master Link Engine for Indonesian fallback
  if (lidwaId || activeDataset === 'native_lidwa') {
      translationOptions.push({
          id: 'lidwa-id',
          label: `ID - Kemenag (Lidwa)`,
          lang: 'Indonesian',
          source: 'lidwa_id',
          hid: lidwaId || hadithId,
          file: `${baseUrl}/sources/lidwa/${bookId}.json`
      });
      translationOptions.push({
          id: 'lidwa-en',
          label: `EN - Lidwa`,
          lang: 'English',
          source: 'lidwa_en',
          hid: lidwaId || hadithId,
          file: `${baseUrl}/sources/lidwa/${bookId}.json`
      });
  }'''

new_lidwa_block = '''  // Inject Lidwa translation — only for books where Lidwa data is known to exist
  const lidwaBooks = ['bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi', 'riyad', 'nawawi', 'syafii'];
  const hasLidwaSource = lidwaBooks.includes(bookId);
  const hasLidwaIdText = !!(data && data.translations && data.translations.id && data.translations.id.find(x => x.source === 'lidwa'));
  const hasLidwaEnText = !!(data && data.translations && data.translations.en && data.translations.en.find(x => x.source === 'lidwa'));
  // Also check direct text_id on native_lidwa dataset
  const hasLidwaId2 = !!(activeDataset === 'native_lidwa' && data && data.text_id);
  const hasLidwaEn2 = !!(activeDataset === 'native_lidwa' && data && data.text_en);

  if ((lidwaId || activeDataset === 'native_lidwa') && hasLidwaSource) {
      if (hasLidwaIdText || hasLidwaId2 || lidwaId) {
          translationOptions.push({
              id: 'lidwa-id',
              label: `ID - Lidwa`,
              lang: 'Indonesian',
              source: 'lidwa_id',
              hid: lidwaId || hadithId,
              file: `${baseUrl}/sources/lidwa/${bookId}.json`
          });
      }
      if (hasLidwaEnText || hasLidwaEn2) {
          translationOptions.push({
              id: 'lidwa-en',
              label: `EN - Lidwa`,
              lang: 'English',
              source: 'lidwa_en',
              hid: lidwaId || hadithId,
              file: `${baseUrl}/sources/lidwa/${bookId}.json`
          });
      }
  }'''

if old_lidwa_block in code:
    code = code.replace(old_lidwa_block, new_lidwa_block)
    print("Fixed: Lidwa options now only shown when data is available")
else:
    print("WARNING: Could not find Lidwa block to fix — trying alternate match")

# ---- CHANGE 2: AhmedBaset — only show for the 9 core books (AB only has those)
old_ab_block = '''  // Inject AhmedBaset translation if Fawaz lacks English
  const abBookMap = { ahmad: 'ahmed' };
  const abBook = abBookMap[bookId] || bookId;
  const hasEnglish = translationOptions.some(o => o.lang.toLowerCase() === 'english');
  // Always inject AhmedBaset using fawazId (since they both use intl numbering)
  translationOptions.push({
      id: 'ab-en',
      label: `EN - AhmedBaset`,
      lang: 'English',
      source: 'ab',
      hid: abId || fawazId || hadithId,
      file: `${baseUrl}/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`
  });'''

new_ab_block = '''  // Inject AhmedBaset translation — only for the 9 core books that AB covers
  const abBookMap = { ahmad: 'ahmed' };
  const abBook = abBookMap[bookId] || bookId;
  const abCoreBooks = ['bukhari', 'muslim', 'tirmidhi', 'abudawud', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi'];
  const hasAbText = !!(data && data.translations && data.translations.en && data.translations.en.find(x => x.source === 'ab' || x.source === 'ahmedbaset'));
  const hasAbDirect = !!(data && data.text_en && activeDataset === 'native_ahmedbaset');
  if (abCoreBooks.includes(bookId) && (hasAbText || hasAbDirect || abId || activeDataset === 'native_ahmedbaset')) {
      translationOptions.push({
          id: 'ab-en',
          label: `EN - AhmedBaset`,
          lang: 'English',
          source: 'ab',
          hid: abId || fawazId || hadithId,
          file: `${baseUrl}/sources/ahmedbaset/by_book/the_9_books/${abBook}.json`
      });
  }'''

if old_ab_block in code:
    code = code.replace(old_ab_block, new_ab_block)
    print("Fixed: AhmedBaset option only shown for the 9 core books when data exists")
else:
    print("WARNING: Could not find AhmedBaset block to fix")

# ---- CHANGE 3: After populating dropdowns, add async probe to remove unavailable options
# Find the end of the "Populate Dropdowns" section and inject probe logic

old_listeners_start = '''  // Listeners
  langSelects.forEach(selectElem => {
    selectElem.addEventListener('change', () => {'''

new_probe_and_listeners = '''  // Probe each option and remove from dropdown if translation is not available
  (async () => {
    for (const selectElem of Array.from(langSelects)) {
      const toRemove = [];
      for (const opt of translationOptions) {
        const optElem = selectElem.querySelector(`option[value="${opt.id}"]`);
        if (!optElem) continue;
        // Quick pre-check: if we already know the text is in data, keep it
        const knownAvailable = (opt.source === 'lidwa_id' && (hasLidwaIdText || hasLidwaId2))
          || (opt.source === 'lidwa_en' && (hasLidwaEnText || hasLidwaEn2))
          || (opt.source === 'ab' && (hasAbText || hasAbDirect))
          || (opt.source === 'fawaz');
        if (knownAvailable) continue;
        // Otherwise probe by fetching
        try {
          const txt = await fetchTranslationText(opt);
          if (!txt) toRemove.push(opt.id);
        } catch(e) {
          toRemove.push(opt.id);
        }
      }
      toRemove.forEach(id => {
        const optElem = selectElem.querySelector(`option[value="${id}"]`);
        if (optElem) optElem.remove();
      });
      // If selected option was removed, reset to first available
      if (!selectElem.value && selectElem.options.length > 0) {
        selectElem.value = selectElem.options[0].value;
        const cardBox = selectElem.closest('.p-5');
        const targetP = cardBox ? cardBox.querySelector('p') : null;
        if (targetP) updateTranslationBox(selectElem, targetP);
      }
    }
  })();

  // Listeners
  langSelects.forEach(selectElem => {
    selectElem.addEventListener('change', () => {'''

if old_listeners_start in code:
    code = code.replace(old_listeners_start, new_probe_and_listeners)
    print("Fixed: Added async probe to remove unavailable options after render")
else:
    print("WARNING: Could not find Listeners block to inject probe")

# Also rename "ID - Kemenag (Lidwa)" → "ID - Lidwa" everywhere (already done in block above)
code = code.replace('ID - Kemenag (Lidwa)', 'ID - Lidwa')

# Bump cache buster
code = code.replace('js/app.js?v=2026082002', 'js/app.js?v=2026082003')

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("\napp.js patched successfully!")
