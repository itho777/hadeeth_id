const fs = require('fs');
let txt = fs.readFileSync('js/app.js', 'utf8');
txt = txt.replace(/Korpus Sunan/g, '⭐️ Korpus Sunan');
txt = txt.replace(/100% Sahih/g, '⭐️ 100% Sahih');
txt = txt.replace(/Jami' Tergrading/g, "⭐️ Jami' Tergrading");
txt = txt.replace(/â\xad ï¸/g, ''); // strip the garbage
txt = txt.replace(/â­ ï¸/g, '');
txt = txt.replace(/⭐️ ⭐️/g, '⭐️');
fs.writeFileSync('js/app.js', txt);
