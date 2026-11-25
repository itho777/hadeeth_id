#!/usr/bin/env python3
"""Apply the app schema through the Supabase Management API.

Usage:
  SUPABASE_ACCESS_TOKEN=sbp_... python scripts/apply_supabase_migration.py --write

A personal access token is required because PostgREST and the service-role key
cannot execute DDL. Create one at
https://supabase.com/dashboard/account/tokens (never commit it).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIGRATION = ROOT / "supabase" / "migrations" / "20261125000000_mobile_sync_and_hotd.sql"
PROJECT_REF = "idokyspokenbmzoegahq"


def env_value(name: str) -> str:
    if os.getenv(name):
        return os.environ[name].strip()
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                if k.strip() == name:
                    return v.strip().strip('"').strip("'")
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--project", default=PROJECT_REF)
    args = ap.parse_args()
    if not MIGRATION.exists():
        sys.exit(f"missing {MIGRATION}")
    sql = MIGRATION.read_text(encoding="utf-8")
    token = env_value("SUPABASE_ACCESS_TOKEN")
    print(f"project={args.project} sql_chars={len(sql)} token={'set' if token else 'missing'}")
    if not args.write:
        print("dry run; pass --write to execute")
        return 0
    if not token:
        sys.exit("SUPABASE_ACCESS_TOKEN missing (env or .env); create one at /dashboard/account/tokens")
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{args.project}/database/query",
        data=json.dumps({"query": sql}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read().decode("utf-8", "replace")
            print("HTTP", r.status, body[:1000])
    except urllib.error.HTTPError as exc:
        print("HTTP", exc.code, exc.read(2000).decode("utf-8", "replace"))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
