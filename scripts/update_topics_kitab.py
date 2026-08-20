import re

with open('topics-in-kitab.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add fetching of topics_counts.json
fetch_books_code = """
            // Load books
            const booksRes = await fetch('data/books_v2.json?v=' + Date.now());
            const books = await booksRes.json();
            const nineBooks = books.slice(0, 9); // Kutubut Tis'ah
            
            // Load counts
            let counts = {};
            try {
                const countsRes = await fetch('data/api/topics_counts.json');
                counts = await countsRes.json();
            } catch(e) { console.error('Counts not found'); }
"""
content = re.sub(r'            // Load books.*?const nineBooks = books\.slice\(0, 9\); // Kutubut Tis\'ah', fetch_books_code.strip(), content, flags=re.DOTALL)

# Change the html loop to use a simple small card
new_html_loop = """
                let count = 0;
                if (counts[book.id] && topic) {
                    count = counts[book.id][topic.name_en] || 0;
                }

                html += `<a href="topic-hadiths.html?book=${book.id}&topic=${topicId}" class="book-card bg-surface dark:bg-[#1e293b] border border-outline-variant/20 dark:border-[#334155] rounded-xl overflow-hidden hover:shadow-md transition-all flex items-center justify-between p-4 cursor-pointer group card-lift">
                  <div class="flex flex-col gap-1">
                      <h3 class="font-bold text-primary dark:text-white group-hover:text-secondary dark:group-hover:text-[#10b981] transition-colors text-sm">
                        <span data-lang-en>${titleEn}</span>
                        <span data-lang-id style="display:none">${titleId}</span>
                      </h3>
                      <p class="text-xs text-on-surface-variant dark:text-gray-400">
                        <span data-lang-en>${book.author_en || ''}</span>
                        <span data-lang-id style="display:none">${book.author_id || book.author_en || ''}</span>
                      </p>
                  </div>
                  <div class="flex items-center gap-3">
                      <span class="text-sm text-secondary dark:text-[#10b981]" dir="rtl">${book.title_ar}</span>
                      <span class="bg-primary/10 dark:bg-primary/20 text-primary dark:text-[#10b981] text-xs font-bold px-2 py-1 rounded">
                        ${count} <span data-lang-en>Hadiths</span><span data-lang-id style="display:none">Hadits</span>
                      </span>
                  </div>
                </a>`;
"""
content = re.sub(r'                html \+= `<a href="topic-hadiths\.html\?book=\$\{book\.id\}&topic=\$\{topicId\}".*?</a>`;', new_html_loop.strip(), content, flags=re.DOTALL)

with open('topics-in-kitab.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated topics-in-kitab.html successfully.")
