const fs = require('fs');
let txt = fs.readFileSync('js/app.js', 'utf8');
const searchString = `        return (h.text_en && h.text_en.toLowerCase().indexOf(q) >= 0) ||
               (h.text_id && h.text_id.toLowerCase().indexOf(q) >= 0) ||
               (h.text_ar && h.text_ar.indexOf(q) >= 0) ||
               (String(h.hadith_number).indexOf(q) >= 0);`;
const replaceString = `        let en = h.text_en || (h.translations && h.translations.en && h.translations.en[0] && h.translations.en[0].text) || '';
        let id = h.text_id || (h.translations && h.translations.id && h.translations.id[0] && h.translations.id[0].text) || '';
        let ar = h.text_ar || (h.translations && h.translations.ar && h.translations.ar[0] && h.translations.ar[0].text) || '';
        let num = String(h.id || h.hadith_number || '');
        return (en.toLowerCase().indexOf(q) >= 0) ||
               (id.toLowerCase().indexOf(q) >= 0) ||
               (ar.indexOf(q) >= 0) ||
               (num.indexOf(q) >= 0);`;
txt = txt.replace(searchString, replaceString);
fs.writeFileSync('js/app.js', txt);
