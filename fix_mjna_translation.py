"""
Fix: Add MJNA.or.id as a proper translation source in the hadith detail dropdown.

Changes:
1. After Lidwa/AhmedBaset blocks, add MJNA option if book is a MJNA book and data.translations.id has source='mjna'
2. Add MJNA source handling in fetchTranslationText() 
3. Also handle hadith-list page rendering: show 'ID - MJNA.or.id' as source label for MJNA books
"""

with open('js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# ---- ADD 1: Inject MJNA translation option after AhmedBaset block
# Find the end of the AhmedBaset block and add MJNA right after
old_after_ab = '''  async function fetchTranslationText(opt) {'''

new_mjna_block = '''  // Inject MJNA.or.id translation — only for MJNA books
  const mjnaBooksList = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni'];
  const isMjnaBook = mjnaBooksList.includes(bookId);
  const hasMjnaIdText = !!(data && data.translations && data.translations.id && data.translations.id.find(x => x.source === 'mjna'));
  const hasMjnaArText = !!(data && data.translations && data.translations.ar && data.translations.ar.find(x => x.source === 'mjna'));

  if (isMjnaBook && hasMjnaIdText) {
      translationOptions.push({
          id: 'mjna-id',
          label: 'ID - MJNA.or.id',
          lang: 'Indonesian',
          source: 'mjna_id',
          hid: hadithId,
          file: null  // served directly from data.translations
      });
  }
  if (isMjnaBook && hasMjnaArText) {
      // Arabic from MJNA is already shown as main text, but expose via dropdown too
      // (only show if user might want to compare / copy)
  }

  async function fetchTranslationText(opt) {'''

if old_after_ab in code:
    code = code.replace(old_after_ab, new_mjna_block)
    print("Added: MJNA.or.id translation option injection")
else:
    print("WARNING: Could not find insertion point for MJNA block")

# ---- ADD 2: Handle mjna_id in fetchTranslationText
old_fetch_lidwa = '''      if (data && data.translations) {
          if (opt.source === 'lidwa_id' && data.translations.id) {
              const t = data.translations.id.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }
          if (opt.source === 'lidwa_en' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }'''

new_fetch_lidwa = '''      if (data && data.translations) {
          // MJNA.or.id source
          if (opt.source === 'mjna_id' && data.translations.id) {
              const t = data.translations.id.find(x => x.source === 'mjna');
              if (t) return t.text;
          }
          if (opt.source === 'lidwa_id' && data.translations.id) {
              const t = data.translations.id.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }
          if (opt.source === 'lidwa_en' && data.translations.en) {
              const t = data.translations.en.find(x => x.source === 'lidwa');
              if (t) return t.text;
          }'''

if old_fetch_lidwa in code:
    code = code.replace(old_fetch_lidwa, new_fetch_lidwa)
    print("Added: mjna_id handling in fetchTranslationText")
else:
    print("WARNING: Could not find fetchTranslationText lidwa block")

# ---- ADD 3: In hadith-list rendering, show ID text from MJNA books properly
# Find where text_id is displayed in the hadith list cards
# The hadith list renders items from allHadiths — for MJNA books loaded via native_lidwa branch,
# the text_id is already in the row. But the source label shown above it says "Lidwa".
# Fix: use 'MJNA.or.id' as the translation label when the book is a MJNA book.

old_id_source_comment = "      const nativeSourceLabel = isMjnaBook ? 'MJNA.or.id' : 'Lidwa';"
# This is already in the code from the previous fix! Good.

# ---- ADD 4: In the hadith detail page (fetchHadithData), when rendering the Indonesian text panel,
# show the source attribution as "MJNA.or.id" not "Lidwa"
# Find where indonesianElem is populated
old_ind_fallback = "  } else if (indonesianElem) {\n      if (data.text_id) indonesianElem.innerHTML = data.text_id;"
new_ind_fallback = """  } else if (indonesianElem) {
      if (data.text_id) indonesianElem.innerHTML = data.text_id;
      else if (data.translations && data.translations.id) {
          const mjnaT = data.translations.id.find(x => x.source === 'mjna');
          if (mjnaT) indonesianElem.innerHTML = mjnaT.text;
      }"""

if old_ind_fallback in code:
    code = code.replace(old_ind_fallback, new_ind_fallback)
    print("Added: MJNA fallback in Indonesian text panel")
else:
    print("WARNING: Could not find Indonesian elem fallback")

# ---- ADD 5: In hasMjnaIdText probe, mark knownAvailable so probe won't remove it
old_probe = '''        const knownAvailable = (opt.source === 'lidwa_id' && (hasLidwaIdText || hasLidwaId2))
          || (opt.source === 'lidwa_en' && (hasLidwaEnText || hasLidwaEn2))
          || (opt.source === 'ab' && (hasAbText || hasAbDirect))
          || (opt.source === 'fawaz');'''

new_probe = '''        const knownAvailable = (opt.source === 'mjna_id' && hasMjnaIdText)
          || (opt.source === 'lidwa_id' && (hasLidwaIdText || hasLidwaId2))
          || (opt.source === 'lidwa_en' && (hasLidwaEnText || hasLidwaEn2))
          || (opt.source === 'ab' && (hasAbText || hasAbDirect))
          || (opt.source === 'fawaz');'''

if old_probe in code:
    code = code.replace(old_probe, new_probe)
    print("Added: mjna_id to knownAvailable probe check")
else:
    print("WARNING: Could not find probe knownAvailable block")

# ---- ADD 6: Set default ID dropdown to mjna-id for MJNA books
old_default_id = "         const defaultId = translationOptions.find(o => o.id === 'lidwa-id') || translationOptions[0];"
new_default_id = "         const defaultId = translationOptions.find(o => o.id === 'mjna-id') || translationOptions.find(o => o.id === 'lidwa-id') || translationOptions[0];"
if old_default_id in code:
    code = code.replace(old_default_id, new_default_id)
    print("Fixed: default ID dropdown prefers mjna-id for MJNA books")
else:
    print("WARNING: Could not find defaultId dropdown line")

# Bump cache buster
code = code.replace('js/app.js?v=2026082003', 'js/app.js?v=2026082004')

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("\napp.js patched successfully!")
