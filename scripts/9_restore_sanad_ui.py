import os

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
      let rawiIds = data.rawis;
      
      // Filter out Prophet (1) since we hardcode it at the top
      // And filter out the author if it's already there? The old code just mapped whatever was in fawaz_to_rawis.
      
      narrators = rawiIds.map((rId, idx) => {
        const rawiData = rawisDict[rId] || {};
        const isFirst = idx === 0 || (rawiData.grade && rawiData.grade.toLowerCase().includes('sahab'));
        
        let enName = rawiData.en || 'Transmitter ' + rId;
        let idName = rawiData.id || 'Perawi ' + rId;
        
        return {
          rawi_id: rId,
          name: enName + (isFirst && !enName.includes('رضي الله عنه') ? ' (رضي الله عنه)' : ''),
          name_id: idName,
          roleEn: rawiData.role || (isFirst ? 'SAHABI (COMPANION) • GRADE: THIQAH' : 'TRANSMITTER (RAWI) • GRADE: ' + (rawiData.grade || 'THIQAH')),
          roleId: rawiData.roleId || (isFirst ? 'SAHABAT NABI • DERAJAT: TSIQAH' : 'PERAWI (RAWI) • DERAJAT: ' + (rawiData.grade || 'TSIQAH')),
          ar: rawiData.ar || idName,
          kunyah: rawiData.kunyah || (isFirst ? 'Abu Abdillah' : '-'),
          residence: rawiData.residence || (isFirst ? 'Madinah' : '-'),
          death_ah: rawiData.death_ah || (isFirst ? 'Early Era' : '-'),
          counts: rawiData.counts || '-',
          remarks: rawiData.grade ? 'Grade: ' + rawiData.grade : 'No remarks'
        };
      });
    }
  } catch (err) {
    console.warn('Failed to load sanad chain:', err);
  }

  if (narrators.length === 0) {
    narrators = [
      { rawi_id: null, name: "Sanad tidak terdeteksi", name_id: "Sanad tidak terdeteksi", roleEn: "UNKNOWN", roleId: "TIDAK DIKETAHUI", ar: "غير معروف", kunyah: "-", residence: "-", death_ah: "-", counts: "-", remarks: "Sistem belum mendeteksi teks sanad" }
    ];
  }

  const countText = document.getElementById('sanad-count-text');
  if (countText) {
    countText.innerHTML = `
      <span data-lang-en>${narrators.length} Narrators</span>
      <span data-lang-id style="display:none">${narrators.length} Perawi</span>
    `;
  }

  let html = `
    <div class="sanad-line"></div>

    <!-- Source: Prophet Muhammad -->
    <div class="sanad-node relative z-10 bg-gradient-to-r from-sunan-emerald to-emerald-800 text-white rounded-xl p-5 shadow-sm border border-emerald-600">
      <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-sunan-emerald border-2 border-white dark:border-ink-black flex items-center justify-center text-white text-[10px]">ﷺ</div>
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[10px] uppercase font-bold tracking-widest text-emerald-200">
            <span data-lang-en>SOURCE OF REVELATION</span>
            <span data-lang-id style="display:none">SUMBER WAHYU</span>
          </span>
          <h3 class="font-bold text-lg">
            <span data-lang-en>The Prophet Muhammad ﷺ</span>
            <span data-lang-id style="display:none">Nabi Muhammad ﷺ</span>
          </h3>
        </div>
        <span class="font-arabic-body text-xl" dir="rtl">محمد رسول الله ﷺ</span>
      </div>
    </div>
  `;

  // Filter out the Prophet (ID "1" or name containing Prophet) from the dynamic loop since we hardcode him above
  const filteredNarrators = narrators.filter(nr => nr.rawi_id !== "1" && !nr.name.toLowerCase().includes('prophet muhammad'));

  // Render Narrators from Companion down to Direct Sheikh of Author
  filteredNarrators.forEach((nr, idx) => {
    let rawiSlug = nr.rawi_id;
    if (!rawiSlug && nr.name) {
      const cleanName = nr.name.replace(/\(.*?\)/g, '').replace(/[^a-zA-Z0-9\s]/g, '').trim().toLowerCase().replace(/\s+/g, '_');
      rawiSlug = `rawi_${cleanName}`;
    }
    const profileUrl = `profile-detail.html?id=${encodeURIComponent(rawiSlug || 'rawi_abu_hurairah')}`;

    const roleEn = nr.roleEn;
    const roleId = nr.roleId;
    const nameEn = nr.name;
    const nameId = nr.name_id;
    const displayArName = nr.ar;
    
    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    html += `
      <div class="sanad-node relative z-10 bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-5 shadow-sm hover:border-sunan-emerald/50 transition-colors flex flex-col gap-3">
        <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-secondary text-white border-2 border-white dark:border-ink-black flex items-center justify-center text-[10px]">${idx + 1}</div>
        
        <div class="flex justify-between items-start border-b border-outline-variant/20 dark:border-[#334155] pb-3">
          <div>
            <span class="text-[10px] uppercase font-bold text-sunan-emerald dark:text-[#10b981]">
              <span data-lang-en>${escapeHtml(roleEn)}</span>
              <span data-lang-id style="display:none">${escapeHtml(roleId)}</span>
            </span>
            <a href="${profileUrl}" class="font-bold text-base text-primary dark:text-white hover:text-sunan-emerald dark:hover:text-[#10b981] hover:underline flex items-center gap-1 mt-0.5">
              <span data-lang-en>${escapeHtml(nameEn)}</span>
              <span data-lang-id style="display:none">${escapeHtml(nameId)}</span>
              <span class="material-symbols-outlined text-xs">open_in_new</span>
            </a>
          </div>
          <span class="font-arabic-body text-lg text-secondary dark:text-[#10b981]" dir="rtl">${escapeHtml(displayArName)}</span>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">KUNYAH:</span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.kunyah)}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>SETTLED IN:</span>
              <span data-lang-id style="display:none">DOMISILI:</span>
            </span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.residence)}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>WAFAT (DIED):</span>
              <span data-lang-id style="display:none">WAFAT:</span>
            </span>
            <span class="font-semibold text-primary dark:text-white">${escapeHtml(nr.death_ah)}</span>
          </div>
          <div>
            <span class="text-outline dark:text-gray-400 block text-[10px] uppercase font-bold">
              <span data-lang-en>TOTAL HADITHS:</span>
              <span data-lang-id style="display:none">TOTAL HADITS:</span>
            </span>
            <span class="font-semibold text-sunan-emerald dark:text-[#10b981]">${escapeHtml(nr.counts)}</span>
          </div>
        </div>

        ${nr.remarks ? `
          <div class="mt-2 pt-2 border-t border-outline-variant/10 dark:border-[#334155] text-xs text-on-surface-variant dark:text-gray-300 italic">
            <span class="font-bold text-secondary dark:text-[#10b981] not-italic text-[10px] uppercase block mb-0.5">
              <span data-lang-en>SCHOLAR REMARKS (JARH WA TA'DIL):</span>
              <span data-lang-id style="display:none">CATATAN ULAMA (JARH WA TA'DIL):</span>
            </span>
            "${escapeHtml(nr.remarks)}"
          </div>
        ` : ''}
      </div>
    `;
  });

  // Final Node: Collector & Author
  const authorNamesEn = {
    bukhari: 'Imam al-Bukhari',
    muslim: 'Imam Muslim',
    abudawud: 'Imam Abu Dawood',
    tirmidhi: 'Imam at-Tirmidhi',
    nasai: 'Imam an-Nasa\\'i',
    ibnmajah: 'Imam Ibn Majah',
    malik: 'Imam Malik bin Anas',
    ahmad: 'Imam Ahmad bin Hanbal',
    darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'
  };

  const authorNamesId = {
    bukhari: 'Imam al-Bukhari',
    muslim: 'Imam Muslim',
    abudawud: 'Imam Abu Daud',
    tirmidhi: 'Imam at-Tirmidzi',
    nasai: 'Imam an-Nasa\\'i',
    ibnmajah: 'Imam Ibn Majah',
    malik: 'Imam Malik bin Anas',
    ahmad: 'Imam Ahmad bin Hanbal',
    darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'
  };

  const authorNameEn = authorNamesEn[bookId.toLowerCase()] || 'Imam al-Bukhari';
  const authorNameId = authorNamesId[bookId.toLowerCase()] || 'Imam al-Bukhari';

  const authorIdMap = { 'bukhari': 'rawi_al_bukhari', 'muslim': 'rawi_muslim_ibn_hajjaj', 'abudawud': 'rawi_abu_dawud', 'tirmidhi': 'rawi_al_tirmidhi', 'nasai': 'rawi_al_nasai', 'ibnmajah': 'rawi_ibn_majah', 'malik': 'rawi_malik_bin_anas', 'ahmad': 'rawi_ahmad', 'darimi': 'rawi_darimi' };
  const authorProfileUrl = authorIdMap[bookId] ? `profile-detail.html?id=${authorIdMap[bookId]}` : `profile-detail.html?id=rawi_al_bukhari`;

  html += `
    <div class="sanad-node relative z-10 bg-primary text-white dark:bg-[#0f172a] border border-primary dark:border-[#334155] rounded-xl p-5 shadow-sm">
      <div class="absolute -left-11 top-6 w-6 h-6 rounded-full bg-primary border-2 border-white dark:border-ink-black flex items-center justify-center text-[10px]">📚</div>
      <div class="flex justify-between items-center">
        <div>
          <span class="text-[10px] uppercase font-bold tracking-widest text-[#10b981]">
            <span data-lang-en>COLLECTOR & AUTHOR</span>
            <span data-lang-id style="display:none">KOLEKTOR & PENULIS</span>
          </span>
          <a href="${authorProfileUrl}" class="font-bold text-lg hover:underline flex items-center gap-1 text-white">
            <span data-lang-en>${escapeHtml(authorNameEn)}</span>
            <span data-lang-id style="display:none">${escapeHtml(authorNameId)}</span>
            <span class="material-symbols-outlined text-xs">open_in_new</span>
          </a>
          <p class="text-xs text-gray-300">
            <span data-lang-en>Preserved in Authentic Canonical Corpus</span>
            <span data-lang-id style="display:none">Tercatat dalam Koleksi Kitab Shahih Utama</span>
          </p>
        </div>
      </div>
    </div>
  `;
  container.innerHTML = html;
  
  if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
}
"""

content = content[:start_idx] + new_func + content[end_idx:]

with open(APP_JS, 'w', encoding='utf-8') as f:
    f.write(content)
print("Successfully restored old Sanad UI design.")
