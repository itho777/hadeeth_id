import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

books = ['ibnukhuzaimah', 'ibnuhibban', 'mustadrak', 'daruquthni']
for book in books:
    path = f'data/api/{book}.ndjson'
    with open(path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
    first = json.loads(first_line)
    print(f'=== {book} ===')
    print('keys:', list(first.keys()))
    if 'translations' in first:
        for lang, txs in first['translations'].items():
            for tx in txs:
                src = tx.get('source', '?')
                has_text = bool(tx.get('text', ''))
                print(f'  [{lang}] source={src}, has_text={has_text}')
    print('has text_ar:', bool(first.get('text_ar')))
    print('has text_id:', bool(first.get('text_id')))
    print('has text_en:', bool(first.get('text_en')))
    print()
