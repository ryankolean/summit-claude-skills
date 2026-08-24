#!/usr/bin/env python3
"""Parse saved posts out of an Instagram 'Download Your Information' export.

usage: parse_export.py <export.zip|export_dir> [--state FILE] [--all] [--stats]

Emits one JSON object per line for saves not yet processed:
  {shortcode, url, kind, saved_at, caption, author, author_name, hashtags,
   brand_partner, collections}

Two export layouts are supported:

Current (list of records, captions included):
  your_instagram_activity/saved/saved_posts.json
    [{"timestamp": <unix>, "fbid": "...", "label_values": [
        {"label": "URL", "value": "...", "href": "..."},
        {"label": "Caption", "value": "..."},
        {"title": "Owner", "dict": [{"dict": [{"label": "Username", ...}]}]},
        {"title": "Hashtags", "dict": [...]},
        {"title": "Brand partner", "dict": [...]}]}]

Legacy (older archives):
  {"saved_saved_media": [{"title": "<author>",
     "string_map_data": {"Saved on": {"href": "<url>", "timestamp": <unix>}}}]}
"""
import json, re, sys, zipfile
from pathlib import Path

SHORTCODE = re.compile(r"/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)")
KIND = re.compile(r"instagram\.com/(p|reel|reels|tv)/")
MOJIBAKE = ("â", "ð", "Ã", "Â", "\x9f")


def demojibake(s):
    """Meta writes UTF-8 bytes reinterpreted as latin-1 for most, but not all,
    captions. Only repair strings that actually show the tell-tale markers, and
    only keep the repair if it decodes cleanly."""
    if not s or not any(m in s for m in MOJIBAKE):
        return s
    try:
        fixed = s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s
    return fixed if sum(fixed.count(m) for m in MOJIBAKE) < sum(s.count(m) for m in MOJIBAKE) else s


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


def flat_labels(entries):
    """[{'label': 'Username', 'value': 'x'}, ...] -> {'Username': 'x'}"""
    out = {}
    for e in entries or []:
        if isinstance(e, dict) and "label" in e:
            out[e["label"]] = e.get("value") or e.get("href") or ""
    return out


def nested_blocks(lv):
    """A titled block holds [{'dict': [...labels...]}, ...]."""
    for item in lv.get("dict") or []:
        if isinstance(item, dict):
            yield flat_labels(item.get("dict"))


def parse_record(rec):
    """Current format: one saved post."""
    labels, blocks = {}, {}
    for lv in rec.get("label_values", []):
        if "label" in lv:
            labels[lv["label"]] = lv.get("value") or lv.get("href") or ""
        elif lv.get("title"):
            blocks[lv["title"]] = list(nested_blocks(lv))

    url = labels.get("URL", "")
    m = SHORTCODE.search(url)
    if not m:
        return None
    owner = (blocks.get("Owner") or [{}])[0]
    partner = (blocks.get("Brand partner") or [{}])[0]
    kind = KIND.search(url)
    return {
        "shortcode": m.group(1),
        "url": url,
        "kind": {"reels": "reel"}.get(kind.group(1), kind.group(1)) if kind else "post",
        "saved_at": rec.get("timestamp"),
        "caption": demojibake(labels.get("Caption", "")),
        "author": owner.get("Username", ""),
        "author_name": demojibake(owner.get("Name", "")),
        "hashtags": [h.get("Name", "") for h in blocks.get("Hashtags", []) if h.get("Name")],
        "brand_partner": partner.get("Username", ""),
        "collections": [],
    }


def parse_legacy(item):
    smd = item.get("string_map_data") or {}
    entry = smd.get("Saved on") or next(iter(smd.values()), {})
    url = entry.get("href", "")
    m = SHORTCODE.search(url)
    if not m:
        return None
    kind = KIND.search(url)
    return {
        "shortcode": m.group(1),
        "url": url,
        "kind": {"reels": "reel"}.get(kind.group(1), kind.group(1)) if kind else "post",
        "saved_at": entry.get("timestamp"),
        "caption": "",
        "author": item.get("title") or "",
        "author_name": "",
        "hashtags": [],
        "brand_partner": "",
        "collections": [],
    }


def collection_index(blobs):
    """shortcode -> [collection names]. Collections nest their posts."""
    out = {}
    for name, blob in blobs:
        if "saved_collections" not in name:
            continue
        for coll in blob if isinstance(blob, list) else []:
            labels = {}
            posts = []
            for lv in coll.get("label_values", []):
                if "label" in lv:
                    labels[lv["label"]] = lv.get("value", "")
                elif lv.get("dict") or lv.get("title") is not None:
                    posts.extend(nested_blocks(lv))
            cname = demojibake(labels.get("Name", "")).strip()
            if not cname:
                continue
            for p in posts:
                m = SHORTCODE.search(p.get("URL", ""))
                if m:
                    out.setdefault(m.group(1), []).append(cname)
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

    colls = collection_index(blobs)
    records, skipped = [], 0
    for name, blob in blobs:
        if "saved_posts" not in name:
            continue
        if isinstance(blob, list):
            items = [parse_record(r) for r in blob]
        else:
            items = [parse_legacy(i) for i in blob.get("saved_saved_media", [])]
        for r in items:
            if not r:
                skipped += 1
                continue
            if r["shortcode"] in seen:
                continue
            r["collections"] = sorted(set(colls.get(r["shortcode"], [])))
            records.append(r)

    for r in records:
        # U+2028/U+2029 are real line breaks to str.splitlines(); left raw they
        # would split a JSONL record in half for any Python consumer
        line = json.dumps(r, ensure_ascii=False)
        for ch in ("\u2028", "\u2029", "\x85"):
            line = line.replace(ch, "\\u%04x" % ord(ch))
        print(line)

    print(f"{len(records)} new saves ({skipped} unparseable)", file=sys.stderr)
    if "--stats" in sys.argv:
        from collections import Counter
        kinds = Counter(r["kind"] for r in records)
        cc = Counter(c for r in records for c in r["collections"])
        uncollected = sum(1 for r in records if not r["collections"])
        print(f"  kinds: {dict(kinds)}", file=sys.stderr)
        print(f"  with caption: {sum(1 for r in records if r['caption'])}", file=sys.stderr)
        print(f"  uncollected: {uncollected}", file=sys.stderr)
        print(f"  collections: {len(cc)}", file=sys.stderr)
        for n, c in cc.most_common(15):
            print(f"    {n}: {c}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
