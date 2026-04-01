---
name: architect-plan-for-dispatch
description: >
  Full-discovery planning skill that analyzes a GitHub repo, designs a complete
  implementation plan, and produces a structured markdown execution file for
  Claude Dispatch. Chains after interrogate. Activates when the user says
  "architect this", "plan for dispatch", "architect-plan-for-dispatch", "design
  this for dispatch", or when a large body of work needs thorough planning before
  handing off to Dispatch workers. Covers greenfield builds, refactors,
  migrations, infrastructure, documentation, and any complex multi-task project.
---

# Architect Plan for Dispatch

Take a fully-scoped project (post-interrogation) and produce a complete,
dependency-aware execution plan that a human reviews and hands to Claude
Dispatch. The plan must be detailed enough that each Dispatch worker can execute
its task with zero follow-up questions, and structured to minimize total token
burn across all workers.

## When to Activate

**Manual triggers:**
- "Architect this"
- "Plan for dispatch"
- "Architect-plan-for-dispatch"
- "Design this for dispatch"
- "Build me a dispatch plan"
- "Break this down for dispatch"

**Auto-detect triggers:**
- User has completed an interrogate session and the scoped project is complex
  (multi-file, multi-domain, or multi-step)
- User describes a project and mentions "dispatch", "workers", "parallel", or
  "hand off"
- User wants to build something large and mentions planning before executing

**Do NOT activate** when:
- The task is small enough for a single Claude session (under ~30 minutes of work)
- The user says "just build it" or "skip planning"
- The user is mid-execution on an already-planned task

## Prerequisites

This skill assumes the interrogate skill has already run, or the user has
provided a complete project scope including: goal, constraints, audience,
format, and assumptions. If the scope is incomplete, trigger interrogate first
and return here after.

Required context:
- A configured GitHub repo (default: `ryankolean` org, user specifies repo name)
- A clear project scope (from interrogate or user-provided brief)

## Phase 1: Repo Analysis and Code Report

Before designing anything, understand what exists. Pull and analyze the full
repository.

### What to Analyze

1. **Structure:** Directory tree, file organization patterns, module boundaries
2. **Dependencies:** Package manifests (package.json, requirements.txt, go.mod,
   Cargo.toml, etc.), version constraints, dependency graph
3. **Existing patterns:** Code conventions, architecture style, naming, error
   handling, test patterns, state management
4. **Configuration:** Environment setup, build tooling, CI/CD, deployment config
5. **Documentation:** README, inline docs, API docs, architectural decision
   records
6. **Tech stack:** Languages, frameworks, libraries, database, infrastructure
7. **Test coverage:** Test structure, coverage gaps, testing frameworks in use
8. **Entry points:** Main files, route definitions, API surface, CLI commands

### Code Report Output

Generate a code report and commit it to the repo at:

```
.claude/dispatch/reports/code-report-<SHORT_HASH>.md
```

Where `<SHORT_HASH>` is the first 8 characters of the current HEAD commit hash.

**Code report template:**

```markdown
# Code Report
**Repo:** <owner>/<repo>
**Commit:** <full_hash>
**Generated:** <ISO-8601 timestamp>
**Branch:** <branch_name>

## Tech Stack
- **Languages:** [list with versions]
- **Frameworks:** [list with versions]
- **Database:** [type and version if detectable]
- **Build tooling:** [bundler, compiler, task runner]
- **Test framework:** [framework and runner]
- **CI/CD:** [platform and config location]

## Architecture Overview
[2-5 sentences describing the overall architecture pattern, data flow, and
module boundaries. Reference specific directories.]

## Directory Structure
[Abbreviated tree showing top 2-3 levels with annotations for what each
major directory contains.]

## Key Patterns Observed
- **Code style:** [conventions, linting, formatting]
- **Error handling:** [pattern used]
- **State management:** [approach]
- **API design:** [REST/GraphQL/RPC, versioning]
- **Authentication:** [if present]

## Dependencies of Note
[List only dependencies that are architecturally significant — ORMs, state
libraries, auth packages, build tools. Skip utilities.]

## Test Coverage Assessment
- **Test structure:** [where tests live, naming convention]
- **Coverage gaps:** [areas with no or minimal testing]
- **Test types present:** [unit, integration, e2e, snapshot]

## Risks and Technical Debt
[Anything that could impact the planned work — outdated dependencies, missing
types, inconsistent patterns, known issues in README/issues.]
```

If a previous code report exists at a different commit hash, note the delta:
what changed between that report and this one. This enables historical diffing
across planning sessions.

## Phase 2: Architecture and Design

With the code report complete, design the solution. This phase produces the
high-level design decisions before breaking into tasks.

### Design Deliverables

For each project, produce:

1. **Approach statement:** 2-3 sentences on the chosen approach and why
   alternatives were rejected.

2. **Component map:** Which parts of the system are affected. For each:
   - What exists today (from code report)
   - What changes
   - Why

3. **Data flow:** How data moves through the new/modified system. Include
   inputs, transformations, storage, and outputs.

4. **Interface contracts:** API signatures, function signatures, type
   definitions, or schema changes that downstream tasks will depend on. Define
   these FIRST so parallel workers share the same contracts.

5. **Risk register:** Identify the top 3-5 risks and mitigations.

### Token Efficiency Principles

Every design decision should consider Dispatch token cost:

- **Define shared contracts early.** Interface definitions, types, and schemas
  go in a dedicated task that runs first. All downstream tasks reference these
  contracts rather than re-deriving them.
- **Minimize context per worker.** Each task should include ONLY the context
  that worker needs — not the full project background. Reference specific files
  and line ranges, not "the codebase."
- **Prefer small, focused tasks.** A worker that touches 1-3 files burns fewer
  tokens than one that needs to understand 15 files. Decompose aggressively.
- **Front-load decisions.** Every ambiguity left in a task prompt causes the
  worker to reason about alternatives, burning tokens. Make decisions in the
  plan, not in the worker.
- **Use file manifests as blinders.** When a task lists exactly which files to
  read and write, the worker skips scanning the full repo.

## Phase 3: Task Decomposition

Break the design into discrete, dispatchable tasks. Each task is a unit of
work for one Dispatch worker.

### Task Structure

Every task in the plan MUST include ALL of the following fields:

```markdown
### Task <N>: <Descriptive Name>

**Execution group:** <group_letter> (A = runs first, B = after A completes, etc.)
**Depends on:** <task numbers, or "none" for parallel-ready tasks>
**Estimated tokens:** <number> (input + output estimate for the worker)
**Recommended model:** <model_tier>
**Risk level:** low | medium | high

#### Instructions
[Precise, complete instructions. The worker should be able to execute this with
zero follow-up questions. Include:
- Exactly what to build/change
- Which files to read for context (specific paths)
- Which files to create or modify (specific paths)
- Code patterns to follow (reference existing code)
- Edge cases to handle
- What NOT to do]

#### Acceptance Criteria
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Each criterion should be verifiable by reading the output]

#### File Manifest
| Action | Path | Notes |
|--------|------|-------|
| READ   | src/auth/middleware.ts | Existing auth pattern to follow |
| CREATE | src/payments/handler.ts | New payment handler |
| MODIFY | src/routes/index.ts | Add payment routes |

#### Risk Flags
[If risk level is medium or high, explain what could go wrong and what the
human should review before merging this task's output.]
```

### Execution Groups

Tasks are organized into execution groups that define parallelism:

- **Group A:** Foundation tasks with no dependencies. Run in parallel.
  Examples: shared types, interface contracts, config scaffolding.
- **Group B:** Tasks that depend on Group A outputs. Run in parallel with
  each other once A completes.
- **Group C+:** Subsequent dependency layers. Continue the pattern.
- **Group FINAL:** Integration, testing, and verification tasks that run
  after all other groups complete.

Within each group, all tasks are parallel-safe. Between groups, there is a
hard dependency barrier.

### Model Tiering Defaults

Recommend a model for each task based on complexity. These are defaults — the
user can override per task or globally.

| Tier | Default Model | Use When |
|------|--------------|----------|
| **Speed** | Haiku (or fastest available) | File scaffolding, boilerplate generation, simple config changes, type definitions, straightforward CRUD |
| **Balanced** | Sonnet (or mid-tier available) | Feature implementation, moderate refactors, test writing, API integration, documentation |
| **Power** | Opus (or most capable available) | Complex architecture decisions, security-critical code, multi-file refactors with subtle dependencies, performance optimization |

When new models are released, re-evaluate these tiers based on published
benchmarks and cost-per-token. The principle is: use the cheapest model that
can reliably complete the task on the first attempt. A retry costs more than
using a slightly more expensive model upfront.

**User override format:** If the user specifies model preferences, honor them.
Accept overrides at two levels:
- **Global:** "Use Sonnet for everything" — applies to all tasks
- **Per-task:** "Use Opus for task 3" — applies to that task only

## Phase 4: Plan Assembly and Commit

### Plan File Structure

Assemble the full plan as a single markdown file and commit to:

```
.claude/dispatch/plans/<YYYY-MM-DD>-<slug>.md
```

Where `<slug>` is a kebab-case name derived from the project goal
(e.g., `2026-04-01-auth-system-refactor.md`).

**Full plan template:**

```markdown
# Dispatch Plan: <Project Name>

**Created:** <ISO-8601 timestamp>
**Repo:** <owner>/<repo>
**Branch:** <branch_name>
**Base commit:** <full_hash>
**Code report:** .claude/dispatch/reports/code-report-<short_hash>.md

## Project Summary
[2-3 sentences from the interrogate brief. What we're building and why.]

## Scope
**In scope:**
- [Explicit list of what this plan covers]

**Out of scope:**
- [Explicit list of what this plan does NOT cover]

## Design Decisions
[From Phase 2 — approach statement, key decisions, and why alternatives
were rejected. Keep this brief but sufficient for a human reviewer to
understand the rationale.]

## Execution Overview

| Group | Tasks | Parallelism | Estimated Total Tokens |
|-------|-------|-------------|----------------------|
| A     | 1, 2, 3 | All parallel | ~X,XXX |
| B     | 4, 5 | All parallel (after A) | ~X,XXX |
| FINAL | 6 | Sequential | ~X,XXX |
| **Total** | **6 tasks** | | **~XX,XXX** |

## Model Budget

| Model | Task Count | Est. Tokens | Est. Relative Cost |
|-------|-----------|-------------|-------------------|
| Haiku | X | X,XXX | $ |
| Sonnet | X | X,XXX | $$ |
| Opus | X | X,XXX | $$$ |

## Tasks

[All tasks from Phase 3, in execution group order]

---

## Handoff Instructions

To execute this plan with Claude Dispatch:

1. Review all tasks above. Edit any instructions, acceptance criteria, or
   model assignments as needed.
2. For each execution group (A, B, C, ..., FINAL), dispatch all tasks in
   that group to Dispatch workers.
3. Wait for the group to complete before starting the next group.
4. After Group FINAL completes, review the integration task output and
   run the full acceptance criteria checklist.

### Dispatch Commands

For each task, provide Dispatch with:
- The task instructions (copy the Instructions section)
- The file manifest (so the worker knows its scope)
- The acceptance criteria (so the worker can self-verify)
- The recommended model (or your override)

### Risk Summary

| Task | Risk | Mitigation |
|------|------|-----------|
| [task #] | [risk description] | [what to check] |
```

### Commit Convention

Commit the plan and code report with the message:

```
chore(dispatch): add plan — <project-slug>

Plan: .claude/dispatch/plans/<filename>.md
Code report: .claude/dispatch/reports/code-report-<hash>.md
```

If running in Claude.ai (no git access), output both files for the user to
commit manually or via Claude Code.

## Rules

1. **Never skip the code report.** Even for greenfield projects, analyze the
   repo to understand existing conventions, CI/CD, and tooling. A greenfield
   project in an existing repo still has context.

2. **Every task must be self-contained.** A Dispatch worker receives ONLY its
   task section. It cannot see other tasks, the design decisions, or the
   project summary. Write instructions accordingly — include all necessary
   context within the task itself.

3. **Front-load interface contracts.** If multiple tasks share types, schemas,
   or API contracts, create a Group A task that defines them. Never let two
   parallel workers independently invent the same interface.

4. **Be specific about file paths.** "Update the auth module" is not a task
   instruction. "Modify `src/auth/middleware.ts` to add rate limiting using the
   pattern in `src/auth/csrf.ts`" is.

5. **Estimate tokens conservatively.** Round up. A task that runs 20% over
   budget is cheaper than a retry. Include both input tokens (files the worker
   must read) and output tokens (code the worker must write).

6. **Never include secrets, API keys, or credentials in plan files.** Reference
   environment variable names instead.

7. **When in doubt, make a smaller task.** Two focused tasks that each succeed
   on the first attempt cost less than one large task that needs a retry.

8. **Include rollback guidance for high-risk tasks.** If a task modifies
   critical infrastructure, production config, or security boundaries, the
   task's risk flags should include how to revert.

9. **Honor the user's model overrides.** If the user specifies model preferences
   globally or per-task, apply them. Offer your tiering recommendation but
   don't override their choice.

10. **Adapt model recommendations to current offerings.** When you are aware of
    new models (through search, user mention, or updated knowledge), update
    the tiering recommendations. The tiers are based on capability and cost,
    not fixed model names.

## Cross-Surface Behavior

**In Claude Code (has git access):**
- Clone/pull the repo directly
- Generate the code report from live code analysis
- Commit both plan and code report to the repo
- Display a summary in the terminal

**In Claude.ai (no git access):**
- User provides the repo name; skill uses GitHub API (via web search/fetch)
  to analyze public repo structure and key files
- For private repos, user uploads key files or provides context
- Output both the code report and plan as downloadable markdown files
- Provide the user with commit instructions and file paths

## Chaining

- **interrogate → architect-plan-for-dispatch:** Interrogate scopes the
  project, then this skill designs and plans the execution
- **architect-plan-for-dispatch → [Claude Dispatch]:** Human reviews the plan,
  then provides it to Dispatch workers for execution
- **architect-plan-for-dispatch → architect-plan-for-dispatch:** Re-run on the
  same repo at a later commit to generate an updated code report and diff
  against the previous plan
