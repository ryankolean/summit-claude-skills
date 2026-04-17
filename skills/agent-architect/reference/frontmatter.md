# Subagent Frontmatter Reference

## Contents
- Required fields
- Optional fields
- Skills injection
- Verifying the current spec

## Required fields

- `name` — lowercase + hyphens, unique within scope
- `description` — when to invoke; the routing rule for auto-delegation. See [description-patterns.md](description-patterns.md)

## Optional fields

| Field | Notes |
|---|---|
| `tools` | Comma-separated allowlist. Omit to inherit ALL parent tools including MCP. Use `Agent(<agent-name>)` syntax to restrict which subagents this agent can spawn |
| `disallowedTools` | Comma-separated denylist; subtracts from inherited or specified tools |
| `model` | `sonnet`, `opus`, `haiku`, full model ID, or `inherit` (default) |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan` |
| `skills` | Comma-separated skills to inject at subagent startup |
| `maxTurns` | Integer cap on subagent turns |
| `color` | UI background color in `/agents` view. Verify the field is in the current spec before including; on some Claude Code versions this may be a wizard-only setting rather than a frontmatter field |

## Skills injection (`skills:` frontmatter)

Pre-loads named skills into the subagent's context at startup, before it sees the parent's invocation. Use when:

- The subagent always needs domain knowledge that lives in a Claude Skill
- You want consistent conventions without runtime skill discovery
- The skill encodes output formats, tool patterns, or anti-patterns the agent must follow

Example:

```yaml
---
name: candidate-sourcer
description: PROACTIVELY sources dental candidates from public registries when the user mentions a new role or specialty.
tools: WebFetch, WebSearch, Read, Write
model: sonnet
skills: dental-recruiting-playbook, npi-registry-lookup
---
```

Confirm the named skills exist and are accessible to the subagent's scope before listing them.

## Verifying the current spec

The Claude Code subagent frontmatter spec evolves. Before generating, check:

- https://code.claude.com/docs/en/sub-agents
- https://docs.claude.com/en/docs/claude-code/sub-agents

Confirm whether each field above is still supported, whether new fields exist, and whether default values changed. If the spec has changed, generate against the latest fields and note the change to the user.
