#!/usr/bin/env python3
"""Read-only preflight for `site_r2.py upload`.

Shows what would be uploaded, skipped, and pruned. Never prints credentials.
"""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("site_r2", os.path.join(ROOT, "scripts", "site_r2.py"))
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def main():
    items = site.load_manifest()
    remote = site.remote_map()
    wanted = {i["key"] for i in items}
    stale = sorted(set(remote) - wanted)
    upload = [i for i in items if i["key"] not in remote]
    changed = [i for i in items if i["key"] in remote and remote[i["key"]][0] != i["bytes"]]
    same = len(items) - len(upload) - len(changed)
    print(f"manifest: {len(items)} objects, {sum(i['bytes'] for i in items)/2**20:.2f} MiB")
    print(f"R2:       {len(remote)} objects, {sum(v[0] for v in remote.values())/2**20:.2f} MiB")
    print(f"new: {len(upload)}  size-changed: {len(changed)}  identical: {same}")
    print(f"prune would delete: {len(stale)} objects "
          f"({sum(remote[k][0] for k in stale)/2**20:.2f} MiB)")
    for k in stale[:20]:
        print(f"  STALE {k}  {remote[k][0]:,} B")
    print(f"upload bytes: {sum(i['bytes'] for i in upload+changed)/2**20:.2f} MiB")


if __name__ == "__main__":
    main()
