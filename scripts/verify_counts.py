import glob, json;
for f in glob.glob('data/rawis/profiles/rawi_*.json'):
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
    c = data.get('book_counts', {})
    print("{} {:>4} / {:>4}  (Total: {})".format(data['id'].ljust(30), c.get('bukhari', 0), c.get('muslim', 0), data.get('hadith_count', 0)))
