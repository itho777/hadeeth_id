#!/usr/bin/env python3
"""Apply client-side fixes for the 2026-11-20 audit.

Byte-exact replacements on CRLF files. Every replacement is asserted to occur
exactly once (or an expected count) so a silent miss cannot pass as a fix.
"""
from pathlib import Path
import sys
import re

ROOT = Path(r"G:/hadeeth_id")
NL = "\r\n"
changes = []


def patch(rel, pairs):
    p = ROOT / rel
    text = p.read_bytes().decode("utf-8")
    for old, new, expected in pairs:
        n = text.count(old)
        if n != expected:
            print(f"FAIL {rel}: expected {expected} occurrence(s), found {n}: {old[:120]!r}")
            sys.exit(1)
        text = text.replace(old, new)
        changes.append((rel, old[:70]))
    p.write_bytes(text.encode("utf-8"))
    print(f"patched {rel}: {len(pairs)} replacement group(s)")


# ---------------------------------------------------------------- app.js
app = []

# 1. Narrator link: brackets must stay adjacent to the name in innerText.
app.append((
    '      return `[<a href="profile-detail.html?${urlParams.toString()}" class="font-semibold text-primary-600 dark:text-primary-400 hover:underline inline-flex items-center gap-0.5" title="View Scholar Profile">\r\n'
    '                <span class="inline-block translate-y-[2px] opacity-70">\r\n'
    '                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>\r\n'
    '                </span>\r\n'
    '                ${displayName}\r\n'
    '              </a>]`;',
    '      return `[<a href="profile-detail.html?${urlParams.toString()}" class="font-semibold text-primary-600 dark:text-primary-400 hover:underline" title="View Scholar Profile">${displayName}</a>]`;',
    1,
))

# 2. Mojibake left in JS string literals.
app.append(("      ar: 'Ù…ØµÙ†Ù\x81 ابن أبي شيبة',", "      ar: 'مصنف ابن أبي شيبة',", 1))
app.append(("name_ar: 'كتاب Ø§Ù„Ù\x81Ø±Ø§Ø¦Ø¶'", "name_ar: 'كتاب الفرائض'", 1))
app.append(("name_ar: 'كتاب Ù\x81Ø¶Ø§Ø¦Ù„ القرآن'", "name_ar: 'كتاب فضائل القرآن'", 1))
app.append(("name_ar: 'Ø§Ù„Ù\x81ØµÙ„ الأول'", "name_ar: 'الفصل الأول'", 1))
app.append(("'بنØª': 'bint'", "'بنت': 'bint'", 1))
app.append(("'Ù†Ø§Ù\x81Ø¹': 'Nafi\\''", "'نافع': 'Nafi\\''", 1))
app.append(("ar: \"غير Ù…Ø¹Ø±ÙˆÙ\x81\"", "ar: \"غير معروف\"", 1))
app.append((".replace(/\\(رضي الله عنهØ§\\)/gi, '')", ".replace(/\\(رضي الله عنه\\)/gi, '')", 1))

# 3. Topic cards: English fallback from the edition files.
app.append((
    "  async function updateTopicPaginationUI() {",
    """  async function enrichTopicEnglish(items) {
    if (!Array.isArray(items) || items.length === 0 || !window.HadeethAPI) return;
    const need = items.filter(x => !x.text_en && !(x.translations && x.translations.en && x.translations.en.length));
    if (need.length === 0) return;
    // ahmad and darimi have no eng-<book> edition in the R2 catalogue.
    if (bookId === 'ahmad' || bookId === 'darimi') return;

    const baseUrl = window.__HADEETH_BASE__ ? window.__HADEETH_BASE__ + '/data' : window.location.origin + window.location.pathname.replace(/\\/[^/]*$/, '') + '/data';
    const cacheKey = '__topicLinkGraph_' + bookId;
    if (window[cacheKey] === undefined) {
      window[cacheKey] = null;
      try {
        const resp = await fetch(`${baseUrl}/links/${bookId}.json`);
        if (resp.ok) window[cacheKey] = await resp.json();
      } catch (e) { window[cacheKey] = null; }
    }
    const graph = window[cacheKey];
    if (!graph || !graph.fawaz_to_lidwa) return;

    const lidwaToFawaz = {};
    Object.keys(graph.fawaz_to_lidwa).forEach(f => {
      const lidwa = String(graph.fawaz_to_lidwa[f]);
      if (!(lidwa in lidwaToFawaz)) lidwaToFawaz[lidwa] = f;
    });

    const enCache = window.__topicEnCache || (window.__topicEnCache = new Map());
    await Promise.all(need.map(async item => {
      const lidwaNum = String(window.HadeethAPI.hadithNumberOf(item, 'lidwa'));
      const fawazNum = lidwaToFawaz[lidwaNum];
      if (!fawazNum) return;
      const key = bookId + ':' + fawazNum;
      let txt = enCache.get(key);
      if (txt === undefined) {
        try { txt = await window.HadeethAPI.getEditionText('eng', bookId, fawazNum); }
        catch (e) { txt = null; }
        enCache.set(key, txt || '');
      }
      if (txt) {
        item.text_en = txt;
        item.en_link_text = '[Terjemahan EN: Fawazahmed #' + fawazNum + ']';
      }
    }));
  }

  async function updateTopicPaginationUI() {""",
    1,
))
app.append((
    "        pageData = await window.HadeethAPI.getHadithsBatch(bookId, pageIds, 'lidwa');",
    "        pageData = await window.HadeethAPI.getHadithsBatch(bookId, pageIds, 'lidwa');\r\n        await enrichTopicEnglish(pageData);",
    1,
))

# 4. Topic card markup: div inside p + debug source line.
app.append(("<div class='mb-2 text-xs text-blue-500 font-semibold'>", "<span class='block mb-2 text-xs text-blue-500 font-semibold'>", 4))
app.append(("${escapeHtml(idLinkText)}</div>", "${escapeHtml(idLinkText)}</span>", 4))
app.append(("<div class='mb-2 text-xs text-amber-500 font-semibold'>", "<span class='block mb-2 text-xs text-amber-500 font-semibold'>", 3))
app.append(("${escapeHtml(enLinkText)}</div>", "${escapeHtml(enLinkText)}</span>", 3))
app.append(("        + '<p class=\"text-[11px] text-blue-500/70 mt-1 italic\">Source: unified NDJSON engine</p></div>';", "        + '</div>';", 3))

# 5. Sanad: no fake narrator, no Bukhari collector for other books.
app.append((
    """  if (narrators.length === 0) {
    narrators = [
      { rawi_id: null, name: "Sanad tidak terdeteksi", name_id: "Sanad tidak terdeteksi", roleEn: "UNKNOWN", roleId: "TIDAK DIKETAHUI", ar: "غير معروف", kunyah: "-", residence: "-", death_ah: "-", counts: "-", remarks: "Sistem belum mendeteksi teks sanad" }
    ];
  }
""".replace("\n", "\r\n"),
    """  if (narrators.length === 0) {
    const countTextEmpty = document.getElementById('sanad-count-text');
    if (countTextEmpty) {
      countTextEmpty.innerHTML = '<span data-lang-en>0 Narrators</span><span data-lang-id style="display:none">0 Perawi</span>';
    }
    const emptyContainer = document.getElementById('sanad-nodes-container');
    if (emptyContainer) {
      emptyContainer.innerHTML = `
        <div class="sanad-node relative z-10 bg-surface dark:bg-[#1e293b] border border-outline-variant/30 dark:border-[#334155] rounded-xl p-6 shadow-sm flex items-start gap-3">
          <span class="material-symbols-outlined text-secondary dark:text-[#10b981]">info</span>
          <div>
            <h3 class="font-bold text-base text-primary dark:text-white">
              <span data-lang-en>Chain of narration not available</span>
              <span data-lang-id style="display:none">Rantai sanad belum tersedia</span>
            </h3>
            <p class="text-sm text-on-surface-variant dark:text-gray-300 mt-1">
              <span data-lang-en>The digital source for this collection does not include narrator metadata. The Arabic matn is still complete.</span>
              <span data-lang-id style="display:none">Sumber digital kitab ini tidak menyertakan metadata perawi. Teks matan Arab tetap lengkap.</span>
            </p>
          </div>
        </div>`;
    }
    if (window.LangSystem) window.LangSystem.apply(window.LangSystem.get());
    return;
  }
""".replace("\n", "\r\n"),
    1,
))
app.append(("remarks: rawiData.grade ? 'Grade: ' + rawiData.grade : 'No remarks'", "remarks: rawiData.grade ? 'Grade: ' + rawiData.grade : ''", 1))

# 6. Author metadata: use the real author, never Bukhari as a fallback.
app.append((
    "    const authorNameEn = authorNamesEn[bookId.toLowerCase()] || 'Imam al-Bukhari';\r\n"
    "    const authorNameId = authorNamesId[bookId.toLowerCase()] || 'Imam al-Bukhari';\r\n"
    "    const authorIdMap = { 'bukhari': 'rawi_al_bukhari', 'muslim': 'rawi_muslim_ibn_hajjaj', 'abudawud': 'rawi_abu_dawud', 'tirmidhi': 'rawi_al_tirmidhi', 'nasai': 'rawi_al_nasai', 'ibnmajah': 'rawi_ibn_majah', 'malik': 'rawi_malik_bin_anas', 'ahmad': 'rawi_ahmad', 'darimi': 'rawi_darimi' };\r\n"
    "    const authorProfileUrl = authorIdMap[bookId] ? `profile-detail.html?id=${authorIdMap[bookId]}` : `profile-detail.html?id=rawi_al_bukhari`;",
    "    const authorNameEn = authorNamesEn[bookId.toLowerCase()] || 'Unknown Author';\r\n"
    "    const authorNameId = authorNamesId[bookId.toLowerCase()] || 'Penulis tidak diketahui';\r\n"
    "    const authorIdMap = { 'bukhari': 'rawi_al_bukhari', 'muslim': 'rawi_muslim_ibn_hajjaj', 'abudawud': 'rawi_abu_dawud', 'tirmidhi': 'rawi_al_tirmidhi', 'nasai': 'rawi_al_nasai', 'ibnmajah': 'rawi_ibn_majah', 'malik': 'rawi_malik_bin_anas', 'ahmad': 'rawi_ahmad', 'darimi': 'rawi_darimi' };\r\n"
    "    const authorProfileUrl = authorIdMap[bookId] ? `profile-detail.html?id=${authorIdMap[bookId]}` : '';",
    1,
))

# Add the authors that were missing from the two maps.
app.append((
    "      tirmidhi: 'Imam at-Tirmidhi', nasai: 'Imam an-Nasa\\'i', ibnmajah: 'Imam Ibn Majah',\r\n"
    "      malik: 'Imam Malik bin Anas', ahmad: 'Imam Ahmad bin Hanbal', darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'\r\n    };",
    "      tirmidhi: 'Imam at-Tirmidhi', nasai: 'Imam an-Nasa\\'i', ibnmajah: 'Imam Ibn Majah',\r\n"
    "      malik: 'Imam Malik bin Anas', ahmad: 'Imam Ahmad bin Hanbal', darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi',\r\n"
    "      muntaqa: 'Imam Majd al-Din Ibn Taymiyya', maani: 'Imam Abu Ja\\'far al-Tahawi', masabih: 'Imam Abu Muhammad al-Baghawi',\r\n"
    "      umdat: 'Imam Ibn Daqiq al-\\'Id', shah: 'Shah Waliullah Dehlawi', nawawi: 'Imam an-Nawawi',\r\n"
    "      riyad: 'Imam an-Nawawi', riyad_arab: 'Imam an-Nawawi', shamail: 'Imam at-Tirmidhi', bulugh: 'Ibn Hajar al-Asqalani',\r\n"
    "      adab: 'Imam al-Bukhari', mishkat: 'Al-Tabrizi', qudsi: 'Multiple', dehlawi: 'Shah Waliullah Dehlawi',\r\n"
    "      tabarani: 'Imam at-Tabarani', tabarani_kabir: 'Imam at-Tabarani', syafii: 'Imam as-Syafi\\'i',\r\n"
    "      ibn_abi_shaybah: 'Imam Ibn Abi Shaybah', ibnukhuzaimah: 'Imam Ibn Khuzaimah', ibnuhibban: 'Imam Ibn Hibban',\r\n"
    "      mustadrak: 'Imam al-Hakim al-Nishapuri', daruquthni: 'Imam ad-Daruquthni'\r\n    };",
    1,
))
app.append((
    "      tirmidhi: 'Imam at-Tirmidzi', nasai: 'Imam an-Nasa\\'i', ibnmajah: 'Imam Ibn Majah',\r\n"
    "      malik: 'Imam Malik bin Anas', ahmad: 'Imam Ahmad bin Hanbal', darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi'\r\n    };",
    "      tirmidhi: 'Imam at-Tirmidzi', nasai: 'Imam an-Nasa\\'i', ibnmajah: 'Imam Ibn Majah',\r\n"
    "      malik: 'Imam Malik bin Anas', ahmad: 'Imam Ahmad bin Hanbal', darimi: 'Imam Abdullah bin Abdul Rahman ad-Darimi',\r\n"
    "      muntaqa: 'Imam Majd ad-Din Ibnu Taimiyyah', maani: 'Imam Abu Ja\\'far ath-Thahawi', masabih: 'Imam Abu Muhammad al-Baghawi',\r\n"
    "      umdat: 'Imam Ibnu Daqiq al-\\'Id', shah: 'Shah Waliullah ad-Dahlawi', nawawi: 'Imam an-Nawawi',\r\n"
    "      riyad: 'Imam an-Nawawi', riyad_arab: 'Imam an-Nawawi', shamail: 'Imam at-Tirmidzi', bulugh: 'Ibnu Hajar al-Asqalani',\r\n"
    "      adab: 'Imam al-Bukhari', mishkat: 'Al-Tabrizi', qudsi: 'Beragam', dehlawi: 'Shah Waliullah ad-Dahlawi',\r\n"
    "      tabarani: 'Imam ath-Thabarani', tabarani_kabir: 'Imam ath-Thabarani', syafii: 'Imam asy-Syafi\\'i',\r\n"
    "      ibn_abi_shaybah: 'Imam Ibnu Abi Syaibah', ibnukhuzaimah: 'Imam Ibnu Khuzaimah', ibnuhibban: 'Imam Ibnu Hibban',\r\n"
    "      mustadrak: 'Imam al-Hakim an-Naisaburi', daruquthni: 'Imam ad-Daruquthni'\r\n    };",
    1,
))

# Collector node: link only when a profile exists.
app.append((
    "          <a href=\"${authorProfileUrl}\" class=\"font-bold text-lg hover:underline flex items-center gap-1 text-white\">\r\n"
    "            <span data-lang-en>${escapeHtml(authorNameEn)}</span>\r\n"
    "            <span data-lang-id style=\"display:none\">${escapeHtml(authorNameId)}</span>\r\n"
    "            <span class=\"material-symbols-outlined text-xs\">open_in_new</span>\r\n"
    "          </a>",
    "          ${authorProfileUrl ? `<a href=\"${authorProfileUrl}\" class=\"font-bold text-lg hover:underline flex items-center gap-1 text-white\">` : '<span class=\"font-bold text-lg flex items-center gap-1 text-white\">'}\r\n"
    "            <span data-lang-en>${escapeHtml(authorNameEn)}</span>\r\n"
    "            <span data-lang-id style=\"display:none\">${escapeHtml(authorNameId)}</span>\r\n"
    "            ${authorProfileUrl ? '<span class=\"material-symbols-outlined text-xs\">open_in_new</span>' : ''}\r\n"
    "          ${authorProfileUrl ? '</a>' : '</span>'}",
    1,
))

# 7. bookMasterDict: the five books that rendered bare slugs.
app.append((
    "    daruquthni: {\r\n"
    "      name: 'Sunan Daruquthni',\r\n"
    "      ar: 'سنن الدارقطني',\r\n"
    "      author: 'Imam Ad-Daruquthni',\r\n"
    "      authorId: 'rawi_bukhari', // fallback\r\n"
    "      type: \"Sunan\",\r\n"
    "      badgeClass: 'bg-indigo-600 text-white',\r\n"
    "      desc: 'A collection focusing on legal hadiths and detailing hidden defects (ilal) in chains.',\r\n"
    "      desc_id: 'Koleksi yang berfokus pada hadits fiqih dan merinci cacat tersembunyi (ilal) dalam sanad.',\r\n"
    "      kitabCount: '📚 1 Kitab',\r\n"
    "      hadithCount: '📖 236 Hadits',\r\n"
    "      authenticity: '⭐️ Sunan',\r\n"
    "      datasetInfo: { native_mjna: { kitab: '📚 1 Kitab', hadith: '📖 236 Hadits (MJNA)', numbering: 'Penomoran: MJNA (1–239)' } }\r\n"
    "    }\r\n"
    "  };",
    "    daruquthni: {\r\n"
    "      name: 'Sunan Daruquthni',\r\n"
    "      ar: 'سنن الدارقطني',\r\n"
    "      author: 'Imam Ad-Daruquthni',\r\n"
    "      authorId: 'rawi_bukhari', // fallback\r\n"
    "      type: \"Sunan\",\r\n"
    "      badgeClass: 'bg-indigo-600 text-white',\r\n"
    "      desc: 'A collection focusing on legal hadiths and detailing hidden defects (ilal) in chains.',\r\n"
    "      desc_id: 'Koleksi yang berfokus pada hadits fiqih dan merinci cacat tersembunyi (ilal) dalam sanad.',\r\n"
    "      kitabCount: '📚 1 Kitab',\r\n"
    "      hadithCount: '📖 236 Hadits',\r\n"
    "      authenticity: '⭐️ Sunan',\r\n"
    "      datasetInfo: { native_mjna: { kitab: '📚 1 Kitab', hadith: '📖 236 Hadits (MJNA)', numbering: 'Penomoran: MJNA (1–239)' } }\r\n"
    "    },\r\n"
    "    muntaqa: {\r\n"
    "      name: 'Muntaqa al-Akhbar',\r\n"
    "      ar: 'منتقى الأخبار',\r\n"
    "      author: 'Imam Majd al-Din Ibn Taymiyya',\r\n"
    "      authorId: '',\r\n"
    "      type: 'Musnad',\r\n"
    "      badgeClass: 'bg-teal-700 text-white',\r\n"
    "      desc: 'A collection of legal hadiths compiled by Imam Majd al-Din Ibn Taymiyya.',\r\n"
    "      desc_id: 'Koleksi hadits hukum yang disusun oleh Imam Majd ad-Din Ibnu Taimiyyah.',\r\n"
    "      kitabCount: '📚 1.109 Kitab',\r\n"
    "      hadithCount: '📖 3.944 Hadits',\r\n"
    "      authenticity: '⭐️ Musnad',\r\n"
    "      datasetInfo: { native_turath: { kitab: '📚 1.109 Kitab', hadith: '📖 3.944 Hadits', numbering: 'Penomoran: Turath (1–3944)' } }\r\n"
    "    },\r\n"
    "    maani: {\r\n"
    "      name: \"Ma'ani al-Athar\",\r\n"
    "      ar: 'معاني الآثار',\r\n"
    "      author: \"Imam Abu Ja'far al-Tahawi\",\r\n"
    "      authorId: '',\r\n"
    "      type: 'Sunan',\r\n"
    "      badgeClass: 'bg-indigo-600 text-white',\r\n"
    "      desc: 'A comparative collection of legal traditions by Imam al-Tahawi.',\r\n"
    "      desc_id: 'Koleksi hadits hukum komparatif karya Imam ath-Thahawi.',\r\n"
    "      kitabCount: '📚 1 Kitab',\r\n"
    "      hadithCount: '📖 7.013 Hadits',\r\n"
    "      authenticity: '⭐️ Sunan',\r\n"
    "      datasetInfo: { native_turath: { kitab: '📚 1 Kitab', hadith: '📖 7.013 Hadits', numbering: 'Penomoran: Turath (1–7013)' } }\r\n"
    "    },\r\n"
    "    masabih: {\r\n"
    "      name: 'Masabih al-Sunna',\r\n"
    "      ar: 'مصابيح السنة',\r\n"
    "      author: 'Imam Abu Muhammad al-Baghawi',\r\n"
    "      authorId: '',\r\n"
    "      type: 'Sunan',\r\n"
    "      badgeClass: 'bg-amber-600 text-white',\r\n"
    "      desc: 'The original collection later expanded into Mishkat al-Masabih.',\r\n"
    "      desc_id: 'Koleksi asal yang kemudian diperluas menjadi Misykah al-Mashabih.',\r\n"
    "      kitabCount: '📚 1 Kitab',\r\n"
    "      hadithCount: '📖 4.929 Hadits',\r\n"
    "      authenticity: '⭐️ Sunan',\r\n"
    "      datasetInfo: { native_turath: { kitab: '📚 1 Kitab', hadith: '📖 4.929 Hadits', numbering: 'Penomoran: Turath (1–4929)' } }\r\n"
    "    },\r\n"
    "    umdat: {\r\n"
    "      name: 'Umdat al-Ahkam',\r\n"
    "      ar: 'عمدة الأحكام',\r\n"
    "      author: \"Imam Ibn Daqiq al-'Id\",\r\n"
    "      authorId: '',\r\n"
    "      type: \"Jawami'\",\r\n"
    "      badgeClass: 'bg-teal-600 text-white',\r\n"
    "      desc: 'A concise selection of legal hadiths agreed upon by Bukhari and Muslim.',\r\n"
    "      desc_id: 'Pilihan ringkas hadits hukum yang disepakati Bukhari dan Muslim.',\r\n"
    "      kitabCount: '📚 1 Kitab',\r\n"
    "      hadithCount: '📖 414 Hadits',\r\n"
    "      authenticity: '⭐️ Jawami',\r\n"
    "      datasetInfo: { native_turath: { kitab: '📚 1 Kitab', hadith: '📖 414 Hadits', numbering: 'Penomoran: Turath (1–414)' } }\r\n"
    "    },\r\n"
    "    shah: {\r\n"
    "      name: \"Shah Waliullah's Arba'in\",\r\n"
    "      ar: 'أربعون الشاه ولي الله',\r\n"
    "      author: 'Shah Waliullah Dehlawi',\r\n"
    "      authorId: '',\r\n"
    "      type: \"Arba'un\",\r\n"
    "      badgeClass: 'bg-emerald-700 text-white',\r\n"
    "      desc: 'Forty selected hadiths by Shah Waliullah Dehlawi.',\r\n"
    "      desc_id: 'Empat puluh hadits pilihan Shah Waliullah ad-Dahlawi.',\r\n"
    "      kitabCount: '📚 1 Kitab',\r\n"
    "      hadithCount: '📖 40 Hadits',\r\n"
    "      authenticity: '⭐️ Arbaun',\r\n"
    "      datasetInfo: { native_turath: { kitab: '📚 1 Kitab', hadith: '📖 40 Hadits', numbering: 'Penomoran: Turath (1–40)' } }\r\n"
    "    }\r\n"
    "  };",
    1,
))

# 8. Chapter cards: short display number + honest row count.
app.append((
    "      const hadithCount = ch.hadith_count != null ? ch.hadith_count\r\n"
    "        : (ch.hadith_end && ch.hadith_start ? (ch.hadith_end - ch.hadith_start + 1) : '');",
    "      const hadithCount = ch.hadith_count != null ? ch.hadith_count\r\n"
    "        : (ch.hadith_end && ch.hadith_start ? (ch.hadith_end - ch.hadith_start + 1) : '');\r\n"
    "      const displayNum = ch.display_number || chNum;\r\n"
    "      const rowCountNote = (ch.row_count && hadithCount && Number(ch.row_count) !== Number(hadithCount)) ? ` (${ch.row_count} riwayat)` : '';",
    1,
))
app.append((
    "          <div class=\"flex gap-4 items-center\">\r\n"
    "            <div class=\"w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/10 text-secondary dark:text-[#10b981] font-bold text-sm flex items-center justify-center flex-shrink-0\">${chNum === 0 || chNum === '0' ? 'M' : chNum}</div>",
    "          <div class=\"flex gap-4 items-center\">\r\n"
    "            <div class=\"w-10 h-10 rounded-full bg-secondary/10 dark:bg-[#10b981]/10 text-secondary dark:text-[#10b981] font-bold text-sm flex items-center justify-center flex-shrink-0\">${displayNum === 0 || displayNum === '0' ? 'M' : displayNum}</div>",
    1,
))
app.append((
    "${escapeHtml(hadithRange)}${hadithCount ? ` &bull; ${hadithCount} hadiths` : ''}",
    "${escapeHtml(hadithRange)}${hadithCount ? ` &bull; ${hadithCount} hadiths` : ''}${rowCountNote}",
    1,
))
app.append((
    "        const titleId = ch.title_id || `Kitab ${chNum}`;",
    "        const titleId = ch.title_id || ch.title_ar || `Kitab ${chNum}`;",
    1,
))
app.append((
    "${titleAr ? `<span class=\"text-xs text-on-surface-variant dark:text-gray-400 font-arabic-body\" dir=\"rtl\">${escapeHtml(titleAr)}</span>` : ''}",
    "${titleAr && titleAr !== titleId ? `<span class=\"text-xs text-on-surface-variant dark:text-gray-400 font-arabic-body\" dir=\"rtl\">${escapeHtml(titleAr)}</span>` : ''}",
    3,
))

patch("js/app.js", app)

# ---------------------------------------------------------------- hadith.html
patch("hadith.html", [
    (
        '        <p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed" data-english-text>\r\n        </p>',
        '        <div class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed" data-english-text>\r\n          <span class="text-xs text-outline dark:text-gray-500 italic">English translation not available for this hadith.</span>\r\n        </div>',
        1,
    ),
    (
        '        <p class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed" data-indonesian-text>\r\n        </p>',
        '        <div class="text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed" data-indonesian-text>\r\n          <span class="text-xs text-outline dark:text-gray-500 italic">Terjemahan Indonesia tidak tersedia untuk hadits ini.</span>\r\n        </div>',
        1,
    ),
])

# ---------------------------------------------------------------- privacy.html
patch("privacy.html", [("Ã¢â‚¬â€\x9d", "—", 8)])

# ---------------------------------------------------------------- scholars.html
scholars_raw = (ROOT / "scholars.html").read_bytes().decode("utf-8")

cp1252_rev = {}
for i in range(32, 256):
    try:
        cp1252_rev[bytes([i]).decode("cp1252")] = i
    except Exception:
        pass
for i in (0x81, 0x8D, 0x8F, 0x90, 0x9D):
    cp1252_rev[chr(i)] = i


def demojibake_segment(s):
    out = bytearray()
    for ch in s:
        o = ord(ch)
        if o < 256:
            out.append(o)
        elif ch in cp1252_rev:
            out.append(cp1252_rev[ch])
        else:
            return s
    try:
        return out.decode("utf-8")
    except UnicodeDecodeError:
        return s


def demojibake_mixed(s):
    parts = re.split(r"([\u0600-\u06FF]+)", s)
    return "".join(p if re.fullmatch(r"[\u0600-\u06FF]+", p or "") else demojibake_segment(p) for p in parts)


start = scholars_raw.index("const arNameDict = {")
end = scholars_raw.index("\n  };", start)
block = scholars_raw[start:end]
fixed_block = re.sub(r"('[^']*':\s*')([^']*)(')", lambda m: m.group(1) + demojibake_mixed(m.group(2)) + m.group(3), block)
scholars_raw = scholars_raw[:start] + fixed_block + scholars_raw[end:]

# dateStr is escaped later, so the entity must be a literal character here.
scholars_raw = scholars_raw.replace("dateStr += ` &bull; ${cityStr}`;", "dateStr += ` • ${cityStr}`;")

(ROOT / "scholars.html").write_bytes(scholars_raw.encode("utf-8"))
print("patched scholars.html: arNameDict + bullet")

print("OK", len(changes), "groups")
