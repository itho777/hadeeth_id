import io
with io.open('../js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

start_str = "const txt = await fetchTranslationText(opt);"
end_str = "targetBox.innerHTML = output;"
start_idx = js.find(start_str)
end_idx = js.find(end_str, start_idx) + len(end_str)

print("Found?", start_idx != -1)

new_render = """const txt = await fetchTranslationText(opt);
        if (txt) {
            let output = typeof TafseerLinker !== 'undefined' ? TafseerLinker.parse(txt) : txt;
            
            // Flag mismatch risks
            let isMismatchRisk = false;
            // Cross-dataset links are always a risk
            if (activeDataset === 'native_lidwa' && opt.source !== 'lidwa_id' && opt.source !== 'lidwa_en') isMismatchRisk = true;
            if (activeDataset === 'fawazahmed' && (opt.source === 'lidwa_id' || opt.source === 'lidwa_en' || opt.source === 'ab')) isMismatchRisk = true;
            if (activeDataset === 'native_ahmedbaset' && opt.source !== 'ab') isMismatchRisk = true;
            // Fawazahmed English translations are known to be padded/desynced for Muslim/Bukhari
            if (opt.source !== 'lidwa_id' && opt.source !== 'lidwa_en' && opt.source !== 'ab' && opt.source !== 'ara-' + bookId && opt.source !== 'fawaz') isMismatchRisk = true;
            
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

js = js[:start_idx] + new_render + js[end_idx:]

with io.open('../js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)