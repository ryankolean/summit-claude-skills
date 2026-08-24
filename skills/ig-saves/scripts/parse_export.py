#!/usr/bin/env python3
"""Parse saved posts out of an Instagram 'Download Your Information' export.

usage: parse_export.py <export.zip|export_dir> [--state FILE] [--all]

Emits one JSON object per line for saves not yet seen:
  {"shortcode", "url", "author", "saved_at", "collection"}

Export layout (verified against Instagram archives):
  your_instagram_activity/saved/saved_posts.json
    {"saved_saved_media": [
       {"title": "<author>",
        "string_map_data": {"Saved on": {"href": "<url>", "timestamp": <unix>}}}]}
"""
import json, re, sys, zipfile
from pathlib import Path

SHORTCODE = re.compile(r"/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)")


def load_members(src: Path):
    """Yield (name, parsed_json) for every saved_* file in a zip or directory."""
    want = ("saved_posts.json", "saved_collections.json")
    if src.is_file() and src.suffix.lower() == ".zip":
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.rsplit("/", 1)[-1] in want:
                    try:
                        yield n, json.loads(z.read(n))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
    else:
        for n in want:
            for p in src.rglob(n):
                try:
                    yield str(p), json.loads(p.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue


def collection_map(blobs):
    """URL -> collection name. The collections file has drifted between export
    versions, so match structurally rather than on exact keys."""
    out = {}

    def walk(node, label=None):
        if isinstance(node, dict):
            name = node.get("title") or node.get("name") or label
            smd = node.get("string_map_data") or {}
            for entry in smd.values():
                if isinstance(entry, dict) and entry.get("href"):
                    out[entry["href"]] = label or name
            for k, v in node.items():
                walk(v, name if k in ("string_list_data", "media", "posts") else label)
        elif isinstance(node, list):
            for item in node:
                walk(item, label)

    for name, blob in blobs:
        if "saved_collections" in name:
            walk(blob)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    src = Path(args[0]).expanduser()
    if not src.exists():
        print(f"no such export: {src}", file=sys.stderr)
        return 1

    state_path = Path.home() / ".cache/ig-saves/state.json"
    if "--state" in sys.argv:
        state_path = Path(sys.argv[sys.argv.index("--state") + 1]).expanduser()
    seen = set()
    if state_path.exists() and "--all" not in sys.argv:
        try:
            seen = set(json.loads(state_path.read_text()).get("processed", []))
        except json.JSONDecodeError:
            pass

    blobs = list(load_members(src))
    if not blobs:
        print("no saved_posts.json found — is this an Instagram export?", file=sys.stderr)
        return 1
    colls = collection_map(blobs)

    count = 0
    for name, blob in blobs:
        if "saved_posts" not in name:
            continue
        for item in blob.get("saved_saved_media", []):
            smd = item.get("string_map_data") or {}
            entry = smd.get("Saved on") or next(iter(smd.values()), {})
            url = entry.get("href", "")
            m = SHORTCODE.search(url)
            if not m or m.group(1) in seen:
                continue
            print(json.dumps({
                "shortcode": m.group(1),
                "url": url,
                "author": item.get("title") or "",
                "saved_at": entry.get("timestamp"),
                "collection": colls.get(url),
            }))
            count += 1
    print(f"{count} new saves", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
