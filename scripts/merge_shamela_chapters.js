const fs = require('fs');

const bookId = 'tabarani';
const chaptersPath = `data/chapters/${bookId}.json`;
const ndjsonPath = `data/api/${bookId}.ndjson`;

// 1. Read chapters
const chsObj = JSON.parse(fs.readFileSync(chaptersPath, 'utf8'));
const chapters = Object.values(chsObj);

// We want to find pseudo-chapters (title_ar === 'Bab Tambahan' or similar)
// and merge them into the last valid chapter.
let lastValidId = null;
const chapterMap = {}; // old_id -> new_id
const newChapters = [];

for (const ch of chapters) {
  if (ch.title_ar === 'Bab Tambahan' || ch.title_ar === '') {
    if (lastValidId !== null) {
      chapterMap[ch.id] = lastValidId;
    } else {
      // If there is no valid chapter yet, just keep it or make a dummy valid
      newChapters.push(ch);
      lastValidId = ch.id; 
      chapterMap[ch.id] = ch.id;
    }
  } else {
    lastValidId = ch.id;
    chapterMap[ch.id] = ch.id;
    newChapters.push(ch);
  }
}

console.log(`Original chapters: ${chapters.length}, Merged down to: ${newChapters.length}`);

// 2. Read NDJSON and update chapter_ids
console.log('Reading NDJSON...');
const lines = fs.readFileSync(ndjsonPath, 'utf8').split('\n');
const outLines = [];
let movedCount = 0;

for (const line of lines) {
  if (!line.trim()) continue;
  try {
    const h = JSON.parse(line);
    const oldChId = String(h.chapter_id);
    const newChId = chapterMap[oldChId];
    if (newChId && newChId !== oldChId) {
      h.chapter_id = newChId;
      movedCount++;
    }
    outLines.push(JSON.stringify(h));
  } catch(e) {
    console.error('Error parsing:', e);
  }
}

console.log(`Moved ${movedCount} hadiths to parent chapters.`);
fs.writeFileSync(ndjsonPath, outLines.join('\n') + '\n', 'utf8');

// 3. Update chapters JSON
const newChsObj = {};
for (const ch of newChapters) {
  newChsObj[ch.id] = ch;
}
fs.writeFileSync(chaptersPath, JSON.stringify(newChsObj, null, 2), 'utf8');
console.log('Saved updated chapters.');
