import sqlite3
conn = sqlite3.connect('scratch/SunnahDb.db')
print("Musnad count:", conn.execute('SELECT COUNT(*) FROM Hadiths WHERE Book = "musnad"').fetchone())
