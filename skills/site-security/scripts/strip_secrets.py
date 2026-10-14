#!/usr/bin/env python3
"""Filter scanner JSON-lines output so plaintext secrets never reach disk.

Usage: <tool> --json | strip_secrets.py trufflehog > out.json
Drops fields that carry the raw secret and keeps detector, location and
verification status.
"""
import json
import sys

DROP = {
    "trufflehog": {"Raw", "RawV2", "Redacted", "ExtraData"},
}


def main() -> int:
    tool = sys.argv[1] if len(sys.argv) > 1 else "trufflehog"
    drop = DROP.get(tool, set())
    for line in sys.stdin:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        print(json.dumps({k: v for k, v in obj.items() if k not in drop}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
