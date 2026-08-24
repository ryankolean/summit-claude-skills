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

| Flag | Purpose |
|---|---|
| `--limit N` | Max posts per run (default 20). Rerun to continue |
| `--sleep N` | Seconds between fetches (default 4). Do not lower it |
| `--mode balanced` | Also extract frames — for visual/design saves |
| `--all` (parser) | Ignore state and re-emit everything |

Posts that are private, deleted, or rate-limited are staged with
`status: unavailable` rather than silently dropped. Report them; don't retry in a loop.

## Classification — the two axes

Every save gets both. `idea_type` says what it is (mindspace's existing enum);
`disposition` says what happens to it. Disposition is the axis that decides where a
card lands and when it is done.

| disposition | idea_type | Destination | Done when |
|---|---|---|---|
| `queue` | `build` | mindspace `inbox/` | Card carries a concrete first step |
| `evaluate` | `try` | mindspace card, tool named in the title | Tool installed and kept, or rejected with a reason |
| `adopt` | `read` | A CLAUDE.md rule or a skill — **not** a card | Rule text merged, or explicitly declined |
| `reconstruct` | `research` | mindspace card with a research task | Claim independently verified or disproved |
| `reference` | `explore` | mindspace card **with frames** | Retrievable when building something similar |
| `intel` | `research` | mindspace card scoped to summit / rare-find | Insight recorded against a specific offer |
| `personal` | any | mindspace `project: personal` + `subcategory` | Filed under its topic |
| `expired` | — | `archive/YYYY-MM/`, no card | Marked processed, never resurfaces |

### Precedence ladder

Many saves match several shapes, so order decides. **First match wins:**

1. `personal` — non-work topic, whatever collection Instagram put it in. Instagram
   collections are assigned loosely; a hand-massage reel filed under "Interesting
   knowledge" is still personal. Judge the content, never the collection name.
2. `expired` — names a superseded tool or model, or `saved_at` is older than 18
   months and the content is a tool list. Evergreen technique never expires on age
   alone.
3. `adopt` — the transcript is self-contained and it changes how you work.
4. `evaluate` — names a specific installable tool, repo, or MCP server.
5. `queue` — describes a concrete buildable artifact.
6. `intel` — pricing, offers, positioning, business model.
7. `reference` — the value is visual.
8. `reconstruct` — gated, and the payload is genuinely absent from the transcript.

### Never trade a DM for the answer

Roughly a quarter of work-flavored saves are lead magnets: "comment X and I'll send
it." Do **not** DM for these, and do not create a chase list.

`reconstruct` means: capture the *claim* the reel makes, then run it through our own
research and evaluation. The reel is a prompt for investigation, not a source. The
card records what was claimed, what we verified independently, and the verdict. If a
technique is worth having, we can derive it — and we end up understanding it rather
than owning someone's PDF.

`reconstruct` sits last on the ladder on purpose. A gated reel that explains its
technique fully in the transcript is `adopt` or `evaluate`; the gate is irrelevant
when the substance is already there. Only reels where the payload truly never
arrives fall through.

### Personal subcategories

`personal` saves carry a `subcategory` drawn from the topic, not from the Instagram
collection name (those are inconsistent — "food", "Food", and "Food N Stuff" are the
same thing). Normalize to: `food`, `drinks`, `home`, `garden`, `travel`, `health`,
`relationships`, `gifts`, `pets`, `games`, `kids`, `style`, `finance`, `career`,
`misc`.

`finance` and `career` cover personal money and personal job-search material —
debt mechanics, asset protection, job-market reality. They are personal even when
Instagram filed them under a business collection, and they are not `intel`: `intel`
is only for material that informs a Summit or Rare Find offer.

### Thin transcripts

About a quarter of reels carry their meaning on screen rather than in speech. Two
distinct failure shapes, both measured on a real batch (35 of 124):

- **Thin** — transcript under 30 words. The caption usually carries the meaning.
- **Music-only** — whisper faithfully transcribes the backing track, so the card
  reads as song lyrics. Detect it: three or more of `yeah|oh oh|la la|baby|woah`
  in a transcript under 120 words. The transcript is worse than useless here
  because it looks like content while saying nothing about the reel.

Never classify a music-only reel from its transcript. Re-run it with
`--mode balanced` and read the frames, or leave it unclassified. Anything heading
for `reference` needs the frames pass regardless — that disposition is defined by
visual value, so a transcript-only `reference` card is empty by construction.

### Dedupe on content, not just shortcode

The same reel gets reposted by different accounts, so `state.json` (keyed on
shortcode) will not catch it. Before creating cards, fingerprint the first ~25 words
of each transcript and collapse matches — one card, with the other URLs listed as
alternate sources. Measured rate on the first batch: 1 duplicate pair in 124, which
scales to a meaningful number across ~1,100 saves.

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
