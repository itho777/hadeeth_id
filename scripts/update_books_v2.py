import json

with open('data/books_v2.json', 'r', encoding='utf-8') as f:
    books = json.load(f)
    
FAWAZ_BOOKS = {
    'bukhari': ['ara-bukhari', 'ara-bukhari1', 'ben-bukhari', 'eng-bukhari', 'fra-bukhari', 'ind-bukhari', 'rus-bukhari', 'tam-bukhari', 'tur-bukhari', 'urd-bukhari'],
    'muslim': ['ara-muslim', 'ara-muslim1', 'ben-muslim', 'eng-muslim', 'fra-muslim', 'ind-muslim', 'rus-muslim', 'tam-muslim', 'tur-muslim', 'urd-muslim'],
    'nasai': ['ara-nasai', 'ara-nasai1', 'ben-nasai', 'eng-nasai', 'fra-nasai', 'ind-nasai', 'tur-nasai', 'urd-nasai'],
    'abudawud': ['ara-abudawud', 'ara-abudawud1', 'ben-abudawud', 'eng-abudawud', 'fra-abudawud', 'ind-abudawud', 'rus-abudawud', 'tur-abudawud', 'urd-abudawud'],
    'tirmidhi': ['ara-tirmidhi', 'ara-tirmidhi1', 'ben-tirmidhi', 'eng-tirmidhi', 'ind-tirmidhi', 'tur-tirmidhi', 'urd-tirmidhi'],
    'ibnmajah': ['ara-ibnmajah', 'ara-ibnmajah1', 'ben-ibnmajah', 'eng-ibnmajah', 'fra-ibnmajah', 'ind-ibnmajah', 'tur-ibnmajah', 'urd-ibnmajah'],
    'malik': ['ara-malik', 'ara-malik1', 'ben-malik', 'eng-malik', 'fra-malik', 'ind-malik', 'tur-malik', 'urd-malik'],
    'dehlawi': ['ara-dehlawi', 'ara-dehlawi1', 'eng-dehlawi', 'fra-dehlawi'],
    'nawawi': ['ara-nawawi', 'ara-nawawi1', 'ben-nawawi', 'eng-nawawi', 'fra-nawawi', 'tur-nawawi'],
    'qudsi': ['ara-qudsi', 'ara-qudsi1', 'eng-qudsi', 'fra-qudsi']
}

for b in books:
    b_id = b['id']
    if b_id in FAWAZ_BOOKS:
        b['editions'] = FAWAZ_BOOKS[b_id]
    else:
        # clear any fake editions
        b['editions'] = []

with open('data/books_v2.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)

print("Updated books_v2.json successfully.")
