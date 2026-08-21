const fs = require('fs');
const path = require('path');

const books = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'ahmad', 'malik', 'darimi', 'nawawi'];
const apiDir = path.join(__dirname, '..', 'data', 'api');
const rawisDir = path.join(__dirname, '..', 'data', 'rawis');
const indexesDir = path.join(rawisDir, 'indexes');

if (!fs.existsSync(indexesDir)) {
  fs.mkdirSync(indexesDir, { recursive: true });
}

// 10 buckets based on the last character of the rawi ID
const buckets = {};
for (let i = 0; i <= 9; i++) buckets[String(i)] = {};

console.log('Building grouped narrator hadith indexes...');

for (const book of books) {
  const filePath = path.join(apiDir, `${book}.ndjson`);
  if (!fs.existsSync(filePath)) {
    console.log(`Skipping ${book}, file not found.`);
    continue;
  }
  
  console.log(`Processing ${book}...`);
  const lines = fs.readFileSync(filePath, 'utf8').split('\n');
  
  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const h = JSON.parse(line);
      const sanad = h.sanad || h.rawis || [];
      const hadithNum = h.hadith_number || h.id;
      
      const processedIds = new Set();
      
      for (const rawi of sanad) {
        let rawiId = null;
        if (rawi.source === 'lidwa' && rawi.id) {
          rawiId = `lidwa_${rawi.id}`;
        } else if (rawi.id) {
          rawiId = String(rawi.id);
        } else if (rawi.rawi_id) {
          rawiId = String(rawi.rawi_id);
        }
        
        if (rawiId && !processedIds.has(rawiId)) {
          const lastChar = rawiId.slice(-1);
          if (buckets[lastChar]) {
            if (!buckets[lastChar][rawiId]) buckets[lastChar][rawiId] = [];
            buckets[lastChar][rawiId].push({ b: book, i: hadithNum });
            processedIds.add(rawiId);
          }
        }
      }
    } catch (e) {
      console.error(`Error parsing hadith in ${book}:`, e.message);
    }
  }
}

let totalCount = 0;
for (const [char, indexMap] of Object.entries(buckets)) {
  const outputPath = path.join(indexesDir, `idx_${char}.json`);
  fs.writeFileSync(outputPath, JSON.stringify(indexMap));
  const count = Object.keys(indexMap).length;
  totalCount += count;
  const size = (fs.statSync(outputPath).size / 1024).toFixed(1);
  console.log(`Wrote idx_${char}.json - ${count} narrators (${size} KB)`);
}

console.log(`Done! Grouped ${totalCount} narrators into 10 files.`);
