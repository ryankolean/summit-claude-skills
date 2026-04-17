# Self-learning protocol

The brain-dump skill writes to `_meta/learnings.md` after every session and proposes SKILL.md promotions when high-value patterns emerge.

## What gets logged after every session

Append a dated entry to `_meta/learnings.md` covering:

- **Session ID**: `YYYY-MM-DD-HHMM`
- **Mode(s)**: capture, triage, review, search
- **Items processed**: count + brief list (titles)
- **Classification corrections**: every time the user changed a project, idea-type, priority, or tag from what the skill proposed. Format: `proposed → accepted`.
- **New tags added**: tags that didn't exist in `patterns.json` before this session
- **New projects/types proposed**: any user-approved additions to taxonomy
- **Calendar events created**: count + High vs. Medium vs. Low breakdown
- **Friction notes**: anything that felt clunky, ambiguous, or required re-work
- **Source-type observations**: any pattern about how a particular source (e.g. Substack, X threads, dental industry blogs) was handled

Use the template at `templates/learnings-entry.md`.

## High-value pattern detection

Scan recent learnings (last 30 entries or 30 days, whichever is greater). A pattern is **high-value** if any of these conditions hold:

### Pattern 1: Repeated correction
Same correction applied 3+ times across sessions. Examples:
- Skill proposes `medium` priority, user changes to `high` for items tagged `summit`
- Skill puts Substack content in `personal/read`, user moves to `summit/research`
- Skill suggests 30-min calendar duration, user always extends to 60-min

**Promotion proposal**: codify the corrected behavior as the new default.

### Pattern 2: Tag promotion
A tag in `patterns.json` crosses **frequency 10**.

**Promotion proposal**: consider adding as a sub-axis or first-class field in taxonomy.md. Example: if `llm-evals` reaches 12, propose adding as a sub-category under `research`.

### Pattern 3: Recurring source not handled well
Same source type (publication, platform, app) shows up 3+ times with friction notes about extraction.

**Promotion proposal**: add a new section to `references/capture-flow.md` for that source.

### Pattern 4: User-defined convention
User uses the same custom phrase or shortcut 2+ times that isn't in SKILL.md. Examples:
- "Action this for next Tuesday" → user has a recurring pattern Claude should learn
- "Tag this with the dental thing" → user has shorthand for a tag cluster

**Promotion proposal**: add the phrase to a "user shorthand" section in SKILL.md.

### Pattern 5: New mode emergence
User asks for something the existing 5 modes don't cover, 2+ times. Examples:
- "Show me everything I captured this week" → digest mode
- "Merge these three ideas into one" → merge mode

**Promotion proposal**: propose a new mode with execution rules.

## How to propose a promotion

At session end, if a high-value pattern is detected:

1. Phrase the proposal as a single, concrete change. Not "Should I improve handling of Substack?" — instead: "I noticed Substack bylines were missed 3 times in a row. Should I add a Substack-specific extraction rule that checks for the byline class `.publication-logo + a` before falling back to generic byline extraction? (yes / no / edit)"

2. If user says **yes**: edit the relevant file (SKILL.md, taxonomy.md, capture-flow.md, etc.) with a clearly marked block:
   ```
   <!-- learned: YYYY-MM-DD -->
   {new content}
   <!-- /learned -->
   ```
   Commit to `summit-claude-skills` repo with message: `brain-dump: promote learning — {brief description}`.

3. If user says **edit**: incorporate their change, then proceed as yes.

4. If user says **no**: log the rejection in learnings.md so the same proposal isn't surfaced again immediately.

## Learnings.md retention

Don't truncate learnings.md — it's the long-term memory of the skill. If file size becomes an issue (>500KB), the next promotion proposal should include archiving older learnings to `_meta/archive/learnings-{YYYY-Q}.md`.

## Hard constraint

Never edit SKILL.md or any reference file without explicit user approval. The promotion proposal is always a **question**, not an action.
