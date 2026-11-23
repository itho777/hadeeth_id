#!/usr/bin/env python3
"""Reconcile the artifact's ids against the corpus, and explain any gap."""
import importlib.util
import json
import sys
import types

sys.modules.setdefault("sentence_transformers", types.ModuleType("sentence_transformers"))

spec = importlib.util.spec_from_file_location("vh", r"G:\hadeeth_id\scripts\vectorize_hadeeth.py")
vh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vh)

objs, _ = vh.hadith_objects()
expected = []
skipped = []
for name, source, path in objs:
    for rec in vh.stream(path):
        rid = rec.get("id")
        if rid is None:
            skipped.append((source, name, None, "id is None"))
            continue
        text = vh.embed_text(rec)
        if not text:
            skipped.append((source, name, rid, "no usable text"))
            continue
        expected.append(vh.safe_id(source, name, rid))

got = [json.loads(l) for l in open(r"G:\hadeeth_id\vectors\hadeeth_ids.ndjson", encoding="utf-8") if l.strip()]
gotset = set(got)
expectedset = set(expected)

print("expected embeddable:", len(expected))
print("ids in artifact    :", len(got))
print("order identical    :", expected == got)
print("missing from artifact:", len([e for e in expected if e not in gotset]))
print("extra in artifact    :", len([g for g in got if g not in expectedset]))
print("--- skipped records (%d) ---" % len(skipped))
for s in skipped:
    print("  ", s)
