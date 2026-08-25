import io
import re

with io.open('../js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add window.inspectAlignment function at the end of the file
inspect_fn = """
window.inspectAlignment = async function(bookId, source, hid) {
    Swal.fire({
        title: 'Verifying Alignment...',
        text: 'Fetching the native Arabic text attached to this translation...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });
    
    try {
        let nativeArabic = "";
        let sourceName = "";
        
        if (source === 'lidwa_id' || source === 'lidwa' || source === 'lidwa_en') {
            sourceName = "Lidwa Native Dataset";
            const lidwaData = await window.HadeethAPI.getHadith(bookId, hid, 'lidwa');
            if (lidwaData) {
                nativeArabic = lidwaData.text_ar || lidwaData.text_id || "No Arabic text found in Lidwa source.";
            }
        } else if (source === 'ab') {
            sourceName = "AhmedBaset Dataset";
            const abData = await window.HadeethAPI.getHadith(bookId, hid, 'ab');
            if (abData) {
                nativeArabic = abData.text_ar || abData.text_en || "No text found.";
            }
        } else {
            sourceName = "Fawazahmed Base Dataset";
            const ara = await window.HadeethAPI.getEdition('ara', bookId);
            if (ara && ara.hadiths) {
                const h = ara.hadiths.find(x => String(x.hadithnumber || x.id) === String(hid));
                if (h) nativeArabic = h.text;
            }
        }
        
        if (!nativeArabic) {
            Swal.fire('Not Found', `Could not load the native Arabic text for ID #${hid} from ${sourceName}.`, 'error');
            return;
        }
        
        Swal.fire({
            title: 'Translation Source Alignment',
            html: `
                <div class="text-left text-sm mb-4 text-gray-700 dark:text-gray-300">
                    This translation was pulled from <b>${sourceName} (ID: ${hid})</b>.<br/><br/>
                    Because translations are often padded or numbered differently (e.g. skipping the Muqaddimah), they can sometimes desync from the main Arabic text.<br/><br/>
                    <b>Compare the original Arabic text below with the main page:</b>
                </div>
                <div class="p-4 bg-gray-100 dark:bg-gray-800 rounded border border-gray-300 dark:border-gray-700 max-h-64 overflow-y-auto">
                    <p class="font-arabic text-2xl leading-loose text-right" dir="rtl">${nativeArabic}</p>
                </div>
            `,
            width: '700px',
            confirmButtonText: 'Close'
        });
    } catch(e) {
        Swal.fire('Error', 'Failed to fetch native text.', 'error');
    }
};
"""

if "window.inspectAlignment =" not in js:
    js += "\n" + inspect_fn

# 2. Inject the warning into updateTranslationBox
old_render = """        const txt = await fetchTranslationText(opt);
        if (txt) {
            let output = typeof TafseerLinker !== 'undefined' ? TafseerLinker.parse(txt) : txt;
            
            if (opt.source !== 'fawaz' && activeDataset === 'fawazahmed') {
               output = `<div class="mb-2 text-xs text-blue-500 font-semibold">[Linked via Arabic matching -> ${opt.source.toUpperCase()} #${opt.hid}]</div>` + output;
            }
            
            targetBox.innerHTML = output;"""

new_render = """        const txt = await fetchTranslationText(opt);
        if (txt) {
            let output = typeof TafseerLinker !== 'undefined' ? TafseerLinker.parse(txt) : txt;
            
            // Flag mismatch risks
            let isMismatchRisk = false;
            // Cross-dataset links are always a risk
            if (activeDataset === 'native_lidwa' && opt.source !== 'lidwa_id' && opt.source !== 'lidwa_en') isMismatchRisk = true;
            if (activeDataset === 'fawazahmed' && (opt.source === 'lidwa_id' || opt.source === 'lidwa_en' || opt.source === 'ab')) isMismatchRisk = true;
            if (activeDataset === 'native_ahmedbaset' && opt.source !== 'ab') isMismatchRisk = true;
            // Fawazahmed English translations are known to be padded/desynced for Muslim/Bukhari
            if (opt.source.startsWith('eng-') || window.fawazEditions?.[bookId]?.['eng']?.find(e => e.name === opt.source)) isMismatchRisk = true;
            
            if (isMismatchRisk) {
                const warnHtml = `<div class="mb-4 text-xs flex flex-col sm:flex-row sm:items-center gap-2 bg-yellow-500/10 text-yellow-700 dark:text-yellow-500 p-2.5 rounded border border-yellow-500/30">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined text-[16px]">warning</span>
                        <span><b>Alignment Notice:</b> Translation dynamically linked from <b>${opt.label}</b> (ID #${opt.hid}).</span>
                    </div>
                    <button onclick="inspectAlignment('${bookId}', '${opt.source}', '${opt.hid}')" class="sm:ml-auto mt-1 sm:mt-0 px-3 py-1 bg-yellow-500/20 hover:bg-yellow-500/30 rounded transition text-yellow-800 dark:text-yellow-400 font-semibold flex items-center gap-1">
                        <span class="material-symbols-outlined text-[14px]">policy</span>
                        Verify Match
                    </button>
                </div>`;
                output = warnHtml + output;
            } else if (opt.source !== 'fawaz' && activeDataset === 'fawazahmed') {
                output = `<div class="mb-2 text-xs text-blue-500 font-semibold">[Linked via Arabic matching -> ${opt.source.toUpperCase()} #${opt.hid}]</div>` + output;
            }
            
            targetBox.innerHTML = output;"""

js = js.replace(old_render, new_render)

with io.open('../js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Injected inspectAlignment into app.js")