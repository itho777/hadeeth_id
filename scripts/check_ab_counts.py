# -*- coding: utf-8 -*-
import json, codecs

with codecs.open("check_ab_counts.txt", "w", "utf-8") as out:
    count_muq = 0
    count_iman = 0
    with open("../data/api/muslim.ndjson", "rb") as f:
        for line in f:
            obj = json.loads(line.decode('utf-8'))
            hid = obj.get('id')
            if type(hid) == int:
                if 1 <= hid <= 7: count_muq += 1
                if 8 <= hid <= 222: count_iman += 1 # Iman is usually 8 to 222 in Int'l? Let's just print the ID range.
    
    out.write("Muqaddimah (1-7) count: " + str(count_muq) + "\n")