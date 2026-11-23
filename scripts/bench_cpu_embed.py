import json, time, os
os.environ.setdefault("OMP_NUM_THREADS", "8")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import torch
from sentence_transformers import SentenceTransformer

torch.set_num_threads(8)
print("threads", torch.get_num_threads(), flush=True)

t0 = time.time()
model = SentenceTransformer("BAAI/bge-m3", device="cpu")
print(f"load {time.time()-t0:.1f}s", flush=True)

rows = []
with open("export_site/search/ahmad.ndjson", encoding="utf-8") as fh:
    for i, line in enumerate(fh):
        if i >= 256:
            break
        d = json.loads(line)
        t = " | ".join(x for x in (d.get("text_ar"), d.get("text_id"), d.get("text_en")) if x)[:2000]
        if t:
            rows.append(t)
print("docs", len(rows), flush=True)

for seq in (512, 256):
    model.max_seq_length = seq
    for bs in (8, 16, 32):
        t0 = time.time()
        with torch.inference_mode():
            model.encode(rows[:128], batch_size=bs, normalize_embeddings=True,
                         show_progress_bar=False, convert_to_numpy=True)
        el = time.time() - t0
        rate = 128 / el
        print(f"seq={seq} bs={bs}: {el:.1f}s  {rate:.2f} docs/s  -> full corpus {153920/rate/3600:.1f} h", flush=True)
