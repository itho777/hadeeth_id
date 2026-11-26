#!/usr/bin/env python3
"""Re-emit the repaired riyad/syafii payloads with their original CRLF endings.

The shipped objects use CRLF. Rewriting with LF shifted every byte offset by one
and changed 1,889 rows that had no defect, so the repair is re-applied from the
backup and written back with CRLF. Byte deltas are then reported per row: only
the rows carrying an artifact may differ.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_audit"))
sys.path.insert(0, str(ROOT / "scripts"))

from fix_rn_artifacts import fix_row, repair  # noqa: E402
from site_r2 import build_index_map  # noqa: E402

BACKUP = ROOT / "_audit/backup_2026-11-26"
IDX = ROOT / "_audit/index_2026-11-26"
PAIRS = [
    ("riyad.ndjson", ROOT / "data/api/riyad.ndjson", ROOT / "data/sources/hadeeth_id/riyad.ndjson"),
    ("syafii.ndjson", ROOT / "data/api/syafii.ndjson", ROOT / "data/sources/hadeeth_id/syafii.ndjson"),
]


def main() -> int:
    IDX.mkdir(parents=True, exist_ok=True)
    for name, *dests in PAIRS:
        raw = (BACKUP / name).read_bytes()
        assert raw.count(b"\r\n") and b"\n" not in raw.replace(b"\r\n", b""), f"{name}: not pure CRLF"
        lines = [l for l in raw.split(b"\r\n") if l.strip()]
        out_lines = []
        totals: dict[str, int] = {}
        changed_rows = 0
        for line in lines:
            row = json.loads(line.decode("utf-8"))
            fixed = fix_row(row, totals)
            if fixed != row:
                changed_rows += 1
            out_lines.append(json.dumps(fixed, ensure_ascii=False).encode("utf-8"))
        out = b"\r\n".join(out_lines) + b"\r\n"
        print(f"{name}: rows={len(lines)} changed_rows={changed_rows} rules={totals} "
              f"bytes {len(raw)} -> {len(out)}")
        assert b"rnrn" not in out, f"{name}: rnrn survived"
        for dest in dests:
            dest.write_bytes(out)
            print(f"  wrote {dest.relative_to(ROOT)}")
        idx = IDX / f"{Path(name).stem}_index.ndjson"
        n = build_index_map(dests[0], idx)
        data = dests[0].read_bytes()
        bad = 0
        for line in idx.read_text(encoding="utf-8").splitlines():
            e = json.loads(line)
            chunk = data[e["s"]:e["e"] + 1]
            try:
                row = json.loads(chunk.decode("utf-8"))
            except Exception:
                bad += 1
                continue
            if str(row.get("hadith_number")) != str(e["n"]):
                bad += 1
        print(f"  index {idx.name}: rows={n} bad_slices={bad}")
        if bad:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
