#!/usr/bin/env python3
"""Patch site_r2.py: genuine Fawaz rows, per-book crosswalk links, grading provenance.

All replacements are asserted; a partial match aborts without writing.
"""
from pathlib import Path
import sys

P = Path(__file__).resolve().parents[1] / "scripts" / "site_r2.py"
raw = P.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")

def sub(old, new, count=1):
    global text
    got = text.count(old)
    if got != count:
        print(f"ABORT: expected {count} match(es), found {got}\n---\n{old[:400]}")
        sys.exit(1)
    text = text.replace(old, new, count)

sub("import os\nimport sqlite3\n", "import os\nimport re\nimport sqlite3\n")

helper = '''
AR_DIA = re.compile(r"[\\u0617-\\u061A\\u064B-\\u0652\\u0670\\u06D6-\\u06ED\\u0640]")

GRADE_LABELS = {
    "lidwa": "Lidwa / Irsyad",
    "fawaz": "Fawaz Ahmed (sunnah.com)",
    "atif_hf": "Atif HF (sunnah.com)",
    "ahmedbaset": "AhmedBaset (Darussalam)",
    "usm": "USM (daftar Munkar)",
}

ATIF_FILES = {
    "bukhari": "Sahih al-Bukhari",
    "muslim": "Sahih Muslim",
    "abudawud": "Sunan Abi Dawud",
    "tirmidhi": "Jami` at-Tirmidhi",
    "nasai": "Sunan an-Nasa'i",
    "ibnmajah": "Sunan Ibn Majah",
}
USM_FILES = {"abudawud": "abudaud", "nasai": "nasai"}


def load_crosswalk():
    """book -> {fawaz number: lidwa number}, the real cross-reference.

    ``data/links/fawaz_<book>.json`` is an identity file and must never be used
    as a join. ``link_graph.json`` is the authoritative mapping.
    """
    p = DATA / "link_graph.json"
    if not p.exists():
        return {}
    doc = json.loads(p.read_text(encoding="utf-8"))
    edges = doc.get("fawaz_to_lidwa", doc)
    out = {}
    for key, value in edges.items():
        book, sep, num = str(key).partition("_")
        if not sep:
            continue
        out.setdefault(book, {})[num] = str(value)
    return out


def _ar_key(value):
    """Diacritic- and punctuation-insensitive Arabic key for cross-source joins."""
    s = AR_DIA.sub("", value or "")
    s = re.sub(r"[^\\u0600-\\u06FF]+", " ", s)
    return " ".join(s.split())[:2000]


def _grader(label, fallback):
    m = re.search(r"\\(([^)]+)\\)", label or "")
    if m and not m.group(1).strip().isdigit():
        return m.group(1).strip()
    return fallback


def _add_grade(store, key, entry):
    store.setdefault(str(key), []).append(entry)


def load_grade_sources(book, crosswalk):
    """Every grading source, indexed by lidwa id and by fawaz id.

    Sources: Lidwa's own grade column, Fawaz's multi-scholar list, Atif HF and
    AhmedBaset's Darussalam/Al-Albani labels (joined by Arabic text, because
    their numbering diverges), and the USM Munkar list where it is in range.
    """
    by_lidwa, by_fawaz = {}, {}
    cw = crosswalk.get(book, {})
    reverse = {}
    for fnum, lid in cw.items():
        reverse.setdefault(str(lid), str(fnum))

    fawaz_path = DATA / "sources" / "fawaz_combined_v2" / f"{book}.json"
    fawaz_rows = json.loads(fawaz_path.read_text(encoding="utf-8")) if fawaz_path.exists() else []
    fawaz_by_num = {}
    for row in fawaz_rows:
        num = str(row.get("hadithnumber") or "").strip()
        if not num:
            continue
        fawaz_by_num[num] = row
        for g in row.get("grades") or []:
            grade = str(g.get("grade") or "").strip()
            if not grade:
                continue
            entry = {
                "src": "fawaz",
                "src_label": GRADE_LABELS["fawaz"],
                "by": str(g.get("name") or "").strip() or "sunnah.com",
                "grade": grade,
            }
            _add_grade(by_fawaz, num, entry)
            lid = cw.get(num)
            if lid:
                _add_grade(by_lidwa, lid, entry)

    lidwa_path = DATA / "sources" / "lidwa" / f"{book}.ndjson"
    if lidwa_path.exists():
        with open(lidwa_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                num = str(row.get("hadith_number") or "").strip()
                grade = str(row.get("grade") or row.get("grade_id") or "").strip()
                if not num or not grade:
                    continue
                entry = {
                    "src": "lidwa",
                    "src_label": GRADE_LABELS["lidwa"],
                    "by": "Lidwa / Irsyad",
                    "grade": grade,
                }
                _add_grade(by_lidwa, num, entry)
                fnum = reverse.get(num)
                if fnum:
                    _add_grade(by_fawaz, fnum, entry)

    # Atif and AhmedBaset use sunnah.com numbering, which diverges from Fawaz
    # for many books (Muslim uses 8a/8b suffixes). Join on the Arabic text.
    text_index = {}
    for num, row in fawaz_by_num.items():
        key = _ar_key(row.get("text_ara"))
        if key:
            text_index.setdefault(key, num)

    atif_name = ATIF_FILES.get(book)
    if atif_name:
        p = DATA / "sources" / "atif_hf" / f"{atif_name}.json"
        if p.exists():
            for row in json.loads(p.read_text(encoding="utf-8")):
                grade = str(row.get("Grade") or "").strip()
                if not grade:
                    continue
                num = text_index.get(_ar_key(row.get("Arabic_Text")))
                if not num:
                    continue
                entry = {
                    "src": "atif_hf",
                    "src_label": GRADE_LABELS["atif_hf"],
                    "by": _grader(grade, "sunnah.com"),
                    "grade": grade,
                }
                _add_grade(by_fawaz, num, entry)
                lid = cw.get(num)
                if lid:
                    _add_grade(by_lidwa, lid, entry)

    ab_path = DATA / "sources" / "ahmedbaset_graded" / "by_book" / "the_9_books" / f"{book}.json"
    if ab_path.exists():
        doc = json.loads(ab_path.read_text(encoding="utf-8"))
        for row in doc.get("hadiths") or []:
            grade = str(row.get("grade_en") or "").strip()
            if not grade:
                continue
            num = text_index.get(_ar_key(row.get("arabic")))
            if not num:
                continue
            entry = {
                "src": "ahmedbaset",
                "src_label": GRADE_LABELS["ahmedbaset"],
                "by": _grader(grade, "Darussalam"),
                "grade": grade,
            }
            _add_grade(by_fawaz, num, entry)
            lid = cw.get(num)
            if lid:
                _add_grade(by_lidwa, lid, entry)

    usm_name = USM_FILES.get(book)
    if usm_name:
        p = DATA / "sources" / "usm_parsed" / f"{usm_name}.json"
        if p.exists():
            for num, grade in json.loads(p.read_text(encoding="utf-8")).items():
                num = str(num)
                if num not in fawaz_by_num or not str(grade).strip():
                    continue
                entry = {
                    "src": "usm",
                    "src_label": GRADE_LABELS["usm"],
                    "by": "USM",
                    "grade": str(grade).strip(),
                }
                _add_grade(by_fawaz, num, entry)
                lid = cw.get(num)
                if lid:
                    _add_grade(by_lidwa, lid, entry)

    for store in (by_lidwa, by_fawaz):
        for key, items in list(store.items()):
            seen, out = set(), []
            for entry in items:
                sig = (entry.get("src"), entry.get("by", ""), entry.get("grade"))
                if sig in seen:
                    continue
                seen.add(sig)
                out.append(entry)
            store[key] = out
    return {"by_lidwa": by_lidwa, "by_fawaz": by_fawaz}


'''
sub("def lidwa_master(book, old_path, num_map, dst):", helper + "def lidwa_master(book, old_path, num_map, dst, gradings_by_id=None):")

sub('            for key in ("grade", "grade_id", "gradings", "status", "elevation", "source"):\n                if key in prior:\n                    row[key] = prior[key]\n',
    '            for key in ("grade", "grade_id", "status", "elevation", "source"):\n                if key in prior:\n                    row[key] = prior[key]\n            if gradings_by_id:\n                graded = gradings_by_id.get(str(num))\n                if graded:\n                    row["gradings"] = graded\n')

old_intl = '''def international_master(book, src, dst):
    """Second dataset: existing international rows, chapter from its own edition."""
    refs = edition_reference_map(book)
    dst.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(src, encoding="utf-8") as f, dst.open("w", encoding="utf-8", newline="\\n") as out:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            r.pop("chapter_id", None)
            num = str(r.get("hadith_number", "")).strip()
            if num in refs:
                r["chapter_id"] = refs[num]
            out.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\\n")
            n += 1
    return n, refs
'''
new_intl = '''def international_master(book, lidwa_path, dst, crosswalk, gradings_by_id=None):
    """Genuine international rows, built from the Fawaz source itself.

    The previous version copied the Lidwa master and only swapped chapter_id,
    which made ``api/fawaz`` a second copy of Lidwa under a false name. This
    reads ``data/sources/fawaz_combined_v2/<book>.json``: Fawaz numbering,
    Fawaz Arabic/translation text and Fawaz's own scholar grades. The mapped
    Lidwa row contributes only the sanad fields (rawis/status/elevation) and a
    cross-referenced fallback text; ``lidwa_id`` comes from link_graph.json.
    """
    src = DATA / "sources" / "fawaz_combined_v2" / f"{book}.json"
    if not src.exists():
        return None
    fawaz_rows = json.loads(src.read_text(encoding="utf-8"))
    if not fawaz_rows:
        return None
    refs = edition_reference_map(book)
    cw = crosswalk.get(book, {})
    ab_map = {}
    ab_path = DATA / "links" / f"{book}.json"
    if ab_path.exists():
        for fnum, meta in json.loads(ab_path.read_text(encoding="utf-8")).items():
            if isinstance(meta, dict) and meta.get("ahmedbaset_id"):
                ab_map[str(fnum)] = str(meta["ahmedbaset_id"])

    lidwa = {}
    if Path(lidwa_path).exists():
        with open(lidwa_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                lidwa[str(row.get("hadith_number"))] = row

    dst.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with dst.open("w", encoding="utf-8", newline="\\n") as out:
        for r in fawaz_rows:
            num = str(r.get("hadithnumber") or "").strip()
            if not num:
                continue
            lid = cw.get(num)
            lrow = lidwa.get(str(lid)) if lid else None
            text_ar = str(r.get("text_ara") or "").strip()
            text_en = str(r.get("text_eng") or "").strip()
            text_id = str(r.get("text_ind") or "").strip()
            ar_src = "fawazahmed" if text_ar else "lidwa"
            en_src = "fawazahmed" if text_en else "lidwa"
            id_src = "fawazahmed" if text_id else "lidwa"
            if lrow:
                text_ar = text_ar or str(lrow.get("text_ar") or "")
                text_en = text_en or str(lrow.get("text_en") or "")
                text_id = text_id or str(lrow.get("text_id") or "")
            translations = {}
            if text_ar:
                translations["ar"] = [{"source": ar_src, "text": text_ar}]
            if text_en:
                translations["en"] = [{"source": en_src, "text": text_en}]
            if text_id:
                translations["id"] = [{"source": id_src, "text": text_id}]
            for key, code in (("text_urd", "ur"), ("text_ben", "bn"), ("text_fra", "fr")):
                value = str(r.get(key) or "").strip()
                if value:
                    translations[code] = [{"source": "fawazahmed", "text": value}]

            row = {
                "id": int(num) if num.isdigit() else num,
                "book": book,
                "hadith_number": num,
                "lidwa_id": [str(lid)] if lid and lrow else [],
                "text_ar": text_ar,
                "text_id": text_id,
                "text_en": text_en,
                "rawis": (lrow or {}).get("rawis") or [],
                "translations": translations,
            }
            if lrow:
                for key in ("status", "elevation", "grade", "grade_id"):
                    if lrow.get(key):
                        row[key] = lrow[key]
            if num in ab_map:
                row["ab_id"] = ab_map[num]
            if gradings_by_id:
                graded = gradings_by_id.get(num)
                if graded:
                    row["gradings"] = graded
            if num in refs:
                row["chapter_id"] = refs[num]
            out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\\n")
            n += 1
    return n, refs
'''
sub(old_intl, new_intl)

sub('    num_map, kitab_names = load_bab_maps()\n    counts = {}\n',
    '    num_map, kitab_names = load_bab_maps()\n    crosswalk = load_crosswalk()\n    counts = {}\n')

sub('        if book in CORE9:\n            built = lidwa_master(book, p, num_map.get(book, {}), OUT / "api" / name)\n',
    '        if book in CORE9:\n            grade_sets = load_grade_sources(book, crosswalk)\n            built = lidwa_master(book, p, num_map.get(book, {}), OUT / "api" / name,\n                                 grade_sets["by_lidwa"])\n')

sub('                fz_dst = OUT / "api" / "fawaz" / name\n                fz_n, fz_refs = international_master(book, p, fz_dst)\n                add(fz_dst, f"api/fawaz/{name}")\n                report.append((f"api/fawaz/{name}", fz_n, f"international, refs {len(fz_refs)}"))\n                continue\n',
    '                fz_dst = OUT / "api" / "fawaz" / name\n                fz = international_master(book, OUT / "api" / name, fz_dst, crosswalk,\n                                          grade_sets["by_fawaz"])\n                if fz:\n                    fz_n, fz_refs = fz\n                    add(fz_dst, f"api/fawaz/{name}")\n                    report.append((f"api/fawaz/{name}", fz_n, f"fawaz, refs {len(fz_refs)}"))\n                continue\n')

sub('        for path in sorted(links_dir.glob("*.json")):\n            doc = json.loads(path.read_text(encoding="utf-8"))\n',
    '        for path in sorted(links_dir.glob("*.json")):\n            # fawaz_*.json are identity maps; the real edge lists are added below.\n            if path.stem.startswith("fawaz_"):\n                continue\n            doc = json.loads(path.read_text(encoding="utf-8"))\n')

sub('            report.append((f"links/{path.stem}.ndjson", len(out), "-"))\n\n    meta_src = DATA / "meta" / "fawaz_editions.json"\n',
    '            report.append((f"links/{path.stem}.ndjson", len(out), "-"))\n\n        # 12b. Per-book Fawaz->Lidwa edge lists, built from the real mapping.\n        for book, edges in sorted(load_crosswalk().items()):\n            dst = OUT / "links" / f"fawaz_{book}.ndjson"\n            write_ndjson(dst, ({"k": k, "v": v} for k, v in edges.items()))\n            add(dst, f"links/fawaz_{book}.ndjson")\n            report.append((f"links/fawaz_{book}.ndjson", len(edges), "-"))\n\n    meta_src = DATA / "meta" / "fawaz_editions.json"\n')

out = text.replace("\n", "\r\n") if crlf else text
P.write_bytes(out.encode("utf-8"))
print(f"patched {P} ({'CRLF' if crlf else 'LF'})")
