const fs = require('fs');
const chs = JSON.parse(fs.readFileSync('data/chapters/tabarani.json', 'utf8'));

const out = {};
let lastValid = null;
let mergedCount = 0;

for (let k in chs) {
  let ch = chs[k];
  let title_ar = ch.title_ar ? ch.title_ar.trim() : '';
  
  if (title_ar === 'باب' || title_ar === 'باب.' || title_ar === 'باب:') {
    // Merge into lastValid
    if (lastValid && ch.first_hadith !== null) {
      if (lastValid.first_hadith === null) {
        lastValid.first_hadith = ch.first_hadith;
      }
      if (ch.last_hadith !== null) {
        lastValid.last_hadith = ch.last_hadith;
      }
    }
    mergedCount++;
    // Skip adding to out
  } else {
    out[k] = ch;
    lastValid = ch;
  }
}

fs.writeFileSync('data/chapters/tabarani.json', JSON.stringify(out, null, 2), 'utf8');
console.log(`Merged ${mergedCount} 'Bab' sub-chapters.`);
console.log(`Remaining chapters: ${Object.keys(out).length}`);
