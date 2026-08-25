const fs = require('fs');
let txt = fs.readFileSync('js/app.js', 'utf8');

const regex = /var searchInput = document\.getElementById\('topic-search-input'\);\s*if \(searchInput\) \{\s*searchInput\.addEventListener\('input', function\(\) \{\s*var q = searchInput\.value\.toLowerCase\(\);\s*filteredHadiths = !q \? \[\.\.\.allHadiths\] : allHadiths\.filter\(function\(h\) \{([\s\S]*?)\}\);\s*currentPage = 1;\s*updateTopicPaginationUI\(\);\s*\}\);\s*\}/m;

const replacement = `var searchInput = document.getElementById('topic-search-input');
  var searchBtn = document.getElementById('topic-search-btn');
  
  function executeTopicSearch() {
      var q = searchInput ? searchInput.value.toLowerCase() : '';
      filteredHadiths = !q ? [...allHadiths] : allHadiths.filter(function(h) {
          let en = h.text_en || (h.translations && h.translations.en && h.translations.en[0] && h.translations.en[0].text) || '';
          let id = h.text_id || (h.translations && h.translations.id && h.translations.id[0] && h.translations.id[0].text) || '';
          let ar = h.text_ar || (h.translations && h.translations.ar && h.translations.ar[0] && h.translations.ar[0].text) || '';
          let num = String(h.id || h.hadith_number || '');
          return (en.toLowerCase().indexOf(q) >= 0) ||
                 (id.toLowerCase().indexOf(q) >= 0) ||
                 (ar.indexOf(q) >= 0) ||
                 (num.indexOf(q) >= 0);
      });
      currentPage = 1;
      updateTopicPaginationUI();
  }

  if (searchBtn) {
      searchBtn.addEventListener('click', executeTopicSearch);
  }
  if (searchInput) {
      searchInput.addEventListener('keypress', function(e) {
          if (e.key === 'Enter') executeTopicSearch();
      });
  }`;

txt = txt.replace(regex, replacement);
fs.writeFileSync('js/app.js', txt);
