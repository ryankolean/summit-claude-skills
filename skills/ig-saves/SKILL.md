---
name: ig-saves
description: >
  Turn Instagram saved posts into mindspace idea cards, then into content angles.
  Parses saves out of Instagram's official data export, enriches each one with its
  caption plus a watch-video transcript, and stages them for triage into
  ~/mindspace. Activates when the user says "process my Instagram saves", "ingest
  my saves export", "what did I save on Instagram", or asks to turn a saved reel
  into content ideas or hooks.
---

# Instagram Saves → mindspace

Two phases, deliberately separate: **ingest** is mechanical (scripts), **triage** is
judgment (you). Never let a script author an idea card — project, tags, and framing
are decisions, not fields.

## Why the export, not a cookie daemon

Instagram has no official saved-posts API. Every "auto-sync my saves" tool drives the
private web API with a session cookie lifted from DevTools, which violates Instagram's
ToS and risks the account — instagrapi's maintainers call it "fragile in production."
The official export carries the same saves with no such risk. The trade is a manual
request every week or two instead of a cron job. That trade was made deliberately;
do not quietly "improve" this by adding cookie auth.

## Phase 1 — Ingest

**Requesting the export** (the user does this; ~15 min to 48 h to arrive):
Instagram → Accounts Center → Your information and permissions → Download your
information → **JSON** format → Saved posts. The download link expires after 4 days.

Then:

```bash
# 1. Parse new saves out of the export (zip or unzipped dir)
python3 ~/.claude/skills/ig-saves/scripts/parse_export.py ~/Downloads/instagram-export.zip \
  > /tmp/saves.jsonl

# 2. Enrich each with caption + transcript (rate-limited on purpose)
bash ~/.claude/skills/ig-saves/scripts/enrich.sh --limit 20 < /tmp/saves.jsonl
```

Staged files land in `~/.cache/ig-saves/pending/<shortcode>.md` — frontmatter plus
caption and transcript. State lives in `~/.cache/ig-saves/state.json`; a save already
staged is skipped, and one already processed is never re-emitted.

The export itself carries the caption, author, hashtags, brand partner and collection
membership, so the only network call per save is the transcript fetch. Records also
survive captions containing newlines, quotes and emoji: `enrich.sh` hands each record
to `stage_card.py` as a file rather than shell-expanding it.

Real exports use a newer layout than most published parsers describe — a flat list of
records with `label_values`, where the author lives in a nested `Owner` block. The
parser handles that and the legacy `saved_saved_media` shape. Two decoding traps it
already handles: most captions are UTF-8 reinterpreted as latin-1 (repaired only when
the tell-tale markers appear), and `U+2028`/`U+2029`/`U+0085` are escaped on output
because Python's `splitlines()` treats them as line breaks and would split a JSONL
record in half.

| Flag | Purpose |
|---|---|
| `--limit N` | Max posts per run (default 20). Rerun to continue |
| `--sleep N` | Seconds between fetches (default 4). Do not lower it |
| `--mode balanced` | Also extract frames — for visual/design saves |
| `--all` (parser) | Ignore state and re-emit everything |

Posts that are private, deleted, or rate-limited are staged with
`status: unavailable` rather than silently dropped. Report them; don't retry in a loop.

## Phase 2 — Triage into mindspace

Read `~/mindspace/AGENTS.md` and `_meta/schema.md` first — they are authoritative and
they change. Then for each staged file:

1. Read the caption and transcript. For a visual/design save, or when the transcript
   is thin, read the frames from its `manifest:` path — the reel's *look* is often
   the point, and text alone will miss it.
2. Decide `project`, `idea_type`, `tags`, `priority`, and `suggested_action`. Ask
   when a save is genuinely ambiguous rather than guessing a project.
3. Write the card to `~/mindspace/inbox/` as `YYYY-MM-DD-HHMM-{slug}.md`, matching the
   schema exactly: `source: social`, `source_platform: instagram`,
   `source_author: <handle>`, `source_url: <post url>`.
4. Put the faithful source material under `## Context / source` — quote the caption and
   the transcript lines that carry the idea. That section is evidence, not summary.
5. Update `_meta/index.json`. Commit with a `capture:` prefix. No emojis.
6. Close the loop — never hand-edit the state JSON:

```bash
python3 ~/.claude/skills/ig-saves/scripts/mark_processed.py <shortcode> [<shortcode> ...]
python3 ~/.claude/skills/ig-saves/scripts/mark_processed.py --list   # what is still staged
```

`priority: high` auto-creates a Google Calendar event — be deliberate.

## Phase 3 — Content angles (on request only)

When the user asks for angles on a card, append a block to the existing card rather
than rewriting it, mirroring the `<!-- research: ... -->` convention already in use:

```
<!-- angles: 2026-08-23T14:00:00-04:00 -->
## Content angles
### Hooks
- three variations, each a different emotional entry point
### Outline
Hook -> key points -> CTA
### Platform notes
- Instagram / TikTok / YouTube differences worth the reshoot
<!-- /angles -->
```

Ground every angle in what the source actually did — cite timestamps from the
transcript. Generic hook templates are worthless; the value is in why *this* post
worked. Do not invent engagement numbers.

## Do not

- Do not add cookie-based or private-API fetching (see above)
- Do not write directly to `library/` — captures land in `inbox/` and get triaged
- Do not let a script generate card summaries, tags, or projects
- Do not batch more than ~20 posts per run; the sleep between fetches is deliberate

## Dependencies

`python3`, `yt-dlp`, and the `watch-video` skill (which brings ffmpeg + whisper).
