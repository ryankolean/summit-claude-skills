# Stage 4 — Assemble rough cut

Execute the EDL with ffmpeg.

## Input
`edl.json` (stage 3), `staged/*.mp4` (stage 1).

## Steps

1. Extract each cut as a separate file:
   ```bash
   mkdir -p cuts
   jq -c '.cuts[] | {clip,in,out,label}' edl.json | nl -ba | while read i line; do
     clip=$(echo "$line" | jq -r .clip)
     tin=$(echo "$line" | jq -r .in)
     tout=$(echo "$line" | jq -r .out)
     ffmpeg -ss "$tin" -to "$tout" -i "staged/${clip}.mp4" \
       -c:v libx264 -preset fast -crf 18 \
       -c:a aac -ar 48000 \
       -avoid_negative_ts make_zero \
       "cuts/$(printf %03d $i).mp4" -y
   done
   ```
   Note: `-ss` BEFORE `-i` would be faster but less accurate. Put after for frame-accurate cuts.

2. Build concat list:
   ```bash
   ls cuts/*.mp4 | sed "s|^|file '$(pwd)/|; s|$|'|" > cuts/concat.txt
   ```

3. Concat:
   ```bash
   ffmpeg -f concat -safe 0 -i cuts/concat.txt -c copy rough-cut.mp4 -y
   ```
   If concat copy fails (codec drift), re-encode: drop `-c copy`.

4. Verify duration matches `edl.json.estimated_duration` ± 0.5s:
   ```bash
   ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 rough-cut.mp4
   ```

## Output
`rough-cut.mp4`, `cuts/*.mp4`.

## Pitfalls
- `-c copy` concat fails silently if any cut has different codec params from the rest. If duration is off by > 1s, force re-encode.
- Phone footage with rotation metadata: pre-bake rotation in stage 1 (`-vf transpose=...`) or concat will misorient.
- Audio click at cut boundaries: add 20ms fade in/out per cut with `afade=t=in:d=0.02,afade=t=out:d=0.02:st=<dur-0.02>`.
