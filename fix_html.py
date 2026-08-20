import re
text = open('index.html', encoding='utf-8').read()
m = re.search(r'<a href="hadith-list\.html\?book=malik".*?</a>', text, re.DOTALL)
if m:
    malik = m.group(0)
    syafii = malik.replace('malik', 'syafii').replace('Muwatta Malik', "Musnad Syafi'i").replace("Muwatha' Malik", "Musnad Syafi'i")
    syafii = syafii.replace('1,595 Ahadith', '1,800 Ahadith').replace('1.595 Hadits', '1.800 Hadits')
    syafii = syafii.replace('Compiled by Imam Malik, one of the earliest and most respected collections.', "The famous collection attributed to Imam Al-Shafi'i.")
    syafii = syafii.replace('Disusun oleh Imam Malik, salah satu koleksi paling awal dan dihormati.', "Koleksi hadits musnad dari Imam As-Syafi'i.")
    text = text.replace(malik, malik + '\n' + syafii)
    open('index.html', 'w', encoding='utf-8').write(text)
    print('Success')
