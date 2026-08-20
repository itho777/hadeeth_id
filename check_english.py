import sqlite3

db_path = 'lidwa_new.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

books = ['bukhari', 'muslim', 'ahmad', 'abudaud', 'tirmidzi', 'nasai', 'ibnumajah', 'malik', 'darimi']

for book in books:
    c.execute("SELECT COUNT(*) FROM had_agregat WHERE imam = ? AND Isi_English IS NOT NULL AND Isi_English != ''", (book,))
    count = c.fetchone()[0]
    print("Book {}: {} English translations".format(book, count))

conn.close()
