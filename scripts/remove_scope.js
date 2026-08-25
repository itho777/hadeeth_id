const fs = require('fs');
let txt = fs.readFileSync('topic-hadiths.html', 'utf8');
txt = txt.replace(/<div class="flex items-center gap-1 w-full sm:w-auto">[\s\S]*?<\/select>\s*<\/div>/, '');
fs.writeFileSync('topic-hadiths.html', txt);
