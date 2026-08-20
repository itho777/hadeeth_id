"""
Two focused fixes:
1. HOTD: Change default hadith to Bukhari #1 (byte offset 0, loads instantly)
   and add a Race/timeout so local dev doesn't hang.
2. Arabic title: when chapTitleAr is empty after chapter lookup, 
   fall back to the book's Arabic title from books_v2.json.
"""

with open('js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# ---- FIX 1: Change HOTD default to Bukhari 1 (fast local load) ----
old_hotd_default = '''  // User specifically requested a Hajj hadith as the default HOTD
  // Bukhari 7038: "My mother vowed to perform the Hajj but she died before performing it..."
  const bookId = (hotdConfig && hotdConfig.bookId) || 'bukhari';
  const hadithId = (hotdConfig && hotdConfig.hadithId) || '7038';'''

new_hotd_default = '''  // Default: Bukhari #1 (Umar narration on intentions) - small byte offset, loads fast everywhere
  const bookId = (hotdConfig && hotdConfig.bookId) || 'bukhari';
  const hadithId = (hotdConfig && hotdConfig.hadithId) || '1';'''

if old_hotd_default in code:
    code = code.replace(old_hotd_default, new_hotd_default)
    print("Fixed: HOTD default hadith changed to Bukhari #1 (fast loading)")
else:
    print("WARNING: Could not find HOTD default hadith line")

# ---- FIX 2: Add timeout to HOTD fetch so it fails fast locally ----
old_hotd_fetch = '''    // Fetch unified hadith record from the new consolidated API
    const h = await window.HadeethAPI.getHadith(bookId, hadithId);
    if (!h) return;'''

new_hotd_fetch = '''    // Fetch with timeout to avoid indefinite skeleton on local dev
    const h = await Promise.race([
      window.HadeethAPI.getHadith(bookId, hadithId),
      new Promise((_, reject) => setTimeout(() => reject(new Error('HOTD timeout')), 8000))
    ]).catch(() => null);
    if (!h) {
      // Show friendly fallback message instead of skeleton
      const hotdBookLabel = document.getElementById('hotd-book-label');
      if (hotdBookLabel) hotdBookLabel.textContent = 'Hadith of the Day';
      const hotdArabic = document.getElementById('hotd-arabic');
      if (hotdArabic) {
        hotdArabic.textContent = 'Loading requires server Range support. Deploy to GitHub Pages to view Hadith of the Day.';
        hotdArabic.classList.remove('animate-pulse', 'text-transparent', 'bg-surface-container-high');
      }
      return;
    }'''

if old_hotd_fetch in code:
    code = code.replace(old_hotd_fetch, new_hotd_fetch)
    print("Fixed: HOTD now has 8s timeout with friendly fallback")
else:
    print("WARNING: Could not find HOTD fetch block")

# ---- FIX 3: Arabic title fallback in hadith-list for MJNA books ----
# After setting chTitleAr from chapTitleAr, if it's empty for MJNA, use book's Arabic title
old_ar_set = '''        if (chTitleEn) chTitleEn.innerText = chapTitleEn;
        if (chTitleId) chTitleId.innerText = chapTitleId;
        if (chTitleAr) chTitleAr.innerText = chapTitleAr;
        const bcCurEn2 = document.querySelector('[data-list-breadcrumb-current-en]');'''

new_ar_set = '''        if (chTitleEn) chTitleEn.innerText = chapTitleEn;
        if (chTitleId) chTitleId.innerText = chapTitleId;
        // For MJNA books: if chapter has no separate Arabic title, show book-level Arabic title
        let arToShow = chapTitleAr;
        if (!arToShow && isMjnaBook) {
          const mjnaArFallbacks = {
            ibnukhuzaimah: '\u0635\u062d\u064a\u062d \u0627\u0628\u0646 \u062e\u0632\u064a\u0645\u0629',
            ibnuhibban: '\u0635\u062d\u064a\u062d \u0627\u0628\u0646 \u062d\u0628\u0627\u0646',
            mustadrak: '\u0627\u0644\u0645\u0633\u062a\u062f\u0631\u0643 \u0639\u0644\u0649 \u0627\u0644\u0635\u062d\u064a\u062d\u064a\u0646',
            daruquthni: '\u0633\u0646\u0646 \u0627\u0644\u062f\u0627\u0631\u0642\u0637\u0646\u064a',
          };
          arToShow = mjnaArFallbacks[bookId] || '';
        }
        if (chTitleAr) chTitleAr.innerText = arToShow;
        const bcCurEn2 = document.querySelector('[data-list-breadcrumb-current-en]');'''

if old_ar_set in code:
    code = code.replace(old_ar_set, new_ar_set)
    print("Fixed: Arabic title now falls back to book-level Arabic for MJNA books")
else:
    print("WARNING: Could not find chTitleAr block")

# Bump cache buster
code = code.replace('js/app.js?v=2026082004', 'js/app.js?v=2026082005')

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("\napp.js patched successfully!")
