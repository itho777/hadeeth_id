#!/usr/bin/env node
/**
 * Contract test for js/api.js against the live R2 bucket.
 *
 *   node scripts/api_smoke.js
 *
 * Loads the real browser module with a minimal window/document shim, then makes
 * real HTTP requests: every book resolved through its content map, a sample of
 * hadith numbers, chapter runs, and the narrator registry. Exits non-zero on
 * any failure, so it can gate a deploy.
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const API = path.join(__dirname, '..', 'js', 'api.js');
const src = fs.readFileSync(API, 'utf8');

let calls = 0;
let bytes = 0;
const realFetch = globalThis.fetch;
function countingFetch(url, opts) {
  calls++;
  return realFetch(url, opts).then(res => {
    const len = parseInt(res.headers.get('content-length') || '0', 10);
    if (len) bytes += len;
    return res;
  });
}

const sandbox = {
  window: { location: { href: 'https://hadeeth.id/', pathname: '/' } },
  document: { querySelector: () => null },
  localStorage: { getItem: () => null },
  fetch: countingFetch,
  AbortController, setTimeout, clearTimeout, TextDecoder, URL, console,
};
sandbox.window.window = sandbox.window;
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
const api = sandbox.window.HadeethAPI;

let pass = 0, fail = 0;
function reset() { calls = 0; bytes = 0; }
function check(name, ok, detail) {
  if (ok) { pass++; console.log(`  PASS  ${name}  ${detail || ''}`); }
  else { fail++; console.log(`  FAIL  ${name}  ${detail || ''}`); }
}

(async () => {
  console.log('== registry ==');
  reset();
  const books = await api.getBooks();
  check('24 books', books.length === 24, `got ${books.length}`);
  const tab = books.find(b => b.id === 'tabarani');
  check('tabarani ships its full 21,850', tab && tab.hadiths_count === 21850, `got ${tab && tab.hadiths_count}`);
  check('one request for the registry', calls === 1, `${calls} requests, ${(bytes / 1024).toFixed(1)} KB`);

  console.log('\n== hadith by number (id != number) ==');
  for (const [book, num, wantId] of [['bukhari', 5, 6], ['bukhari', 6999, 7554], ['muslim', 300, 201], ['tabarani', 13654, 13545]]) {
    reset();
    const h = await api.getHadith(book, String(num));
    check(`${book} #${num}`, h && String(h.hadith_number) === String(num) && String(h.id) === String(wantId),
      h ? `id=${h.id} n=${h.hadith_number} reqs=${calls} bytes=${bytes}` : 'null');
  }

  console.log('\n== chapter runs ==');
  reset();
  const ch = await api.getChapterHadiths('adab', 1);
  check('adab chapter 1', ch.length > 0, `${ch.length} hadiths, ${calls} reqs, ${(bytes / 1024).toFixed(1)} KB`);
  reset();
  const chb = await api.getChapterHadiths('bukhari', 1);
  check('bukhari refuses full-file scan', chb.length === 0 && bytes < 2_000_000, `${chb.length} hadiths, ${(bytes / 1024).toFixed(1)} KB`);

  console.log('\n== narrators ==');
  reset();
  const rawis = await api.getActiveRawis();
  check('14,298 narrators keyed by rawi_id', Object.keys(rawis).length === 14298 && !!rawis['19944'], `${Object.keys(rawis).length} entries`);

  console.log('\n== every book resolves through its map ==');
  let bookOk = 0, entries = 0;
  for (const b of books) {
    const idx = await api.fetchNdjsonIndex('api', b.id);
    if (!Array.isArray(idx) || !idx.length) { console.log(`  MISSING ${b.id}`); continue; }
    entries += idx.length;
    const picks = [idx[0], idx[Math.floor(idx.length / 2)], idx[idx.length - 1]];
    let good = 0;
    for (const e of picks) {
      const h = await api.getHadith(b.id, String(e.n));
      if (h && String(h.hadith_number) === String(e.n)) good++;
    }
    if (good === picks.length) bookOk++;
    else console.log(`  BAD   ${b.id}  ${good}/${picks.length}`);
  }
  check(`${books.length} books`, bookOk === books.length, `${bookOk}/${books.length} resolved, ${entries} index entries`);

  console.log(`\nRESULT: ${pass} pass, ${fail} fail`);
  process.exit(fail ? 1 : 0);
})();
