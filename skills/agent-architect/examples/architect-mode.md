# Architect Mode — Input/Output Examples

Each example shows the user's request as input, the scoping question(s) Claude asks, and the resulting subagent file as output. Follow this style.

## Example 1: Postgres migration reviewer

**Input (user request):**
> I need an agent that reviews Postgres migrations before I apply them.

**Scoping question (one focused question):**
> Should this run automatically whenever you mention a migration file (use "MUST BE USED" directive), or only when you explicitly invoke it? And does it need Bash to dry-run the migration, or just Read/Glob/Grep to inspect SQL?

**Output (generated `.claude/agents/migration-reviewer.md`):**

```yaml
---
name: migration-reviewer
description: MUST BE USED for all Postgres migration files before they are applied. Checks for missing indexes, irreversible operations, and lock-acquiring statements.
tools: Read, Glob, Grep, Bash
model: sonnet
---

# Migration Reviewer

Reviews Postgres migration files for safety before deployment.

## When invoked
Read the migration file path passed by the parent.

## Process
1. Parse SQL statements
2. Flag irreversible operations (DROP, TRUNCATE without WHERE)
3. Check for ACCESS EXCLUSIVE locks on busy tables
4. Verify index strategy on new columns
5. Confirm rollback path exists

## Output format
Bulleted findings, each with line number, severity (critical / major / minor), and remediation.

## Boundaries
- Do NOT modify the migration file
- Do NOT apply the migration
- When SQL intent is ambiguous, return findings with "needs human review"

## Report / Response
**Status:** complete | partial | blocked
**Summary:** Migration review summary in one sentence
**Findings:** bulleted list with line, severity, remediation
**Obstacles:** if partial or blocked, what stopped you
**Next steps:** recommend apply / revise / abort
```

---

## Example 2: Security-focused code reviewer

**Input:**
> I want a security reviewer that runs on every PR.

**Scoping question:**
> Should this auto-delegate when you mention PR / merge / pull request (use "PROACTIVELY"), and is read-only inspection enough or does it also need Bash for dependency audits?

**Output (frontmatter only, body follows the same template):**

```yaml
---
name: security-reviewer
description: PROACTIVELY reviews code changes for security issues when the user mentions PR, merge, or pull request. Focuses on auth, input validation, secret handling, and dependency CVEs.
tools: Read, Glob, Grep, Bash
model: sonnet
---
```

---

## Example 3: Dependency upgrade auditor

**Input:**
> Build me an agent that audits package upgrades.

**Scoping question:**
> Should this auto-delegate when you change `package.json` or `requirements.txt`, and should it actually run `npm audit` / `pip-audit` (needs Bash) or just inspect the diffs?

**Output (frontmatter only):**

```yaml
---
name: dependency-upgrade-auditor
description: MUST BE USED when the user modifies package.json, requirements.txt, Pipfile, Cargo.toml, or other dependency manifests. Runs the appropriate audit tool, parses output, cross-references CVEs, and recommends safe-to-upgrade vs. requires-manual-review buckets.
tools: Read, Glob, Grep, Bash
model: sonnet
---
```
