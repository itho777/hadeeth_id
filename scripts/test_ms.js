const fs = require('fs');
const chs = JSON.parse(fs.readFileSync('data/chapters/tabarani.json', 'utf8'));

for (let k in chs) {
  let title_ar = chs[k].title_ar || '';
  
  let clean = title_ar.replace(/ms\d+/gi, '').replace(/[0-9\s\-]+/g, '').trim();
  if (clean && title_ar.match(/ms\d+/i)) {
    console.log("Original:", title_ar);
    console.log("Cleaned:", title_ar.replace(/ms\d+/gi, '').replace(/\s+/g, ' ').trim());
    console.log("---");
  }
}
