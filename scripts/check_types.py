import json

def getType(id):
    if id in ['bukhari','muslim','tirmidhi','ibnukhuzaimah','ibnuhibban']:
        return 'jami'
    if id in ['abudawud','nasai','ibnmajah','darimi','daruquthni']:
        return 'sunan'
    if id in ['ahmad','syafii']:
        return 'musnad'
    if id == 'malik':
        return 'mushannaf'
    if id == 'tabarani':
        return 'mujam'
    if id == 'mustadrak':
        return 'mustadrak'
    if id in ['nawawi','qudsi','shah','adab','bulugh','mishkat','riyad','riyad_arab','shamail']:
        return 'jawami'
    return 'other'

TYPE_LABELS = {'jami':"Jami'",'sunan':"Sunan",'musnad':"Musnad",'mushannaf':"Mushannaf",'mujam':"Mu'jam",'mustadrak':"Mustadrak",'jawami':"Jawami'",'other':"Kitab"}

d = json.load(open('data/books_v2.json', encoding='utf-8'))
for i, b in enumerate(d):
    t = getType(b['id'])
    print(f"{i:2} {b['id']:20} -> {TYPE_LABELS[t]}")
