---
name: design-a-system
description: >
  Designs a system from concept to implementation-ready blueprint across four
  system classes — user interface, code architecture, business process, and
  automation pipeline. Runs a structured five-phase workflow: scope, identify
  parts, define interfaces and flow, specify failure and evolution paths, then
  hand off to a build skill. Use when the user says "design a system for...",
  "design this system", "how should this system work", "sketch a system for X",
  "what should this system look like", or when the user is about to build
  something non-trivial and has described the outcome but not the parts.
  Sibling to `systemize` (promotes an existing action into a system component)
  and `architect-plan-for-dispatch` (produces an execution plan once a design
  exists). This is the thinking step before those.
---

# Design a System

Compress the "thinking through how a system should work" loop. The user has an outcome in mind — a product feature, a refactor, an internal workflow, an automation — and needs the system's shape, parts, interfaces, and failure paths worked out before any code or process gets written.

This is the design step. Not implementation. Not component promotion (`systemize`). Not execution planning (`architect-plan-for-dispatch`).

## Layered Knowledge

This skill uses a three-layer load model. Stay shallow by default; descend only when you need the depth.

| Layer | What | Where | When loaded |
|---|---|---|---|
| 0 | Skill name + description | frontmatter above | always in context |
| 1 | This SKILL.md — phases, rules, chaining | this file | on invocation |
| 2 | Phase playbook, system-class deep dives, anti-patterns, document templates | `references/`, `templates/` | only when a phase needs them |

**Layer 2 manifest:**

- `references/phase-playbook.md` — exact question wording, decomposition rules, contract-review checks per phase.
- `references/system-classes.md` — UI / Code / Process / Pipeline-specific vocabulary, flow patterns, and class-typical failure modes.
- `references/anti-patterns.md` — failure modes of the design dialog itself.
- `templates/design-document.md` — the Phase 5 hand-off artifact skeleton.

Read a Layer 2 file when you enter the phase that depends on it. Do not preload all four.

## When to Activate

**Manual triggers:**

- "Design a system for {X}"
- "Design this system"
- "How should this system work?"
- "Sketch a system for {X}"
- "What should this system look like?"
- "Help me think through {system}"

**Auto-detect triggers:**

- User describes a non-trivial outcome (product feature, workflow, pipeline) but has not described the parts, interfaces, or data flow.
- User is about to invoke `architect-plan-for-dispatch` on a concept that does not yet have a system design.
- User says "I want to build X" and X spans more than one surface (UI + API, frontend + backend, data + logic, multiple people + handoffs).

**Do NOT activate when:**

- User already has a working action and wants to elevate it (use `systemize`).
- User already has a design and wants an execution plan (use `architect-plan-for-dispatch`).
- Task is a single function, script, or one-off change.
- User explicitly says "just build it" and the scope is small.

## System Classes

| Class | Examples | Primary artifacts |
|---|---|---|
| **UI** | App screen, form flow, dashboard, component tree | Component hierarchy, state model, data-binding map |
| **Code architecture** | Service, module layout, library, API surface | Module map, interface contracts, dependency graph |
| **Business process** | Intake workflow, approval flow, review cycle | Role/responsibility map, handoff sequence, decision tree |
| **Automation pipeline** | Scraper + enrich + notify, cron chain, webhook flow | Stage diagram, trigger/input/output per stage, error paths |

If the class is ambiguous, ask before Phase 0. Once the class is known, load `references/system-classes.md` for class-specific vocabulary.

## Five-Phase Workflow

Each phase has a one-line job here. Detailed prompts and rubrics live in `references/phase-playbook.md` — load it when you enter the phase.

| Phase | Job | Output |
|---|---|---|
| 0 — Pre-Design Scan | Read existing systems, skills, prior designs. | Internal context inventory. |
| 1 — Scope | Establish outcome, actors, boundary, constraints, success criteria. | One-paragraph scope statement (confirmed). |
| 2 — Parts | Decompose the system into the minimum set of named parts. | Part inventory table. |
| 3 — Interfaces and Flow | Define input/output/state per part; draw the data and control flow. | Per-part contracts + ASCII flow diagram. |
| 4 — Failure and Evolution | Name failure modes, responses, evolution path, redesign triggers. | Failure-mode table + evolution notes. |
| 5 — Hand-Off | Produce the design document and offer one next step. | `templates/design-document.md` filled in. |

## Periodic Table — Sibling and Neighbor Skills

Every skill knows its neighbors. Cite the right one rather than recreating its work.

### Upstream (feeds in)

- `interrogate` — ambiguous request gets scoped first.
- `brain-dump` capture — a mindspace card with an idea that needs a design before it can be built.
- Direct user outcome description.

### Downstream (feeds out)

- `architect-plan-for-dispatch` — design becomes a buildable execution plan.
- `devils-advocate` — stress-test the design before build.
- `design-doc-review` — principal-engineer hardening.
- `systemize` — promote one of the parts into a first-class, reusable system component.
- `prompt-architect` / `prompt-to-skill` — build an individual part as a Claude workflow.

### Parallel

- `delegate` — decide which parts are full-auto, AI-assisted, or human-owned.
- `decompose` — when Phase 2 needs help breaking a part into sub-parts.

## Rules

1. **Scope before parts.** Never list parts before the scope paragraph is confirmed. Unclear scope produces noise parts.
2. **One question at a time.** The design dialog follows the `interrogate` pattern. Never stack questions.
3. **Reference, don't rebuild.** If a part already exists as a skill, component, service, or process — cite it by name.
4. **Every part has a contract.** No exceptions. "It just works" is not a contract.
5. **Design for failure explicitly.** Phase 4 is not optional. A design without failure modes is a wish.
6. **Name things precisely.** A part's name should tell the reader what it does without needing the description column.
7. **Keep the part count low.** If decomposition exceeds eight parts, challenge whether the scope is too big or whether parts should be merged.
8. **Defer technology choices.** This skill designs the system's shape. Language, framework, database belong in the build plan.
9. **Produce a document, not a monologue.** The hand-off artifact is the value.
10. **Don't recurse into implementation.** If asked "how do I code this?" mid-dialog, park it in Open Questions and continue.
11. **Stay in Layer 1 unless a phase requires Layer 2.** Don't preload references or templates.

## Anti-Patterns

Common failure modes of the design dialog itself live in `references/anti-patterns.md`. Load it during Phase 5 review, or when the user asks "what's wrong with this design?"
