#!/usr/bin/env python3
"""Watch for the Colab vector artifact and the Kaggle fallback.

Prints only on a state change, so a 90-minute wait stays quiet.
Exits 0 when the artifact lands (and verifies it) or the Kaggle kernel finishes.
"""
import glob
import json
import os
import subprocess
import sys
import time

DOWNLOADS = r"C:\Users\waverider\Downloads"
ZIP = os.path.join(DOWNLOADS, "hadeeth_vectors.zip")
FINAL = r"G:\hadeeth_id\vectors"
VEC = os.path.join(FINAL, "hadeeth_vectors_f16.bin")
IDS = os.path.join(FINAL, "hadeeth_ids.ndjson")
SLUG = "ithosuryoputro/hadeeth-vectorize"
DEADLINE = time.time() + 95 * 60


def kaggle_status():
    try:
        p = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "status", SLUG],
                           capture_output=True, text=True, timeout=120)
        out = (p.stdout or "") + (p.stderr or "")
    except Exception:
        return ""
    for s in ("QUEUED", "RUNNING", "COMPLETE", "ERROR", "CANCELED"):
        if s in out:
            return s
    return ""


def find_zip():
    if os.path.exists(ZIP):
        return ZIP, os.path.getsize(ZIP)
    for p in glob.glob(os.path.join(DOWNLOADS, "hadeeth_vectors*.zip")):
        return p, os.path.getsize(p)
    return "", 0


def unzip_and_verify(zpath):
    import zipfile
    os.makedirs(FINAL, exist_ok=True)
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
        zf.extractall(FINAL)
    print(f"extracted {len(names)} files from {os.path.basename(zpath)}: {names}")
    p = subprocess.run([sys.executable, r"G:\hadeeth_id\scripts\verify_vectors.py", "--dir", FINAL],
                       capture_output=True, text=True, timeout=1800)
    try:
        rep = json.loads(p.stdout)
    except Exception:
        print("verify output:\n" + (p.stdout or p.stderr)[-2000:])
        return 1
    print(json.dumps(rep, indent=2))
    return 0 if rep.get("ok") else 1


last_state = None
last_size = 0
while time.time() < DEADLINE:
    kst = kaggle_status()
    zpath, zsize = find_zip()
    state = (kst, bool(zpath), zsize // (1 << 20))

    if state != last_state:
        stamp = time.strftime("%H:%M:%S")
        bits = [f"[{stamp}] kaggle={kst or 'unknown'}"]
        if zpath:
            bits.append(f"zip={os.path.basename(zpath)} {zsize/1e6:.1f} MB")
        else:
            bits.append("zip=absent")
        print("  ".join(bits), flush=True)
        last_state = state

    if zpath and zsize > 100_000_000:
        time.sleep(20)                      # let the browser finish writing
        z2, s2 = find_zip()
        if s2 == os.path.getsize(z2):
            print("artifact landed, verifying...", flush=True)
            sys.exit(unzip_and_verify(z2))

    if kst == "COMPLETE" and not zpath:
        print("Kaggle kernel COMPLETE - pulling via pull_vectors_if_ready.py", flush=True)
        sys.exit(subprocess.run([sys.executable, r"G:\hadeeth_id\scripts\pull_vectors_if_ready.py"]).returncode)

    if kst in ("ERROR", "CANCELED") and not zpath:
        print(f"Kaggle kernel ended {kst}; waiting on Colab only", flush=True)

    time.sleep(45)

print(f"monitor window elapsed. kaggle={kaggle_status() or 'unknown'} zip={'yes' if find_zip()[0] else 'no'}", flush=True)
