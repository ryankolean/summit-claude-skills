---
name: watch-video
description: >
  Let Claude actually watch a video or reel — downloads it, extracts timestamped
  frames, and produces a timestamped transcript, then reads the frames as images.
  Activates when the user shares a video/reel/short URL or local video file and
  asks what's in it, what someone said, to summarize it, find a moment, pull
  quotes, critique visuals, or extract on-screen text. Works with YouTube, TikTok,
  Instagram reels, X, Loom, and local .mp4/.mov/.mkv/.webm files.
---

# Watch Video

Claude cannot ingest video directly — only images and text. This skill converts a
video into both: **timestamped frames** (read as images) plus a **timestamped
transcript**. Reading them together is what "watching" means here.

## When to Activate

- User pastes a video URL and asks anything about its contents
- "What happens in this reel?" / "Summarize this video" / "What does he say at 2:30?"
- "Pull the on-screen text from this" / "What's the hook in the first 3 seconds?"
- User references a local video file and asks about its content

Do **not** activate for downloading only — that's `cli-yt-dlp`.

## Usage

```bash
bash ~/.claude/skills/watch-video/scripts/watch.sh <url|path> [options]
```

Prints one line: the path to `MANIFEST.md`. **Read that manifest, then read every
frame it lists, in order.** The manifest carries the transcript inline.

### Options

| Flag | Purpose |
|---|---|
| `--mode transcript` | Captions/transcript only, zero frames. Fastest — often no download at all |
| `--mode efficient` | Uniform sampling, cap 50 frames |
| `--mode balanced` | Scene-change detection, cap 60 frames (default) |
| `--start TS --end TS` | Focused window at 2fps; downloads only that section |
| `--frames N` | Override the frame cap |
| `--width N` | Longest side in px (default 768) |
| `--ocr` | Grayscale + contrast + sharpen at 1024px, for on-screen text |
| `--cookies-browser chrome` | Login-walled Instagram/TikTok content |
| `--lang xx` | Transcript language (default `en`) |
| `--model M` | Whisper model — name (`small.en`, `medium.en`) or full path |
| `--prompt "..."` | Bias whisper's vocabulary; `--prompt ""` disables the default |
| `--keep` | Reuse an existing work directory instead of rebuilding |

## Choosing a Mode

Cost is the frames, not the transcript. Claude image tokens ≈ `width × height / 750`.
At the 768px default each frame is ~440 tokens.

| Question type | Mode | ~Tokens |
|---|---|---|
| "What did they say?" | `transcript` | ~0 image tokens |
| "Summarize this 30s reel" | `balanced` | ~10–25k |
| "Find the moment X happens" | `transcript` first, then `--start/--end` around the hit | ~5k |
| "Read the text on screen" | `--ocr --frames 15` | ~15k |
| "Critique the edit/pacing" | `balanced --frames 60` | ~26k |

Default to `transcript` first on anything longer than ~5 minutes. Locate the moment
in text, then spend frames only on the window that matters.

## Workflow

1. Run the script. Note the reported frame count and token estimate.
2. If the estimate is over ~40k, rerun with a lower `--frames` or a focused window
   rather than reading it all.
3. Read `MANIFEST.md`.
4. Read every frame listed, in order. Frame filenames carry their source timestamp
   (`004_t03-31.jpg` = 3:31), so visual observations can be cited by time.
5. Answer from frames + transcript together. Cite timestamps.

## Instagram Reels and TikTok

Public posts usually work unauthenticated. Login-walled ones need browser cookies:

```bash
bash ~/.claude/skills/watch-video/scripts/watch.sh <reel-url> --cookies-browser chrome
```

Reels are portrait — the script caps the **longest** side, so a 9:16 frame lands at
432×768 (~440 tokens), not 768×1365. Short reels get dense coverage automatically
(~1 frame/1.5s under 60s).

`instagram:user` and several `tiktok:*` bulk extractors are marked broken upstream.
Single post/reel URLs are the reliable path.

## Transcript Sources

1. **Native captions** via yt-dlp — free, instant, no video download
2. **Local whisper.cpp** fallback — `whisper-cli` + a model from `~/.cache/whisper/`,
   runs offline, no API key

Installed: **small.en** (488MB, default) and medium.en (1.5GB). base.en was removed —
the vocabulary prompt made it redundant. Auto-select order is `small.en` >
`medium.en` > `base.en` > `tiny.en`, so dropping a smaller model back into
`~/.cache/whisper/` just works.

Whisper is seeded with a technical vocabulary prompt by default, which matters more
than model size. Measured on the same 67s reel:

| model | time | proper nouns |
|---|---|---|
| base.en, no prompt | 2.1s | "cloud", "inversal", "or ring" — all wrong (since removed) |
| small.en, no prompt | 4.2s | Claude right; Vercel and Oura still wrong |
| medium.en, no prompt | 9.2s | same as small.en — no gain for 2.2x the time |
| **small.en + prompt** | **4.2s** | **Claude, Vercel, Oura all correct** |
| medium.en + prompt | 8.2s | identical output to small.en + prompt |

So small.en is the default and medium.en is reserved for hard audio (heavy accents,
noise, crosstalk) — reach for it with `--model medium.en`, not by default. Extend the
vocabulary per job with `--prompt "Ledgr, EstateSync, Supabase, ..."`.

A silent clip yields no transcript file, and the manifest says "visual only" — that is
not an error.

## Dependencies

`ffmpeg`, `ffprobe`, `yt-dlp`, `python3`; `whisper-cli` only for the fallback path.

## Troubleshooting

- **HTTP 403 / nsig errors** — yt-dlp is stale. `brew upgrade yt-dlp`. YouTube breaks
  extractors constantly; anything older than ~a month is suspect.
- **Empty transcript** — no speech in the clip, or captions unavailable and whisper
  missing. Check the manifest's transcript line.
- **429 on captions** — the script requests only `en`/`en-orig`/`en-US`; broad
  wildcards trigger rate limits.
- **Work directory** — `~/.cache/claude-watch/<slug>/`. Delete freely; `--keep`
  reuses it to avoid re-downloading.
