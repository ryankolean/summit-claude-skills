# Phase Playbook

Detailed prompts, rules, and rubrics for each phase of `design-a-system`. SKILL.md gives the spine; load this when you need the exact question wording, decomposition rules, or contract review checks.

## Phase 0: Pre-Design Scan

Before the design dialog, understand the landscape.

1. **Read the user's existing systems** from memory (`~/.claude/projects/.../memory/`), active project files, and recent conversation. Never design in isolation.
2. **Read the existing skill set** from the session's available skills list. Note skills that produce outputs this system might consume, or consume outputs this system might produce.
3. **Check for prior design docs** on the same topic (mindspace cards, `.claude/dispatch/`, README sections, inline comments).

Internal inventory (do not show unless asked):

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

Ask one question at a time. Follow the `interrogate` pattern. Stop as soon as scope is clear.

1. **Outcome.** "What does this system achieve when it runs? Describe the change it causes in the world, not the steps."
2. **Actors.** "Who or what triggers this system, and who or what consumes the output? Humans, other systems, schedules, events?"
3. **Boundary.** "What's explicitly in scope, and what's explicitly out? Name at least one thing that's tempting to include but you're choosing to exclude."
4. **Constraints.** "What constraints must the design respect? Budget, latency, data sensitivity, compliance, hosting, tech stack, team size."
5. **Success criteria.** "How will you know this system is working? Name one quantitative and one qualitative signal."

Produce a one-paragraph scope statement and confirm before moving on.

## Phase 2: Parts

### Decomposition rules

- **Start with the minimum number of parts that could satisfy the scope.** Three similar parts beat a premature abstraction. Four is usually enough; eight is rarely necessary.
- **Every part must earn its place.** Ask "what breaks if I remove this?" for each part. If nothing breaks, delete it.
- **Name parts by responsibility, not by technology.** `LeadIntake` beats `SupabaseFunction`. `ApprovalRouter` beats `IfElseBlock`.
- **Reference existing skills or components by name** when a part maps to one. Composition over creation.

### Output: Part Inventory

| # | Name | Responsibility | Class-specific type |
|---|---|---|---|
| 1 | {name} | {one sentence} | {Component / Module / Role / Stage} |
| 2 | {name} | {one sentence} | {…} |

Confirm before moving on.

## Phase 3: Interfaces and Flow

### Interface contract per part

```
{Part name}
  Input:  {field | type | source}
  Output: {field | type | consumers}
  State:  {what it remembers between runs, or "stateless"}
```

### Data/control flow

Textual diagram. ASCII is fine:

```
[Trigger] -> [Part 1] -> [Part 2] -> [Part 3] -> [Consumer]
                |
                v
           [Part 4 (side effect)]
```

Class-specific flow guidance lives in `references/system-classes.md`.

### Contract review

- "Does every part's input come from a named source (trigger, another part, or user)?"
- "Does every part's output have at least one named consumer?"
- "Is there a part whose output goes nowhere? Delete it or repurpose it."

## Phase 4: Failure and Evolution

### Failure modes per part

| Part | Failure mode | Response | Escalation |
|---|---|---|---|
| {name} | {what can go wrong} | {automatic response} | {when to notify user} |

Prompt explicitly: "What's the worst thing this system can do if a part fails silently? Design around that."

Common failure modes by class live in `references/system-classes.md`.

### Evolution path

- **Where does this system grow?** One sentence per anticipated extension.
- **What would force a redesign?** Name the assumption that, if invalidated, breaks the current design.
- **What's the deprecation path?** How does this system get retired cleanly if replaced?

## Phase 5: Hand-Off

Produce the final design document using `templates/design-document.md` and offer one next step (not all).

Next-step menu:

1. "Want me to plan the build?" -> `architect-plan-for-dispatch`
2. "Want me to stress-test this design?" -> `devils-advocate`
3. "Want a principal-engineer-level review?" -> `design-doc-review`
4. "Want to promote one of these parts into a reusable component?" -> `systemize`
5. "Want me to write the prompt or skill for a specific part?" -> `prompt-architect` or `prompt-to-skill`
