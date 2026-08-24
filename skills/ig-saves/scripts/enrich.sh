#!/usr/bin/env bash
# enrich.sh — turn parse_export.py output into staged capture files.
# Reads JSONL on stdin, writes ~/.cache/ig-saves/pending/<shortcode>.md
set -euo pipefail

# resolve watch-video: a sibling checkout first, then the installed skill
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
WATCH=""
for cand in "$SELF_DIR/../../watch-video/scripts/watch.sh" \
            "$HOME/.claude/skills/watch-video/scripts/watch.sh"; do
  if [ -x "$cand" ]; then WATCH="$cand"; break; fi
done
[ -n "$WATCH" ] || WATCH="$HOME/.claude/skills/watch-video/scripts/watch.sh"
PENDING="$HOME/.cache/ig-saves/pending"
LIMIT=20
SLEEP=4
MODE=transcript

while [ $# -gt 0 ]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --sleep) SLEEP="$2"; shift 2 ;;
    --mode)  MODE="$2"; shift 2 ;;          # transcript (default) or balanced for frames
    --pending) PENDING="$2"; shift 2 ;;
    -h|--help) sed -n '2,4p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$PENDING"
[ -x "$WATCH" ] || { echo "watch-video skill not found at $WATCH" >&2; exit 1; }

n=0; ok=0; failed=0
while IFS= read -r line; do
  [ -n "$line" ] || continue
  [ "$n" -ge "$LIMIT" ] && { echo "note: stopped at --limit $LIMIT; rerun to continue" >&2; break; }
  n=$((n+1))

  eval "$(printf '%s' "$line" | python3 -c '
import json, shlex, sys
d = json.load(sys.stdin)
for k in ("shortcode", "url", "author", "collection"):
    print(f"{k.upper()}={shlex.quote(str(d.get(k) or ""))}")
ts = d.get("saved_at")
if ts:
    import datetime
    print("SAVED_AT=" + shlex.quote(
        datetime.datetime.fromtimestamp(int(ts)).astimezone().isoformat(timespec="seconds")))
else:
    print("SAVED_AT=")
')"

  out="$PENDING/$SHORTCODE.md"
  [ -f "$out" ] && { echo "skip $SHORTCODE (already staged)" >&2; continue; }

  # public metadata via a single JSON dump — captions are multi-line, so
  # tab-delimited --print output cannot be parsed reliably
  meta_json=$(yt-dlp --no-warnings --quiet --no-progress --skip-download --no-playlist \
                -J "$URL" 2>/dev/null || true)
  if [ -z "$meta_json" ]; then
    echo "unavailable: $SHORTCODE ($URL) — private, deleted, or rate-limited" >&2
    failed=$((failed+1))
    printf -- '---\nshortcode: %s\nurl: %s\nauthor: %s\ncollection: %s\nsaved_at: %s\nstatus: unavailable\n---\n\nCould not fetch. Private, deleted, or rate-limited.\n' \
      "$SHORTCODE" "$URL" "$AUTHOR" "${COLLECTION:-null}" "${SAVED_AT:-null}" > "$out"
    sleep "$SLEEP"
    continue
  fi
  caption=$(printf '%s' "$meta_json" | python3 -c 'import json,sys; print((json.load(sys.stdin).get("description") or "").strip())')
  duration=$(printf '%s' "$meta_json" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("duration") or "")')

  manifest=$("$WATCH" "$URL" --mode "$MODE" --out "$HOME/.cache/ig-saves/media/$SHORTCODE" 2>/dev/null | tail -1 || true)
  transcript=""
  [ -n "$manifest" ] && [ -f "$(dirname "$manifest")/transcript.txt" ] \
    && transcript=$(cat "$(dirname "$manifest")/transcript.txt")
  # Instagram rarely reports duration in metadata; the manifest probed the file
  if [ -z "$duration" ] && [ -n "$manifest" ] && [ -f "$manifest" ]; then
    duration=$(sed -n 's/^- duration: \([0-9]*\)s.*/\1/p' "$manifest" | head -1)
  fi

  {
    echo "---"
    echo "shortcode: $SHORTCODE"
    echo "url: $URL"
    echo "author: $AUTHOR"
    echo "collection: ${COLLECTION:-null}"
    echo "saved_at: ${SAVED_AT:-null}"
    echo "duration_s: ${duration:-null}"
    echo "manifest: ${manifest:-null}"
    echo "status: enriched"
    echo "---"
    echo
    echo "## Caption"
    echo
    printf '%s\n' "$caption"
    echo
    echo "## Transcript"
    echo
    if [ -n "$transcript" ]; then printf '%s\n' "$transcript"; else echo "(none — silent, or audio unavailable)"; fi
  } > "$out"

  ok=$((ok+1))
  echo "staged $SHORTCODE (@$AUTHOR)" >&2
  sleep "$SLEEP"
done

echo "enriched: $ok  unavailable: $failed  -> $PENDING" >&2
