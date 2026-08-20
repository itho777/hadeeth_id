"""
Comprehensive fix for profile-detail.html:
1. Fix Mojibake in static Arabic labels (Kunyah, Settled In, bio-provenance-text, page title, meta)
2. Add missing switchBioTab() and filterEvalTab() JS functions
3. Remove duplicate Scholars nav link
"""

import re

with open('profile-detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────
# 1. Fix Mojibake in the static "Kunyah / Kuniyah" label line
# The corrupted text Ã˜Â£Ã˜Â¨Ã™Ë†/Ã˜Â£Ã™â€¦ should be أبو/أم
# ─────────────────────────────────────────────────────────────────
html = html.replace(
    'Kunyah / Kuniyah (Ã˜Â£Ã˜Â¨Ã™Ë†/Ã˜Â£Ã™â€¦)',
    'Kunyah / Kuniyah (أبو/أم)'
)
html = html.replace(
    'Kuniyah / Gelar (Ã˜Â£Ã˜Â¨Ã™Ë†/Ã˜Â£Ã™â€¦)',
    'Kuniyah / Gelar (أبو/أم)'
)

# ─────────────────────────────────────────────────────────────────
# 2. Fix Mojibake in the "Settled In" label
# "بلد الإقامة" → corrupted as Ã˜Â¨Ã™â€žÃ˜Â¯ Ã˜Â§Ã™â€žÃ˜Â¥Ã™â€šÃ˜Â§Ã™â€¦Ã˜Â©
# ─────────────────────────────────────────────────────────────────
html = html.replace(
    'Settled In (Ã˜Â¨Ã™â€žÃ˜Â¯ Ã˜Â§Ã™â€žÃ˜Â¥Ã™â€šÃ˜Â§Ã™â€¦Ã˜Â©)',
    'Settled In (بلد الإقامة)'
)
html = html.replace(
    'Tempat Tinggal / Wafat (Ã˜Â¨Ã™â€žÃ˜Â¯ Ã˜Â§Ã™â€žÃ˜Â¥Ã™â€šÃ˜Â§Ã™â€¦Ã˜Â©)',
    'Tempat Tinggal / Wafat (بلد الإقامة)'
)

# ─────────────────────────────────────────────────────────────────
# 3. Fix Mojibake in bio-provenance-text  
# "تقريب التهذيب" → corrupted
# ─────────────────────────────────────────────────────────────────
html = html.replace(
    '>Source: Taqrib al-Tahdhib (Ã˜ÂªÃ™â€šÃ˜Â±Ã™Å Ã˜Â¨ Ã˜Â§Ã™â€žÃ˜ÂªÃ™â€¡Ã˜Â°Ã™Å Ã˜Â¨) Ã¢â‚¬â€ Hafiz Ibn Hajar al-\'Asqalani<',
    '>Source: Taqrib al-Tahdhib (تقريب التهذيب) — Hafiz Ibn Hajar al-\'Asqalani<'
)

# ─────────────────────────────────────────────────────────────────
# 4. Fix Mojibake in page <title>
# ─────────────────────────────────────────────────────────────────
html = html.replace(
    "<title>Narrator Profile: 'Umar bin Al-Khattab Ã¢â‚¬â€ HADEETH.ID</title>",
    "<title>Narrator Profile — HADEETH.ID</title>"
)

# ─────────────────────────────────────────────────────────────────
# 5. Fix Mojibake in meta description
# ─────────────────────────────────────────────────────────────────
html = html.replace(
    'content="HADEETH.ID Ã¢â‚¬â€ Scholar &amp; Rawi Detailed Biography',
    'content="HADEETH.ID — Scholar &amp; Rawi Detailed Biography'
)

# ─────────────────────────────────────────────────────────────────
# 6. Remove duplicate "Scholars" nav link (line 47 is the extra one)
# We keep the one with the active styling (line 48)
# ─────────────────────────────────────────────────────────────────
html = html.replace(
    '    <a href="scholars.html" class="hover:underline" data-i18n="nav_scholars">Scholars</a>\n',
    ''
)

# ─────────────────────────────────────────────────────────────────
# 7. Add missing switchBioTab and filterEvalTab JS functions
#    Insert them just before the closing </script> of the renderProfileData block
# ─────────────────────────────────────────────────────────────────
tab_functions = '''
  // ── Bio Source Tab Switcher ──────────────────────────────────
  const BIO_TABS = {
    taqrib: {
      label_en: 'Taqrib al-Tahdhib',
      label_id: 'Taqrib at-Tahdzib',
      provenance: 'Source: Taqrib al-Tahdhib (تقريب التهذيب) — Hafiz Ibn Hajar al-Asqalani'
    },
    wiki: {
      label_en: 'Wikipedia / Wikidata',
      label_id: 'Wikipedia / Wikidata',
      provenance: 'Source: Wikipedia / Wikidata (CC BY-SA 4.0)'
    },
    siyar: {
      label_en: "Siyar A\\'lam al-Nubala",
      label_id: "Siyar A\\'lam an-Nubala",
      provenance: "Source: Siyar A\\'lam al-Nubala (سير أعلام النبلاء) — Imam al-Dhahabi"
    }
  };

  let _activeBioTab = 'taqrib';

  function switchBioTab(tabId) {
    _activeBioTab = tabId;
    const tabs = ['taqrib', 'wiki', 'siyar'];
    tabs.forEach(t => {
      const btn = document.getElementById('tab-btn-' + t);
      if (!btn) return;
      if (t === tabId) {
        btn.className = 'px-3 py-1.5 rounded-lg bg-primary dark:bg-[#10b981] text-white dark:text-black font-bold shadow-sm transition-all';
      } else {
        btn.className = 'px-3 py-1.5 rounded-lg text-outline dark:text-gray-400 hover:text-primary dark:hover:text-white transition-all';
      }
    });
    const meta = BIO_TABS[tabId] || BIO_TABS.taqrib;
    const prov = document.getElementById('bio-provenance-text');
    if (prov) prov.textContent = meta.provenance;
    // Bio content: show placeholder since we don't have multi-source data yet
    const content = document.getElementById('bio-stories-content');
    if (content) {
      content.innerHTML = '<p class="text-xs text-outline dark:text-gray-400 italic p-4 text-center">Loading ' + meta.label_en + ' data...</p>';
    }
  }

  // ── Eval Critic Tab Switcher ──────────────────────────────────
  let _activeEvalTab = 'all';

  function filterEvalTab(tabId) {
    _activeEvalTab = tabId;
    const tabs = ['all', 'ibnhajar', 'dhahabi'];
    tabs.forEach(t => {
      const btn = document.getElementById('eval-tab-' + t);
      if (!btn) return;
      if (t === tabId) {
        btn.className = 'px-3 py-1.5 rounded-lg bg-primary dark:bg-[#10b981] text-white dark:text-black font-bold shadow-sm transition-all cursor-pointer';
      } else {
        btn.className = 'px-3 py-1.5 rounded-lg text-outline dark:text-gray-400 hover:text-primary dark:hover:text-white transition-all cursor-pointer';
      }
    });
    // Filter visible remark cards
    document.querySelectorAll('#remarks-grid [data-critic]').forEach(card => {
      card.style.display = (tabId === 'all' || card.dataset.critic === tabId) ? '' : 'none';
    });
  }
'''

# Insert functions before the closing </script> tag of the last script block
html = html.replace(
    '  // Call it when DOM is ready\n  document.addEventListener(\'DOMContentLoaded\', () => {',
    tab_functions + '\n  // Call it when DOM is ready\n  document.addEventListener(\'DOMContentLoaded\', () => {'
)

with open('profile-detail.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('profile-detail.html fully patched!')
