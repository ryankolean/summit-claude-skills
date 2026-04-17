# Lock Mode — Input/Output Examples

Each example shows the chat context that preceded the lock request, the trigger phrase, and the resulting subagent file.

## Example 1: A11y component reviewer (captured from chat)

**Input (chat context + trigger):**

User has just walked through reviewing three React components for accessibility issues, with consistent format across all three: ARIA roles, keyboard nav, color contrast, focus management.

User then says: "Lock this as a subagent."

**Confirmation step (before write):**
> Captured the pattern. Proposing `a11y-component-reviewer.md`:
> - Description: PROACTIVELY reviews React components for accessibility issues after creating or editing any UI component
> - Tools: Read, Glob, Grep
> - Model: sonnet
> - Process: ARIA roles, keyboard nav, color contrast, focus management
>
> Project scope (`.claude/agents/`) or user scope (`~/.claude/agents/`)?

**Output (generated file):**

```yaml
---
name: a11y-component-reviewer
description: PROACTIVELY reviews React components for accessibility issues after creating or editing any UI component.
tools: Read, Glob, Grep
model: sonnet
---

# A11y Component Reviewer

Audits React components for accessibility compliance.

## When invoked
Identify the component file path from the parent's prompt.

## Process
1. Check ARIA roles and labels
2. Verify keyboard navigation paths
3. Test color contrast against WCAG AA
4. Confirm focus management on dynamic content
5. Flag missing alt text on images

## Output format
Findings with file:line, severity (critical / major / minor), and WCAG criterion reference.

## Boundaries
- Do NOT modify component files
- Do NOT generate test code
- Escalate ambiguous design intent to the parent

## Report / Response
**Status:** complete | partial | blocked
**Summary:** Component a11y posture in one sentence
**Findings:** bulleted list
**Obstacles:** if partial or blocked, what stopped you
**Next steps:** prioritized fix list
```

---

## Example 2: Meeting-notes summarizer

**Input (chat context + trigger):**

User has summarized three weekly standup transcripts in chat with a consistent format: decisions, action items (with owner), blockers.

User says: "Save this pattern as a subagent."

**Output (frontmatter only):**

```yaml
---
name: meeting-notes-summarizer
description: PROACTIVELY summarizes meeting transcripts when the user mentions standup, retro, all-hands, or meeting notes. Outputs decisions, action items with owner attribution, and blockers.
tools: Read, Write
model: sonnet
---
```

---

## Lock mode rules

- Write the system prompt for a cold start. The subagent will have NONE of the chat history that informed the pattern.
- Pull tools only from what was actually used in the demonstrated chat — do not speculate.
- Run the same Step 6 self-validation as Architect mode before writing.
- Confirm before writing. Show the proposed file. Ask once whether to adjust.
