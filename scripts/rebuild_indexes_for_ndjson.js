const fs = require('fs');
const path = require('path');

const apiDir = 'data/api';
const files = fs.readdirSync(apiDir);

for (const filename of files) {
  if (filename.endsWith('.ndjson') && !filename.startsWith('topics_metadata')) {
    const ndjsonPath = path.join(apiDir, filename);
    const baseName = filename.replace('.ndjson', '');
    const indexPath = path.join(apiDir, `${baseName}_ndjson_index.json`);
    
    console.log(`Rebuilding index for ${ndjsonPath}...`);
    
    let dictMeta = {};
    let arrayKey = null;
    
    if (fs.existsSync(indexPath)) {
      try {
        const oldIdx = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
        dictMeta = oldIdx.metadata || {};
        arrayKey = oldIdx.array_key || null;
      } catch (e) {
      }
    }
    
    const idIndex = {};
    const chapterIndex = {};
    let currentOffset = 0;
    
    const content = fs.readFileSync(ndjsonPath);
    // iterate bytes to find newlines since byte length is important
    let lineStart = 0;
    for (let i = 0; i < content.length; i++) {
      if (content[i] === 10) { // \n
        const lineBytes = content.slice(lineStart, i + 1);
        const byteLen = lineBytes.length;
        const startByte = currentOffset;
        const endByte = currentOffset + byteLen - 1;
        
        try {
          const str = lineBytes.toString('utf8');
          if (str.trim().length > 0) {
             const item = JSON.parse(str);
             const itemId = String(item.id || item.hadithnumber || item.hadith_number || '');
             const chapterId = String(item.chapter_id || item.chapter_number || '');
             
             if (itemId && itemId !== 'undefined' && itemId !== 'None') {
               idIndex[itemId] = [startByte, endByte];
             }
             if (chapterId && chapterId !== 'undefined' && chapterId !== 'None') {
               if (!chapterIndex[chapterId]) {
                 chapterIndex[chapterId] = { start: startByte, end: endByte };
               } else {
                 chapterIndex[chapterId].end = endByte;
               }
             }
          }
        } catch (e) {
        }
        
        currentOffset += byteLen;
        lineStart = i + 1;
      }
    }
    
    const idxPayload = {
      metadata: dictMeta,
      array_key: arrayKey,
      hadiths: idIndex,
      chapters: chapterIndex
    };
    
    fs.writeFileSync(indexPath, JSON.stringify(idxPayload), 'utf8');
  }
}

console.log('Done rebuilding indices.');
