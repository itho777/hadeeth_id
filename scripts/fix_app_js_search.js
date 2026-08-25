const fs = require('fs');
let txt = fs.readFileSync('js/app.js', 'utf8');

const searchMarker = "var searchInput = document.getElementById('topic-search-input');";
const updateMarker = "updateTopicPaginationUI();\n}";

let startIdx = txt.indexOf(searchMarker);
if (startIdx !== -1) {
    let nextFuncIdx = txt.indexOf("window.inspectAlignment", startIdx);
    if (nextFuncIdx !== -1) {
        let replacement = `  var searchInput = document.getElementById('topic-search-input');
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
  }

  updateTopicPaginationUI();
}

`;
        txt = txt.slice(0, startIdx) + replacement + txt.slice(nextFuncIdx);
        fs.writeFileSync('js/app.js', txt);
        console.log("Replaced successfully!");
    } else {
        console.log("Could not find window.inspectAlignment");
    }
} else {
    console.log("Could not find searchMarker");
}
