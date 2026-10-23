#!/usr/bin/env python3
"""Run npm audit on every package-lock.json in a repo and merge the reports.

Usage: npm_audit.py REPO LOCKFILES
LOCKFILES is a newline-separated list of package-lock.json paths relative to
REPO. Prints one npm audit report; each vulnerability carries _lockfile so its
finding points at the right file. Exits 2 if any audit errored, so scan.sh
records npm-audit as failed rather than clean.
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo = Path(sys.argv[1])
    merged = {"auditReportVersion": 2, "vulnerabilities": {}}
    for lock in [l for l in sys.argv[2].splitlines() if l]:
        r = subprocess.run(["npm", "audit", "--json", "--prefix", str((repo / lock).parent)],
                           capture_output=True, text=True)
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            data = None
        # npm audit exits 1 when it finds vulnerabilities; that still counts as ran.
        if r.returncode not in (0, 1) or not isinstance(data, dict) or "error" in data:
            reason = data.get("error") if isinstance(data, dict) else r.stderr.strip()
            print(f"npm audit failed for {lock}: {str(reason)[:200]}", file=sys.stderr)
            return 2
        for name, vuln in (data.get("vulnerabilities") or {}).items():
            merged["vulnerabilities"][f"{lock}:{name}"] = dict(vuln, name=vuln.get("name", name), _lockfile=lock)
    json.dump(merged, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
