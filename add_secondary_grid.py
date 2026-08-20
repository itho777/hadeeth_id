import re
text = open('index.html', encoding='utf-8').read()

secondary_html = """
    <!-- Secondary Collections Grid -->
    <section class="w-full flex flex-col gap-stack-md pt-8">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-secondary dark:text-[#10b981]">collections_bookmark</span>
        <h2 class="font-headline-lg-mobile text-headline-lg-mobile text-primary dark:text-white font-bold" data-i18n="other_collections_title">Other Collections</h2>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" id="secondary-grid">
        <!-- Dynamic Book Cards will be injected here by app.js -->
      </div>
    </section>
"""

# Insert secondary_html right after tisah-grid section
text = re.sub(
    r'(<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" id="tisah-grid">\s*<!-- Dynamic Book Cards will be injected here by app.js -->\s*</div>\s*</section>)',
    r'\1\n' + secondary_html,
    text
)

# And add the option to the search kitabs dropdown
text = text.replace('<option value="ahmad">Musnad Ahmad</option>', '<option value="ahmad">Musnad Ahmad</option>\n            <option value="syafii">Musnad Syafi\'i</option>')

open('index.html', 'w', encoding='utf-8').write(text)
