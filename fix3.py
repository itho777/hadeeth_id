text = open('js/app.js', encoding='utf-8').read()

start_idx = text.find('  el.innerHTML = `')
end_idx = text.find('}\n\ndocument.addEventListener')

correct = '''  el.innerHTML = `
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl px-4 py-3 shadow-sm">
      <div class="flex items-center gap-1.5 shrink-0">
        <span class="material-symbols-outlined text-secondary dark:text-[#10b981]" style="font-size:16px">numbers</span>
        <span class="text-[11px] font-bold text-on-surface-variant dark:text-gray-400 uppercase tracking-wide whitespace-nowrap">${isId ? 'Sistem Penomoran:' : 'Numbering System:'}</span>
      </div>
      <div class="flex flex-wrap items-center gap-2 flex-1">
        ${pillsHtml}
      </div>
    </div>
  `;
}

function getHeaderHtml(bookId, displayNum, activeSources, activeNote, pillsHtml) {
  return `
    <div class="flex items-start gap-4">
      <div class="flex-shrink-0 mt-0.5">
        <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 dark:bg-[#10b981]/20 text-primary dark:text-[#10b981] font-bold text-sm border border-primary/20 dark:border-[#10b981]/30">#${displayNum}</span>
      </div>
      <div class="flex flex-col gap-2 flex-1 min-w-0">
        <div class="flex flex-wrap gap-2 items-center">
          ${pillsHtml}
        </div>
        <div class="text-[11px] text-outline dark:text-gray-500 leading-snug">
          <span class="font-semibold text-on-surface-variant dark:text-gray-400">${escapeHtml(activeSources)}</span>
          ${activeNote ? `<span class="block mt-0.5 text-secondary/80 dark:text-[#10b981]/70"> ${escapeHtml(activeNote)}</span>` : ''}
        </div>
      </div>
    </div>
  `;
}'''
if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + correct + text[end_idx:]
    open('js/app.js', 'w', encoding='utf-8').write(text)
    print("Fixed!")
else:
    print("Not found", start_idx, end_idx)
