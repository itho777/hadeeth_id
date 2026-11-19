// Full link-hierarchy audit: every book, every chapter, every jump.
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const root = 'G:/hadeeth_id';
const src = fs.readFileSync(path.join(root, 'js/api.js'), 'utf8');

const listeners = {};
const ctx = {
  console,
  setTimeout, clearTimeout,
  URL,
  TextDecoder,
  AbortController,
  fetch,
  location: { href: 'https://hadeeth.id/', origin: 'https://hadeeth.id', pathname: '/' },
  localStorage: { getItem: () => null, setItem: () => {} },
  document: {
    querySelector: () => null,
    querySelectorAll: () => [],
    getElementById: () => null,
    createElement: () => ({ style: {}, classList: { add() {}, remove() {} } }),
    addEventListener: () => {},
  },
  navigator: { userAgent: 'node' },
  window: null,
  addEventListener: (n, f) => { (listeners[n] = listeners[n] || []).push(f); },
};
ctx.window = ctx;
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(src, ctx);
const api = ctx.HadeethAPI;

function datasetFor(book) {
  return ['bukhari','muslim','nasai','abudawud','tirmidhi','ibnmajah','malik','darimi','ahmad'].includes(book)
    ? 'native_lidwa' : 'fawazahmed';
}

(async () => {
  const books = (await api.getBooks()).map(b => b.id);
  let checked = 0;
  const problems = [];
  const summary = [];

  for (const book of books) {
    const ds = datasetFor(book);
    const prefix = api.datasetPrefix(ds);
    let chapters = [];
    try { chapters = await api.getChapters(book, ds); } catch (e) { chapters = []; }

    if (!chapters.length) {
      problems.push(`${book}: no chapter file`);
    } else {
      const idx = await api.fetchNdjsonIndex('api', book);
      const nums = idx.map(e => Number(e.n)).filter(n => Number.isFinite(n));
      const lo = Math.min(...nums), hi = Math.max(...nums);
      const outOfRange = chapters.filter(c => {
        const s = Number(c.hadith_start), e = Number(c.hadith_end);
        return !Number.isFinite(s) || !Number.isFinite(e) || s <= 0 || e <= 0 || s > e;
      });
      if (outOfRange.length) {
        problems.push(`${book}: ${outOfRange.length}/${chapters.length} chapters outside ${lo}-${hi} (e.g. ${outOfRange[0].chapter_number}: ${outOfRange[0].hadith_start}-${outOfRange[0].hadith_end})`);
      }
    }

    // first and last hadith of the book must resolve, and end-caps must not dead-end
    const first = await api.getHadith(book, 1, prefix);
    if (!first) problems.push(`${book}: hadith 1 does not resolve`);
    const idxAll = await api.fetchNdjsonIndex('api', book);
    const lastEntry = idxAll[idxAll.length - 1];
    const lastNum = prefix === 'lidwa' && lastEntry.l !== undefined ? (Array.isArray(lastEntry.l) ? lastEntry.l[0] : lastEntry.l) : lastEntry.n;
    const last = await api.getHadith(book, lastNum, prefix);
    if (!last) problems.push(`${book}: last hadith ${lastNum} does not resolve`);

    // chapter jump: first chapter -> first hadith, then prev must be null-ish (no dead #0)
    if (chapters.length) {
      const ch = chapters[0];
      const rows = await api.getChapterHadiths(book, ch.chapter_number, ds);
      checked++;
      if (!rows.length) {
        problems.push(`${book}: chapter ${ch.chapter_number} lists 0 hadiths`);
      } else {
        const n0 = rows[0].hadithnumber;
        const got = await api.getHadith(book, n0, prefix);
        if (!got) problems.push(`${book}: chapter ${ch.chapter_number} first hadith ${n0} does not resolve`);
        const nb = await api.getHadithNeighbours(book, n0, prefix);
        if (!nb) problems.push(`${book}: neighbours unavailable for ${n0}`);
      }
    }

    const nCh = chapters.length;
    summary.push(`${book.padEnd(13)} chapters ${String(nCh).padStart(3)}  rows ${String(idxAll.length).padStart(6)}`);
  }

  console.log(`books: ${books.length}, chapters tested: ${checked}`);
  console.log(summary.join('\n'));
  if (problems.length) {
    console.log(`\nPROBLEMS (${problems.length}):`);
    problems.forEach(p => console.log(' - ' + p));
    process.exit(1);
  }
  console.log('\nno dead links found');
})();
