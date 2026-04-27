# Stage 6 — Subtitles

Generate SRT from word-timestamped transcript. Optionally burn into video.

## Input
`transcript.json` (stage 2), `edl.json` (stage 3) for time remapping.

## Steps

1. Remap word timestamps from source-clip time to rough-cut time using EDL:
   - For each cut `c` in EDL, words inside `[c.in, c.out]` shift to `cumulative_offset + (word.t - c.in)`.
   - Words outside any cut are dropped.

2. Group words into subtitle lines:
   - Max 32 chars per line (IG Reel safe).
   - Max 2 lines per cue.
   - New cue on punctuation OR > 0.5s gap OR line-length cap.
   - Cue duration: `last_word.t1 - first_word.t0`, clamped to [1.0s, 4.0s].

3. Write `subtitles.srt`:
   ```
   1
   00:00:00,120 --> 00:00:02,840
   Claude can now edit
   entire videos for you.

   2
   00:00:02,900 --> 00:00:05,310
   It just took raw footage
   and turned it into this.
   ```

4. (Optional) Burn into video — see stage 7. For sidecar use case (YouTube, IG auto-captions), ship `subtitles.srt` alongside `final.mp4`.

## Style burn-in (ffmpeg `subtitles` filter)

```bash
ffmpeg -i rough-cut.mp4 \
  -vf "subtitles=subtitles.srt:force_style='Fontname=Inter,Fontsize=58,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=3,Outline=4,Shadow=0,Alignment=2,MarginV=240'" \
  -c:a copy subtitled.mp4 -y
```
- `Alignment=2` = bottom-center. `MarginV` = pixels from bottom.
- For IG/TikTok kinetic captions (highlighted current word), generate ASS instead of SRT and use `\k` karaoke timing tags.

## Pitfalls
- SRT `-->` is literal arrow + spaces — no unicode dash.
- Subtitle drift after stage 4 concat is the #1 bug. Always remap from EDL, never trust source-clip timestamps.
- Burn-in is destructive. Keep an un-subtitled master.
- Emoji and special chars need a font that has them — Inter doesn't ship emoji glyphs. Fall back to system emoji font via `fontconfig`.
