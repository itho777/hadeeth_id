import re
text = open('js/app.js', encoding='utf-8').read()

new_functions = r'''window.__switchNumbering = function(systemId) {
  localStorage.setItem('numbering_system', systemId);
  const url = new URL(location.href);
  url.searchParams.delete('dataset');
  location.href = url.toString();
};

function renderNumberingBanner(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;

  const currentSys = localStorage.getItem('numbering_system') || 'international';
  const isId = window.LangSystem && window.LangSystem.isIdMode();

  const options = [
    { id: 'international', label: 'International Numbering', labelId: 'Penomoran Internasional (Fawaz)' },
    { id: 'lidwa', label: 'Lidwa Native Numbering', labelId: 'Penomoran Bawaan Lidwa' }
  ];

  const pillsHtml = options.map(opt => {
    const label = isId ? opt.labelId : opt.label;
    if (opt.id === currentSys) {
      return `<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-secondary dark:bg-[#10b981] text-white dark:text-black select-none">
        <span class="material-symbols-outlined text-[13px]" style="font-size:13px">check_circle</span>${escapeHtml(label)}
      </span>`;
    }
    return `<button
        onclick="window.__switchNumbering('${opt.id}')"
        class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border border-outline-variant/40 dark:border-[#334155] text-on-surface-variant dark:text-gray-400 hover:border-secondary dark:hover:border-[#10b981] hover:text-secondary dark:hover:text-[#10b981] bg-surface-container-low dark:bg-[#0f172a] transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[13px]" style="font-size:13px">swap_horiz</span>${escapeHtml(label)}
      </button>`;
  }).join('');

  el.innerHTML = `
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

# Replace the three functions
text = re.sub(r'window\.__switchDataset = function.*?function getHeaderHtml.*?  `;\n}', new_functions, text, flags=re.DOTALL)

# Update callers
text = text.replace('renderDatasetBanner(bookId, \'dataset-banner\');', 'renderNumberingBanner(\'dataset-banner\');')
text = text.replace('renderDatasetBanner(bookId, \'dataset-banner-list\', activeDataset);', 'renderNumberingBanner(\'dataset-banner-list\');')
text = text.replace('getHeaderHtml(bookId, num, isIdLang ? activeDs.labelId : activeDs.label, isIdLang ? activeDs.label : activeDs.labelId, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml)', 'getHeaderHtml(bookId, displayNum, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml)')
text = text.replace('getHeaderHtml(bookId, hadithId, isIdLang ? activeDs.labelId : activeDs.label, isIdLang ? activeDs.label : activeDs.labelId, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml)', 'getHeaderHtml(bookId, displayNum, isIdLang ? activeDs.sourcesId : activeDs.sources, isIdLang ? activeDs.noteId : activeDs.note, pillsHtml)')

open('js/app.js', 'w', encoding='utf-8').write(text)
