import sqlite3

db_path = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

books = ['bukhari', 'muslim', 'ahmad', 'abudaud', 'tirmidzi', 'nasai', 'ibnumajah', 'malik', 'darimi']

print("Checking English translation counts in lidwa.db...")
print("-" * 50)
total_english = 0

for book in books:
    try:
        c.execute("SELECT COUNT(*) FROM had_agregat WHERE imam = ? AND Isi_English IS NOT NULL AND Isi_English != '' AND Isi_English != 'NULL'", (book,))
        count = c.fetchone()[0]
        total_english += count
        print("Book {} : {} English translations".format(book.ljust(10), count))
    except Exception as e:
        print("Book {} : Error ({})".format(book.ljust(10), e))

print("-" * 50)
print("Total English Translations: {}".format(total_english))

conn.close()
