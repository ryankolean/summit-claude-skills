---
name: cli-yt-dlp
description: >
  Teach Claude how to use yt-dlp to download video, audio, captions, and metadata
  from YouTube, Instagram, TikTok, X, Loom and 1000+ other sites. Activates when
  the user wants to download or archive a video, rip audio from a URL, grab
  subtitles or a transcript, fetch a playlist or channel, or troubleshoot 403s,
  nsig errors, or login-walled content. For understanding what is *in* a video,
  use watch-video instead.
---

# yt-dlp — Media Acquisition

**Repo:** https://github.com/yt-dlp/yt-dlp

Fork of youtube-dl with far better extractor coverage and maintenance. Pairs with
ffmpeg for merging, remuxing, and post-processing.

## When to Activate

- "Download this video / rip the audio / save this reel"
- "Get me the transcript/captions for this URL"
- "Grab this whole playlist / channel"
- 403s, nsig extraction failures, cookie or login-wall problems

**Not** for video comprehension — that's the `watch-video` skill.

## Metadata First

Always inspect before downloading. Costs nothing, avoids surprises.

```bash
yt-dlp --skip-download --print "%(title)s | %(duration)s s | %(resolution)s" URL
yt-dlp -F URL                                    # list every available format
yt-dlp --skip-download --write-info-json -o "%(title)s.%(ext)s" URL
```

## Format Selection

```bash
yt-dlp URL                                       # best available, auto-merged
yt-dlp -f 'bv*[height<=1080]+ba/b[height<=1080]' URL   # cap at 1080p
yt-dlp -f 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]' URL    # force mp4/m4a
yt-dlp -f 'ba' URL                               # audio stream only
yt-dlp -S 'res:720,fps,codec:h264' URL           # sort preferences instead of filtering
```

`bv*`=best video, `ba`=best audio, `b`=best pre-merged. The `/` separated groups are
fallbacks, tried left to right. Merging needs ffmpeg on PATH.

## Audio Extraction

```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 URL      # best-quality mp3
yt-dlp -x --audio-format m4a URL                        # m4a, usually no re-encode
yt-dlp -x --audio-format wav --postprocessor-args "-ac 1 -ar 16000" URL   # whisper-ready
```

## Captions and Transcripts

```bash
yt-dlp --list-subs URL                           # what's actually available
yt-dlp --skip-download --write-subs --sub-langs en --convert-subs srt URL
yt-dlp --skip-download --write-auto-subs --sub-langs en --convert-subs srt URL
yt-dlp --embed-subs --sub-langs en URL           # burn into the container
```

Request **exact** language codes. A wildcard like `--sub-langs "en.*"` pulls every
auto-translated track (`en-ar`, `en-zh`, …) and reliably triggers HTTP 429.

## Partial Downloads

```bash
yt-dlp --download-sections "*90-150" URL         # seconds 90–150 only
yt-dlp --download-sections "*1:30-2:30" URL      # same, timestamps
```

Adding `--force-keyframes-at-cuts` gives exact cut points but forces a re-encode
(roughly 2× slower). Skip it unless frame-exact boundaries matter.

## Playlists and Channels

```bash
yt-dlp --no-playlist URL                         # single video from a playlist URL
yt-dlp -I 1:10 PLAYLIST_URL                      # items 1–10
yt-dlp --dateafter 20260101 CHANNEL_URL          # only recent uploads
yt-dlp -o "%(playlist_index)02d - %(title)s.%(ext)s" PLAYLIST_URL
yt-dlp --download-archive done.txt PLAYLIST_URL  # resumable, skips completed items
```

## Login-Walled Content

```bash
yt-dlp --cookies-from-browser chrome URL         # chrome|safari|firefox|edge|brave
yt-dlp --cookies cookies.txt URL                 # Netscape-format cookie file
```

Instagram reels, private/members content, and age-gated videos need this. Close the
browser first if cookie extraction fails on a locked database. Never commit a cookie
file — it is a live session credential.

## Output Templates

```bash
yt-dlp -o "~/Videos/%(uploader)s/%(upload_date)s - %(title)s.%(ext)s" URL
yt-dlp -o "%(id)s.%(ext)s" URL                   # stable, filesystem-safe
yt-dlp --restrict-filenames URL                  # ASCII only, no spaces
```

## Post-Processing

```bash
yt-dlp --remux-video mp4 URL                     # change container, no re-encode
yt-dlp --recode-video mp4 URL                    # re-encode (slow)
yt-dlp --embed-thumbnail --embed-metadata URL
yt-dlp --split-chapters URL
```

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| HTTP 403, nsig extraction failed, signature errors | Stale yt-dlp. `brew upgrade yt-dlp` — YouTube breaks extractors constantly |
| "ffmpeg not found" / only single stream downloads | ffmpeg missing or broken; verify with `ffmpeg -version` |
| HTTP 429 | Too many parallel requests, usually from wildcard `--sub-langs`. Narrow it, or add `--sleep-requests 1` |
| Login required / empty result on Instagram | Needs `--cookies-from-browser` |
| "CURRENTLY BROKEN" extractor | Upstream regression — `instagram:user` and several `tiktok:*` bulk extractors. Use single post URLs |
| Sectioned download 403s | Older yt-dlp hands unusable CDN URLs to ffmpeg. Upgrade, or download in full |

Check version age first on any failure: `yt-dlp --version`. Anything older than about
a month is the prime suspect.

## Install / Update

```bash
brew install yt-dlp          # also: brew upgrade yt-dlp
yt-dlp -U                    # only for standalone-binary installs, not brew
```
