const fs = require('fs');
const chs = JSON.parse(fs.readFileSync('data/chapters/tabarani.json', 'utf8'));

const out = {};
let lastValid = null;
let mergedBabTypoCount = 0;
let deletedNullCount = 0;

for (let k in chs) {
  let ch = chs[k];
  let title_ar = ch.title_ar ? ch.title_ar.trim() : '';
  let clean_title = title_ar.replace(/\s+/g, '');
  
  if (clean_title === 'باب' || clean_title === 'بأب') {
    // It's a typo of Bab (like 'ب اب' or 'ب أب') or just another Bab we missed
    // Merge into lastValid
    if (lastValid && ch.first_hadith !== null) {
      if (lastValid.first_hadith === null) {
        lastValid.first_hadith = ch.first_hadith;
      }
      if (ch.last_hadith !== null) {
        lastValid.last_hadith = ch.last_hadith;
      }
    }
    mergedBabTypoCount++;
    // Skip adding to out
  } else if (ch.first_hadith === null && ch.last_hadith === null) {
    // Empty structural header (like "باب الألف")
    // Delete it, no hadiths to merge
    deletedNullCount++;
  } else {
    out[k] = ch;
    lastValid = ch;
  }
}

fs.writeFileSync('data/chapters/tabarani.json', JSON.stringify(out, null, 2), 'utf8');
console.log(`Merged ${mergedBabTypoCount} typo 'Bab' sub-chapters (e.g. 'ب اب').`);
console.log(`Deleted ${deletedNullCount} empty structural headers (first_hadith === null).`);
console.log(`Remaining chapters: ${Object.keys(out).length}`);
