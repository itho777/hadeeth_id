import re
text = open('index.html', encoding='utf-8').read()

# Add to the select dropdown
text = text.replace(
    '<option value="malik" data-lang-en="Muwatta Malik" data-lang-id="Muwatha\' Malik">Muwatha\' Malik</option>',
    '<option value="malik" data-lang-en="Muwatta Malik" data-lang-id="Muwatha\' Malik">Muwatha\' Malik</option>\n              <option value="syafii" data-lang-en="Musnad Syafi\'i" data-lang-id="Musnad Syafi\'i">Musnad Syafi\'i</option>'
)

# Add to the collections grid
malik_card = """        <a href="hadith-list.html?book=malik" class="bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-5 hover:shadow-md transition-all group flex flex-col justify-between h-full">
          <div>
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/20 flex items-center justify-center text-secondary dark:text-[#10b981] group-hover:bg-secondary group-hover:text-white dark:group-hover:bg-[#10b981] dark:group-hover:text-black transition-colors">
                <span class="material-symbols-outlined">auto_stories</span>
              </div>
              <h3 class="font-bold text-lg text-primary dark:text-white" data-lang-en="Muwatta Malik" data-lang-id="Muwatha' Malik">Muwatha' Malik</h3>
            </div>
            <p class="text-sm text-outline dark:text-gray-400 mb-4" data-lang-en="Compiled by Imam Malik, one of the earliest and most respected collections." data-lang-id="Disusun oleh Imam Malik, salah satu koleksi paling awal dan dihormati.">Compiled by Imam Malik...</p>
          </div>
          <div class="flex justify-between items-center text-xs font-semibold">
            <span class="text-secondary dark:text-[#10b981]" data-lang-en="1,595 Ahadith" data-lang-id="1.595 Hadits">1.595 Hadits</span>
            <span class="material-symbols-outlined text-outline dark:text-gray-500 group-hover:text-secondary dark:group-hover:text-[#10b981] transition-colors">arrow_forward</span>
          </div>
        </a>"""

syafii_card = """        <a href="hadith-list.html?book=syafii" class="bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-5 hover:shadow-md transition-all group flex flex-col justify-between h-full">
          <div>
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/20 flex items-center justify-center text-secondary dark:text-[#10b981] group-hover:bg-secondary group-hover:text-white dark:group-hover:bg-[#10b981] dark:group-hover:text-black transition-colors">
                <span class="material-symbols-outlined">menu_book</span>
              </div>
              <h3 class="font-bold text-lg text-primary dark:text-white" data-lang-en="Musnad Syafi'i" data-lang-id="Musnad Syafi'i">Musnad Syafi'i</h3>
            </div>
            <p class="text-sm text-outline dark:text-gray-400 mb-4" data-lang-en="The famous collection attributed to Imam Al-Shafi'i." data-lang-id="Koleksi hadits musnad dari Imam As-Syafi'i.">The famous collection attributed to Imam Al-Shafi'i.</p>
          </div>
          <div class="flex justify-between items-center text-xs font-semibold">
            <span class="text-secondary dark:text-[#10b981]" data-lang-en="1,800 Ahadith" data-lang-id="1.800 Hadits">1.800 Hadits</span>
            <span class="material-symbols-outlined text-outline dark:text-gray-500 group-hover:text-secondary dark:group-hover:text-[#10b981] transition-colors">arrow_forward</span>
          </div>
        </a>"""

if malik_card in text:
    text = text.replace(malik_card, malik_card + '\n' + syafii_card)
    open('index.html', 'w', encoding='utf-8').write(text)
    print("Success")
else:
    print("Malik card not found in index.html")
