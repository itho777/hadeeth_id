import re
text = open('js/app.js', encoding='utf-8').read()

# Delete renderDatasetBanner entirely
text = re.sub(r'function renderDatasetBanner\(bookId, containerId, forceDataset\).*?el\.innerHTML = `\n.*?\n  `;\n}', '', text, flags=re.DOTALL)

# Update getHeaderHtml to remove dataset label pill
old_header = r'''function getHeaderHtml(bookId, id, activeDsLabel, activeDsLabelId, activeSources, activeNote, pillsHtml) {
  return `
    <div class="flex items-start gap-4">
      <div class="flex-shrink-0 mt-0.5">
        <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 dark:bg-[#10b981]/20 text-primary dark:text-[#10b981] font-bold text-sm border border-primary/20 dark:border-[#10b981]/30">#${id} (${activeDsLabel})</span>
      </div>'''

new_header = r'''function getHeaderHtml(bookId, displayNum, activeSources, activeNote, pillsHtml) {
  return `
    <div class="flex items-start gap-4">
      <div class="flex-shrink-0 mt-0.5">
        <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 dark:bg-[#10b981]/20 text-primary dark:text-[#10b981] font-bold text-sm border border-primary/20 dark:border-[#10b981]/30">#${displayNum}</span>
      </div>'''

text = text.replace(old_header, new_header)

# Fix callers of getHeaderHtml
text = text.replace('getHeaderHtml(bookId, num, isIdLang ? activeDs.labelId : activeDs.label, isIdLang ? activeDs.label : activeDs.labelId, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml);', 'getHeaderHtml(bookId, displayNum, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml);')
text = text.replace('getHeaderHtml(bookId, hadithId, isIdLang ? activeDs.labelId : activeDs.label, isIdLang ? activeDs.label : activeDs.labelId, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml);', 'getHeaderHtml(bookId, displayNum, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml);')

open('js/app.js', 'w', encoding='utf-8').write(text)
