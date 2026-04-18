---
name: chat-to-code-prompt
description: Package the relevant content from the current Claude.ai chat into a clipboard-ready, self-contained prompt for a fresh Claude Code session. Activates when the user says "chat-to-code-prompt", "send to Claude Code", "make a CC prompt", "package this for Claude Code", "handoff to CC", or any variant. Produces one of three formats — task, plan, or context — chosen by the user at activation. Output is a single fenced markdown block at the end of the response so it can be tap-and-hold copied on mobile.
---

# chat-to-code-prompt

## Purpose
Bridge the gap between a Claude.ai chat and Claude Code. Take whatever has been discussed, decided, or scoped in the current chat and convert it into a clean, self-contained prompt that a fresh Claude Code session can execute with zero additional context from the user.

The output is always a single fenced markdown block, ready to paste into a new Claude Code session.

## Activation
Triggered by any of:
- "chat-to-code-prompt"
- "send to Claude Code" / "send this to CC"
- "make a CC prompt" / "Claude Code prompt for this"
- "package this for Claude Code"
- "handoff to Claude Code" / "handoff to CC"
- "convert this to a Claude Code prompt"

## Execution

### Step 1 — Pick the format
Call `ask_user_input_v0` with a single question. Do not infer or skip — always ask.

Question: **"What kind of prompt am I packaging?"**
Options (single_select):
- "Task — build/fix/refactor"
- "Plan — implement this design"
- "Context — continue this work"

### Step 2 — Extract chat content
Pull only what's relevant to the chosen format:

- **Task:** action verb + deliverable, repo/branch, files involved, constraints, success criteria, notes
- **Plan:** plan name, repo, overview, phases, decisions already made, out of scope, definition of done
- **Context:** topic, repo, background, what's been done, current state, open questions, suggested next move

Do not invent files, paths, or facts. If the chat lacks a piece (e.g., no repo named), either omit the field, mark it `<TBD by Ryan>`, or use the most-recently-mentioned repo and flag the assumption above the code block.

### Step 3 — Apply Claude Code framing
- State the working directory / repo at the top of the prompt
- Reference any `CLAUDE.md` if it was mentioned in the chat
- Front-load the deliverable
- Use action verbs (Build, Fix, Refactor, Migrate, Implement, Continue)
- List constraints explicitly — CC will execute, not clarify
- Mention any tool conventions (e.g., `git format-patch` + `git am` fallback if push fails in the container)
- Strip all Claude.ai chat artifacts: no "as we discussed", "in our chat", "I mentioned earlier"
- Make the prompt 100% self-contained — assume the receiving CC session has zero memory of this chat

### Step 4 — Output
Above the code block, write 2–3 lines max:
- Format mode chosen
- One-line "paste into a fresh CC session in `<repo>`" instruction
- Any flagged assumptions

Then output the full prompt as a single fenced markdown block so it's tap-and-hold copyable on mobile.

After the block, optionally offer one follow-up: save to file, scaffold the target repo with `gh-repo-create`, or chain into `architect-plan-for-dispatch` if the scope is large.

## Templates

### Task
````markdown
# <Action verb + deliverable>

**Repo:** <repo>
**Branch:** <branch or "current">

## Context
<1–3 sentences of background — what and why>

## Goal
<one clear sentence>

## Files involved
- `path/to/file` — <what changes>
- ...

## Constraints
- <don't touch X>
- <follow CLAUDE.md / convention Y>

## Success criteria
- [ ] <observable outcome>
- [ ] <test passes>

## Notes
<anything else CC needs cold>
````

### Plan
````markdown
# Implement: <plan name>

**Repo:** <repo>
**Reference:** <CLAUDE.md / spec / link>

## Overview
<2–4 sentences>

## Phases
1. <Phase 1> — <what + why>
2. <Phase 2> — ...

## Decisions already made
- <decision> — <rationale>

## Out of scope
- <thing not to do>

## Definition of done
- [ ] <outcome>
- [ ] <outcome>
````

### Context handoff
````markdown
# Continue: <topic>

**Repo:** <repo or N/A>

## Background
<3–5 sentences on what was being worked on and why>

## What's been done
- ...

## Current state
- ...

## Open questions
- ...

## Suggested next move
<1–2 sentences>
````

## Rules
- **One fenced code block.** Always at the end of the response.
- **Self-contained.** Never reference "the chat" or "earlier" inside the prompt.
- **Never invent.** No fabricated files, paths, repos, or facts. Mark unknowns `<TBD by Ryan>`.
- **Push back on empty chats.** If there's nothing usable, ask what to package — don't generate filler.
- **Flag assumptions.** Default to the most-recently-mentioned repo only when obvious; call it out above the block.
- **No emojis.** Markdown headings, bullets, and checkboxes only.

## Chaining
- **Upstream:** Any chat — planning, debugging, scoping, design.
- **Downstream:** Pasted into Claude Code.
- **Adjacent:** `prompt-architect` for general-purpose Claude prompts; this skill is CC-specific and assumes an executing agent.
- **Composes with:** For very large multi-task bodies of work, prefer `architect-plan-for-dispatch` instead — it produces a structured execution file rather than a single prompt.

## Example

**User:** We've been scoping the DTST migration — let's pack this for CC.

**Claude:** [calls `ask_user_input_v0` with the format question]

**User:** Plan — implement this design

**Claude:**
Mode: Plan. Paste into a fresh Claude Code session opened in `~/code/dtst` (`ryankolean/dtst`). Assumed repo from chat — flag if wrong.

````markdown
# Implement: DTST migration from Tauri to local-first web app

**Repo:** ryankolean/dtst
**Reference:** CLAUDE.md, MIGRATION-EXECUTE.md (both at repo root)

## Overview
Migrate DTST from Tauri to a pure local-first web app. Stack: React 18 + Vite + TS + Tailwind + Zustand + TanStack Table + Recharts (frontend), Node/Express (backend). Backups live at `~/Library/Application Support/com.summitsoftware.dtst/backups/` and must remain readable.

## Phases
1. Scaffold Vite + React 18 + TS frontend — replace Tauri shell
2. Stand up Node/Express backend — local-only, no auth
3. ...

## Decisions already made
- Local-first only — no cloud sync in v1
- Keep existing JSON schema for backups — no migration needed

## Out of scope
- Multi-user
- Cloud deployment

## Definition of done
- [ ] `npm run dev` boots frontend + backend
- [ ] All 13 Dispatch tasks complete and committed
- [ ] Existing backups load cleanly
````

Want me to save this to a file or chain into `architect-plan-for-dispatch`?
