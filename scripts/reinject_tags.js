const fs = require('fs');
const path = require('path');

const topicTags = JSON.parse(fs.readFileSync('data/lidwa_extracts/topic_tags.json', 'utf8'));
const tagMap = {};
for (const t of topicTags) tagMap[t.tag_id] = t.name_en;

const indMaps = {};
for (let i = 1; i <= 14; i++) {
  const tagName = tagMap[i];
  if (fs.existsSync('data/lidwa_extracts/ind_' + i + '.json')) {
    const data = JSON.parse(fs.readFileSync('data/lidwa_extracts/ind_' + i + '.json', 'utf8'));
    for (const d of data) {
      const bookRaw = String(d.Sumber).toLowerCase().replace(/\s/g, '');
      const num = String(d.NoHdt);
      const key = bookRaw + '_' + num;
      if (!indMaps[key]) indMaps[key] = [];
      if (!indMaps[key].includes(tagName)) indMaps[key].push(tagName);
    }
  }
}

const bookMappings = {
  'bukhari': 'bukhari',
  'muslim': 'muslim',
  'abudawud': 'abudaud',
  'tirmidhi': 'tirmidzi',
  'nasai': 'nasa\'i',
  'ibnmajah': 'ibnumajah',
  'ahmad': 'ahmad',
  'malik': 'malik',
  'darimi': 'darimi'
};

for (const [bookFile, sumberStr] of Object.entries(bookMappings)) {
  const ndjsonPath = `data/api/${bookFile}.ndjson`;
  if (!fs.existsSync(ndjsonPath)) {
    console.log(`Skipping ${bookFile}`);
    continue;
  }
  
  console.log(`Processing ${bookFile}...`);
  const lines = fs.readFileSync(ndjsonPath, 'utf8').split('\n');
  const outLines = [];
  let count = 0;
  
  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const h = JSON.parse(line);
      const lidwaIds = Array.isArray(h.lidwa_id) ? h.lidwa_id : (h.lidwa_id ? [h.lidwa_id] : []);
      
      const sumberKey = sumberStr.replace(/\s/g, '').toLowerCase();
      let hadithTags = [];
      
      for (const lId of lidwaIds) {
        const key = sumberKey + '_' + lId;
        if (indMaps[key]) {
          for (const t of indMaps[key]) {
            if (!hadithTags.includes(t)) hadithTags.push(t);
          }
        }
      }
      
      if (hadithTags.length > 0) count++;
      h.tags = hadithTags;
      outLines.push(JSON.stringify(h));
    } catch(e) {
      console.error(e);
    }
  }
  
  fs.writeFileSync(ndjsonPath, outLines.join('\n') + '\n', 'utf8');
  console.log(`Finished ${bookFile}. Tagged ${count} hadiths.`);
}
