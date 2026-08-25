const fs = require('fs');
let txt = fs.readFileSync('topic-hadiths.html', 'utf8');

const searchStr = `<div class="relative w-full sm:flex-1">
        <span class="material-symbols-outlined absolute left-3 top-2.5 text-outline dark:text-gray-400 text-sm">search</span>
        <input type="text" id="topic-search-input" placeholder="Search within chapter or type keyword..." data-i18n="search_within_chapter" class="w-full pl-9 pr-4 py-2 text-xs bg-surface-container-low dark:bg-[#0f172a] border border-outline-variant/30 dark:border-[#334155] rounded-lg text-primary dark:text-white focus:outline-none focus:border-secondary dark:focus:border-[#10b981]"/>
      </div>`;

const replaceStr = `<div class="relative w-full sm:flex-1 flex gap-2">
        <div class="relative w-full">
          <span class="material-symbols-outlined absolute left-3 top-2.5 text-outline dark:text-gray-400 text-sm">search</span>
          <input type="text" id="topic-search-input" placeholder="Search within chapter or type keyword..." data-i18n="search_within_chapter" class="w-full pl-9 pr-4 py-2 text-xs bg-surface-container-low dark:bg-[#0f172a] border border-outline-variant/30 dark:border-[#334155] rounded-lg text-primary dark:text-white focus:outline-none focus:border-secondary dark:focus:border-[#10b981]"/>
        </div>
        <button id="topic-search-btn" class="px-4 py-2 bg-secondary dark:bg-[#10b981] text-white dark:text-black font-bold rounded-lg text-xs hover:opacity-90 transition-all cursor-pointer shadow-sm whitespace-nowrap">
          <span data-lang-en>Search</span><span data-lang-id style="display:none">Cari</span>
        </button>
      </div>`;

txt = txt.replace(searchStr, replaceStr);
fs.writeFileSync('topic-hadiths.html', txt);
