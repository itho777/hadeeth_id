const https = require('https');

https.get('https://hadits.in/viewer/lib.min.js?s=1786682121', (resp) => {
  let data = '';
  resp.on('data', (chunk) => { data += chunk; });
  resp.on('end', () => {
    const urls = data.match(/https?:\/\/[^\s\'\"]+/g);
    if(urls) console.log('Found URLs:', [...new Set(urls)]);
    
    const endpoints = data.match(/\/api\/[^\s\'\"]+/g);
    if(endpoints) console.log('Found API endpoints:', [...new Set(endpoints)]);
    
    const fetches = data.match(/url\s*:\s*[\'\"][^\'\"]+[\'\"]/g);
    if(fetches) console.log('Found AJAX urls:', [...new Set(fetches)]);
    
    const endpoints2 = data.match(/[\'\"][^\'\"]+\.json[\'\"]/g);
    if(endpoints2) console.log('Found json endpoints:', [...new Set(endpoints2)]);
  });
}).on("error", (err) => {
  console.log("Error: " + err.message);
});
