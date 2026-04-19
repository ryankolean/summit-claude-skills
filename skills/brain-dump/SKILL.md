---
name: brain-dump
description: Capture, structure, and organize ideas from any source (URLs, screenshots, text, voice transcripts, calendar inbox events, iOS Shortcut payloads) into the ryankolean/mindspace GitHub repo. Classifies along two axes (project + idea-type) with emergent tags, auto-schedules High-priority items via Google Calendar reminder-hub conventions, and self-improves by appending to learnings.md after every session. Activates on "brain dump", "capture this", "add to mindspace", "process my inbox", "mindspace review", "what did I capture about X", or when the user shares a URL/screenshot/idea fragment without explicit instructions.
---

# brain-dump

Living capture-and-organize system. Turns scattered inputs (saved tweets, screenshots, half-formed thoughts, articles, voice memos) into structured, scheduleable, searchable knowledge in `ryankolean/mindspace`.

## Operating modes

The skill runs in one of six modes. Identify the mode from the user's intent before executing.

| Mode | Trigger | Output |
|---|---|---|
| **capture** | User shares a single item or batch with no other instruction | Structured idea card(s) in `inbox/` or `library/`, optional Calendar event |
| **triage** | "Process my inbox", "triage mindspace", "clear the inbox" | All inbox items moved to `library/` or `archive/` with classification |
| **review** | "Mindspace review", "what's stale", "what haven't I actioned" | Surface stale items, prompt revisit/archive/escalate |
| **search** | "What did I capture about X", "find ideas on Y" | Filtered list from `index.json` + grep across `library/` |
| **research** | "research backfill", "research today", "research card X", "research refresh X" | Append `## Research` block to one or more cards; commit + push |
| **self-learn** | End of every session OR user says "promote learnings" | Append to `_meta/learnings.md`; if high-value pattern, prompt SKILL.md update |

## Bootstrap (first-time setup)

If the repo doesn't exist yet, run the `gh-repo-create` skill with these parameters: name `mindspace`, visibility `private`, description `Personal idea capture and triage system. Managed by the brain-dump skill.` Then push the contents of `mindspace-init/` (provided alongside this skill) as the initial commit.

## Capture mode — execution rules

1. **Identify input type.** URL, image (screenshot/photo), plain text, voice transcript, calendar inbox event, iOS Shortcut payload, file attachment, or "other." If multiple items in one batch, process each independently then summarize at the end.

2. **Extract content.**
   - URLs: `web_fetch` the page. If the URL is a social media post (X/Twitter, LinkedIn, Reddit, HN, YouTube), extract the post body, author, and key replies. Note the platform.
   - Images: describe the visible content. If the screenshot contains text, transcribe it. If it's a UI/product screenshot, identify the product and the feature shown.
   - Voice transcripts: split into discrete ideas if the transcript covers multiple topics. One idea = one card.
   - Calendar inbox events (`[Inbox] ...`): pull title + description, treat description as the idea body.

3. **Propose classification** — present this block to the user for approval before writing:

   ```
   Title: <concise, action-flavored, ≤12 words>
   Project: <one of: summit | dtst | carrot-hire | stockx | rare-find | healthspan | personal | NEW: ...>
   Idea-type: <one of: build | research | buy | read | watch | try | explore | NEW: ...>
   Tags: [<2-5 emergent tags, lowercase, hyphenated>]
   Priority: <high | medium | low>
   Suggested action: <single sentence, action verb first>
   Suggested schedule: <ISO date or "no schedule">
   Destination: <inbox | library/{project}/{idea-type}>
   ```

4. **Honor user adjustments.** If user edits any field, use the edited version. If user says "looks good" or just confirms, proceed.

5. **Write the idea card** using the template at `templates/idea-card.md`. File naming: `YYYY-MM-DD-HHMM-{slug}.md` where slug is 3-5 words from the title, lowercase, hyphenated. Commit message: `capture: {title}`.

6. **Calendar policy.**
   - Priority **High** → auto-create event via reminder-hub conventions (no confirmation). Title format: `[{Project}] {Title}`. Description includes the suggested action, link to the idea card in mindspace, `Priority: High`, `Project: {project}`, `Category: {idea-type}`.
   - Priority **Medium** or **Low** → present the proposed event to the user, ask "Schedule this? (y/n/edit)" before creating.
   - Priority **Low** with no clear action → no calendar event, just store in library.

7. **Update `_meta/index.json`** with the new entry. Update `_meta/patterns.json` with any new tags (increment frequency counter; if new tag, add with frequency 1).

## Triage mode — execution rules

1. List every file in `inbox/`. If empty, report "Inbox is clear" and exit.
2. For each item, present a one-line summary + proposed classification (same block as capture step 3, condensed). Allow batch operations: "Approve all," "Skip 3," "Archive 5," etc.
3. Move approved items to `library/{project}/{idea-type}/`. Archive killed items to `archive/{YYYY-MM}/`. Apply scheduling policy from capture step 6.
4. Commit in batches: one commit per project triaged. Commit message: `triage: process N inbox items into {project}`.

## Review mode — execution rules

1. Read `_meta/index.json`. Identify items in `library/` with `status: library` and `captured` older than 14 days with no `last_touched` field.
2. Group by project. Present each group with: title, idea-type, age, suggested next move (revisit / archive / escalate to High).
3. Apply user decisions. Update `last_touched` on revisited items; archive killed items; for escalations, run the calendar policy from capture step 6.
4. Commit message: `review: triage N stale items`.

## Search mode — execution rules

1. Parse the user's query for: project filter, idea-type filter, tag filter, free-text terms.
2. Filter `_meta/index.json` first (fast path).
3. If query needs body content, grep through matching files in `library/`.
4. Return ranked results: title, project/type, captured date, one-line summary, file path.
5. If user wants to act on a result, jump into capture-style classification on that existing card to update/reschedule.

## Research mode — execution rules

1. Determine scope from invocation:
   - "backfill" → all cards in `_meta/index.json` without a `<!-- research: -->` block
   - "today" / "tomorrow's tasks" → cards where `suggested_schedule` matches the requested day
   - "refresh <id>" → that one card; override staleness check
   - "card <id>" → that one card; respect staleness
2. For each card in scope, check the body for an existing `<!-- research: ISO_TIMESTAMP -->` marker:
   - Absent → process
   - Present and timestamp ≥ 4 days ago → process (replace block atomically)
   - Present and timestamp < 4 days ago → skip silently (unless invocation is `refresh`)
3. Dispatch one research subagent per card in parallel batches of 5. See `references/research-protocol.md` for the per-card algorithm and `templates/research-block.md` for the output format.
4. After each subagent returns its block, locate the card markdown file. If the file already has a `<!-- research:` block, replace from `<!-- research:` through `<!-- /research -->` (DOTALL match). Otherwise append a blank line then the new block at end of file.
5. Run `./viewer/build.sh` once at the end to regenerate `viewer/index.html`.
6. Commit: `research: enrich N cards`. Stage all touched cards plus `viewer/index.html`. Push.

## Self-learn protocol

**After every session that wrote, moved, or archived files**, before responding "done," do this:

1. Append a dated entry to `_meta/learnings.md` covering:
   - What inputs were processed
   - Any classification decisions that felt forced or ambiguous
   - New tags added to `patterns.json`
   - Calendar events created
   - Anything the user corrected (this is the most valuable signal)

2. Scan recent learnings for **high-value patterns**:
   - Same correction made 3+ times → propose SKILL.md update
   - New tag promoted to top-10 frequency → propose adding to taxonomy.md
   - Recurring source type not yet handled (e.g. "I keep getting Substack URLs and you don't extract author bylines") → propose new extraction rule
   - User-defined shortcut or convention used 2+ times → propose codifying

3. **If a high-value pattern is detected**, end the session by asking: "I noticed {pattern}. Should I promote this into SKILL.md as a permanent rule? (yes / no / edit my proposal: ...)" Wait for response. If yes, edit SKILL.md with a clearly marked block:

   ```
   <!-- learned: YYYY-MM-DD -->
   {new rule}
   <!-- /learned -->
   ```

   Then commit to `summit-claude-skills` with message: `brain-dump: promote learning — {brief description}`.

4. **Rebuild the viewer.** If `viewer/build.sh` exists in the mindspace repo root, run `./viewer/build.sh` and stage the regenerated `viewer/index.html`. This keeps the baked HTML snapshot in sync with the cards that just landed. If `viewer/` doesn't exist in this repo, skip silently (backward-compatible).

5. Commit the session's final state (learnings.md update + viewer rebuild if applicable) with message: `learn: session {YYYY-MM-DD HHMM}`.

## Integration points

- **reminder-hub**: scheduled events follow `[Project] Task title` convention with `Priority: X\nProject: X\nCategory: X` in description. See `references/integrations.md`.
- **GitHub**: all writes go through `gh` CLI or the GitHub API. PAT required for push from container; `git format-patch` + `git am` is the documented fallback per CLAUDE.md conventions.
- **iOS Shortcut**: `references/integrations.md` includes the shortcut blueprint for share-sheet capture from mobile.
- **Voice mode**: when user dictates "brain dump" + ramble, treat the transcript as input. Split on topic shifts. One idea per card.
- **Calendar inbox**: any event titled `[Inbox] *` is pulled into mindspace on the next session that runs in capture or triage mode.
- **Viewer**: `viewer/index.html` is a self-contained baked HTML snapshot of the brain dump (timeline / kanban / tag-network views). Regenerated by `viewer/build.sh` at session end (see self-learn protocol step 4). Spec: `docs/superpowers/specs/2026-04-18-mindspace-viewer-design.md`.

## Output discipline

- No emojis (per Ryan's standing preference).
- Idea card titles: action-flavored, no clickbait, ≤12 words.
- Summaries: 2-3 sentences. Not copies of the source — distillation in Ryan's voice.
- Tags: lowercase, hyphenated, max 5 per card. Prefer reusing existing tags from `patterns.json`.
- Commit messages: lowercase prefix (`capture:`, `triage:`, `review:`, `learn:`), past-tense not required, one line preferred.

## Reference files

- `references/taxonomy.md` — current project + idea-type definitions
- `references/capture-flow.md` — detailed step-by-step for each input type
- `references/integrations.md` — reminder-hub format, iOS Shortcut spec, voice mode
- `references/research-protocol.md` — per-card research algorithm: phases, budgets, failure modes, worked example
- `references/self-learning-protocol.md` — full pattern detection rules and SKILL.md edit conventions
- `templates/idea-card.md` — frontmatter + body template
- `templates/learnings-entry.md` — learnings.md append template
- `templates/research-block.md` — research output template appended to card bodies

## Hard constraints

- Never auto-create a calendar event for Medium or Low priority items without confirmation.
- Never modify SKILL.md without explicit user approval (the self-learn promotion always asks first).
- Never delete from `library/` — only move to `archive/`.
- Never commit to mindspace without writing to `_meta/index.json` in the same commit.
- Always run `viewer/build.sh` (if present) before the final session commit, so the baked HTML snapshot stays in lockstep with the data.
- Never run research on a card whose existing `<!-- research: -->` block is < 4 days old, except when invoked explicitly as `research refresh <id>`.
