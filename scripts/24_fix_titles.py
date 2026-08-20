import os

APP_JS_PATH = "js/app.js"

with open(APP_JS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

OLD_INIT = """      // Set defaults
      if (idx === 0) {
         const defaultEn = translationOptions.find(o => o.id.includes('eng-bukhari') || (o.lang==='English' && (o.source==='fawaz' || o.source==='ab'))) || translationOptions[0];
         if (defaultEn) selectElem.value = defaultEn.id;
      } else {
         const defaultId = translationOptions.find(o => o.id === 'lidwa-id') || translationOptions[0];
         if (defaultId) selectElem.value = defaultId.id;
      }
  });"""

NEW_INIT = """      // Set defaults
      if (idx === 0) {
         const defaultEn = translationOptions.find(o => o.id.includes('eng-bukhari') || (o.lang==='English' && (o.source==='fawaz' || o.source==='ab'))) || translationOptions[0];
         if (defaultEn) selectElem.value = defaultEn.id;
      } else {
         const defaultId = translationOptions.find(o => o.id === 'lidwa-id') || translationOptions[0];
         if (defaultId) selectElem.value = defaultId.id;
      }
      
      // Update the header span dynamically
      const spanTitle = selectElem.parentElement.querySelector('span');
      if (spanTitle && selectElem.selectedIndex >= 0) {
          const opt = selectElem.options[selectElem.selectedIndex];
          if (opt) {
              const langName = opt.text.split(' - ')[0];
              spanTitle.innerText = langName + " TRANSLATION";
          }
      }
  });"""

OLD_LISTENERS = """  // Listeners
  langSelects.forEach(selectElem => {
    selectElem.addEventListener('change', () => {
      const cardBox = selectElem.closest('.p-5');
      const targetP = cardBox ? cardBox.querySelector('p') : null;
      if (targetP) {
          updateTranslationBox(selectElem, targetP);
      }
      if (window.switchSyarahLang) {
          // Sync syarah lang loosely
          const val = selectElem.value.toLowerCase();
          window.switchSyarahLang(val.includes('id') || val.includes('ind') ? 'id' : 'en');
      }
    });
  });"""

NEW_LISTENERS = """  // Listeners
  langSelects.forEach(selectElem => {
    selectElem.addEventListener('change', () => {
      const cardBox = selectElem.closest('.p-5');
      const targetP = cardBox ? cardBox.querySelector('p') : null;
      
      // Update title dynamically on change
      const spanTitle = selectElem.parentElement.querySelector('span');
      if (spanTitle && selectElem.selectedIndex >= 0) {
          const opt = selectElem.options[selectElem.selectedIndex];
          if (opt) {
              const langName = opt.text.split(' - ')[0];
              spanTitle.innerText = langName + " TRANSLATION";
          }
      }
      
      if (targetP) {
          updateTranslationBox(selectElem, targetP);
      }
      if (window.switchSyarahLang) {
          // Sync syarah lang loosely
          const val = selectElem.value.toLowerCase();
          window.switchSyarahLang(val.includes('id') || val.includes('ind') ? 'id' : 'en');
      }
    });
  });"""

content = content.replace(OLD_INIT, NEW_INIT)
content = content.replace(OLD_LISTENERS, NEW_LISTENERS)

with open(APP_JS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated js/app.js translation titles")
