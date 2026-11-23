# Offline vector artifact — hadeeth.id corpus

Built by `scripts/vectorize_hadeeth.py` on a Kaggle T4 GPU (kernel
`ithosuryoputro/hadeeth-vectorize`), pulled and verified by
`scripts/pull_vectors_if_ready.py`.

**Status: complete and verified.**

| | |
|---|---|
| Documents | **153,914** |
| Dimensions | 1024 (`BAAI/bge-m3`) |
| dtype | float16, L2-normalised |
| Vector file | 315,215,872 bytes (300.6 MB) |
| Build time | 2,698.7 s (57.0 docs/s) |
| Built at | 2026-11-23T22:13:40Z |
| GPU used | 0.29 h of a 30 h monthly quota |

## Files

| File | Shape / format | Purpose |
|---|---|---|
| `hadeeth_vectors_f16.bin` | `(153914, 1024)` raw float16, row-major, L2-normalised | Dense bge-m3 embeddings |
| `hadeeth_ids.ndjson` | one JSON string per line, 153,914 lines | Meili document id for each row, same order |
| `meta.json` | JSON | model, dims, counts, per-shard breakdown, timing |

## Invariants

- Row `i` of the vector file belongs to id on line `i` of the ids file.
- Ids are byte-identical to the `hadiths` index ids (same `safe_id` function as `hadith_sync.py`).
- Model: `BAAI/bge-m3`, 1024 dimensions, max sequence length 512, text truncates at 2000 chars.
- Source text: `text_ar | text_id | text_en` from the same `api/*.ndjson` rows Meili ingests.
- dtype is **float16**; a consumer needing Vectorize must upcast to float32 (Vectorize stores 32-bit floats).
- Artifact order is corpus order (shard order in `meta.json["shards"]`), not sorted.

## Coverage gap — 6 records

The corpus holds 153,920 rows; 153,914 are embedded. The 6 absent ones have
empty `text_ar`, `text_id` and `text_en` in the source and carry their text
only in a `translations` map (`ur`, `fr`, …), which `embed_text()` does not read:

| source | collection | id |
|---|---|---|
| fawaz | muslim | 5115 |
| fawaz | muslim | 7317 |
| fawaz | muslim | 7520 |
| fawaz | tirmidhi | 391.2 |
| fawaz | tirmidhi | 458 |
| fawaz | tirmidhi | 1561.2 |

They remain keyword-searchable in Meili. Recovering them semantically needs
`embed_text()` to fall back to `translations`, which would change the text
recipe for those rows only — a deliberate decision, not an oversight.

## Verify

```bash
python scripts/verify_vectors.py --dir vectors
python scripts/reconcile_ids.py          # walks the corpus and explains any gap
```

`verify_vectors.py` checks row/id count, duplicates, id byte length, finiteness,
L2 norms, zero rows and meta agreement. Last run: `ok: true`, 20,000 rows
sampled, norms 0.99976–1.00049 (mean 1.00008), 0 zero rows, 19,997 distinct.

## Why offline first

Cloudflare Vectorize free plan allows 5,000,000 stored vector dimensions.
This corpus needs 153,914 x 1024 = 157,607,936 — 31x over. The vectors are
therefore kept as a portable artifact until the storage/search backend is
decided. Workers Paid would cover it (10M dims included, then $0.05/100M).

Meili cannot host them either: adding a `userProvided` embedder to the
populated `hadiths` index is refused (`no vectors provided for document ...`).
