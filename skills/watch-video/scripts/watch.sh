#!/usr/bin/env bash
# watch.sh — turn a video (URL or local file) into frames + a timestamped
# transcript that Claude can read. Prints a manifest path on stdout.
set -euo pipefail

usage() {
  cat <<'USAGE'
usage: watch.sh <url|path> [options]

  --mode M          transcript | efficient | balanced | focused   (default: balanced)
  --start TS        window start (seconds or HH:MM:SS), implies focused
  --end TS          window end
  --frames N        hard cap on frame count (default: mode-dependent)
  --width N         longest side in px (default: 768, ocr: 1024)
  --ocr             grayscale + contrast + sharpen, for on-screen text
  --cookies-browser B   chrome|safari|firefox — for login-walled reels/TikTok
  --lang L          whisper language (default: en)
  --model M         whisper model: name (small.en, medium.en) or full path
  --prompt TEXT     bias whisper toward these terms; "" disables the default
  --out DIR         work directory (default: ~/.cache/claude-watch/<slug>)
  --keep            reuse existing work directory instead of rebuilding
USAGE
}

[ $# -ge 1 ] || { usage; exit 1; }

SRC="$1"; shift
MODE=balanced START="" END="" CAP="" WIDTH="" OCR=0 COOKIES="" LANG=en OUT="" KEEP=0
MODEL_ARG=""
# whisper mishears technical proper nouns badly; seeding its vocabulary fixes them
PROMPT="Claude, Claude Code, Anthropic, Vercel, GitHub, Supabase, Oura ring, API, repo, TypeScript."

while [ $# -gt 0 ]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --start) START="$2"; MODE=focused; shift 2 ;;
    --end) END="$2"; MODE=focused; shift 2 ;;
    --frames) CAP="$2"; shift 2 ;;
    --width) WIDTH="$2"; shift 2 ;;
    --ocr) OCR=1; shift ;;
    --cookies-browser) COOKIES="$2"; shift 2 ;;
    --lang) LANG="$2"; shift 2 ;;
    --model) MODEL_ARG="$2"; shift 2 ;;
    --prompt) PROMPT="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --keep) KEEP=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
done

[ -n "$WIDTH" ] || { [ "$OCR" = 1 ] && WIDTH=1024 || WIDTH=768; }
case "$MODE" in
  transcript) : ;;
  efficient)  [ -n "$CAP" ] || CAP=50 ;;
  balanced)   [ -n "$CAP" ] || CAP=60 ;;
  focused)    [ -n "$CAP" ] || CAP=120 ;;
  *) echo "bad --mode: $MODE" >&2; exit 1 ;;
esac

for bin in ffmpeg ffprobe; do
  command -v "$bin" >/dev/null || { echo "missing dependency: $bin" >&2; exit 1; }
done

slug=$(printf '%s' "$SRC" | shasum | cut -c1-10)
base=$(basename "$SRC" | tr -cd '[:alnum:]._-' | cut -c1-40)
WD="${OUT:-$HOME/.cache/claude-watch/${base:-video}-$slug}"
[ "$KEEP" = 1 ] || rm -rf "$WD"
mkdir -p "$WD/frames"

# ---------------------------------------------------------------- acquire
YTDLP_COMMON=(--no-warnings --no-playlist --no-progress --quiet)
LOG="$WD/ytdlp.log"
dl() { # run yt-dlp quietly; dump the log only if it fails
  if ! yt-dlp "$@" >>"$LOG" 2>&1; then
    echo "yt-dlp failed:" >&2; tail -20 "$LOG" >&2; return 1
  fi
}
[ -n "$COOKIES" ] && YTDLP_COMMON+=(--cookies-from-browser "$COOKIES")

to_sec() { # HH:MM:SS | MM:SS | SS -> seconds
  awk -F: '{n=NF; s=0; for(i=1;i<=n;i++) s=s*60+$i; printf "%d", s}' <<<"$1"
}
REQ_START=""; REQ_END=""; OFFSET=0; SECTIONED=0; CAPTIONS=0
[ -n "$START" ] && REQ_START=$(to_sec "$START")
[ -n "$END" ] && REQ_END=$(to_sec "$END")

VIDEO=""
if [ -f "$SRC" ]; then
  ext="${SRC##*.}"
  ln -sf "$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")" "$WD/src.$ext"
  VIDEO="$WD/src.$ext"
  TITLE=$(basename "$SRC")
else
  command -v yt-dlp >/dev/null || { echo "missing dependency: yt-dlp" >&2; exit 1; }
  TITLE=$(yt-dlp "${YTDLP_COMMON[@]}" --skip-download --print '%(title)s' "$SRC" 2>/dev/null | tail -1)

  # Captions first: free, instant, no video bytes.
  dl "${YTDLP_COMMON[@]}" --skip-download --write-subs --write-auto-subs \
    --sub-langs "${LANG},${LANG}-orig,${LANG}-US" --convert-subs srt \
    -o "$WD/cap.%(ext)s" "$SRC" 2>/dev/null || true
  cap_srt=$(find "$WD" -maxdepth 1 -name 'cap*.srt' | head -1)
  if [ -n "$cap_srt" ]; then
    mv "$cap_srt" "$WD/transcript.srt"
  else
    cap_vtt=$(find "$WD" -maxdepth 1 -name 'cap*.vtt' | head -1)
    [ -n "$cap_vtt" ] && ffmpeg -v error -y -i "$cap_vtt" "$WD/transcript.srt" 2>/dev/null || true
  fi
  [ -s "$WD/transcript.srt" ] && CAPTIONS=1 || rm -f "$WD/transcript.srt"

  if [ "$MODE" = transcript ] && [ -f "$WD/transcript.srt" ]; then
    :   # captions covered it — no download at all
  elif [ "$MODE" = transcript ]; then
    dl "${YTDLP_COMMON[@]}" -f 'ba/b' -o "$WD/audio.%(ext)s" "$SRC"
    VIDEO=$(find "$WD" -maxdepth 1 -name 'audio.*' | head -1)
  else
    DL_EXTRA=""
    if [ -n "$REQ_START" ] && [ -n "$REQ_END" ]; then
      DL_EXTRA="--download-sections *${REQ_START}-${REQ_END}"
      SECTIONED=1; OFFSET="$REQ_START"
    fi
    # OCR needs every pixel available; otherwise 720p keeps downloads small
    FMT='bv*[height<=720]+ba/b[height<=720]/bv*+ba/b'
    [ "$OCR" = 1 ] && FMT='bv*+ba/b'
    dl "${YTDLP_COMMON[@]}" $DL_EXTRA -f "$FMT" \
      -o "$WD/video.%(ext)s" "$SRC"
    VIDEO=$(find "$WD" -maxdepth 1 -name 'video.*' | head -1)
  fi
fi
[ -n "$TITLE" ] || TITLE=$(basename "$SRC")

DUR=0
if [ -n "$VIDEO" ]; then
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO" | cut -d. -f1)
  [ -n "$DUR" ] && [ "$DUR" -gt 0 ] 2>/dev/null || DUR=0
fi

W_START=0; W_END="$DUR"
if [ "$SECTIONED" = 0 ]; then
  [ -n "$REQ_START" ] && W_START="$REQ_START"
  [ -n "$REQ_END" ] && W_END="$REQ_END"
fi
[ "$W_END" -gt "$W_START" ] 2>/dev/null || W_END="$DUR"
SPAN=$((W_END - W_START))

# ------------------------------------------------------------- transcript
if [ ! -f "$WD/transcript.srt" ] && [ -n "$VIDEO" ]; then
  # small.en first: with the vocabulary prompt it matches medium.en at half the runtime
  MODEL="${MODEL_ARG:-${WHISPER_MODEL:-}}"
  case "$MODEL" in
    "") for m in small.en medium.en base.en tiny.en; do
          [ -f "$HOME/.cache/whisper/ggml-$m.bin" ] && MODEL="$HOME/.cache/whisper/ggml-$m.bin" && break
        done ;;
    */*) : ;;                                        # explicit path
    *) MODEL="$HOME/.cache/whisper/ggml-${MODEL%.bin}.bin" ;;
  esac
  HAS_AUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$VIDEO" | head -1)
  if [ -z "$HAS_AUDIO" ]; then
    echo "note: no audio track — visual only" >&2
  elif command -v whisper-cli >/dev/null && [ -f "$MODEL" ]; then
    ffmpeg -v error -y -i "$VIDEO" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$WD/audio.wav" || true
    whisper-cli -m "$MODEL" -f "$WD/audio.wav" -l "$LANG" \
      ${PROMPT:+--prompt "$PROMPT" --carry-initial-prompt} \
      -osrt -of "$WD/transcript" -np >/dev/null 2>&1 || echo "warn: whisper failed" >&2
    rm -f "$WD/audio.wav"
  else
    echo "warn: no captions and whisper-cli/model unavailable — visual only" >&2
  fi
fi

# SRT -> [MM:SS] text
if [ -f "$WD/transcript.srt" ]; then
  SRT_OFFSET=$([ "$CAPTIONS" = 1 ] && echo 0 || echo "$OFFSET")
  python3 "$(dirname "$0")/srt2txt.py" "$WD/transcript.srt" "$SRT_OFFSET" > "$WD/transcript.txt" || true
  [ -s "$WD/transcript.txt" ] || rm -f "$WD/transcript.txt"   # silent clip
fi

# ----------------------------------------------------------------- frames
VF="scale='if(gt(iw,ih),${WIDTH},-2)':'if(gt(iw,ih),-2,${WIDTH})'"
[ "$OCR" = 1 ] && VF="format=gray,eq=contrast=1.35,${VF},unsharp=5:5:1.1"

fmt_ts() { awk -v s="$1" -v o="$OFFSET" 'BEGIN{s+=o; printf "%02d-%02d", int(s/60), int(s%60)}'; }

TIMES=""
if [ "$MODE" != transcript ] && [ -n "$VIDEO" ] && [ "$DUR" -gt 0 ]; then
  SCENE_FILE=""
  if [ "$MODE" = balanced ]; then
    ffprobe -v error -f lavfi -i "movie=${VIDEO},select=gt(scene\,0.28)" \
      -show_entries frame=pts_time -of csv=p=0 2>/dev/null \
      | tr -d ',' | grep -E '^[0-9.]+$' > "$WD/scenes.txt" || true
    [ -s "$WD/scenes.txt" ] && SCENE_FILE="$WD/scenes.txt"
  fi
  TIMES=$(python3 "$(dirname "$0")/pick_times.py" "$W_START" "$W_END" "$CAP" "$MODE" $SCENE_FILE)

  i=0
  while read -r t; do
    [ -n "$t" ] || continue
    i=$((i+1))
    out="$WD/frames/$(printf '%03d' "$i")_t$(fmt_ts "$t").jpg"
    ffmpeg -v error -y -ss "$t" -i "$VIDEO" -frames:v 1 -vf "$VF" -q:v 3 "$out" </dev/null || true
  done <<< "$TIMES"
fi

# --------------------------------------------------------------- manifest
FRAMES=$(find "$WD/frames" -name '*.jpg' | sort)
NFRAMES=$(printf '%s\n' "$FRAMES" | grep -c . || true)
EST=0
if [ "${NFRAMES:-0}" -gt 0 ]; then
  first=$(printf '%s\n' "$FRAMES" | head -1)
  dims=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$first")
  EST=$(awk -F, -v n="$NFRAMES" '{printf "%d", $1*$2/750*n}' <<<"$dims")
fi

{
  echo "# Watch manifest: $TITLE"
  echo
  echo "- source: \`$SRC\`"
  echo "- duration: $([ "$SECTIONED" = 1 ] && echo "${DUR}s (section)" || echo "${DUR}s") | window: $((W_START+OFFSET))s-$((W_END+OFFSET))s | mode: $MODE"
  echo "- frames: ${NFRAMES:-0} | est. image tokens: ~${EST}"
  [ -f "$WD/transcript.txt" ] && echo "- transcript: \`$WD/transcript.txt\`" || echo "- transcript: none (visual only)"
  echo
  if [ "${NFRAMES:-0}" -gt 0 ]; then
    echo "## Frames (read every one, in order)"
    echo
    printf '%s\n' "$FRAMES" | while read -r f; do
      ts=$(basename "$f" | sed -E 's/^[0-9]+_t([0-9]{2})-([0-9]{2})\.jpg/\1:\2/')
      echo "- t=$ts — \`$f\`"
    done
    echo
  fi
  if [ -f "$WD/transcript.txt" ]; then
    echo "## Transcript"
    echo
    echo '```'
    cat "$WD/transcript.txt"
    echo '```'
  fi
} > "$WD/MANIFEST.md"

echo "$WD/MANIFEST.md"
