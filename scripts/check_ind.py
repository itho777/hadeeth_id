# -*- coding: utf-8 -*-
import sqlite3
import codecs
conn = sqlite3.connect('../data/sources/lidwa/lidwa.new.db')
c = conn.cursor()
with codecs.open('check_muslim.txt', 'w', 'utf-8') as out:
    c.execute("SELECT NoHdt, Kitab, Terjemah FROM ind_2 WHERE NoHdt IN (61, 93, 135, 136)")
    for row in c.fetchall():
        out.write(u"NoHdt: " + unicode(row[0]) + u" | Kitab: " + unicode(row[1]) + u" | Text: " + unicode(row[2][:100].replace('\n', ' ')) + u"\n")