# -*- coding: utf-8 -*-
import sqlite3, codecs

with codecs.open("check_lidwa_chap4.txt", "w", "utf-8") as out:
    conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
    c = conn.cursor()
    c.execute("SELECT ID_Kitab, Kitab_Indonesia FROM datakitab_muslim ORDER BY ID_Kitab ASC LIMIT 5")
    for row in c.fetchall():
        out.write("Kitab " + str(row[0]) + ": " + row[1] + "\n")
        
    c.execute("SELECT ID_Kitab, ID_Bab, Bab_Indonesia FROM databab_muslim WHERE ID_Kitab IN (0, 1) ORDER BY ID_Kitab ASC, ID_Bab ASC LIMIT 10")
    for row in c.fetchall():
        out.write("Bab " + str(row[0]) + "." + str(row[1]) + ": " + row[2][:100] + "\n")