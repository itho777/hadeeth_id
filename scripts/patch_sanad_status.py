with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

old_status = 'if (statusEl) statusEl.innerHTML = `<span data-lang-en>Connected (Muttasil)</span><span data-lang-id style="display:none">Bersambung (Muttashil)</span>`;'
new_status = 'if (statusEl) statusEl.innerHTML = `<span data-lang-en>N/A (Not in dataset)</span><span data-lang-id style="display:none">N/A (Tidak tercatat)</span>`;'
app_js = app_js.replace(old_status, new_status)

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("Patched sanad status hardcode.")
