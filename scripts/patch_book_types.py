import re

with open('books.html', 'r', encoding='utf-8') as f:
    html = f.read()

target_getType = """  function getType(id) {
    if (['bukhari','muslim','tirmidhi'].includes(id)) return 'jami';
    if (['abudawud','nasai','ibnmajah','darimi'].includes(id)) return 'sunan';
    if (id === 'ahmad') return 'musnad';
    if (id === 'malik') return 'mushannaf';
    if (['nawawi','qudsi','shah','adab','bulugh','mishkat','riyad','shamail'].includes(id)) return 'jawami';
    return 'other';
  }"""

replacement_getType = """  function getType(id) {
    if (['bukhari','muslim','tirmidhi','ibnukhuzaimah','ibnuhibban'].includes(id)) return 'jami';
    if (['abudawud','nasai','ibnmajah','darimi','daruquthni'].includes(id)) return 'sunan';
    if (['ahmad','syafii'].includes(id)) return 'musnad';
    if (id === 'malik') return 'mushannaf';
    if (id === 'tabarani') return 'mujam';
    if (id === 'mustadrak') return 'mustadrak';
    if (['nawawi','qudsi','shah','adab','bulugh','mishkat','riyad','riyad_arab','shamail'].includes(id)) return 'jawami';
    return 'other';
  }"""

target_labels = """  const TYPE_LABELS = {'jami':"Jami'",'sunan':"Sunan",'musnad':"Musnad",'mushannaf':"Mushannaf",'jawami':"Jawami'",'other':"Kitab"};"""
replacement_labels = """  const TYPE_LABELS = {'jami':"Jami'",'sunan':"Sunan",'musnad':"Musnad",'mushannaf':"Mushannaf",'mujam':"Mu'jam",'mustadrak':"Mustadrak",'jawami':"Jawami'",'other':"Kitab"};"""


if target_getType in html:
    html = html.replace(target_getType, replacement_getType)
if target_labels in html:
    html = html.replace(target_labels, replacement_labels)

with open('books.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated getType and TYPE_LABELS in books.html")

