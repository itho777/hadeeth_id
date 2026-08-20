import re

text = open('js/app.js', encoding='utf-8').read()

new_text = text.replace(
    "'malik': { id: 'malik', name: 'Muwatta Malik', nameId: 'Muwatha\\' Malik', count: 1595, prefix: 'Muwatta Malik' },",
    "'malik': { id: 'malik', name: 'Muwatta Malik', nameId: 'Muwatha\\' Malik', count: 1595, prefix: 'Muwatta Malik' },\n  'syafii': { id: 'syafii', name: 'Musnad Syafi\\'i', nameId: 'Musnad Syafi\\'i', count: 1800, prefix: 'Musnad Syafi\\'i' },"
)

new_text = new_text.replace(
    "const validBooksWithNote = ['bukhari', 'muslim'];",
    "const validBooksWithNote = ['bukhari', 'muslim', 'syafii'];"
)

new_text = new_text.replace(
    "'muslim': 'Shahih Muslim (7.563 hadits)'",
    "'muslim': 'Shahih Muslim (7.563 hadits)',\n        'syafii': 'Musnad Syafi\\'i (1.800 hadits)'"
)

new_text = new_text.replace(
    "'muslim': 'Sahih Muslim (7,563 hadiths)'",
    "'muslim': 'Sahih Muslim (7,563 hadiths)',\n        'syafii': 'Musnad Syafi\\'i (1,800 hadiths)'"
)

open('js/app.js', 'w', encoding='utf-8').write(new_text)
