const fs = require('fs');
let txt = fs.readFileSync('js/app.js', 'utf8');
txt = txt.replace(/â\xad ï¸/g, '⭐️');
txt = txt.replace(/â­ ï¸/g, '⭐️');
fs.writeFileSync('js/app.js', txt);
