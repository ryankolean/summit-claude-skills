#!/usr/bin/env python3
"""Decide pass / block / could-not-verify from findings.json and a policy.

Usage: gate.py RUN_DIR [--policy FILE] [--mode audit|gate|monitor] [--profile brochure|app]

Exit codes:
  0  pass (or audit/monitor mode, which never blocks)
  1  blocked: an unsuppressed finding at a blocking severity
  2  could not verify: a tool the policy requires did not run
The decision and reasons are written to RUN_DIR/gate.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_POLICY = Path(__file__).resolve().parent.parent / "policy.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    ap.add_argument("--mode", default="audit")
    ap.add_argument("--profile", default="brochure")
    a = ap.parse_args()
    run = Path(a.run_dir)
    data = json.loads((run / "findings.json").read_text())
    policy = json.loads(Path(a.policy).read_text())
    prof = policy["profiles"].get(a.profile, policy["profiles"]["brochure"])
    block = set(prof["block_severities"])
    tools = data.get("tools", {})

    reasons, unverified = [], []
    for group in prof.get("required_tools", []):
        options = group if isinstance(group, list) else [group]
        applicable = [t for t in options if tools.get(t, {}).get("status") != "not-applicable"]
        if not applicable:
            continue
        if not any(tools.get(t, {}).get("status") == "ran" for t in applicable):
            unverified.append(" or ".join(applicable))

    blocking = [f for f in data["findings"] if f["severity"] in block]
    for f in blocking:
        reasons.append(f"{f['severity']}: {f['title']} ({f['tool']}, {f['location']})")

    if a.mode != "gate":
        decision, code = "report-only", 0
    elif blocking:
        decision, code = "blocked", 1
    elif unverified:
        decision, code = "could-not-verify", 2
    else:
        decision, code = "pass", 0

    out = {"mode": a.mode, "profile": a.profile, "decision": decision,
           "blocking": reasons, "unverified_required_tools": unverified,
           "block_severities": sorted(block)}
    (run / "gate.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"decision": decision, "blocking": len(reasons), "unverified": unverified}))
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # a broken gate must never look like "blocked" or "pass"
        print(f"gate error: {e}", file=sys.stderr)
        sys.exit(2)
