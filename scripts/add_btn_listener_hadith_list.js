const fs = require('fs');
let txt = fs.readFileSync('js/app.js', 'utf8');

const regex = /if \(searchInput\) \{\s*searchInput\.addEventListener\('keyup', \(e\) => \{\s*if \(e\.key === 'Enter'\) performFilter\(\);\s*\}\);\s*\}/m;

const replacement = `var chapterSearchBtn = document.getElementById('chapter-search-btn');
  if (chapterSearchBtn) {
      chapterSearchBtn.addEventListener('click', performFilter);
  }
  if (searchInput) {
    searchInput.addEventListener('keyup', (e) => {
      if (e.key === 'Enter') performFilter();
    });
  }`;

txt = txt.replace(regex, replacement);
fs.writeFileSync('js/app.js', txt);
console.log('app.js updated');
