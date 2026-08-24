#!/usr/bin/env python3
"""Render one staged capture file from a parse_export.py record.

usage: stage_card.py <record.json>
env:   MANIFEST, TRANSCRIPT, STATUS

Writes markdown to stdout. Keeps captions (newlines, quotes, emoji) out of the
shell entirely — the caller only passes a file path.
"""
import datetime, json, os, sys


def yaml_str(s):
    """Quote defensively; captions carry quotes, colons and newlines."""
    return json.dumps(s or "", ensure_ascii=False)


rec = json.load(open(sys.argv[1], encoding="utf-8"))
manifest = os.environ.get("MANIFEST") or ""
transcript_path = os.environ.get("TRANSCRIPT") or ""
status = os.environ.get("STATUS") or "enriched"

saved_at = rec.get("saved_at")
saved_iso = (
    datetime.datetime.fromtimestamp(int(saved_at)).astimezone().isoformat(timespec="seconds")
    if saved_at else ""
)

out = ["---"]
out.append(f"shortcode: {rec['shortcode']}")
out.append(f"url: {rec['url']}")
out.append(f"kind: {rec.get('kind', '')}")
out.append(f"author: {rec.get('author', '')}")
out.append(f"author_name: {yaml_str(rec.get('author_name'))}")
out.append(f"saved_at: {saved_iso}")
out.append(f"collections: {json.dumps(rec.get('collections', []), ensure_ascii=False)}")
out.append(f"hashtags: {json.dumps(rec.get('hashtags', [])[:12], ensure_ascii=False)}")
if rec.get("brand_partner"):
    out.append(f"brand_partner: {rec['brand_partner']}")
out.append(f"manifest: {manifest or 'null'}")
out.append(f"status: {status}")
out.append("---")
out.append("")

out.append("## Caption")
out.append("")
out.append(rec.get("caption") or "(none)")
out.append("")

out.append("## Transcript")
out.append("")
if transcript_path and os.path.exists(transcript_path):
    text = open(transcript_path, encoding="utf-8").read().strip()
    out.append(text if text else "(none — silent, or audio unavailable)")
elif status == "unavailable":
    out.append("(unavailable — private, deleted, or rate-limited)")
else:
    out.append("(none — silent, or audio unavailable)")
out.append("")

sys.stdout.write("\n".join(out))
