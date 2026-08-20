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
}'''

# Match exactly window.__switchDataset to the end of renderDatasetBanner
# `document.addEventListener('DOMContentLoaded'` is exactly what follows.
text = re.sub(r'window\.__switchDataset = function.*?  \};\n\}(?=\s*document\.addEventListener\(\'DOMContentLoaded\')', new_functions, text, flags=re.DOTALL)

# Update callers
text = text.replace('renderDatasetBanner(bookId, \'dataset-banner\');', 'renderNumberingBanner(\'dataset-banner\');')
text = text.replace('renderDatasetBanner(bookId, \'dataset-banner-list\', activeDataset);', 'renderNumberingBanner(\'dataset-banner-list\');')

open('js/app.js', 'w', encoding='utf-8').write(text)
