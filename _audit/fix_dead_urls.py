from pathlib import Path
import re
p = Path(r"G:/hadeeth_id/profile-detail.html")
t = p.read_bytes().decode("utf-8")
pat = re.compile(r"    // 1\. Try to fetch[\s\S]*?    // 2\. Fallback to scanning all books if index yielded nothing")
new = ("    // The pre-computed narrator index (data/rawis/indexes/idx_*.json) is not\n"
       "    // published; skip the dead fetch and use the token scan below.\n"
       "    // 2. Fallback to scanning all books if index yielded nothing").replace("\n", "\r\n")
t2, n = pat.subn(new, t)
print("replaced", n)
if n != 1:
    raise SystemExit(1)
p.write_bytes(t2.encode("utf-8"))
