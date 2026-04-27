# Stage 7 — Composite + final render

Mux rough cut + overlays + subtitles + music into `final.mp4`.

## Inputs
- `rough-cut.mp4` (stage 4)
- `compositions/out/*.mov` + `overlays.json` (stage 5)
- `subtitles.srt` (stage 6)
- `raw/music.mp3` (optional)

## Composite overlays

Build a single ffmpeg filter graph. Example with 2 overlays:

```bash
ffmpeg \
  -i rough-cut.mp4 \
  -i compositions/out/lower-third-name.mov \
  -i compositions/out/callout-stat.mov \
  -filter_complex "
    [0:v][1:v] overlay=80:H-h-120:enable='between(t,1.5,5.0)' [v1];
    [v1][2:v] overlay=(W-w)/2:200:enable='between(t,12.0,16.5)' [vout]
  " \
  -map "[vout]" -map 0:a \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  composited.mp4 -y
```

Generate the filter_complex programmatically from `overlays.json`.

## Add music (ducked under VO)

```bash
ffmpeg -i composited.mp4 -i raw/music.mp3 \
  -filter_complex "
    [1:a] volume=0.25, aloop=loop=-1:size=2e9 [music];
    [0:a] [music] sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400 [aout]
  " \
  -map 0:v -map "[aout]" -shortest \
  -c:v copy -c:a aac -b:a 192k \
  with-music.mp4 -y
```

## Burn subtitles + final encode

```bash
ffmpeg -i with-music.mp4 \
  -vf "subtitles=subtitles.srt:force_style='Fontname=Inter,Fontsize=58,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=3,Outline=4,Alignment=2,MarginV=240'" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart \
  final.mp4 -y
```

`-movflags +faststart` puts moov atom at the front so it streams before fully downloaded. Mandatory for web upload.

## Thumbnail / poster

```bash
ffmpeg -ss 0.8 -i final.mp4 -frames:v 1 -q:v 2 thumbnail.jpg -y
```

## Verify

```bash
ffprobe -v error -of json -show_format -show_streams final.mp4 \
  | jq '{duration: .format.duration, size: .format.size, w: .streams[0].width, h: .streams[0].height, fps: .streams[0].r_frame_rate}'
```
Expect: 1080×1920, 30/1 fps, duration ≈ target, size < 100 MB.

## Output
`final.mp4`, `thumbnail.jpg`, `subtitles.srt` (sidecar copy).

## Pitfalls
- `pix_fmt yuv420p` is mandatory for QuickTime/iOS/web. Forget it and Safari shows a black frame.
- Sidechain compression duck depth too aggressive (ratio>10) sounds pumpy. Stick to 6–8.
- Subtitles burned BEFORE overlay composite means overlays render on top of subtitles — usually wrong. Burn last.
- IG Reel hard cap: 90s. TikTok: 10min. Validate before upload.
