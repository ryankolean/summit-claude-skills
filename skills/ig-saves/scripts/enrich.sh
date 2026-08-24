#!/usr/bin/env bash
# enrich.sh — turn parse_export.py output into staged capture files.
# Reads JSONL on stdin, writes ~/.cache/ig-saves/pending/<shortcode>.md
#
# Caption, author, hashtags and collections come from the export itself, so the
# only network call per save is the transcript fetch.
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
MEDIA="$HOME/.cache/ig-saves/media"
LIMIT=20
SLEEP=4
MODE=transcript

while [ $# -gt 0 ]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --sleep) SLEEP="$2"; shift 2 ;;
    --mode)  MODE="$2"; shift 2 ;;          # transcript (default) or balanced for frames
    --pending) PENDING="$2"; shift 2 ;;
    --media) MEDIA="$2"; shift 2 ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$PENDING" "$MEDIA"
[ -x "$WATCH" ] || { echo "watch-video skill not found at $WATCH" >&2; exit 1; }

n=0; ok=0; failed=0; skipped=0
while IFS= read -r line; do
  [ -n "$line" ] || continue
  [ "$n" -ge "$LIMIT" ] && { echo "note: stopped at --limit $LIMIT; rerun to continue" >&2; break; }
  n=$((n+1))

  # one temp file per record keeps captions with newlines out of the shell
  rec="$PENDING/.record.json"
  printf '%s' "$line" > "$rec"
  SHORTCODE=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["shortcode"])' "$rec")
  URL=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["url"])' "$rec")

  out="$PENDING/$SHORTCODE.md"
  if [ -f "$out" ]; then
    skipped=$((skipped+1))
    continue
  fi

  manifest=$("$WATCH" "$URL" --mode "$MODE" --out "$MEDIA/$SHORTCODE" 2>/dev/null | tail -1 || true)
  transcript_file=""
  if [ -n "$manifest" ] && [ -f "$(dirname "$manifest")/transcript.txt" ]; then
    transcript_file="$(dirname "$manifest")/transcript.txt"
  fi

  if [ -z "$manifest" ]; then
    failed=$((failed+1))
    status=unavailable
  else
    ok=$((ok+1))
    status=enriched
  fi

  MANIFEST="$manifest" TRANSCRIPT="$transcript_file" STATUS="$status" \
    python3 "$SELF_DIR/stage_card.py" "$rec" > "$out"

  echo "$status $SHORTCODE" >&2
  sleep "$SLEEP"
done
rm -f "$PENDING/.record.json"

echo "enriched: $ok  unavailable: $failed  already staged: $skipped  -> $PENDING" >&2
