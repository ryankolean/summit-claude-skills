#!/usr/bin/env python3
"""Mark saves as processed and clear their staged files.

usage: mark_processed.py <shortcode> [<shortcode> ...] [--state FILE] [--pending DIR]
       mark_processed.py --list        # show what is still staged
"""
import json, sys
from pathlib import Path

argv = sys.argv[1:]


def opt(name, default):
    return Path(argv[argv.index(name) + 1]).expanduser() if name in argv else default


state_path = opt("--state", Path.home() / ".cache/ig-saves/state.json")
pending = opt("--pending", Path.home() / ".cache/ig-saves/pending")
codes = [a for a in argv if not a.startswith("--") and argv[argv.index(a) - 1] not in ("--state", "--pending")]

if "--list" in argv:
    files = sorted(pending.glob("*.md")) if pending.exists() else []
    for f in files:
        head = f.read_text(encoding="utf-8", errors="replace")[:400]
        author = next((l.split(": ", 1)[1] for l in head.splitlines() if l.startswith("author:")), "?")
        status = next((l.split(": ", 1)[1] for l in head.splitlines() if l.startswith("status:")), "?")
        print(f"{f.stem:16} @{author:24} {status}")
    print(f"{len(files)} staged", file=sys.stderr)
    sys.exit(0)

if not codes:
    print(__doc__.strip(), file=sys.stderr)
    sys.exit(2)

state_path.parent.mkdir(parents=True, exist_ok=True)
data = {"processed": []}
if state_path.exists():
    try:
        data = json.loads(state_path.read_text())
    except json.JSONDecodeError:
        pass
processed = set(data.get("processed", []))

added, cleared = 0, 0
for c in codes:
    if c not in processed:
        processed.add(c)
        added += 1
    staged = pending / f"{c}.md"
    if staged.exists():
        staged.unlink()
        cleared += 1

data["processed"] = sorted(processed)
state_path.write_text(json.dumps(data, indent=2) + "\n")
print(f"marked {added} processed ({len(processed)} total), cleared {cleared} staged", file=sys.stderr)
