---
name: context-summary
description: Pack the active tasking of the current Claude.ai chat into a clipboard-ready, token-efficient summary for handoff to a fresh Claude.ai session. Captures only what's needed to continue the active work, know the next action, and know when the work is complete — nothing archival, nothing conversational. Activates when the user says "context summary", "context-summary", "pack the context", "pack this context", "fresh context handoff", "context handoff", "summarize this session", "wrap this for a new chat", or any variant. Output is a single fenced markdown block at the end of the response so it can be tap-and-hold copied on mobile.
---

# context-summary

## Purpose
Let Ryan clear the context window and start a fresh Claude.ai chat without burning tokens rebuilding state. Take the active tasking of the current chat — what's being worked on, what's decided, what's next, how we know we're done — and pack it into a self-contained brief that a fresh Claude instance can pick up cold.

The output is always a single fenced markdown block, ready to paste into a new Claude.ai chat.

## Activation
Triggered by any of:
- "context summary" / "context-summary"
- "pack the context" / "pack this context"
- "fresh context handoff" / "context handoff"
- "summarize this session" / "summarize this session for a fresh context"
- "wrap this for a new chat" / "wrap this up for fresh context"
- "clear context — give me the handoff"

## Execution

### Step 1 — Identify the active tasking
Scan the chat and find the *single active thread of work* — the thing Ryan is currently trying to move forward. Ignore:
- Tangents that didn't pan out
- Background already captured in `userMemories` (unless actively relevant to the next step)
- Fully-resolved questions with no downstream impact
- Conversational filler

If there are multiple active threads, pick the most recent one and flag the others under "Other open threads" at the bottom.

### Step 2 — Extract only what the next session needs
For the active tasking, pull:
- **What** — 1–3 sentences on what's being worked on and why
- **State** — what's done, what's in progress, what's blocked
- **Decisions / constraints** — choices already made that affect continuation (stack, approach, scope boundaries)
- **Artifacts produced this session** — filenames/paths/refs, not full content (unless small and critical)
- **Next action** — the single immediate next step
- **Completion criteria** — how we know the active tasking is done
- **After completion** — what comes next, or "session complete"

Do not invent files, paths, repos, or facts. Mark unknowns `<TBD>`.

### Step 3 — Strip chat artifacts
- No "as we discussed", "earlier in this chat", "I mentioned above"
- No narrative transitions
- No restating userMemories content
- Assume the receiving session has zero memory of this chat

### Step 4 — Output
Above the code block, write 1–2 lines max:
- "Paste into a fresh Claude.ai chat to continue"
- Any flagged assumptions (e.g., "assumed repo: ryankolean/dtst")

Then output the full summary as a single fenced markdown block.

After the block, optionally offer: chain into `chat-to-code-prompt` if the next action is code execution, or `workflow-lock` if the session revealed a repeatable pattern worth templating.

## Template

````markdown
# Context Summary — <active tasking title>

**Project:** <Summit / DTST / Rare Find / Healthspan / StockX / Personal / etc.>
**Repo / location:** <if applicable, else omit>

## Active Tasking
<1–3 sentences on what's being worked on and why>

## State
- **Done:** <what's complete>
- **In progress:** <what's partially done>
- **Blocked on:** <blocker, or "nothing">

## Key decisions / constraints
- <decision or constraint> — <implication for continuation>

## Artifacts produced this session
- `<filename or ref>` — <what it is, where it lives>

## Next action
<the single immediate next step — one sentence>

## Completion criteria
- [ ] <observable outcome>
- [ ] <observable outcome>

## After completion
<what comes next, or "session complete">

## Other open threads (if any)
- <thread> — <1-line status>
````

## Rules
- **One fenced code block.** Always at the end of the response.
- **Task-completion oriented.** The summary exists to let the next session finish the active tasking and know it's done — not to archive the full chat.
- **Token-efficient.** No filler. If a field is empty, omit it entirely. Brevity over completeness.
- **Self-contained.** A fresh Claude instance with no memory of this chat should be able to continue from the summary alone.
- **Reference artifacts, don't inline them.** Filenames and paths, not full contents — unless the artifact is small (< ~20 lines) and critical to the next action.
- **Never invent.** Mark unknowns `<TBD>`.
- **No emojis.** Markdown headings, bullets, checkboxes only.
- **Don't restate userMemories.** Ryan's persistent context is already loaded in every session. Only include memory-adjacent facts if they are actively relevant to the next step.
- **Push back on empty chats.** If there's no active tasking worth packing, say so and ask what to summarize — don't generate filler.

## Chaining
- **Upstream:** Any active working chat — planning, building, debugging, designing.
- **Downstream:** Pasted into a fresh Claude.ai chat.
- **Adjacent:** `chat-to-code-prompt` if the next action is to execute in Claude Code; this skill is for Claude.ai → Claude.ai continuation.
- **Composes with:** `workflow-lock` if the session revealed a reusable pattern; `reminder-hub` if the next action has a deadline worth a calendar entry.

## Example

**User:** getting long in here — give me a context summary

**Claude:**
Paste into a fresh Claude.ai chat to continue. Next action is a walkthrough prep, no repo involved.

````markdown
# Context Summary — Cambourne second walkthrough prep

**Project:** Personal (real estate)

## Active Tasking
Preparing for the second walkthrough of 366 E Cambourne St (week of May 4). Goal is to validate the as-is condition and build the case for negotiating $330K down to $315–320K.

## State
- **Done:** Verbal agreement at $330K, as-is terms confirmed with Shelly (executor), electrical permit (2022) confirmed as panel-only
- **In progress:** Walkthrough checklist — HVAC, roof, foundation, plumbing, windows
- **Blocked on:** nothing

## Key decisions / constraints
- Contingent on Waterford sale (Krysta handling agent outreach in parallel)
- Target reduction: $10–15K off $330K, justified by as-is / estate-sale terms
- Net Waterford proceeds at $365K floor only support 10% down + PMI at $330K Cambourne

## Artifacts produced this session
- Cambourne Command Center React dashboard (Cormorant Garamond + warm cream palette) — local
- Devils-advocate hardening session — scored 82/100

## Next action
Build the walkthrough checklist as a printable one-pager grouped by system, with "evidence for reduction" column.

## Completion criteria
- [ ] Checklist printed and ready for May 4 walkthrough
- [ ] Counteroffer letter drafted, ready to send post-walkthrough

## After completion
Send counteroffer → await Shelly's response → proceed to offer acceptance or walk.
````

Want me to chain into drafting the walkthrough checklist now, or save this summary as-is?
