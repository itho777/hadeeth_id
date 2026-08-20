import sqlite3

books = ['bukhari', 'muslim', 'abudaud', 'tirmidzi', 'nasai', 'ibnumajah', 'darimi', 'ahmad', 'malik']
conn = sqlite3.connect('scratch/lidwa_plaintext.db')

for book in books:
    try:
        res = conn.execute(f"SELECT DISTINCT Derajat FROM derajat_{book}").fetchall()
        print(f"{book.upper()}: {[r[0] for r in res]}")
    except Exception as e:
        print(f"Error for {book}: {e}")
