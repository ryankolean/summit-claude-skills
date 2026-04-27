# Stage 1 — Ingest

Normalize raw footage so downstream stages work on consistent inputs.

## Input
`raw/` directory with arbitrary clips (mov, mp4, mkv, webm). Optional `music.mp3`. Optional `brief.md`.

## Steps

1. Probe each clip:
   ```bash
   for f in raw/*.{mov,mp4,mkv}; do
     [ -e "$f" ] || continue
     ffprobe -v error -of json -show_format -show_streams "$f" > "${f}.probe.json"
   done
   ```

2. Decide canonical spec (default: 9:16 1080×1920 @ 30fps, H.264, AAC 48kHz stereo).

3. Normalize each clip to `staged/`:
   ```bash
   mkdir -p staged
   ffmpeg -i raw/clip-01.mov \
     -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30" \
     -c:v libx264 -preset medium -crf 18 \
     -c:a aac -ar 48000 -ac 2 -b:a 192k \
     staged/clip-01.mp4
   ```

4. Write `manifest.json`:
   ```json
   {
     "spec": {"w":1080,"h":1920,"fps":30,"vcodec":"h264","acodec":"aac"},
     "clips": [
       {"id":"clip-01","src":"staged/clip-01.mp4","duration":42.13,"orig":"raw/clip-01.mov"}
     ],
     "music": "raw/music.mp3"
   }
   ```

## Output
`staged/*.mp4`, `manifest.json`.

## Pitfalls
- VFR (variable frame rate) phone footage — always re-encode to CFR 30fps. Skipping this corrupts cut points.
- HDR clips — strip with `-vf zscale=t=linear:npl=100,zscale=p=bt709,format=yuv420p` before scale.
- Audio sample rate mismatch breaks concat — force 48kHz on every clip.
