with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

target = """  if (langSelect && langSelect.value !== lang) langSelect.value = lang;

  let textExp = data[`explanation_${lang}`] || data[`explanation_en`] || data[`syarah_${lang}`] || data[`syarah_ar`] || '';
  let benefits = data[`benefits_${lang}`] || data[`benefits_en`] || [];"""

replacement = """  let textExp = '';
  let benefits = [];
  let availableLang = lang;

  if (data[`explanation_${lang}`] || data[`syarah_${lang}`]) {
    textExp = data[`explanation_${lang}`] || data[`syarah_${lang}`];
    benefits = data[`benefits_${lang}`] || [];
  } else if (lang === 'id' && (data['explanation_en'] || data['syarah_en'])) {
    textExp = data['explanation_en'] || data['syarah_en'];
    benefits = data['benefits_en'] || [];
    availableLang = 'en';
  } else if (data['syarah_ar']) {
    textExp = data['syarah_ar'];
    availableLang = 'ar';
  } else if (data['explanation_en'] || data['syarah_en']) {
    textExp = data['explanation_en'] || data['syarah_en'];
    benefits = data['benefits_en'] || [];
    availableLang = 'en';
  }

  if (langSelect && langSelect.value !== availableLang) {
    langSelect.value = availableLang;
  }"""

if target in text:
    text = text.replace(target, replacement)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched renderSyarahUI.")
else:
    print("Target not found.")
