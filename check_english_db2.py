import sqlite3

db_path = r'h:\Itho\2026\Project\Hadeeth\data source\lidwa\lidwa.db'
password = "EgSNvjq%7@cW86&J6fWzq9j@5SGhWx7jEtutbps7S@&h%d8f4ewyRkaqHmvr$SSx%qD*HSyuW8BVSJ4hSFH8#$tzdMS9B!rK@wYh$Qp%E6$5AYQpstzV@pXVctq4rzcg4NeTtxPn!YjRSFcUQ$wFufasszaHAcT3Qi&^PH6pHT$vEFsYWY$Ikw@P9ukkBcoGB%@lcsEKA37IIPjYKl!%z!to2JFO5!7M409Mmirv3X1utAZi!XHGWh#&E"

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("PRAGMA key='{}'".format(password))

# Let's verify we can read
try:
    c.execute("SELECT count(*) FROM sqlite_master")
    c.fetchone()
except Exception as e:
    print("Failed to decrypt: {}".format(e))
    exit(1)

books = ['bukhari', 'muslim', 'ahmad', 'abudaud', 'tirmidzi', 'nasai', 'ibnumajah', 'malik', 'darimi']

print("Checking English translation counts in encrypted lidwa.db...")
print("-" * 50)
total_english = 0

for book in books:
    try:
        # Note: SQLCipher queries might be a bit slow, but this is a simple COUNT
        c.execute("SELECT COUNT(*) FROM had_agregat WHERE imam = ? AND Isi_English IS NOT NULL AND Isi_English != '' AND Isi_English != 'NULL'", (book,))
        count = c.fetchone()[0]
        total_english += count
        print("Book {} : {} English translations".format(book.ljust(10), count))
    except Exception as e:
        print("Book {} : Error ({})".format(book.ljust(10), e))

print("-" * 50)
print("Total English Translations: {}".format(total_english))

conn.close()
