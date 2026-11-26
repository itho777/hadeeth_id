#!/usr/bin/env python3
"""Repair the `rn` newline artifacts in the shipped book payloads.

An earlier import unescaped `\r\n` by dropping the backslashes, so the payload
carries the literal letters `rn` wherever a line break belonged. Two books are
affected: riyad and syafii. A third pattern, ` rn` + lowercase, replaced an `m`
in riyad ("rnenjadi" -> "menjadi").

Rules, applied to string fields only:
  rnrn            -> blank line
  " rn" + [a-z]   -> " m"      (a swallowed m, never a line break)
  [a-z]rn + [A-Z] -> line break
  [:.,!?]rn + quote -> line break

Usage:
  python _audit/fix_rn_artifacts.py --dry-run
  python _audit/fix_rn_artifacts.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    ROOT / "data/api/riyad.ndjson",
    ROOT / "data/api/syafii.ndjson",
    ROOT / "data/sources/hadeeth_id/riyad.ndjson",
    ROOT / "data/sources/hadeeth_id/syafii.ndjson",
]
BACKUP = ROOT / "_audit/backup_2026-11-26"

RE_BLANK = re.compile("rnrn")
RE_SWALLOWED_M = re.compile("(?<= )rn(?=[a-z])")
RE_BREAK_UPPER = re.compile("(?<=[a-z])rn(?=[A-Z])")
RE_BREAK_QUOTE = re.compile("(?<=[:.,!?])rn(?=[\"\u201c\u2018])")


def repair(text: str) -> tuple[str, dict[str, int]]:
    counts = {}
    for name, pattern, repl in (
        ("blank", RE_BLANK, "\n\n"),
        ("swallowed_m", RE_SWALLOWED_M, "m"),
        ("break_upper", RE_BREAK_UPPER, "\n"),
        ("break_quote", RE_BREAK_QUOTE, "\n"),
    ):
        text, n = pattern.subn(repl, text)
        counts[name] = n
    return text, counts


def fix_value(value, totals):
    """Walk dicts and lists: riyad keeps its translation bodies nested."""
    if isinstance(value, str):
        if "rn" not in value:
            return value
        new, counts = repair(value)
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
        return new
    if isinstance(value, dict):
        return {k: fix_value(v, totals) for k, v in value.items()}
    if isinstance(value, list):
        return [fix_value(v, totals) for v in value]
    return value


def fix_row(row, totals):
    return fix_value(row, totals)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.write and not args.dry_run:
        ap.error("pass --dry-run or --write")

    grand = 0
    for path in TARGETS:
        if not path.exists():
            print(f"SKIP missing {path.relative_to(ROOT)}")
            continue
        raw = path.read_text(encoding="utf-8")
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        totals: dict[str, int] = {}
        fixed = [fix_row(row, totals) for row in rows]
        before = raw.count("rnrn")
        after = sum(json.dumps(r, ensure_ascii=False).count("rnrn") for r in fixed)
        out = "\n".join(json.dumps(r, ensure_ascii=False) for r in fixed) + "\n"
        print(f"{path.relative_to(ROOT)}: rows={len(rows)} rnrn {before} -> {after} "
              f"rules={totals} bytes {len(raw)} -> {len(out)}")
        if after:
            print(f"  !! {after} rnrn still present, not writing")
            continue
        if args.write:
            BACKUP.mkdir(parents=True, exist_ok=True)
            dest = BACKUP / path.name
            if not dest.exists():
                shutil.copy2(path, dest)
            path.write_text(out, encoding="utf-8", newline="\n")
            print(f"  wrote {path.relative_to(ROOT)} md5={hashlib.md5(out.encode()).hexdigest()}")
        grand += sum(totals.values())
    print(f"total substitutions {grand}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
