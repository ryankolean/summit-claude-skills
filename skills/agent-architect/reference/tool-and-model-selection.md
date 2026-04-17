# Tool and Model Selection

## Contents
- Tool combinations
- MCP tool inheritance gotcha
- Model selection
- Naming convention

## Tool combinations

Default to least-privilege:

- `Read, Glob, Grep` — pure analysis (reviewers, auditors)
- `+ Edit, Write` — file modification (refactor, doc writers)
- `+ Bash` — execution (test runners, deployers, formatters)
- `+ WebFetch, WebSearch` — research and discovery
- Omit `tools` entirely — when the agent legitimately needs the full parent toolset

## MCP tool inheritance gotcha

When `tools` is omitted: the subagent inherits ALL parent tools, including any configured MCP tools.

When `tools` is set to an allowlist: MCP tools are excluded unless explicitly named with their full server-prefixed names (e.g., `BigQuery:bigquery_schema`, `GitHub:create_issue`).

If the agent needs many MCP tools, prefer omitting `tools` over enumerating them.

## Model selection

Default: `inherit` (matches whatever the parent runs).

| Model | Use for |
|---|---|
| `haiku` | Lookup, classification, simple extraction, file routing, fast triage |
| `sonnet` | Balanced reasoning, code review, refactoring, structured generation |
| `opus` | Architecture, complex multi-step planning, deep synthesis across many files |
| `inherit` | When the subagent should match the parent's model (good default) |

## Naming convention

Default: `<role>-<specialty>` for analyst agents (`code-reviewer`, `api-designer`), or `<verb>-<noun>` for action agents (`run-tests`, `triage-bug`). Both are kebab-case, lowercase, hyphen-separated.

Avoid: generic verbs alone (`reviewer`, `helper`), brand or model names in the slug (`opus-reviewer`), numeric version suffixes (`reviewer-v2` — git history handles versioning).

Per Anthropic naming guidance, gerund form (`reviewing-code`, `analyzing-migrations`) is preferred when the surrounding skill ecosystem also uses gerunds. Match the convention of the existing skill collection.
