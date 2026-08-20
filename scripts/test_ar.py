import sqlite3
con = sqlite3.connect('scratch/lidwa_imported.db')
cursor = con.cursor()
cursor.execute("SELECT Isi_Arab FROM had_agregat WHERE imam='ahmad' and NoHdt=1")
row = cursor.fetchone()
with open('test_ar.txt', 'w', encoding='utf-8') as f:
    f.write(row[0])
print('written text')
