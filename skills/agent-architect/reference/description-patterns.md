# Description-Field Patterns

The `description` field is the routing rule for auto-delegation. The parent agent matches the user's request against this string to decide whether to delegate.

## Contents
- Patterns ranked by auto-delegation strength
- Reliability principle
- Anti-patterns
- Default recommendation

## Patterns ranked by auto-delegation strength

| Pattern | Example | Strength |
|---|---|---|
| Bare descriptive | `Reviews code for quality` | Weak — manual only |
| Action-oriented | `Use proactively after writing or modifying code` | Medium |
| `PROACTIVELY` directive | `PROACTIVELY reviews code for security issues after auth changes` | Strong |
| `MUST BE USED for X` directive | `MUST BE USED for all Postgres migration files before they are applied` | Strongest |
| Trigger-phrase explicit | `Use immediately when user mentions PR, merge, or pull request` | Strong + predictable |

## Reliability principle

Auto-delegation reliability varies. Even with directive language, the primary agent may not always match correctly. When reliability matters, design the user's workflow around explicit invocation:

> Use the <agent-name> subagent on <task>

Treat auto-delegation as a convenience, not a contract. Explicit invocation is always safer.

## Anti-patterns

- "Helps with code" — too vague, will not auto-delegate
- "Database helper" — describes what it is, not when to use it
- "Does stuff with files" — useless as a routing rule

Reject these and force the user to specify trigger conditions.

## Default recommendation

When the user has not specified a strong preference: action-oriented language with `PROACTIVELY` for auto-delegation contexts; plain descriptive for explicit-invocation-only agents.
