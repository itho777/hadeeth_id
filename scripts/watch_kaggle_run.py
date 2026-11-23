#!/usr/bin/env python3
"""Wait for the Kaggle vectorizer kernel, then pull its output vectors."""
import os
import subprocess
import sys
import time

SLUG = "ithosuryoputro/hadeeth-vectorize"
OUT = r"G:\hadeeth_id\kaggle_out"
DEADLINE = time.time() + 3 * 3600


def kaggle(*args):
    p = subprocess.run([sys.executable, "-m", "kaggle", *args], capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def status():
    _, out = kaggle("kernels", "status", SLUG)
    for s in ("QUEUED", "RUNNING", "COMPLETE", "ERROR", "CANCELED"):
        if s in out:
            return s
    return "UNKNOWN: " + out.strip()[:200]


last = None
while time.time() < DEADLINE:
    s = status()
    if s != last:
        print(f"[{time.strftime('%H:%M:%S')}] {s}", flush=True)
        last = s
    if s in ("COMPLETE", "ERROR", "CANCELED"):
        break
    time.sleep(60)

if last != "COMPLETE":
    print(f"ended in state {last}", flush=True)
    sys.exit(1)

os.makedirs(OUT, exist_ok=True)
rc, out = kaggle("kernels", "output", SLUG, "-p", OUT)
print("kernels output rc", rc, out[-800:], flush=True)
for root, _, files in os.walk(OUT):
    for f in sorted(files):
        p = os.path.join(root, f)
        print(f"  {os.path.getsize(p):>12,}  {p}", flush=True)
