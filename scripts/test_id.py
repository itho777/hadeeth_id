import sqlite3
con = sqlite3.connect('scratch/lidwa_imported.db')
cursor = con.cursor()
cursor.execute("SELECT Isi_Indonesia FROM had_agregat WHERE imam='ahmad' and NoHdt=1")
row = cursor.fetchone()
print(repr(row[0][:100]))
