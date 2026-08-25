
import glob
import re
import json

suras = set()
files = glob.glob("../data/editions/ind-*.ndjson")
p = re.compile(r"\((?:QS|Qs|qs)\.\s*([^:]+?)\s*:\s*[0-9-]+[a-z]?\)")
for f in files:
    with open(f, "r") as file_in:
        for line in file_in:
            matches = p.findall(line)
            for m in matches:
                suras.add(m.strip().lower())

print(sorted(list(suras)))
