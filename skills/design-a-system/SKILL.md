---
name: design-a-system
description: >
  Designs a system from concept to implementation-ready blueprint across four
  system classes — user interface, code architecture, business process, and
  automation pipeline. Runs a structured five-phase workflow: scope the system,
  identify parts and boundaries, define interfaces and data flow, specify
  failure and evolution paths, then hand off to a build skill. Use when the
  user says "design a system for...", "design this system", "how should this
  system work", "sketch a system for X", "what should this system look like",
  or when the user is about to build something non-trivial and has described
  the outcome but not the parts. Sibling to `systemize` (which promotes an
  existing action into a system component) and `architect-plan-for-dispatch`
  (which produces an execution plan once a design exists). This skill is the
  thinking step before those.
---

# Design a System

Compress the "thinking through how a system should work" loop. The user has
an outcome in mind — a product feature, a refactor, an internal workflow, an
automation — and needs the system's shape, parts, interfaces, and failure
paths worked out before any code or process gets written.

This is the design step. Not implementation. Not component promotion (that's
`systemize`). Not execution planning (that's `architect-plan-for-dispatch`).

## When to Activate

**Manual triggers:**
- "Design a system for {X}"
- "Design this system"
- "How should this system work?"
- "Sketch a system for {X}"
- "What should this system look like?"
- "Help me think through {system}"

**Auto-detect triggers:**
- User describes a non-trivial outcome (product feature, workflow, pipeline)
  but has not described the parts, interfaces, or data flow.
- User is about to invoke `architect-plan-for-dispatch` on a concept that
  does not yet have a system design.
- User says "I want to build X" and X spans more than one surface (UI + API,
  frontend + backend, data + logic, multiple people + handoffs).

**Do NOT activate when:**
- The user already has a working action and wants to elevate it (use
  `systemize` instead).
- The user already has a design and wants an execution plan (use
  `architect-plan-for-dispatch`).
- The task is a single function, script, or one-off change.
- The user explicitly says "just build it" and the scope is small.

## System Classes

This skill handles four system classes. The phases are the same; the
vocabulary and artifacts adapt to the class.

| Class | Examples | Primary artifacts |
|---|---|---|
| **UI** | App screen, form flow, dashboard, component tree | Component hierarchy, state model, data-binding map |
| **Code architecture** | Service, module layout, library, API surface | Module map, interface contracts, dependency graph |
| **Business process** | Intake workflow, approval flow, review cycle | Role/responsibility map, handoff sequence, decision tree |
| **Automation pipeline** | Scraper + enrich + notify, cron chain, webhook flow | Stage diagram, trigger/input/output per stage, error paths |

If the class is ambiguous, ask which one fits before starting Phase 0.

## Phase 0: Pre-Design Scan

Before the design dialog, understand the landscape.

1. **Read the user's existing systems** from memory (`~/.claude/projects/.../memory/`),
   active project files, and recent conversation. Never design in isolation.
2. **Read the existing skill set** from the session's available skills list.
   Note skills that produce outputs this system might consume, or consume
   outputs this system might produce.
3. **Check for prior design docs** on the same topic (mindspace cards,
   `.claude/dispatch/`, README sections, inline comments).

Produce a short internal inventory (do not show unless asked):

```
DESIGN CONTEXT
==============
Adjacent systems: [list or "none"]
Related skills: [list or "none"]
Prior designs for this topic: [list with paths or "none"]
Open constraints from memory: [list relevant feedback/project memories]
```

If a prior design exists, surface it and ask whether to extend or replace.

## Phase 1: Scope

Ask one question at a time. Follow the `interrogate` pattern. Stop as soon as
the scope is clear.

1. **Outcome.** "What does this system achieve when it runs? Describe the
   change it causes in the world, not the steps."
2. **Actors.** "Who or what triggers this system, and who or what consumes
   the output? Humans, other systems, schedules, events?"
3. **Boundary.** "What's explicitly in scope, and what's explicitly out?
   Name at least one thing that's tempting to include but you're choosing
   to exclude."
4. **Constraints.** "What constraints must the design respect? Budget,
   latency, data sensitivity, compliance, hosting, tech stack, team size."
5. **Success criteria.** "How will you know this system is working? Name
   one quantitative and one qualitative signal."

Produce a one-paragraph scope statement and confirm it before moving on.

## Phase 2: Parts

Identify the system's parts. Adapt vocabulary to the class.

### Decomposition rules

- **Start with the minimum number of parts that could satisfy the scope.**
  Three similar parts beat a premature abstraction. Four is usually enough;
  eight is rarely necessary.
- **Every part must earn its place.** Ask "what breaks if I remove this?"
  for each part. If nothing breaks, delete it.
- **Name parts by responsibility, not by technology.** `LeadIntake` beats
  `SupabaseFunction`. `ApprovalRouter` beats `IfElseBlock`.
- **Reference existing skills or components by name** when a part maps to
  one. Composition over creation.

### Output: Part Inventory

| # | Name | Responsibility | Class-specific type |
|---|---|---|---|
| 1 | {name} | {one sentence} | {Component | Module | Role | Stage} |
| 2 | {name} | {one sentence} | {…} |

Confirm with the user before moving on.

## Phase 3: Interfaces and Flow

Every part has an interface contract. This is the non-negotiable step —
without contracts, parts are just blobs.

### Interface contract per part

```
{Part name}
  Input:  {field | type | source}
  Output: {field | type | consumers}
  State:  {what it remembers between runs, or "stateless"}
```

### Data/control flow

Produce a textual flow diagram. ASCII is fine:

```
[Trigger] → [Part 1] → [Part 2] → [Part 3] → [Consumer]
                ↓
           [Part 4 (side effect)]
```

For UI systems, the flow is typically state transitions and data binding.
For code architectures, call graphs and module imports. For business
processes, role handoffs. For automation pipelines, stage transitions with
retries.

### Contract review

Ask:
- "Does every part's input come from a named source (trigger, another part,
  or user)?"
- "Does every part's output have at least one named consumer?"
- "Is there a part whose output goes nowhere? Delete it or repurpose it."

## Phase 4: Failure and Evolution

A design that only describes the happy path is incomplete.

### Failure modes per part

| Part | Failure mode | Response | Escalation |
|---|---|---|---|
| {name} | {what can go wrong} | {automatic response} | {when to notify user} |

Prompt the user explicitly: "What's the worst thing this system can do if a
part fails silently? Design around that."

### Evolution path

- **Where does this system grow?** One sentence per anticipated extension.
- **What would force a redesign?** Name the assumption that, if invalidated,
  breaks the current design.
- **What's the deprecation path?** How does this system get retired
  cleanly if it's replaced?

## Phase 5: Hand-Off

Produce the final design document and offer next steps.

### Design document template

```markdown
# System Design: {name}

**Class:** {UI | Code architecture | Business process | Automation pipeline}
**Owner:** {user or role}
**Status:** Draft | Approved | Implemented

## Scope
{one paragraph from Phase 1}

## Parts
{part inventory table from Phase 2}

## Interfaces
{per-part contracts from Phase 3}

## Flow
{diagram + prose description from Phase 3}

## Failure Modes
{table from Phase 4}

## Evolution
{Phase 4 evolution path}

## Open Questions
{anything the design dialog surfaced but did not resolve}
```

### Next-step offers

Pick the one that fits; don't list all five.

1. **"Want me to plan the build?"** → `architect-plan-for-dispatch`
2. **"Want me to stress-test this design?"** → `devils-advocate`
3. **"Want a principal-engineer-level review?"** → `design-doc-review`
4. **"Want to promote one of these parts into a reusable component?"** →
   `systemize`
5. **"Want me to write the prompt or skill for a specific part?"** →
   `prompt-architect` or `prompt-to-skill`

## Rules

1. **Scope before parts.** Never list parts before the scope paragraph is
   confirmed. Unclear scope produces noise parts.
2. **One question at a time.** The design dialog follows the `interrogate`
   pattern. Never stack questions.
3. **Reference, don't rebuild.** If a part already exists as a skill,
   component, service, or process — cite it by name.
4. **Every part has a contract.** No exceptions. "It just works" is not a
   contract.
5. **Design for failure explicitly.** Phase 4 is not optional. A design
   without failure modes is a wish.
6. **Name things precisely.** A part's name should tell the reader what it
   does without needing the description column.
7. **Keep the part count low.** If the decomposition exceeds eight parts,
   challenge whether the scope is too big or whether parts should be merged.
8. **Defer technology choices.** This skill designs the system's shape.
   Language, framework, and database choices belong in the build plan, not
   the design.
9. **Produce a document, not a monologue.** The hand-off artifact is the
   value — not the conversation that produced it.
10. **Don't recurse into implementation.** If the user asks "how do I code
    this?" during the design dialog, park it in Open Questions and continue.

## Chaining

### Upstream (feeds into design-a-system)
- **interrogate → design-a-system:** Ambiguous request gets scoped first.
- **brain-dump capture → design-a-system:** A mindspace card with an idea
  that needs a design before it can be built.
- **User outcome description → design-a-system:** Direct entry.

### Downstream (design-a-system feeds into)
- **design-a-system → architect-plan-for-dispatch:** Design becomes a
  buildable execution plan.
- **design-a-system → devils-advocate:** Stress-test the design before build.
- **design-a-system → design-doc-review:** Principal-engineer hardening.
- **design-a-system → systemize:** Promote one of the parts into a
  first-class, reusable system component.
- **design-a-system → prompt-architect / prompt-to-skill:** Build an
  individual part as a Claude workflow.

### Parallel
- **design-a-system + delegate:** Use the delegate framework to decide which
  parts are full-auto, AI-assisted, or human-owned.

## Anti-Patterns

**Over-design.** A system with 12 parts, 20 interface fields, and four
failure tables for a weekend project is waste. Match depth to stakes.

**Premature technology binding.** Calling a part `LambdaFunction` instead of
`LeadIntake` locks the design to an implementation choice before the shape
is proven.

**Happy-path-only.** Skipping Phase 4 produces designs that look clean in a
doc and shatter in production.

**Designing around a single user story.** A system designed for one user's
one use case ships brittle. Force the dialog to name at least one adjacent
use case the system should accommodate — or explicitly reject.

**Confusing design with planning.** This skill produces a design. The build
plan — file paths, commits, task ordering — is `architect-plan-for-dispatch`.
Stay on the design side of the line.
