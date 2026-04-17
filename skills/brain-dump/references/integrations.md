# Integrations

## reminder-hub (Google Calendar)

Calendar events created by brain-dump must follow Ryan's existing convention so they show up correctly in his Daily Review.

**Event title format**

```
[{Project}] {Title}
```

Examples:
- `[Summit] Draft Carrot Hire pricing page`
- `[Personal] Order replacement filter for espresso machine`
- `[Healthspan] Spike Oura sleep-stage import`

**Event description format**

```
{One-sentence action statement}

Source: mindspace/{path-to-card}.md
Idea card: https://github.com/ryankolean/mindspace/blob/main/library/{path}

Priority: {High|Medium|Low}
Project: {project-slug}
Category: {build|research|buy|read|watch|try|explore}
```

**Date logic**

- High priority: schedule for the next available weekday morning slot (default: 9:00 AM ET, 30-min duration). If user provides a specific date in the capture, use that.
- Medium priority: propose a date 7-14 days out, ask user to confirm or adjust.
- Low priority: only schedule if user explicitly requests; otherwise no event.

**All-day vs. timed**

- `read`, `watch`, `explore` types → all-day events (these don't need fixed time blocks)
- `build`, `research`, `try` → timed events with reasonable duration (30 min default for spikes, 90 min for deeper work)
- `buy` → all-day on the action date

## iOS Shortcut — share-sheet capture

Ryan can capture from anywhere on iOS by adding a share-sheet shortcut that POSTs directly to the mindspace repo.

**Shortcut blueprint** (build in iOS Shortcuts app):

1. **Receive**: URLs, Images, Text from share sheet
2. **Get current date**: format as `YYYY-MM-DD-HHMM`
3. **Text action**: build the markdown body:
   ```
   ---
   source: shortcut
   source_url: {{URL if present}}
   captured: {{ISO datetime}}
   status: inbox
   ---

   # Untriaged capture from {{date}}

   {{Shortcut Input}}
   ```
4. **Base64 encode** the text (GitHub API requires base64 for content).
5. **URL action**: `https://api.github.com/repos/ryankolean/mindspace/contents/inbox/{{date}}-shortcut.md`
6. **Get contents of URL**:
   - Method: PUT
   - Headers: `Authorization: Bearer {{your PAT}}`, `Accept: application/vnd.github+json`
   - Body (JSON):
     ```json
     {
       "message": "shortcut: capture from iOS",
       "content": "{{base64 body}}"
     }
     ```
7. **Show notification** on success/failure.

**PAT required**: a fine-grained personal access token with `Contents: write` permission scoped to `ryankolean/mindspace` only. Store in iOS Keychain via the Shortcut, never in plain text.

**Triage cadence**: items captured via shortcut land in `inbox/` and wait for the next `triage` mode session.

## Voice mode

When Ryan says "brain dump" followed by a verbal ramble (typically while commuting), the input arrives as a transcript.

**Splitting rules**

- Topic shifts ("anyway, another thing...", "oh, and...", "switching gears...") = card boundary
- Pauses transcribed as ellipses (...) within a topic = same card
- Explicit numbering ("first idea... second idea...") = card boundary

**Voice-mode card naming**: `YYYY-MM-DD-HHMM-voice-{n}-{slug}.md` where `{n}` is the sequence number within the ramble.

**Lightly clean transcript**: fix obvious word-recognition errors (e.g. "DTST" misheard as "detest"), but preserve Ryan's voice and phrasing. Don't over-edit.

## Calendar inbox

Any Google Calendar event titled with `[Inbox]` prefix is treated as a capture target.

**Detection**: at the start of any `capture` or `triage` mode session, search the user's primary calendar for events matching `[Inbox] *` from the last 30 days.

**Processing**: pull title and description, run capture flow, then delete the calendar event to prevent re-capture.

**Use case**: Ryan can add an `[Inbox]` event from any device that has Google Calendar (phone, laptop, watch) without needing the Claude app open.

## GitHub commits

All writes go through `gh` CLI when available, falling back to `git` + PAT.

**Container constraint**: per Ryan's CLAUDE.md, `git push` from container requires PAT. If PAT is unavailable, use `git format-patch` + ship the patch for Ryan to apply locally.

**Commit message conventions**

| Action | Prefix | Example |
|---|---|---|
| Capture single item | `capture:` | `capture: Substack post on RAG eval frameworks` |
| Triage inbox batch | `triage:` | `triage: process 7 inbox items into summit` |
| Review stale items | `review:` | `review: triage 12 stale items` |
| Self-learn append | `learn:` | `learn: session 2026-04-17-1430` |
| SKILL.md promotion | `promote:` | `promote: add Substack byline extraction rule` |

**Branch policy**: commit directly to `main`. This is a personal repo with single author. No PRs.
