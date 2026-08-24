const fs = require('fs');
const chs = JSON.parse(fs.readFileSync('data/chapters/tabarani.json', 'utf8'));

const out = {};
let lastValid = null;
let mergedCount = 0;
let cleanedCount = 0;

for (let k in chs) {
  let ch = chs[k];
  let title = ch.title || '';
  let title_ar = ch.title_ar || '';
  
  // Clean msXXXX and dangling numbers/hyphens
  let clean_title = title.replace(/ms\d+/gi, '').replace(/[\s\-]+/g, ' ').trim();
  let clean_title_ar = title_ar.replace(/ms\d+/gi, '').replace(/[\s\-]+/g, ' ').trim();
  
  // Is it entirely an artifact? (i.e. if we remove numbers and msXXXX, it's empty)
  let isEntirelyArtifact = false;
  let test_ar = title_ar.replace(/ms\d+/gi, '').replace(/[0-9\s\-]+/g, '').trim();
  let test_en = title.replace(/ms\d+/gi, '').replace(/[0-9\s\-]+/g, '').trim();
  
  if (!test_ar && !test_en) {
    isEntirelyArtifact = true;
  }
  
  if (isEntirelyArtifact) {
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
    // Keep it, but use the cleaned title (just remove msXXXX)
    // Wait, if it has numbers in the real title, we want to keep them.
    // So just replace ms\d+ and multiple spaces.
    let final_title = title.replace(/ms\d+/gi, '').replace(/\s+/g, ' ').trim();
    let final_title_ar = title_ar.replace(/ms\d+/gi, '').replace(/\s+/g, ' ').trim();
    
    if (ch.title !== final_title || ch.title_ar !== final_title_ar) {
      cleanedCount++;
      ch.title = final_title;
      ch.title_ar = final_title_ar;
    }
    
    out[k] = ch;
    lastValid = ch;
  }
}

fs.writeFileSync('data/chapters/tabarani.json', JSON.stringify(out, null, 2), 'utf8');
console.log(`Merged ${mergedCount} full artifact chapters.`);
console.log(`Cleaned ${cleanedCount} chapter titles.`);
console.log(`Remaining chapters: ${Object.keys(out).length}`);
