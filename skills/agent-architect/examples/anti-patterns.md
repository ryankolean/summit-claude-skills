# Subagent Anti-Patterns — Extended Catalog

## Contents
- God agents
- Permission escalation
- Tool soup
- Vague descriptions
- Stateful assumptions
- Cross-agent dependencies
- Reinventing built-ins
- Subagent for one-shot prompts

## God agents

**Pattern:** One agent that "does everything" — reviews code, writes tests, deploys, monitors.
**Detection:** Description contains "and" three or more times, or the role spans unrelated domains.
**Fix:** Decompose into separate single-purpose subagents. Each agent should answer "what is the one job?" in a sentence.

## Permission escalation

**Pattern:** Adding `bypassPermissions` without strong justification.
**Detection:** `permissionMode: bypassPermissions` in frontmatter.
**Fix:** Ask why. Prefer `acceptEdits` for trusted edit-heavy agents, or `default` and let the parent decide. Reserve `bypassPermissions` for fully isolated, audited automation.

## Tool soup

**Pattern:** Listing every available tool "just in case."
**Detection:** `tools` line contains 8+ entries, or the agent's stated job needs only 2-3.
**Fix:** Cut to the actual minimum. Tighter scopes mean clearer boundaries and safer execution.

## Vague descriptions

**Pattern:** "Helps with code", "database helper", "does stuff with files."
**Detection:** Description does not specify when to invoke.
**Fix:** Force a specific trigger. "MUST BE USED when X" or "PROACTIVELY when Y."

## Stateful assumptions

**Pattern:** Body assumes the agent will remember the parent's conversation.
**Detection:** Phrases like "as we discussed earlier", "continue from where we left off", "the file you mentioned."
**Fix:** Rewrite for a cold start. Subagents have no conversation history. Pass everything in the invocation prompt.

## Cross-agent dependencies

**Pattern:** Agent A depends on Agent B's mid-execution output.
**Detection:** Body references another subagent's intermediate state.
**Fix:** Subagents return one final message to the parent. Restructure as sequential parent-orchestrated calls.

## Reinventing built-ins

**Pattern:** Custom Explore-clone (read-only Haiku exploration), Plan-clone (read-only planning), or general-purpose-clone (full toolset).
**Detection:** The custom agent's role overlaps cleanly with a built-in.
**Fix:** Use the built-in. Custom subagents earn their place through specialization.

## Subagent for one-shot prompts

**Pattern:** Spinning up a subagent for work that fits in a single parent turn.
**Detection:** The "agent" has one step, no decision logic, and writes nothing.
**Fix:** Just have the parent do it, or use a slash command in `.claude/commands/`.
