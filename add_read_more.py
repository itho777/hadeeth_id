import re

text = open('js/app.js', encoding='utf-8').read()

setup_func = """window.setupReadMore = function() {
  const containers = document.querySelectorAll('.hadith-text-container:not(.read-more-initialized)');
  containers.forEach(container => {
    container.classList.add('read-more-initialized');
    const inner = container.querySelector('.hadith-text-inner');
    const overlay = container.querySelector('.read-more-overlay');
    const btn = container.querySelector('.read-more-btn');
    if (!inner || !overlay || !btn) return;

    // Wait a brief moment for styles to apply if just inserted
    setTimeout(() => {
      // Assuming 10 lines is roughly 350-400px depending on language/text size. Let's use 380px.
      if (inner.scrollHeight > 400) {
        overlay.classList.remove('hidden');
        btn.classList.remove('hidden');

        btn.addEventListener('click', () => {
          if (inner.style.maxHeight === '380px') {
            inner.style.maxHeight = inner.scrollHeight + 'px';
            overlay.classList.add('hidden');
            const isId = window.LangSystem && window.LangSystem.isIdMode();
            btn.innerHTML = `<span data-lang-en style="${isId?'display:none':''}">Show less</span><span data-lang-id style="${isId?'':'display:none'}">Sembunyikan</span> <span class="material-symbols-outlined text-[14px]">expand_less</span>`;
          } else {
            inner.style.maxHeight = '380px';
            overlay.classList.remove('hidden');
            const isId = window.LangSystem && window.LangSystem.isIdMode();
            btn.innerHTML = `<span data-lang-en style="${isId?'display:none':''}">Read more</span><span data-lang-id style="${isId?'':'display:none'}">Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span>`;
            
            // Scroll back into view if it was scrolled past
            const rect = container.getBoundingClientRect();
            if (rect.top < 0) {
              window.scrollBy({ top: rect.top - 80, behavior: 'smooth' });
            }
          }
        });
      } else {
        inner.style.maxHeight = 'none';
      }
    }, 50);
  });
};

"""

# Insert setupReadMore right before document.addEventListener('DOMContentLoaded', ...)
text = text.replace("document.addEventListener('DOMContentLoaded', () => {", setup_func + "document.addEventListener('DOMContentLoaded', () => {")

# 1. loadHadithList
old_text_hadith_list = r"""          ${arText ? `<p class="font-arabic-body text-2xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(arText)}</p>` : ''}
          ${displayText}"""

new_text_hadith_list = r"""          <div class="hadith-text-container relative">
            <div class="hadith-text-inner transition-all duration-300 overflow-hidden" style="max-height: 380px;">
              ${arText ? `<p class="font-arabic-body text-2xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(arText)}</p>` : ''}
              ${displayText}
            </div>
            <div class="read-more-overlay absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-surface dark:from-[#1e293b] to-transparent pointer-events-none hidden"></div>
            <button class="read-more-btn hidden text-secondary dark:text-[#10b981] font-semibold text-xs mt-2 hover:underline flex items-center gap-1 cursor-pointer">
              <span data-lang-en>Read more</span><span data-lang-id>Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span>
            </button>
          </div>"""

# 2. loadTopicHadiths
old_text_topic = r"""          ${arText ? `<p class="font-arabic-body text-2xl text-primary dark:text-white text-right leading-loose" dir="rtl">${arText}</p>` : ''}
          ${displayText}"""

new_text_topic = r"""          <div class="hadith-text-container relative">
            <div class="hadith-text-inner transition-all duration-300 overflow-hidden" style="max-height: 380px;">
              ${arText ? `<p class="font-arabic-body text-2xl text-primary dark:text-white text-right leading-loose" dir="rtl">${arText}</p>` : ''}
              ${displayText}
            </div>
            <div class="read-more-overlay absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-surface dark:from-[#1e293b] to-transparent pointer-events-none hidden"></div>
            <button class="read-more-btn hidden text-secondary dark:text-[#10b981] font-semibold text-xs mt-2 hover:underline flex items-center gap-1 cursor-pointer">
              <span data-lang-en>Read more</span><span data-lang-id>Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span>
            </button>
          </div>"""

# 3. loadHadithCardsList (Home Page)
old_text_cards = r"""        ${araText ? `<p class="font-arabic-body text-xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(araText)}</p>` : ''}
        ${transHtml}"""

new_text_cards = r"""        <div class="hadith-text-container relative">
          <div class="hadith-text-inner transition-all duration-300 overflow-hidden" style="max-height: 380px;">
            ${araText ? `<p class="font-arabic-body text-xl text-primary dark:text-white text-right leading-loose" dir="rtl">${escapeHtml(araText)}</p>` : ''}
            ${transHtml}
          </div>
          <div class="read-more-overlay absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-surface dark:from-[#1e293b] to-transparent pointer-events-none hidden"></div>
          <button class="read-more-btn hidden text-secondary dark:text-[#10b981] font-semibold text-xs mt-2 hover:underline flex items-center gap-1 cursor-pointer">
            <span data-lang-en>Read more</span><span data-lang-id>Selengkapnya</span> <span class="material-symbols-outlined text-[14px]">expand_more</span>
          </button>
        </div>"""

text = text.replace(old_text_hadith_list, new_text_hadith_list)
text = text.replace(old_text_topic, new_text_topic)
text = text.replace(old_text_cards, new_text_cards)

# Call setupReadMore after innerHTML
text = text.replace('container.innerHTML = html;\n    LangSystem.apply(LangSystem.get());', 'container.innerHTML = html;\n    LangSystem.apply(LangSystem.get());\n    if (window.setupReadMore) window.setupReadMore();')
text = text.replace('container.innerHTML = html;\n    if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());', 'container.innerHTML = html;\n    if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());\n    if (window.setupReadMore) window.setupReadMore();')
text = text.replace('container.innerHTML = html;\n  LangSystem.apply(LangSystem.get());', 'container.innerHTML = html;\n  LangSystem.apply(LangSystem.get());\n  if (window.setupReadMore) window.setupReadMore();')

open('js/app.js', 'w', encoding='utf-8').write(text)
print("Done")
