const fs = require('fs');
const chs = JSON.parse(fs.readFileSync('data/chapters/tabarani.json', 'utf8'));

let msCount = 0;
let numberCount = 0;
let entirelyArtifactCount = 0;

for (let k in chs) {
  let title = chs[k].title || '';
  let title_ar = chs[k].title_ar || '';
  
  if (title.match(/ms\d+/i) || title_ar.match(/ms\d+/i)) {
    msCount++;
  }
  
  if (title.match(/^[0-9\s\-]+$/) || title_ar.match(/^[0-9\s\-]+$/)) {
    numberCount++;
  }
  
  // What happens if we strip ms artifacts and numbers? Is it empty?
  let clean = title_ar.replace(/ms\d+/gi, '').replace(/[0-9\s\-]+/g, '').trim();
  if (!clean && title_ar.length > 0) {
    entirelyArtifactCount++;
  }
}

console.log('msCount:', msCount);
console.log('numberCount:', numberCount);
console.log('entirelyArtifactCount (numbers + ms):', entirelyArtifactCount);
