#!/usr/bin/env python3
"""
cf_env.py — Cloudflare credentials for the static-data pipeline.

The token is never stored in this file. It is read from the environment first
(CLOUDFLARE_API_TOKEN), then from the repo's gitignored .env. That keeps a
committed script free of secrets while still working from a fresh checkout that
has .env in place.
"""

import os
from pathlib import Path

ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "0f1e9510fccd3058326be7b5b5ee6802")
DB_UUID = os.environ.get("D1_DATABASE_ID", "154c5a69-39af-477d-938a-c0a2cedeb2f7")
BUCKET  = os.environ.get("R2_BUCKET", "hadeeth-id-static")

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def _from_env_file(key):
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return None


def token():
    t = os.environ.get("CLOUDFLARE_API_TOKEN") or _from_env_file("CLOUDFLARE_API_TOKEN")
    if not t:
        raise SystemExit(
            "CLOUDFLARE_API_TOKEN not set.\n"
            "  put CLOUDFLARE_API_TOKEN=cfut_... in the repo .env (gitignored),\n"
            "  or export it in the shell.")
    return t


def headers(json_body=True):
    h = {"Authorization": f"Bearer {token()}"}
    if json_body:
        h["Content-Type"] = "application/json"
    return h
