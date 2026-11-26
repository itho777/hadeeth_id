"""Read the live registry and record its freshness for the app's About page.

The app always reads books/rows from cdn.hadeeth.id at runtime; this file only
tells the user which snapshot that CDN served when the app was built.
"""
import io, json, urllib.request

URL = 'https://cdn.hadeeth.id/books.ndjson'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as res:
    modified = res.headers.get('Last-Modified', '')
    rows = [json.loads(line) for line in res.read().decode('utf-8').splitlines() if line.strip()]

from email.utils import parsedate_to_datetime
from datetime import timezone, timedelta
updated = parsedate_to_datetime(modified).astimezone(timezone(timedelta(hours=7))).isoformat()

info = {
    'source': 'https://cdn.hadeeth.id',
    'books': len(rows),
    'hadiths': sum(int(r.get('total_hadiths') or 0) for r in rows),
    'updated': updated,
}
with io.open('assets/data/dataset_info.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=1)
print(json.dumps(info, ensure_ascii=False))
