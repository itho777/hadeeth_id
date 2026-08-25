const fs = require('fs');
const topicsIndex = JSON.parse(fs.readFileSync('data/api/topics_index.json', 'utf8'));
const topicsMeta = fs.readFileSync('data/api/topics_metadata.ndjson', 'utf8')
  .trim()
  .split(/\r?\n/)
  .map(l => JSON.parse(l));

const counts = {};

for (const topicId in topicsIndex.topics) {
  const topicObj = topicsMeta.find(t => String(t.id) === topicId);
  if (!topicObj) continue;
  
  const nameEn = topicObj.name_en;
  for (const bookId in topicsIndex.topics[topicId].books) {
    if (!counts[bookId]) counts[bookId] = {};
    counts[bookId][nameEn] = topicsIndex.topics[topicId].books[bookId].length;
  }
}

fs.writeFileSync('data/api/topics_counts.json', JSON.stringify(counts, null, 2));
console.log('Done!');
