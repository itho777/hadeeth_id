#!/usr/bin/env python3
"""Pull the Kaggle vector artifact once the kernel finishes, then verify it.

Silent by design: prints nothing while the kernel is queued or running, so a
no_agent cron job delivers only the final result (or a failure).

    python scripts/pull_vectors_if_ready.py
"""
import json
import os
import subprocess
import sys

SLUG = "ithosuryoputro/hadeeth-vectorize"
OUT = r"G:\hadeeth_id\kaggle_out"
FINAL = r"G:\hadeeth_id\vectors"
VEC = "hadeeth_vectors_f16.bin"
IDS = "hadeeth_ids.ndjson"
META = "meta.json"


def kaggle(*args, timeout=1800):
    p = subprocess.run([sys.executable, "-m", "kaggle", *args], capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def status():
    """Kernel state, or "" when the API call hiccups. A transient timeout or
    network blip must not look like a failure: the caller just retries later."""
    try:
        rc, out = kaggle("kernels", "status", SLUG, timeout=120)
    except Exception:
        return ""
    if rc != 0 and "KernelWorkerStatus" not in out:
        return ""
    for s in ("QUEUED", "RUNNING", "COMPLETE", "ERROR", "CANCELED"):
        if s in out:
            return s
    return ""


def find(name, *roots):
    for root in roots:
        for dp, _, fs in os.walk(root):
            if name in fs:
                return os.path.join(dp, name)
    return ""


def main():
    # Already landed? verify and stop.
    if os.path.exists(os.path.join(FINAL, VEC)) and os.path.exists(os.path.join(FINAL, IDS)):
        rc, out = subprocess.run(
            [sys.executable, r"G:\hadeeth_id\scripts\verify_vectors.py", "--dir", FINAL],
            capture_output=True, text=True, timeout=1800,
        )
        report = json.loads(out.stdout) if out.stdout.strip().startswith("{") else {"raw": out.stdout[-1500:]}
        if report.get("ok"):
            return 0  # nothing new to say
        print("Stored artifact failed verification:\n" + json.dumps(report, indent=2))
        return 1

    st = status()
    if st not in ("COMPLETE", "ERROR", "CANCELED"):
        return 0  # still queued/running, or the API hiccuped: stay silent

    if st != "COMPLETE":
        _, logs = kaggle("kernels", "logs", SLUG, timeout=600)
        tail = [l for l in logs.splitlines() if '"data"' in l][-12:]
        print(f"Kaggle kernel {SLUG} ended in {st}.\n\n" + "\n".join(tail))
        return 1

    os.makedirs(OUT, exist_ok=True)
    rc, out = kaggle("kernels", "output", SLUG, "-p", OUT)
    if rc != 0:
        print(f"kaggle kernels output failed (rc={rc}):\n{out[-1500:]}")
        return 1

    vpath, ipath, mpath = find(VEC, OUT), find(IDS, OUT), find(META, OUT)
    if not vpath or not ipath:
        listing = [os.path.join(dp, f) for dp, _, fs in os.walk(OUT) for f in fs]
        print("Kernel completed but the expected files are missing.\nDownloaded:\n" + "\n".join(listing[:40]))
        return 1

    os.makedirs(FINAL, exist_ok=True)
    for src in (vpath, ipath, mpath):
        if src:
            dst = os.path.join(FINAL, os.path.basename(src))
            if os.path.abspath(src) != os.path.abspath(dst):
                with open(src, "rb") as r, open(dst, "wb") as w:
                    while True:
                        chunk = r.read(1 << 22)
                        if not chunk:
                            break
                        w.write(chunk)

    proc = subprocess.run(
        [sys.executable, r"G:\hadeeth_id\scripts\verify_vectors.py", "--dir", FINAL],
        capture_output=True, text=True, timeout=1800,
    )
    print(proc.stdout.strip() or proc.stderr.strip()[-1500:])
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
