---
name: systemize
description: >
  Convert a singular action, task, or one-off workflow into a modular system
  component that integrates with existing skills and systems. Analyzes the full
  inventory of available skills and system components, then runs a structured
  design dialog to define the component's interfaces, dependencies, data flow,
  and integration points. If no system exists yet, establishes a self-centric
  system architecture with the user at the center. Activates when the user says
  "systemize this", "make this a system", "turn this into a component",
  "system component", "build a system around this", or when the user has a
  working action that should become part of a larger interconnected system
  rather than remaining a standalone skill or one-off workflow. Also activate
  when the user describes wanting things to "work together", "connect",
  "feed into each other", or talks about building infrastructure around
  a recurring process.
---

# Systemize

Elevate a singular action into a system component. Where `workflow-lock`
captures a repeatable process and `prompt-to-skill` installs it as a trigger,
**systemize** asks the harder question: how does this action fit into a larger
system? What feeds it? What consumes its output? What other components does
it depend on, and what depends on it?

The goal is never just another skill — it's a node in an interconnected system
that compounds value over time.

## When to Activate

**Manual triggers:**
- "Systemize this"
- "Make this a system"
- "Turn this into a component"
- "System component"
- "Build a system around this"
- "This needs to be part of something bigger"
- "How does this connect to everything else?"

**Auto-detect triggers:**
- User has a working action/workflow that clearly feeds into or depends on
  other processes they've described
- User mentions wanting things to "work together", "connect", or "be modular"
- User describes an action that overlaps with or duplicates an existing skill
- User is building the same kind of pipeline for the third time
- After a workflow-lock or prompt-to-skill completes, if the locked workflow
  has obvious system integration potential

**Do NOT activate when:**
- The action is truly standalone with no integration potential
- The user explicitly wants a one-off ("just do this once")
- The user says "skip the systems stuff" or "keep it simple"

## Core Concept: Self-Centric System Design

Every system built through this skill places **the user** at the center.
Systems are not abstract enterprise architectures — they are personal
operating systems that serve one person's goals, workflows, and context.

### Self-Centric Principles

1. **You are the hub.** Every system component ultimately serves the user's
   goals, not organizational abstractions. Data flows toward decisions the
   user needs to make.

2. **Context is the connective tissue.** Components share context about the
   user's projects, preferences, and state. A component that can't access
   or contribute to the user's context doesn't belong in the system.

3. **Progressive automation.** Start manual, observe patterns, automate what
   earns it. Never automate before understanding. The delegation framework
   (delegate skill) applies at the component level.

4. **Composability over completeness.** Small components that plug together
   beat monolithic solutions. A system of 5 focused components that each
   do one thing well outperforms 1 component that tries to do everything.

5. **Systems grow from use, not from planning.** Don't design a 20-component
   system on day one. Systemize what exists and works, then let the system
   reveal what it needs next.

## Phase 0: System Inventory

Before designing anything, understand what already exists. This is automatic
and does not require user input.

### Scan Available Resources

1. **Installed skills:** Read the available_skills list from the current
   session context. For each skill, note:
   - Name and purpose
   - What it produces (output type)
   - What it consumes (input type)
   - Which other skills it chains with

2. **Known systems:** Search conversation history and memory for previously
   systemized components. Look for:
   - System registry entries (see Phase 4)
   - References to "system", "pipeline", "workflow chain"
   - Established data flows between components

3. **Active projects:** Reference user memory for current projects and their
   tooling (e.g., Summit, DTST, Carrot Hire, Healthspan, Rare Find).

### Produce the Inventory Report

Generate a concise inventory (do NOT present this to the user unless asked):

```
SYSTEM INVENTORY
================
Active systems: [list or "None — this will be the first"]
Installed skills: [count] ([list categories: cli, workflow, planning, etc.])
Active projects: [list from memory]
Potential integration points: [skills/components that relate to the action]
```

This report informs the design dialog. Claude uses it internally to ask
better questions and suggest integration points the user might not see.

## Phase 1: Action Analysis

Understand the singular action the user wants to systemize.

### Extract the Action DNA

From the conversation, current context, or user description, identify:

1. **What it does:** The core transformation (input → output)
2. **What triggers it:** Event, schedule, or manual invocation
3. **What it needs:** Data, context, credentials, other outputs
4. **What it produces:** Artifacts, decisions, state changes, notifications
5. **How often it runs:** Frequency and pattern
6. **Who cares about the output:** The user, clients, other systems

If any of these are unclear, ask ONE question at a time following the
interrogate skill's pattern. Explain why you're asking.

### Classify the Component Type

Based on the action DNA, classify it into one of these system component types:

| Type | Description | Example |
|------|-------------|---------|
| **Source** | Produces data or events that feed downstream | "Scrape new job postings daily" |
| **Transformer** | Takes input, processes it, passes output downstream | "Score candidates against job requirements" |
| **Sink** | Consumes system output and produces a final artifact | "Generate weekly client report" |
| **Router** | Directs data flow based on conditions | "If high-priority lead, notify immediately; else batch" |
| **State** | Maintains system state that other components read/write | "Client relationship tracker" |
| **Orchestrator** | Coordinates multiple components in sequence or parallel | "End-to-end candidate pipeline" |

A component can have a primary and secondary type (e.g., a Transformer
that also maintains State).

## Phase 2: System Design Dialog

This is the core of the skill — a structured conversation that designs the
component's place in the system. Ask ONE question at a time.

### Dialog Sequence

The dialog adapts based on whether a system already exists.

#### If NO system exists (first systemization):

**Step 1: Establish the system purpose.**
"This is the first component in a new system. Before we design it, I need to
understand what this system is ultimately for. What's the big-picture goal
that this action serves? Not what this action does — what's the larger
outcome you're building toward?"

**Step 2: Name the system.**
"Every system needs an identity. Based on what you've described, I'd suggest
calling this the `{suggested-name}` system. Does that fit, or do you have a
better name?"

**Step 3: Define the system boundary.**
"What's in scope for this system, and what's explicitly out? This prevents
scope creep as we add components."

**Step 4: Design the component.**
Proceed to the component design questions below.

#### If a system EXISTS:

**Step 1: Confirm the target system.**
"I see you have the `{system-name}` system with [N] components. Is this
action joining that system, or starting a new one?"

**Step 2: Identify the integration point.**
"Looking at the existing components, this action seems to [connect
upstream/downstream/parallel] to `{component-name}`. It would
[consume/produce/share state with] that component. Does that match your
mental model?"

**Step 3: Design the component.**
Proceed to the component design questions below.

### Component Design Questions

Ask these one at a time, skipping any that are already clear from context.

1. **Interface contract — Input:**
   "What does this component need to receive to do its job? This could be
   data from another component, user input, an external event, or a
   scheduled trigger."

2. **Interface contract — Output:**
   "What does this component produce that other parts of the system (or you)
   will consume? Be specific about the format and structure."

3. **Dependencies:**
   "Does this component need anything from the existing skill set to work?"
   [Present relevant skills from the inventory as options]

4. **Failure mode:**
   "What happens if this component fails or produces bad output? Should the
   system halt, use a fallback, notify you, or continue with degraded data?"

5. **State requirements:**
   "Does this component need to remember anything between runs? If so, where
   should that state live?"

6. **Automation level:**
   "Should this component run fully automatically, with your review before
   finalizing, or does it always need you in the loop?"
   [Reference the delegate skill's framework if the answer isn't obvious]

7. **Evolution path:**
   "Where do you see this component going? Will it stay roughly this shape,
   or is this a stepping stone to something more complex?"

## Phase 3: Component Specification

After the dialog, produce a formal component specification.

### Component Spec Template

```markdown
# System Component: {component-name}

**System:** {system-name}
**Type:** {Source | Transformer | Sink | Router | State | Orchestrator}
**Version:** 1.0
**Created:** {date}
**Status:** Draft | Active | Deprecated

## Purpose
{One paragraph: what this component does and why it exists in the system.}

## Interface Contract

### Input
| Field | Type | Source | Required | Description |
|-------|------|--------|----------|-------------|
| {field} | {type} | {component or "user"} | {yes/no} | {description} |

### Output
| Field | Type | Consumers | Description |
|-------|------|-----------|-------------|
| {field} | {type} | {component(s) or "user"} | {description} |

## Dependencies

### Skills Required
| Skill | Purpose in This Component |
|-------|--------------------------|
| {skill-name} | {how it's used} |

### System Components Required
| Component | Relationship | Data Exchanged |
|-----------|-------------|----------------|
| {component-name} | {upstream/downstream/peer} | {what flows between them} |

### External Dependencies
| Dependency | Type | Notes |
|------------|------|-------|
| {service/API/tool} | {required/optional} | {access notes} |

## Behavior

### Trigger
{What causes this component to run: schedule, event, manual, upstream signal}

### Process
{Step-by-step logic. Reference skills by name where they handle a step.}

1. {Step 1 — may reference a skill: "Use `{skill-name}` to..."}
2. {Step 2}
3. {Step 3}

### Failure Handling
| Failure Mode | Response | Escalation |
|-------------|----------|-----------|
| {what can go wrong} | {automatic response} | {when to notify user} |

### State Management
{What this component persists between runs, where, and how.
"Stateless" if nothing is persisted.}

## Automation Level
{FULL AUTO | HUMAN REVIEW | HUMAN IN LOOP}
{Brief rationale referencing delegate framework dimensions if applicable.}

## Integration Map
{ASCII or description showing how this component connects to the system.}

Example:
  [Source: Job Scraper] → **[This Component]** → [Sink: Weekly Report]
                                ↕
                    [State: Candidate Tracker]

## Evolution Path
{Where this component is headed. What would trigger a v2.}

## Implementation Notes
{Technical details: which Claude surface runs this (Code, chat, Dispatch),
file paths, config, environment variables, cron expressions, etc.}
```

## Phase 4: System Registry Update

After the component spec is confirmed, update (or create) the system registry.

### System Registry Format

The registry is a single markdown file that tracks all systems and their
components. It lives at a location the user specifies (default: conversation
memory for lightweight tracking, or a file in a repo for persistent systems).

```markdown
# System Registry

## {System Name}
**Purpose:** {one sentence}
**Created:** {date}
**Components:** {count}

### Component Index
| # | Component | Type | Status | Depends On | Feeds Into |
|---|-----------|------|--------|-----------|-----------|
| 1 | {name} | {type} | Active | — | #2 |
| 2 | {name} | {type} | Active | #1 | #3 |
| 3 | {name} | {type} | Draft | #2 | User |

### System Diagram
{ASCII representation of the full system data flow}

### Change Log
| Date | Change | Component(s) |
|------|--------|-------------|
| {date} | Initial creation | #1 |
| {date} | Added {component} | #2 |
```

## Phase 5: Offer Next Steps

After presenting the component spec and updating the registry, offer
contextual next steps:

1. **"Want me to build this?"** — Chain to `architect-plan-for-dispatch`
   if the component needs code, or `prompt-architect` → `prompt-to-skill`
   if it's a Claude-powered workflow.

2. **"Should we systemize another action?"** — If the design dialog revealed
   adjacent actions that should also be components, offer to systemize them.

3. **"Want to stress-test this design?"** — Chain to `devils-advocate` to
   attack the component design and find gaps.

4. **"Ready to see the full system map?"** — Generate or update the visual
   system diagram showing all components and their connections.

5. **"Should this be a Dispatch plan?"** — If the component is complex
   enough, chain to `architect-plan-for-dispatch` for implementation.

## Rules

1. **Always scan the inventory first.** Never design a component without
   knowing what skills and systems already exist. Duplicate components
   waste energy and create confusion.

2. **One question at a time in the design dialog.** Follow the interrogate
   pattern. Never stack questions.

3. **Name things precisely.** Component names should be specific enough that
   anyone reading the system registry immediately understands what each
   component does without opening the spec.

4. **Interface contracts are non-negotiable.** Every component must have
   explicitly defined inputs and outputs. "It just works" is not a contract.
   This is the connective tissue that makes modularity real.

5. **Reference existing skills, don't rebuild them.** If a step in the
   component's process is already handled by an installed skill, reference
   that skill by name. Components compose skills; they don't replace them.

6. **Start small, grow from use.** A system with 2-3 well-designed
   components that actually run beats a 15-component architecture diagram
   that never gets implemented. Resist the urge to over-design.

7. **The user is always the ultimate consumer.** Even in multi-component
   systems, the final output must serve the user's direct goals. If a
   component's output doesn't eventually reach the user or save the user
   time, it doesn't belong.

8. **Never systemize without user confirmation.** Present the component
   spec and get explicit approval before updating the system registry.

9. **Preserve backward compatibility.** When adding a component to an
   existing system, ensure it doesn't break the interface contracts of
   existing components. If it does, flag the breaking change explicitly.

10. **Document the evolution path.** Every component should have a clear
    "where this is going" statement so future systemization sessions can
    build on prior intent rather than re-discovering it.

## Chaining

### Upstream (feeds into systemize)
- **Any successful action → systemize:** The primary entry point. User did
  something that worked, now wants it to be part of a larger system.
- **workflow-lock → systemize:** A locked workflow that needs system context.
- **interrogate → systemize:** Complex systemization benefits from scoping first.

### Downstream (systemize feeds into)
- **systemize → prompt-architect:** Design the Claude prompt for the component.
- **systemize → prompt-to-skill:** Install the component as a permanent skill.
- **systemize → architect-plan-for-dispatch:** Build the component as code.
- **systemize → devils-advocate:** Stress-test the component design.
- **systemize → systemize:** Recursively systemize adjacent actions revealed
  during the design dialog.

### Parallel
- **systemize + delegate:** Use the delegate framework to determine the
  automation level of each component.
- **systemize + design-doc-review:** For complex components, run the spec
  through a design doc review before implementation.

## Anti-Patterns

**Over-systemization:** Not everything needs to be a system component.
If the action is truly standalone, has no upstream or downstream, and
doesn't recur — just do it. Workflow-lock or prompt-to-skill may be the
right level of abstraction.

**Premature abstraction:** Don't create interface contracts for data flows
that don't exist yet. System components should wrap working actions, not
theoretical ones.

**System sprawl:** If the system registry grows beyond 8-10 components,
it's time to evaluate whether some components should be merged, deprecated,
or split into a separate system.

**Ignoring the inventory:** The most common failure is building a component
that duplicates an existing skill or conflicts with an existing component's
interface. The Phase 0 inventory exists to prevent this.
