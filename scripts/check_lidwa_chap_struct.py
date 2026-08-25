# -*- coding: utf-8 -*-
import json, codecs
with codecs.open("check_lidwa_chap_struct.txt", "w", "utf-8") as out:
    with open("../data/lidwa-chapters/muslim.json", "r") as f:
        lidwa = json.load(f)
    out.write(str(type(lidwa)) + "\n")
    if isinstance(lidwa, dict):
        out.write("Keys: " + str(lidwa.keys()[:10]) + "\n")
        # Let's see the first value
        out.write(str(lidwa.values()[0])[:200] + "\n")