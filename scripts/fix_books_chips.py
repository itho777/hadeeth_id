import re

with open('books.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix Mojibake title
html = html.replace('Digital Library A,A Classical Hadith Genres', 'Digital Library — Classical Hadith Genres')
html = html.replace('Digital Library Ã¢â‚¬â€œ Classical Hadith Genres', 'Digital Library — Classical Hadith Genres') # Just in case

# 2. Fix the chips
chips_target = r'<div class="flex items-center gap-2 mt-4 overflow-x-auto pb-2" id="filter-chips">.*?</div>\s+</div>'
chips_replacement = """<div class="flex items-center gap-2 mt-4 overflow-x-auto pb-2" id="filter-chips">
        <button class="chip-btn active px-4 py-1.5 rounded-full text-xs font-semibold bg-primary dark:bg-[#10b981] text-white dark:text-black" data-filter="all">
          <span data-lang-en>All Collections (24)</span><span data-lang-id>Semua Kitab (24)</span>
        </button>
        <button class="chip-btn px-4 py-1.5 rounded-full text-xs font-semibold bg-surface-container-high dark:bg-[#1e293b] text-on-surface-variant dark:text-gray-300 hover:bg-outline-variant/30" data-filter="jami">
          <span>Jami' (الجامع)</span>
        </button>
        <button class="chip-btn px-4 py-1.5 rounded-full text-xs font-semibold bg-surface-container-high dark:bg-[#1e293b] text-on-surface-variant dark:text-gray-300 hover:bg-outline-variant/30" data-filter="sunan">
          <span>Sunan (السنن)</span>
        </button>
        <button class="chip-btn px-4 py-1.5 rounded-full text-xs font-semibold bg-surface-container-high dark:bg-[#1e293b] text-on-surface-variant dark:text-gray-300 hover:bg-outline-variant/30" data-filter="musnad">
          <span>Musnad (المسند)</span>
        </button>
        <button class="chip-btn px-4 py-1.5 rounded-full text-xs font-semibold bg-surface-container-high dark:bg-[#1e293b] text-on-surface-variant dark:text-gray-300 hover:bg-outline-variant/30" data-filter="mujam">
          <span>Mu'jam (المعجم)</span>
        </button>
        <button class="chip-btn px-4 py-1.5 rounded-full text-xs font-semibold bg-surface-container-high dark:bg-[#1e293b] text-on-surface-variant dark:text-gray-300 hover:bg-outline-variant/30" data-filter="mushannaf">
          <span>Mushannaf (المصنف)</span>
        </button>
        <button class="chip-btn px-4 py-1.5 rounded-full text-xs font-semibold bg-surface-container-high dark:bg-[#1e293b] text-on-surface-variant dark:text-gray-300 hover:bg-outline-variant/30" data-filter="mustadrak">
          <span>Mustadrak (المستدرك)</span>
        </button>
        <button class="chip-btn px-4 py-1.5 rounded-full text-xs font-semibold bg-surface-container-high dark:bg-[#1e293b] text-on-surface-variant dark:text-gray-300 hover:bg-outline-variant/30" data-filter="jawami">
          <span>Jawami' (جوامع الكلم)</span>
        </button>
      </div>
    </div>"""

html = re.sub(chips_target, chips_replacement, html, flags=re.DOTALL)

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated books.html filters and header")
