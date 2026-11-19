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
  const chb = await api.getChapterHadiths('bukhari', 1, 'fawazahmed');
  check('bukhari chapter 1 (international)', chb.length === 7 && bytes < 1_000_000,
    `${chb.length} hadiths, ${calls} reqs, ${(bytes / 1024).toFixed(1)} KB`);
  const chl = await api.getChapterHadiths('bukhari', 1, 'native_lidwa');
  check('bukhari chapter 1 (lidwa)', chl.length === 6, `${chl.length} hadiths`);
  reset();
  const chm = await api.getChapterHadiths('muslim', 3);
  check('muslim chapter 3', chm.length > 0 && bytes < 3_000_000, `${chm.length} hadiths, ${(bytes / 1024).toFixed(1)} KB`);

  console.log('\n== topics ==');
  reset();
  const topics = await api.getTopics();
  check('14 topics', topics.length === 14, `got ${topics.length}`);
  const tids = await api.getTopicHadithIds(1, 'bukhari');
  check('topic 1 / bukhari numbers', tids.length > 1000, `${tids.length} numbers`);
  const th = await api.getHadith('bukhari', tids[0]);
  check('topic number resolves', th && String(th.hadith_number) === String(tids[0]), `#${th && th.hadith_number}`);

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
      const h = await api.getHadith(b.id, String(e.n), 'lidwa');
      if (h && String(h.hadith_number) === String(e.n)) good++;
    }
    if (good === picks.length) bookOk++;
    else console.log(`  BAD   ${b.id}  ${good}/${picks.length}`);
  }
  check(`${books.length} books`, bookOk === books.length, `${bookOk}/${books.length} resolved, ${entries} index entries`);

  console.log('\n== nine books: separate international dataset ==');
  const core9 = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah', 'malik', 'ahmad', 'darimi'];
  let fawazOk = 0;
  for (const b of core9) {
    const idx = await api.fetchNdjsonIndex('api', b, 'fawaz');
    const e = idx && idx[Math.floor(idx.length / 2)];
    const h = e && await api.getHadith(b, String(e.n), 'fawaz');
    const ch = await api.getChapters(b, 'fawazahmed');
    if (h && String(h.hadith_number) === String(e.n) && ch.length > 0) fawazOk++;
    else console.log(`  BAD   ${b}  h=${!!h} chapters=${ch.length}`);
  }
  check('9 international datasets', fawazOk === 9, `${fawazOk}/9`);

  console.log(`\nRESULT: ${pass} pass, ${fail} fail`);
  process.exit(fail ? 1 : 0);
})();
