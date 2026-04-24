# System Design: {name}

**Class:** {UI | Code architecture | Business process | Automation pipeline}
**Owner:** {user or role}
**Status:** Draft | Approved | Implemented

## Scope

{One paragraph from Phase 1: outcome, actors, boundary, constraints, success criteria.}

## Parts

| # | Name | Responsibility | Type |
|---|---|---|---|
| 1 | {name} | {one sentence} | {Component / Module / Role / Stage} |
| 2 | {name} | {one sentence} | {…} |

## Interfaces

```
{Part 1}
  Input:  {field | type | source}
  Output: {field | type | consumers}
  State:  {what it remembers, or "stateless"}

{Part 2}
  Input:  ...
  Output: ...
  State:  ...
```

## Flow

```
[Trigger] -> [Part 1] -> [Part 2] -> [Consumer]
```

{One paragraph describing the diagram in prose: who triggers, what fans out, where errors land.}

## Failure Modes

| Part | Failure mode | Response | Escalation |
|---|---|---|---|
| {name} | {what can go wrong} | {automatic response} | {when to notify user} |

## Evolution

- **Growth:** {one sentence per anticipated extension}
- **Redesign trigger:** {assumption that, if invalidated, breaks the current design}
- **Deprecation path:** {how the system retires cleanly}

## Open Questions

{Anything the design dialog surfaced but did not resolve.}
