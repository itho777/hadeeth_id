import sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('  let textExp = \'\';')
end = text.find('  expText.innerHTML = textExp;', start)

replacement = """  let textExp = '';
  let benefits = [];

  // Look for exact lang match, then fallback to English
  textExp = data[`explanation_${lang}`] || data[`explanation_${src}_${lang}`] || data[`explanation_en`] || data[`explanation_${src}_en`] || '';
  benefits = data[`benefits_${lang}`] || data[`benefits_${src}_${lang}`] || data[`benefits_en`] || data[`benefits_${src}_en`] || [];

  if (!textExp) {
    if (src === 'fath') {
      textExp = lang === 'id' ? '<span class="text-outline dark:text-gray-400 italic">Syarah Fathul Bari belum tersedia.</span>' : '<span class="text-outline dark:text-gray-400 italic">Sharh Fath al-Bari is not yet available.</span>';
    } else if (src === 'nawawi') {
      textExp = lang === 'id' ? '<span class="text-outline dark:text-gray-400 italic">Syarah Sahih Muslim (Imam an-Nawawi) belum tersedia.</span>' : '<span class="text-outline dark:text-gray-400 italic">Sharh of Imam an-Nawawi is not yet available.</span>';
    } else {
      textExp = lang === 'id' ? '<span class="text-outline dark:text-gray-400 italic">Syarah (Penjelasan Hadits) belum tersedia untuk hadits ini dalam basis data.</span>' : '<span class="text-outline dark:text-gray-400 italic\">Syarah (Commentary) is not yet available for this Hadith in the database.</span>';
    }
  }

"""

text = text[:start] + replacement + text[end:]
with open(r'g:\Box\AntigravitySync\.gemini\antigravity\scratch\hadeeth_id\js\app.js', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated renderSyarahUI in app.js')
