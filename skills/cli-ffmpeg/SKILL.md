---
name: cli-ffmpeg
description: >
  Covers effective use of FFmpeg for video/audio conversion,
  trimming, filtering, streaming, and multimedia processing. Activates when
  the user wants to convert media files, trim video, create GIFs, extract
  audio, add subtitles, encode for web, or do any audio/video manipulation.
---

# FFmpeg — Multimedia Framework

**Repo:** https://github.com/FFmpeg/FFmpeg

Complete multimedia framework for recording, converting, and streaming audio
and video. Supports hundreds of formats and codecs. The Swiss Army knife of
media processing.

## When to Activate

**Manual triggers:**
- "Convert this video to..."
- "Trim/clip this video"
- "Extract audio from video"
- "Create a GIF from video"
- "Compress this video"
- "Add subtitles"

**Auto-detect triggers:**
- User has a media file and wants to change its format, size, or content
- User mentions encoding, bitrate, codec, resolution, or framerate
- User wants to batch process video or audio files
- User needs to extract frames or create a thumbnail

## Key Commands

### Basic Conversion
```bash
ffmpeg -i input.mp4 output.mkv           # Convert container format
ffmpeg -i input.mov output.mp4           # MOV to MP4
ffmpeg -i input.mp4 -c copy output.mkv  # Copy streams (no re-encode, fast)
ffmpeg -i input.mp4 output.gif          # Video to GIF (basic)
```

### Inspect Media (ffprobe)
```bash
ffprobe input.mp4                                    # Basic info
ffprobe -v quiet -print_format json -show_streams input.mp4  # Full JSON info
ffprobe -v quiet -show_format input.mp4             # Container info only
```

### Codec Selection
```bash
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4   # H.264 video + AAC audio
ffmpeg -i input.mp4 -c:v libx265 -c:a aac output.mp4   # H.265/HEVC (smaller)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm  # VP9 + Opus (web)
ffmpeg -i input.mp4 -c:v copy -c:a mp3 output.mp4      # Re-encode audio only
```

### Trimming and Cutting
```bash
ffmpeg -i input.mp4 -ss 00:01:30 -t 00:00:30 output.mp4  # Start at 1:30, 30s duration
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:02:00 output.mp4 # Start at 1:30, end at 2:00
ffmpeg -ss 00:01:30 -i input.mp4 -t 30 output.mp4        # -ss before -i = faster seek
ffmpeg -i input.mp4 -ss 10 -to 40 -c copy output.mp4    # Keyframe-accurate, no re-encode
```

### Bitrate and Quality
```bash
ffmpeg -i input.mp4 -b:v 1M output.mp4              # 1 Mbps video bitrate
ffmpeg -i input.mp4 -crf 23 output.mp4              # CRF quality (0=lossless, 51=worst; 18-28 typical)
ffmpeg -i input.mp4 -b:a 128k output.mp3            # 128 kbps audio
ffmpeg -i input.mp4 -vn -b:a 192k output.mp3        # Extract audio at 192k
```

### Resolution and Framerate
```bash
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4   # Resize to 720p
ffmpeg -i input.mp4 -vf scale=1920:-1 output.mp4    # Width 1920, height auto
ffmpeg -i input.mp4 -vf scale=-1:720 output.mp4     # Height 720, width auto
ffmpeg -i input.mp4 -r 30 output.mp4                # Set framerate to 30fps
ffmpeg -i input.mp4 -r 24 -vf fps=24 output.mp4    # Force 24fps
```

### Stream Selection (-map)
```bash
ffmpeg -i input.mkv -map 0:v:0 -map 0:a:1 output.mp4  # First video, second audio
ffmpeg -i input.mkv -map 0 -map -0:s output.mp4        # All streams except subtitles
ffmpeg -i input.mkv -vn output.mp3                      # Audio only (-vn = no video)
ffmpeg -i input.mp4 -an output.mp4                      # Video only (-an = no audio)
```

## Advanced Patterns

### High-Quality GIF from Video
```bash
# Two-pass GIF: generate palette first, then encode
ffmpeg -i input.mp4 -ss 5 -t 4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i input.mp4 -i palette.png -ss 5 -t 4 \
  -filter_complex "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" output.gif
```

### Batch Conversion
```bash
# Convert all MKV files to MP4
for f in *.mkv; do ffmpeg -i "$f" -c:v libx264 -c:a aac "${f%.mkv}.mp4"; done

# With fd
fd -e mkv | while read f; do
  ffmpeg -i "$f" -c:v libx264 -c:a aac "${f%.mkv}.mp4"
done
```

### Video Concatenation
```bash
# Create a list file
printf "file '%s'\n" *.mp4 > filelist.txt
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# Concatenate with re-encoding (for different formats/codecs)
ffmpeg -i "concat:part1.ts|part2.ts" -c copy output.ts
```

### Video Filters (-vf)
```bash
ffmpeg -i input.mp4 -vf crop=640:480:100:50 output.mp4     # Crop: w:h:x:y
ffmpeg -i input.mp4 -vf rotate=PI/4 output.mp4              # Rotate 45 degrees
ffmpeg -i input.mp4 -vf transpose=1 output.mp4              # Rotate 90° clockwise
ffmpeg -i input.mp4 -vf hflip output.mp4                    # Horizontal flip
ffmpeg -i input.mp4 -vf vflip output.mp4                    # Vertical flip
ffmpeg -i input.mp4 -vf "eq=brightness=0.1:contrast=1.2" output.mp4  # Brightness/contrast
ffmpeg -i input.mp4 -vf unsharp output.mp4                  # Sharpen
ffmpeg -i input.mp4 -vf "hue=s=0" output.mp4               # Grayscale
```

### Add Text Overlay
```bash
ffmpeg -i input.mp4 -vf \
  "drawtext=text='Hello World':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-50" \
  output.mp4

# With timestamp
ffmpeg -i input.mp4 -vf \
  "drawtext=text='%{pts\:hms}':fontsize=24:fontcolor=white:x=10:y=10" \
  output.mp4
```

### Add Subtitles
```bash
ffmpeg -i input.mp4 -i subtitles.srt -c copy -c:s mov_text output.mp4   # Soft subtitles
ffmpeg -i input.mp4 -vf subtitles=subtitles.srt output.mp4              # Burn in subtitles
```

### Extract Frames / Create Thumbnails
```bash
ffmpeg -i input.mp4 -vf fps=1 frame_%04d.png         # 1 frame per second
ffmpeg -i input.mp4 -ss 00:01:00 -frames:v 1 thumb.jpg  # Single frame at 1:00
ffmpeg -i input.mp4 -vf "thumbnail,scale=320:-1" -frames:v 1 thumb.jpg  # Best thumbnail
```

### Thumbnail Sprite Sheet
```bash
ffmpeg -i input.mp4 -vf "fps=1/10,scale=160:-1,tile=5x5" sprite.jpg
```

### Audio Filters (-af)
```bash
ffmpeg -i input.mp3 -af "volume=2.0" output.mp3              # Double volume
ffmpeg -i input.mp3 -af "loudnorm" output.mp3                # Normalize loudness
ffmpeg -i input.mp3 -af "afade=t=in:st=0:d=3" output.mp3   # Fade in over 3s
ffmpeg -i input.mp3 -af "silenceremove=1:0:-50dB" output.mp3  # Remove silence
ffmpeg -i input.mp4 -af "equalizer=f=1000:width_type=o:width=2:g=10" output.mp4  # EQ boost
```

### Complex Filter Graph (-filter_complex)
```bash
# Overlay logo on video
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "overlay=W-w-10:H-h-10" \
  output.mp4

# Side-by-side video
ffmpeg -i left.mp4 -i right.mp4 \
  -filter_complex "[0:v][1:v]hstack=inputs=2[v];[0:a][1:a]amerge=inputs=2[a]" \
  -map "[v]" -map "[a]" output.mp4

# Picture-in-picture
ffmpeg -i main.mp4 -i overlay.mp4 \
  -filter_complex "[1:v]scale=320:180[pip];[0:v][pip]overlay=W-w-10:H-h-10" \
  output.mp4
```

### Screen Recording (macOS)
```bash
# List input devices
ffmpeg -f avfoundation -list_devices true -i ""

# Record screen + audio
ffmpeg -f avfoundation -i "1:0" -r 30 -c:v libx264 -preset ultrafast screen.mp4
```

### Streaming to RTMP
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset fast -b:v 3000k \
  -c:a aac -b:a 128k -f flv rtmp://live.twitch.tv/app/STREAM_KEY
```

### Hardware Acceleration
```bash
# macOS VideoToolbox
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v h264_videotoolbox output.mp4

# NVIDIA NVENC
ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc output.mp4

# Intel QSV
ffmpeg -hwaccel qsv -i input.mp4 -c:v h264_qsv output.mp4
```

### Compress for Web
```bash
# H.264, good quality, web-compatible
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium \
  -c:a aac -b:a 128k -movflags +faststart output.mp4

# VP9 for web (better compression, open codec)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 \
  -c:a libopus -b:a 96k output.webm
```

## Format Coverage

| Category | Formats |
|---|---|
| Video containers | MP4, MKV, WebM, AVI, MOV, TS, FLV, OGV |
| Video codecs | H.264, H.265/HEVC, VP8, VP9, AV1, MPEG-2, ProRes |
| Audio containers | MP3, AAC, FLAC, WAV, OGG, M4A, OPUS |
| Image sequences | PNG, JPEG, TIFF, BMP, WebP |
| Subtitles | SRT, ASS, WebVTT, MOV_TEXT |

## Chaining with Other Skills

- **cli-imagemagick:** Extract frames with FFmpeg (`-vf fps=1`), then batch-process them with ImageMagick (resize, watermark, color correct)
- **fd:** Use `fd -e mp4` to find all video files, pipe into a shell loop with FFmpeg for batch conversion
- **fzf (cli-fzf):** Use `fd -e mp4 | fzf` to interactively select a video file before running an FFmpeg command
