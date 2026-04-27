---
name: summit-video-pipeline
description: Claude-Code-only video editing pipeline. Turns raw footage + a one-line prompt into a fully edited short-form video with motion graphics, subtitles, and music — without Premiere, DaVinci, or CapCut. Stack: HeyGen HyperFrames (HTML→video render engine, headless Chromium + paused GSAP), browser-use/video-use Claude skill, and nateherkai/hyperframes-student-kit reference workbench. Reverse-engineered from @cooper.simson IG reel (DXiyhqIjn_n). Activate when user says "edit this video", "cut the umms", "make a reel", "add motion graphics", "render the final cut", or hands over raw footage + a brief.
---

# summit-video-pipeline

End-to-end video editing pipeline driven by Claude Code + CLI tools only. No GUI editor in the loop.

## When to use

- User has raw footage (one or more clips) and wants a finished short-form video.
- User wants filler removed (umms, ahs, dead air, retakes).
- User wants motion graphics, lower-thirds, captions, b-roll cuts, or animated overlays.
- User wants the entire edit driven by a single prompt or short brief.

If the task is purely a render of an existing edit, skip stages 1–4 and jump to stage 7.

## Upstream stack (install once)

| Component | Repo | Role |
|---|---|---|
| HyperFrames | `https://github.com/heygen-com/hyperframes` | HTML→video render engine. Headless Chromium + paused GSAP timeline. Apache-2.0. NOT Remotion. |
| video-use skill | `https://github.com/browser-use/video-use` | Claude Code skill (`SKILL.md` + `skills/manim-video/`) that teaches Claude to drive HyperFrames + Manim. |
| Student kit | `https://github.com/nateherkai/hyperframes-student-kit` | Reference workbench: brand system, audio sync, render pipeline, sample compositions. |

Prereqs: Node 20+, FFmpeg, headless Chrome/Chromium, ~5 GB free disk, 16 GB RAM recommended. Run `npx hyperframes doctor` after install.

## CLI tools used

- `ffmpeg` — cut, concat, mux, encode, scale, audio extract.
- `whisper-cli` (whisper-cpp) — transcript + word-level timestamps for cut points and subtitles.
- `npx hyperframes` — HTML→video renderer.
- `manim` (optional, via video-use skill) — programmatic 2D math/diagram animations.
- `yt-dlp` — pull reference footage if needed.
- `imagemagick` — thumbnail/poster generation.

## Pipeline stages

Each stage lives in `references/`. Load only the stages needed for the current task.

| # | Stage | File | Output |
|---|---|---|---|
| 1 | Ingest | `references/stage-1-ingest.md` | Normalized clips, manifest |
| 2 | Transcribe | `references/stage-2-transcribe.md` | Word-timestamped transcript |
| 3 | Cut script | `references/stage-3-cut-script.md` | EDL (cut list) JSON |
| 4 | Assemble | `references/stage-4-assemble.md` | Rough cut MP4 |
| 5 | Motion graphics | `references/stage-5-motion-graphics.md` | HyperFrames HTML compositions → MP4 overlays |
| 6 | Subtitles | `references/stage-6-subtitles.md` | Burned-in or sidecar SRT |
| 7 | Composite + render | `references/stage-7-composite-render.md` | Final MP4 |

## System flow (full pipeline)

```
raw/                        # user drops footage here
  clip-01.mov
  clip-02.mov
  music.mp3 (optional)
brief.md                    # one paragraph: hook, audience, key points, length, vibe
```

1. **Ingest** — normalize fps/resolution/codec, write `manifest.json`.
2. **Transcribe** — whisper-cli over each clip → `transcript.json` w/ word timestamps.
3. **Cut script** — Claude reads transcript + brief, produces `edl.json` (in/out points per clip, ordering, intentional pauses).
4. **Assemble** — ffmpeg concat from EDL → `rough-cut.mp4`.
5. **Motion graphics** — Claude writes HTML/CSS/GSAP compositions in `compositions/`, renders each via `npx hyperframes render` → transparent-background MP4s.
6. **Subtitles** — whisper word timestamps → SRT, optional burn-in via ffmpeg `subtitles=` filter.
7. **Composite + render** — ffmpeg overlay compositions on rough cut, mux audio (music ducked under VO), encode H.264 9:16 1080×1920 → `final.mp4`.

## Operator prompt template

```
Role: Edit this video as a Claude-Code-driven editor using summit-video-pipeline.
Context: [project, audience, platform — e.g. Summit IG Reels]
Objective: [one sentence, e.g. "60s reel teaching Freedom at 45 mini-app"]
Inputs: raw/ + brief.md
Constraints: [length, aspect, vibe, brand colors, no music / music track]
Output: final.mp4 + subtitle.srt + thumbnail.jpg
```

## Single-stage shortcuts

- "transcribe this" → stage 2 only.
- "cut the umms out" → stages 2 + 3 + 4.
- "add a lower-third saying X at 0:12" → stage 5 only.
- "burn captions in" → stage 6 only.
- "render the final" → stage 7 only.

## Quality gates

Before marking done:
- [ ] `final.mp4` plays end-to-end with no black frames or audio dropouts.
- [ ] Subtitle drift ≤ 200ms vs spoken word at any point.
- [ ] Output matches target aspect (9:16 default) — verify `ffprobe`.
- [ ] No watermarks from upstream tools.
- [ ] File size reasonable for platform (< 100 MB for IG Reel).

## Provenance

Reverse-engineered 2026-04-27 from @cooper.simson IG reel `DXiyhqIjn_n`. Cooper's caption: "What took 2 hours in Premiere and a team of experts now takes 10 mins." Cooper explicitly contrasts this with Remotion ("too limited"). HyperFrames is HeyGen's open-source successor approach — HTML/CSS/GSAP + headless Chromium.
