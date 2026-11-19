// Isolated runtime check of the syarah availability UI.
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync('G:/hadeeth_id/js/app.js', 'utf8');

function slice(startMarker, endMarker) {
  const a = src.indexOf(startMarker);
  const b = src.indexOf(endMarker, a);
  if (a < 0 || b < 0) throw new Error('marker not found: ' + startMarker);
  return src.slice(a, b);
}

const code = slice('function hasSyarahText(', 'window.switchSyarahLang = function(langCode)')
  + slice('function renderSyarahUI() {', 'async function loadHadithSyarah(')
  + '\nglobalThis.render = renderSyarahUI;';

function makeEl() {
  return {
    innerHTML: '', innerText: '', text: '', disabled: false, title: '',
    style: { display: '' }, options: [],
    parentElement: { style: { display: '' } },
  };
}

const expText = makeEl();
const langSelect = makeEl();
langSelect.options = ['id', 'en', 'ar'].map(value => ({ value, text: value, disabled: false }));
const tabs = makeEl();
const benefits = makeEl();

const ctx = {
  console,
  document: {
    getElementById(id) {
      return {
        'syarah-explanation-text': expText,
        'syarah-lang-select': langSelect,
        'syarah-source-tabs': tabs,
        'syarah-benefits-list': benefits,
      }[id] || null;
    },
  },
  window: {
    LangSystem: { isIdMode: () => true, apply: () => {}, get: () => 'id' },
    activeSyarahData: [],
    activeSyarahIndex: 0,
    activeSyarahLang: 'id',
  },
  escapeHtml: s => String(s),
  getComputedStyle: () => ({}),
};
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(code, ctx);

let pass = 0, fail = 0;
function check(name, cond, detail = '') {
  if (cond) { pass++; console.log('  PASS  ' + name + (detail ? '  ' + detail : '')); }
  else { fail++; console.log('  FAIL  ' + name + '  ' + detail); }
}

// 1. source with Indonesian text only: EN option disabled, fallback notice shown
ctx.window.activeSyarahData = [
  { source_name_en: 'Fath al-Bari', explanation_id: 'شرح', explanation_en: '', explanation_ar: '' },
];
ctx.window.activeSyarahLang = 'en';
ctx.window.activeSyarahIndex = 0;
ctx.render();
const langOpts = ctx.document.getElementById('syarah-lang-select').options;
check('ID option enabled', langOpts[0].disabled === false);
check('EN option disabled', langOpts[1].disabled === true);
check('AR option disabled', langOpts[2].disabled === true);
check('fallback notice shown', expText.innerHTML.includes('not available'), expText.innerHTML.slice(0, 130));
check('active language switched', ctx.window.activeSyarahLang === 'id', ctx.window.activeSyarahLang);

// 2. source with no text at all: tab disabled, explicit unavailable message
ctx.window.activeSyarahData = [
  { source_name_en: 'Empty', explanation_id: '', explanation_en: '', explanation_ar: '' },
  { source_name_en: 'Has ID', explanation_id: 'موجود', explanation_en: '', explanation_ar: '' },
];
ctx.window.activeSyarahIndex = 0;
ctx.window.activeSyarahLang = 'id';
ctx.render();
check('empty source tab disabled', tabs.innerHTML.includes('disabled'), tabs.innerHTML.slice(0, 200));
check('empty source marked unavailable', tabs.innerHTML.includes('tidak tersedia'));
check('usable source tab clickable', tabs.innerHTML.includes('switchSyarahSource(1)'));
check('switched to usable source', ctx.window.activeSyarahIndex === 1);

// 3. no commentary at all: explicit unavailable message
ctx.window.activeSyarahData = [];
ctx.render();
check('explicit no-commentary notice', expText.innerHTML.includes('Syarah tidak tersedia untuk hadits ini'), expText.innerHTML.slice(0, 160));
check('all languages disabled', langOpts.every(o => o.disabled));

// 4. bilingual source: explicit EN selection stays EN
ctx.window.activeSyarahData = [
  { source_name_en: 'Bilingual', explanation_id: 'TEKS-ID', explanation_en: 'TEXT-EN', explanation_ar: '' },
];
ctx.window.activeSyarahIndex = 0;
ctx.window.activeSyarahLang = 'en';
ctx.render();
check('EN selection kept', expText.innerHTML.includes('TEXT-EN') && ctx.window.activeSyarahLang === 'en');
check('EN option enabled', langOpts[1].disabled === false);
check('AR option disabled', langOpts[2].disabled === true);

// 5. Muse sharh: Arabic-only row renders with its citation and a tab-sized name
ctx.window.activeSyarahData = [
  {
    origin: 'muse', source_name_en: 'Fath al-Bari', syarah_ar: 'الشرح',
    explanation_ar: 'الشرح', source_title_full: 'Fath al-Bari bi-Sharh Sahih al-Bukhari',
    syarah_vol: '1', syarah_page: '9', syarah_url: 'https://app.turath.io/book/1673',
  },
];
ctx.window.activeSyarahIndex = 0;
ctx.window.activeSyarahLang = 'id';
ctx.render();
check('Arabic sharh renders under ID mode', expText.innerHTML.includes('الشرح'));
check('citation shows volume and page', expText.innerHTML.includes('jil. 1') && expText.innerHTML.includes('hlm. 9'));
check('citation links the edition', expText.innerHTML.includes('app.turath.io/book/1673'));
check('tab uses the short name', tabs.innerHTML.includes('Fath al-Bari') && !tabs.innerHTML.includes('bi-Sharh'));

console.log(`\nRESULT: ${pass} pass, ${fail} fail`);
process.exit(fail ? 1 : 0);
