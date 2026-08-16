import os
import re

APP_JS = "js/app.js"

with open(APP_JS, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find("async function loadSanadChain() {")
if start_idx == -1:
    print("Could not find loadSanadChain")
    exit(1)

brace_count = 0
in_function = False
end_idx = -1

for i in range(start_idx, len(content)):
    if content[i] == '{':
        brace_count += 1
        in_function = True
    elif content[i] == '}':
        brace_count -= 1
    
    if in_function and brace_count == 0:
        end_idx = i + 1
        break

if end_idx == -1:
    print("Could not find end of loadSanadChain")
    exit(1)

new_func = """async function loadSanadChain() {
  const container = document.getElementById('sanad-nodes-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const bookId = params.get('book') || 'bukhari';
  const hadithNum = params.get('id') || '1';

  const bookNames = {
    bukhari: 'Sahih al-Bukhari',
    nawawi: 'Forty Nawawi',
    muslim: 'Sahih Muslim',
    abudawud: 'Sunan Abu Dawood',
    tirmidhi: "Jami' al-Tirmidhi",
    nasai: "Sunan an-Nasa'i",
    ibnmajah: 'Sunan Ibn Majah',
    malik: 'Muwatta Malik',
    ahmad: 'Musnad Ahmad',
    darimi: 'Sunan ad-Darimi'
  };
  const bookName = bookNames[bookId.toLowerCase()] || bookId.toUpperCase();
  const isIdLang = (window.LangSystem && window.LangSystem.isIdMode());

  const hadithUrl = `hadith.html?book=${encodeURIComponent(bookId)}&id=${encodeURIComponent(hadithNum)}`;
  const backBtn = document.getElementById('back-to-hadith-btn');
  if (backBtn) backBtn.href = hadithUrl;
  const titleLink = document.getElementById('sanad-title-link');
  if (titleLink) titleLink.href = hadithUrl;

  const titleEn = document.querySelector('#sanad-title [data-lang-en]');
  const titleId = document.querySelector('#sanad-title [data-lang-id]');
  const subEn = document.querySelector('#sanad-subtitle [data-lang-en]');
  const subId = document.querySelector('#sanad-subtitle [data-lang-id]');

  if (titleEn) titleEn.innerText = `Sanad: ${bookName} ${hadithNum}`;
  if (titleId) titleId.innerText = `Sanad: ${bookName} Hadits #${hadithNum}`;
  if (subEn) subEn.innerText = `Chain of narrators (الإسناد) for ${bookName} Hadith #${hadithNum} tracing back to the Messenger of Allah ﷺ.`;
  if (subId) subId.innerText = `Silsilah perawi (الإسناد) untuk ${bookName} Hadits #${hadithNum} yang bersambung sampai ke Rasulullah ﷺ.`;

  const activeDataset = localStorage.getItem('dataset_version') || 'fawazahmed';
  let dsPrefix = 'fawaz';
  if (activeDataset === 'native_lidwa') dsPrefix = 'lidwa';
  else if (activeDataset === 'native_ahmedbaset') dsPrefix = 'ab';

  let narrators = [];
  try {
    const rawisDict = await window.HadeethAPI.getActiveRawis();
    const data = await window.HadeethAPI.getHadith(bookId, hadithNum, dsPrefix);
    
    if (data && data.rawis && data.rawis.length > 0) {
      // The array comes Prophet-first typically if mapped from Kaggle, but let's reverse if needed
      // Actually we will just display exactly as mapped. Kaggle mapping usually puts Prophet (1) first.
      
      let rawiIds = data.rawis;
      
      narrators = rawiIds.map((rId, idx) => {
        const rawiData = rawisDict[rId] || {};
        const isFirst = idx === 0 || (rawiData.grade && rawiData.grade.toLowerCase().includes('sahab')) || rId == '1';
        
        let enName = rawiData.en || 'Transmitter ' + rId;
        let idName = rawiData.id || 'Perawi ' + rId;
        
        return {
          rawi_id: rId,
          name: enName + (rId == '1' && !enName.includes('ﷺ') ? ' ﷺ' : ''),
          name_id: idName + (rId == '1' && !idName.includes('ﷺ') ? ' ﷺ' : ''),
          roleEn: rawiData.role || (isFirst ? 'SAHABI (COMPANION)' : (rawiData.grade ? `RAWI • ${rawiData.grade}` : 'RAWI')),
          roleId: rawiData.roleId || (isFirst ? 'SAHABAT NABI' : (rawiData.grade ? `RAWI • ${rawiData.grade}` : 'RAWI')),
          ar: rawiData.ar || idName,
          grade: rawiData.grade || 'Unknown',
          kunyah: rawiData.kunyah || '-',
          residence: rawiData.residence || '-',
          death_ah: rawiData.death_ah || '-'
        };
      });
    }
  } catch (err) {
    console.warn('Failed to load sanad chain:', err);
  }

  // Clear container
  container.innerHTML = '';
  
  if (narrators.length === 0) {
    container.innerHTML = `
      <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/30 rounded-xl p-8 text-center text-outline dark:text-gray-400 italic shadow-sm">
        <span class="material-symbols-outlined text-4xl mb-2 opacity-50">link_off</span><br/>
        <span data-lang-en>Sanad transmission chain is not available for this hadith in the current dataset.</span>
        <span data-lang-id style="display:none">Silsilah sanad tidak tersedia untuk hadits ini pada dataset aktif.</span>
      </div>
    `;
    const countText = document.getElementById('sanad-count-text');
    if (countText) countText.innerText = '0 Narrators';
    if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
    return;
  }

  // Draw Vertical Line
  const line = document.createElement('div');
  line.className = "absolute left-[24px] top-6 bottom-6 w-0.5 bg-outline-variant/50 dark:bg-[#334155] z-0";
  container.appendChild(line);

  // Render Nodes
  narrators.forEach((n, idx) => {
    const nodeHTML = `
      <div class="flex gap-4 relative z-10 w-full mb-6 group">
        
        <!-- Node Marker -->
        <div class="w-12 h-12 shrink-0 rounded-full bg-surface dark:bg-[#1e293b] border-4 border-manuscript-paper dark:border-ink-black shadow-md flex items-center justify-center relative">
          <div class="w-8 h-8 rounded-full ${idx === 0 ? 'bg-[#10b981]' : 'bg-primary dark:bg-white/10'} flex items-center justify-center text-white dark:text-white font-bold text-sm">
            ${idx + 1}
          </div>
        </div>

        <!-- Node Card -->
        <div class="bg-surface dark:bg-[#1e293b] border border-outline-variant/40 dark:border-[#334155] rounded-xl p-4 sm:p-5 flex-1 shadow-sm hover:shadow-md transition-shadow relative top-[-4px]">
          <div class="flex flex-col sm:flex-row justify-between gap-4">
            
            <div class="flex flex-col gap-1">
              <h4 class="font-bold text-primary dark:text-white text-base md:text-lg">
                <span data-lang-en>${n.name}</span>
                <span data-lang-id style="display:none">${n.name_id}</span>
              </h4>
              <div class="flex flex-wrap gap-2 text-[10px] sm:text-xs uppercase tracking-wider font-bold mt-1">
                <span class="${idx === 0 ? 'bg-[#10b981]/15 text-[#10b981]' : 'bg-primary/10 dark:bg-white/10 text-primary dark:text-gray-300'} px-2.5 py-1 rounded-full">
                  <span data-lang-en>${n.roleEn}</span>
                  <span data-lang-id style="display:none">${n.roleId}</span>
                </span>
                <span class="bg-blue-500/10 text-blue-600 dark:text-blue-400 px-2.5 py-1 rounded-full border border-blue-500/20">
                  <span data-lang-en>Location: ${n.residence}</span>
                  <span data-lang-id style="display:none">Lokasi: ${n.residence}</span>
                </span>
                <span class="bg-purple-500/10 text-purple-600 dark:text-purple-400 px-2.5 py-1 rounded-full border border-purple-500/20">
                  <span data-lang-en>Death: ${n.death_ah} AH</span>
                  <span data-lang-id style="display:none">Wafat: ${n.death_ah} H</span>
                </span>
              </div>
            </div>

            <div class="text-right shrink-0">
              <p class="font-arabic-body text-xl md:text-2xl text-primary dark:text-gray-200" dir="rtl">${n.ar}</p>
              ${n.kunyah !== '-' ? `<p class="text-xs text-outline dark:text-gray-500 mt-2" dir="rtl">كنية: ${n.kunyah}</p>` : ''}
            </div>

          </div>
        </div>

      </div>
    `;
    container.insertAdjacentHTML('beforeend', nodeHTML);
  });

  const countText = document.getElementById('sanad-count-text');
  if (countText) {
    countText.innerText = `${narrators.length} Narrators`;
  }

  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
}
"""

content = content[:start_idx] + new_func + content[end_idx:]

with open(APP_JS, 'w', encoding='utf-8') as f:
    f.write(content)
print("Successfully patched app.js loadSanadChain.")
