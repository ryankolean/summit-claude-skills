---
name: agent-architect
description: Designs, captures, and deploys Claude Code subagents (markdown files in .claude/agents/ or ~/.claude/agents/). Use when the user asks to design, create, scope, or build a subagent, lock a working chat pattern as a subagent, deploy an existing subagent file, convert a skill or slash command into a subagent, or references the /agents command, .claude/agents/ directory, or subagent frontmatter. Not for AGENTS.md, CLAUDE.md, slash commands, hooks, or general skills (use prompt-to-skill for skills).
---

# Agent Architect

Generates Claude Code subagent definition files. Three modes auto-detected from invocation: Architect (scope from a description), Lock (capture a working chat pattern), Push (deploy to project or user scope).

This skill complements the built-in `/agents` "Generate with Claude" wizard. Use the wizard inside Claude Code with a clear concept. Use this skill when scoping in claude.ai, capturing a chat pattern, deploying to a tracked repo, or applying anti-pattern enforcement.

## When to activate

Activate when the user:
- Says "design / create / scope / build a subagent for X" or "I need an agent that Y"
- Says "lock this as a subagent" after demonstrating a working chat pattern
- References `.claude/agents/`, subagent frontmatter, or the `/agents` command
- Asks to convert a skill, slash command, or chat pattern into a subagent

Do NOT activate for skills (use `prompt-to-skill`), slash commands (`.claude/commands/`), AGENTS.md (the agents.md open standard), CLAUDE.md (repo instructions), hooks (lifecycle scripts), or generic prompts (use `prompt-architect`).

## Pre-flight: should this be a subagent?

| User need | Better option |
|---|---|
| Repeatable instruction the parent should always follow | CLAUDE.md entry |
| Manual prompt template the user invokes | Slash command in `.claude/commands/` |
| Domain knowledge loaded on demand | Skill (use `prompt-to-skill`) |
| Lifecycle action (PreToolUse, SubagentStop) | Hook in settings |
| Read-only exploration | Built-in **Explore** subagent |
| Read-only planning | Built-in **Plan** subagent |
| Generic delegation with full tools | Built-in **general-purpose** subagent |
| Specialized, narrow, repeatable task with custom tools/model/prompt | **Custom subagent — proceed** |

If the need fits a non-subagent pattern, surface that and ask before generating.

## Mode detection

| Signal | Mode |
|---|---|
| User describes an agent's purpose with no demonstrated chat pattern | **Architect** |
| "Lock this as a subagent" after a working chat sequence | **Lock** |
| Either followed by "push it" / "ship it" / "deploy it" | adds **Push** |
| "Deploy this agent" with file already in chat | **Push** only |

If ambiguous, ask exactly one clarifying question.

---

## Workflow checklist

Copy this checklist into your response and check off items as you progress:

```
Subagent generation:
- [ ] Step 1: Pre-flight — confirmed subagent is the right tool
- [ ] Step 2: Mode detected (Architect / Lock / Push)
- [ ] Step 3: Scoping interview complete (purpose, tools, model)
- [ ] Step 4: Frontmatter drafted
- [ ] Step 5: System prompt body drafted (When invoked, Process, Output format, Boundaries, Report/Response)
- [ ] Step 6: Self-validation against anti-patterns passed
- [ ] Step 7: Scope confirmed (project / user)
- [ ] Step 8: File written
- [ ] Step 9: Reload reminder + test invocation surfaced
```

Do not skip Step 6.

---

## Architect mode

User describes intent; this mode scopes and generates.

### Scoping interview (max 3 questions, one per turn)

Use the `interrogate` skill's discipline. Skip any question chat already answers.

1. **Purpose and trigger** — What is the single, narrow job? Auto-delegate via `PROACTIVELY` / `MUST BE USED` directive, or only on explicit invocation? See [reference/description-patterns.md](reference/description-patterns.md).
2. **Tools required** — Default to least-privilege. See [reference/tool-and-model-selection.md](reference/tool-and-model-selection.md) for combinations and the MCP inheritance gotcha.
3. **Model tier** — `inherit` is the safe default. Switch to `haiku`, `sonnet`, or `opus` only when there is a clear reason.

### Generation template (strict)

This template is strict — fill in the placeholders, do not restructure. See [reference/frontmatter.md](reference/frontmatter.md) for full field details.

```yaml
---
name: <kebab-case-name>
description: <When to invoke. Use directive language for auto-delegation.>
tools: <comma-separated allowlist OR omit to inherit all parent tools>
model: <sonnet | opus | haiku | inherit>
---

# <Agent Name>

<One-sentence role statement.>

## When invoked
<Immediate first action.>

## Process
1. <Step>
2. <Step>

## Output format
<Specific deliverable structure.>

## Boundaries
- Do NOT <thing to escalate or refuse>
- When unsure, return control to the parent.

## Report / Response
**Status:** complete | partial | blocked
**Summary:** <one paragraph>
**Findings / Output:** <deliverable in the Output format above>
**Obstacles:** <if partial or blocked, what stopped you>
**Next steps:** <optional follow-up for parent>
```

### Step 6 — Self-validation feedback loop

Before writing the file, check the draft against the anti-pattern catalog:

```
Self-validation:
- [ ] Description specifies WHEN to invoke, not just what the agent is
- [ ] Tools list is least-privilege (no "just in case" inclusions)
- [ ] System prompt assumes cold start (no references to chat history)
- [ ] Single narrow job (does not span unrelated domains)
- [ ] Not duplicating a built-in (Explore / Plan / general-purpose)
- [ ] Output format is specific (not "review feedback" or "summary")
- [ ] Report/Response section present with Status field
```

If any item fails, revise the draft and re-check. Do not proceed to write until all items pass. Full catalog with detection patterns and remediations: [examples/anti-patterns.md](examples/anti-patterns.md).

For worked input/output examples, see [examples/architect-mode.md](examples/architect-mode.md).

---

## Lock mode

User has demonstrated a working pattern in chat. Capture it:

1. Identify what the user accomplished, what sequence worked, what signals they looked for, what output format they wanted.
2. Write the system prompt as if instructing a fresh Claude instance from a cold start. The subagent will not have conversation history.
3. Infer frontmatter: `name` from purpose (verb-noun preferred), `description` from the trigger, `tools` from what was actually used, `model` matching what worked.
4. Run the same Step 6 self-validation as Architect mode.
5. Show the proposed file. Ask once whether to adjust before deploying.

For worked input/output examples, see [examples/lock-mode.md](examples/lock-mode.md).

---

## Push mode

Deploy the generated file. See [reference/deployment.md](reference/deployment.md) for scope priority order, container deploy fallback (`git format-patch` + `git am`), and post-deploy reminders.

Quick path: ask scope (project / user), write the file, remind the user that subagents load at session start (run `/agents` to reload), suggest a test invocation.

---

## Subagent constraints

If the user's design assumes any of these, the answer is not a subagent — redirect to a parent-agent prompt or CLAUDE.md instruction:

- No plan mode (begins executing immediately)
- No live thinking output (parent only sees final return)
- No mid-stream coordination (returns one final message)
- No conversation history inheritance (fresh context window)
- No persistent CWD (`cd` does not persist between Bash calls)

---

## Anti-patterns (top 6)

- **God agents** doing everything → force decomposition
- **Tool soup** "just in case" → least-privilege
- **Vague descriptions** → force specific triggers
- **Stateful assumptions** that the agent will remember chat → write for cold start
- **Reinventing built-ins** → use the built-ins
- **Subagent for one-shot prompts** → if it fits in a single parent turn, no subagent needed

Extended catalog: [examples/anti-patterns.md](examples/anti-patterns.md).

---

## Chaining with other skills

- After `interrogate` → Architect mode with scoped requirements
- After successful chat pattern → Lock mode
- Before `architect-plan-for-dispatch` → generate worker subagents the plan will delegate to
- Pair with `prompt-to-skill` → when the agent's domain knowledge should also be a Skill loaded via the `skills:` frontmatter
- After `devils-advocate` → stress-test design before deploy
