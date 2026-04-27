# Stage 2 — Transcribe

Word-level timestamps drive cut points (stage 3) and subtitles (stage 6).

## Tool
`whisper-cli` (whisper-cpp, brew). Model: `ggml-base.en.bin` for speed, `ggml-large-v3.bin` for accuracy. Cache in `~/.cache/whisper/`.

## Steps

1. Extract audio from each staged clip:
   ```bash
   mkdir -p audio
   for f in staged/*.mp4; do
     name=$(basename "$f" .mp4)
     ffmpeg -i "$f" -ar 16000 -ac 1 -c:a pcm_s16le "audio/${name}.wav" -y
   done
   ```

2. Transcribe with word timestamps + JSON:
   ```bash
   for f in audio/*.wav; do
     name=$(basename "$f" .wav)
     whisper-cli -m ~/.cache/whisper/ggml-base.en.bin \
       -f "$f" -ml 1 -oj -of "audio/${name}" 2>/dev/null
   done
   ```
   `-ml 1` = max 1 word per segment → word-level. `-oj` = JSON output.

3. Combine into `transcript.json`:
   ```json
   {
     "clips": [
       {
         "id": "clip-01",
         "words": [
           {"t0": 0.12, "t1": 0.41, "w": "welcome"},
           {"t0": 0.42, "t1": 0.78, "w": "back"}
         ]
       }
     ]
   }
   ```

## Output
`transcript.json`, `audio/*.json` (per-clip whisper JSON).

## Pitfalls
- Whisper hallucinates on silence — drop segments with `confidence < -1.0` (whisper-cpp uses log-prob).
- `-ml 1` can split contractions awkwardly — leave for now, fix at subtitle render with regex.
- For non-English source, swap model to `ggml-base.bin` (multilingual) and pass `-l <lang>`.

## Filler-word detection (used by stage 3)

Mark these for removal candidates: `um`, `uh`, `umm`, `uhh`, `er`, `ah`, `like` (when standalone), `you know`, `I mean`. Also flag any word followed by > 0.6s gap before the next word — usually a stumble or retake.
