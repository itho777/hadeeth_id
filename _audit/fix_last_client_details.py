from pathlib import Path
import sys
p = Path(r"G:/hadeeth_id/js/app.js")
t = p.read_bytes().decode("utf-8")
NL = "\r\n"

def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        print(f"FAIL expected {n}, got {c}: {old[:70]!r}")
        sys.exit(1)
    t = t.replace(old, new)

# Topic EN attribution in the EN-only layout (it was only shown in dual mode).
rep("+ '<p class=\"text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed\"><strong class=\"text-xs text-sunan-emerald dark:text-[#10b981] block mb-1\">English Translation:</strong>' + (enText || enUnavailable) + '</p>'",
    "+ '<p class=\"text-sm text-on-surface-variant dark:text-gray-300 leading-relaxed\"><strong class=\"text-xs text-sunan-emerald dark:text-[#10b981] block mb-1\">English Translation:</strong>' + (enLinkText ? `<span class='block mb-2 text-xs text-amber-500 font-semibold'>${escapeHtml(enLinkText)}</span>` : '') + (enText || enUnavailable) + '</p>'")

# Chapter labels: use the real Arabic chapter title when no ID/EN translation exists.
rep("      const titleEn = ch.title_en || ch.name_en || ch.title || `Chapter ${chNum}`;" + NL +
    "      const titleId = ch.title_id || ch.name_id || titleEn;",
    "      const titleEn = ch.title_en || ch.name_en || ch.title || ch.title_ar || `Chapter ${chNum}`;" + NL +
    "      const titleId = ch.title_id || ch.name_id || ch.title_ar || titleEn;")

p.write_bytes(t.encode("utf-8"))
print("patched app.js topic EN attribution + chapter title fallback")

# Scholars: neutral generic biography instead of asserting 'tsiqah' for every rawi.
p2 = Path(r"G:/hadeeth_id/scholars.html")
t2 = p2.read_bytes().decode("utf-8")
old = "Perawi tsiqah yang tercatat meriwayatkan ${r.hadith_count.toLocaleString('id-ID')} hadits dalam koleksi kitab hadits kanonik Islam."
new = "Terdaftar dalam ${r.hadith_count.toLocaleString('id-ID')} tautan hadits pada data perawi yang tersedia."
print("scholar bio replacements", t2.count(old))
t2 = t2.replace(old, new)
p2.write_bytes(t2.encode("utf-8"))
