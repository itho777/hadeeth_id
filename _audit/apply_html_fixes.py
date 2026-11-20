from pathlib import Path
import re
r = Path(r"G:/hadeeth_id")
p = r / "privacy.html"
t = p.read_bytes().decode("utf-8")
old = "Ã¢â‚¬â€\x9d"
print("privacy mojibake", t.count(old))
p.write_bytes(t.replace(old, "—").encode("utf-8"))

p = r / "scholars.html"
t = p.read_bytes().decode("utf-8")
cp = {}
for i in range(32, 256):
    try:
        cp[bytes([i]).decode("cp1252")] = i
    except Exception:
        pass
for i in (0x81, 0x8D, 0x8F, 0x90, 0x9D):
    cp[chr(i)] = i


def seg(s):
    b = bytearray()
    for ch in s:
        o = ord(ch)
        if o < 256:
            b.append(o)
        elif ch in cp:
            b.append(cp[ch])
        else:
            return s
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return s


def mixed(s):
    parts = re.split(r"([\u0600-\u06FF]+)", s)
    return "".join(x if re.fullmatch(r"[\u0600-\u06FF]+", x or "") else seg(x) for x in parts)


s = t.index("const arNameDict = {")
e = t.index("\n  };", s)
block = t[s:e]
new = re.sub(r"('[^']*':\s*')([^']*)(')", lambda m: m.group(1) + mixed(m.group(2)) + m.group(3), block)
t = t[:s] + new + t[e:]
t = t.replace("dateStr += ` &bull; ${cityStr}`;", "dateStr += ` • ${cityStr}`;")
p.write_bytes(t.encode("utf-8"))
print("scholars arNameDict fixed")
