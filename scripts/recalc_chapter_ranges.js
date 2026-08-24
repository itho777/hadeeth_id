const fs = require('fs');

const bookId = 'tabarani';
const chaptersPath = `data/chapters/${bookId}.json`;
const ndjsonPath = `data/api/${bookId}.ndjson`;

const chsObj = JSON.parse(fs.readFileSync(chaptersPath, 'utf8'));

// Initialize min/max trackers
const chRange = {};
for (const k in chsObj) {
  chRange[k] = { min: Infinity, max: -Infinity };
}

const lines = fs.readFileSync(ndjsonPath, 'utf8').split('\n');
for (const line of lines) {
  if (!line.trim()) continue;
  try {
    const h = JSON.parse(line);
    const cId = String(h.chapter_id);
    // Tabarani has sequential ids or numeric hadithnumbers?
    // Often it's `id` or `hadithnumber`.
    let num = parseInt(h.hadithnumber || h.id, 10);
    
    if (cId && chRange[cId] && !isNaN(num)) {
      if (num < chRange[cId].min) chRange[cId].min = num;
      if (num > chRange[cId].max) chRange[cId].max = num;
    }
  } catch(e) {}
}

let modified = 0;
for (const k in chsObj) {
  if (chRange[k].min !== Infinity) {
    chsObj[k].first_hadith = String(chRange[k].min);
    chsObj[k].last_hadith = String(chRange[k].max);
    modified++;
  } else {
    // Empty chapter
    chsObj[k].first_hadith = null;
    chsObj[k].last_hadith = null;
  }
}

console.log(`Recalculated ranges for ${modified} chapters.`);
fs.writeFileSync(chaptersPath, JSON.stringify(chsObj, null, 2), 'utf8');
