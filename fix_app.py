
text = open('js/app.js', encoding='utf-8').read()
import re
text = re.sub(r', =>', ', () =>', text)
text = text.replace('EN/AR title', 'EN/AR title from ')
text = text.replace('Readsdata/sources/', 'Reads from data/sources/')
text = text.replace('Readsdata/lidwa-chapters/', 'Reads from data/lidwa-chapters/')
text = text.replace('ENAhmedBaset', 'EN from AhmedBaset')
text = text.replace('chapterhadiths', 'chapter from hadiths')
text = text.replace('extracted itgetChapters', 'extracted it from getChapters')
text = text.replace('Arabicfawazahmed0', 'Arabic from fawazahmed0')
text = text.replace('IndonesianLidwa', 'Indonesian from Lidwa')
text = text.replace('liveLidwa', 'live from Lidwa')
text = text.replace('[LinkedLidwa', '[Linked from Lidwa')

open('js/app.js', 'w', encoding='utf-8').write(text)

