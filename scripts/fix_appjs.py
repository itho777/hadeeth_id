import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace everything from "  // BRANCH B — AhmedBaset native hadith loading"
# or wherever it starts, all the way down to "  filteredHadiths = [...allHadiths];"

start_marker = "  // ================================================================\n  // CONSOLIDATED API FETCHING (Single Source of Truth)\n  // ================================================================"
end_marker = "  filteredHadiths = [...allHadiths];"

# wait, the file currently has:
#   // CONSOLIDATED API FETCHING (Single Source of Truth)
# ...
#   } // end primary branch
# 
#   filteredHadiths = [...allHadiths];

new_fetch_logic = """  // ================================================================
  // CONSOLIDATED API FETCHING (Single Source of Truth)
  // ================================================================
  try {
    const chapterHadiths = await window.HadeethAPI.getChapterHadiths(bookId, chapterId);
    
    // Fallback titles if chapter is missing
    let chapTitleEn = `Chapter ${chapterId}`;
    let chapTitleId = `Kitab ${chapterId}`;
    let chapTitleAr = '';

    if (chapterHadiths.length > 0 && chapterHadiths[0]._chapter) {
      const ch = chapterHadiths[0]._chapter;
      if (ch.english) chapTitleEn = ch.english;
      if (ch.indonesian) chapTitleId = ch.indonesian;
      if (ch.arabic) chapTitleAr = ch.arabic;
    }

    if (chTitleEn) chTitleEn.innerText = chapTitleEn;
    if (chTitleId) chTitleId.innerText = chapTitleId;
    if (chTitleAr) chTitleAr.innerText = chapTitleAr;

    const bcCurEn = document.querySelector('[data-list-breadcrumb-current-en]');
    const bcCurId = document.querySelector('[data-list-breadcrumb-current-id]');
    if (bcCurEn) bcCurEn.innerText = chapTitleEn;
    if (bcCurId) bcCurId.innerText = chapTitleId;

    const chMetaEn = document.querySelector('[data-list-chapter-meta-en]');
    const chMetaId = document.querySelector('[data-list-chapter-meta-id]');
    if (chMetaEn) chMetaEn.innerText = `Kitab ${chapterId}`;
    if (chMetaId) chMetaId.innerText = `Kitab ${chapterId}`;

    allHadiths = chapterHadiths.map(h => {
      // Prioritize Arabic from native datasets if available, else fallback
      const textAr = h.data.text_ar || h.data.text || '';
      
      return {
        hadith_number: h.hadithnumber || h.id, // Ensure we use Fawaz ID as the master key
        text_ar: textAr,
        text_en: h.data.text_en || h.data.text || '',
        text_id: h.data.text_id || '',
        grade: h.data.grade || '',
        book_id: bookId,
        _lidwaRef: h.lidwa_id || null,
        _noId: !h.data.text_id
      };
    });

    const total = allHadiths.length;
    const countEl = document.querySelector('[data-list-count-meta-en]');
    const countIdEl = document.querySelector('[data-list-count-meta-id]');
    const countFallback = document.querySelector('[data-list-count-meta]');
    if (countEl) countEl.innerText = `${total} Hadiths in ${bookName} Kitab ${chapterId}`;
    if (countIdEl) countIdEl.innerText = `${total} Hadits dalam ${bookName} Kitab ${chapterId}`;
    if (countFallback && !countEl) countFallback.innerText = `${total} Hadiths — Kitab ${chapterId}`;

  } catch(e) {
    console.error('Failed to load consolidated chapter data:', e);
  }

"""

# Regex replacement
pattern = re.compile(r'  // ================================================================\n  // CONSOLIDATED API FETCHING.*?} // end primary branch\n', re.DOTALL)
new_content = pattern.sub(new_fetch_logic, content)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(new_content)
