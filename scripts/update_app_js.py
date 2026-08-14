import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
APP_JS_PATH = os.path.join(BASE_DIR, "js", "app.js")

def update_app_js():
    with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject dataset version listener
    target = r'(// --- Initialize Books Rendering ---)'
    replacement = r'''// --- Dataset Version Switcher ---
  const versionSelect = document.getElementById('dataset-version');
  if (versionSelect) {
    const currentVersion = localStorage.getItem('dataset_version') || 'primary';
    versionSelect.value = currentVersion;
    
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('book');
    const lidwaBooks = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'darimi', 'ahmad', 'nawawi'];
    
    if (bookId && !lidwaBooks.includes(bookId)) {
       const lidwaOpt = versionSelect.querySelector('option[value="native_lidwa"]');
       if (lidwaOpt) lidwaOpt.disabled = true;
       if (currentVersion === 'native_lidwa') {
          versionSelect.value = 'primary';
          localStorage.setItem('dataset_version', 'primary');
       }
    }
    
    versionSelect.addEventListener('change', (e) => {
      localStorage.setItem('dataset_version', e.target.value);
      location.reload();
    });
  }

  \1'''
    content = re.sub(target, replacement, content, count=1)

    # In renderChapters, check if version is not primary. If so, don't show chapters, show "Read Entire Book"
    target_chapters = r'(async function renderChapters\(\) \{)'
    replacement_chapters = r'''\1
    const v = localStorage.getItem('dataset_version') || 'primary';
    if (v !== 'primary') {
        const chaptersList = document.getElementById('chapters-list');
        if (chaptersList) {
            chaptersList.innerHTML = `<div class="bg-surface dark:bg-[#1e293b] p-8 text-center rounded-xl border border-outline-variant/30">
                <span class="material-symbols-outlined text-4xl text-secondary mb-4">database</span>
                <h3 class="text-xl font-bold text-primary dark:text-white mb-2">Native Dataset Mode</h3>
                <p class="text-on-surface-variant mb-6">Chapter routing is disabled in Native mode. All hadiths will be loaded directly from the raw database.</p>
                <a href="hadith-list.html?book=${bookId}" class="bg-primary text-on-primary px-6 py-3 rounded-lg font-bold hover:opacity-90">View All Hadiths</a>
            </div>`;
            
            const stats = document.getElementById('chapter-stats');
            if (stats) stats.textContent = "Raw Database View";
        }
        return;
    }
'''
    content = re.sub(target_chapters, replacement_chapters, content, count=1)

    with open(APP_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[+] Updated app.js with Version Switcher UI logic")

if __name__ == "__main__":
    update_app_js()
