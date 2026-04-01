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

**Chain triggers (auto-follow after interrogate):**
- When interrogate has completed and the user has confirmed scope
- When the user says "now plan it" or "now break it down" after a scoping session

**Do NOT activate:**
- On small, single-file tasks that don't benefit from parallelism
- When the user says "just do it" or "skip planning"
- If the task is < 3 coherent subtasks

## Pre-flight Check

Before starting, verify you have the answers to all of these. If not, run
[interrogate](../interrogate/SKILL.md) first.

```
PRE-FLIGHT CHECKLIST
─────────────────────────────────────────
□ What is the primary goal?
□ What does "done" look like?
□ What is the target repository / codebase?
□ What tech stack is involved?
□ Are there hard constraints (timeline, budget, tech stack)?
□ Who reviews/approves before merge?
□ Are there external dependencies (APIs, databases, services)?
□ What is the deployment target?
□ Are there security or compliance requirements?
□ Has the user confirmed scope from interrogate?
─────────────────────────────────────────
```

If any box is unchecked, ask before proceeding.

---

## Process

Four phases. Execute in order. Do not skip.

---

### Phase 1: Repo Analysis and Code Report

Understand the existing codebase before designing anything.

#### 1.1 Clone and Read the Repository

If the user has provided a GitHub URL or local path, read it now.

```bash
# Clone if URL provided
git clone [repo-url] /tmp/architect-target 2>/dev/null
cd /tmp/architect-target

# Understand the structure
find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' \
  -not -path '*/vendor/*' -not -path '*/__pycache__/*' | sort | head -100

# Recent activity
git log --oneline -20

# Branch structure
git branch -a | head -20

# Open PRs / issues (if GitHub CLI available)
gh pr list --limit 10 2>/dev/null
gh issue list --limit 10 --state open 2>/dev/null
```

#### 1.2 Detect Tech Stack

Read every relevant config file:

| File | What it reveals |
|---|---|
| `package.json` | Node deps, scripts, test runner |
| `tsconfig.json` | TypeScript config, strictness |
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python version, deps |
| `go.mod` / `go.sum` | Go version, module deps |
| `Cargo.toml` | Rust edition, crate deps |
| `pom.xml` / `build.gradle` | Java/Kotlin version, deps |
| `Dockerfile` / `docker-compose.yml` | Runtime, services |
| `.github/workflows/` | CI/CD pipelines |
| `terraform/` / `pulumi/` / `cdk/` | Infrastructure as code |
| `Makefile` | Build targets |
| `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` | AI agent instructions |
| `.env.example` | Required env vars |

#### 1.3 Map the Architecture

Identify:
- **Entry points** (API routes, CLI commands, event handlers, cron jobs)
- **Domain boundaries** (auth, billing, users, notifications, etc.)
- **Data layer** (which databases, ORMs, migration tools)
- **External integrations** (APIs, SDKs, webhooks)
- **Test structure** (unit, integration, e2e — coverage level)
- **Key abstractions** (services, repositories, middleware, hooks)

#### 1.4 Identify Risk Zones

Flag areas of the codebase that make the implementation harder:
- High-complexity files (> 300 lines, many responsibilities)
- Missing tests in areas that will be touched
- Outdated dependencies that may conflict
- Ambiguous ownership (files with many contributors)
- Known technical debt (TODO/FIXME/HACK comments in affected files)

#### 1.5 Code Report

Produce a structured summary:

```
CODE REPORT
════════════════════════════════════════════════════════
Repository:     [name] ([primary language])
Stack:          [language + framework + DB + infra]
Size:           [N files / N lines of code]
Test coverage:  [% if available, else "unknown"]
CI/CD:          [platform + pipeline status]
Last commit:    [date + author]
Open PRs:       [N]
Open issues:    [N]

Architecture:
  Entry points:    [list]
  Domain areas:    [list]
  Data layer:      [DB + ORM]
  Integrations:    [list]

Risk zones:
  [file/area] — [reason]
  [file/area] — [reason]

CLAUDE.md found: [yes/no — note any special instructions]
════════════════════════════════════════════════════════
```

Present this to the user before proceeding. Ask: "Anything here that looks wrong
before I continue to architecture?"

---

### Phase 2: Architecture and Design

Design the implementation before decomposing into tasks.

#### 2.1 Design the Solution

Based on the Code Report and the scoped requirements, produce a design that covers:

**Data model changes** (if any):
- New tables/collections/models
- Schema migrations required
- Backward compatibility concerns

**API changes** (if any):
- New endpoints or mutations
- Changed contracts (breaking vs. non-breaking)
- Versioning strategy

**Interface contracts** (critical for parallelism):
Define all interfaces between components that will be worked on in parallel.
A Dispatch worker implementing Service A and another implementing Service B
both need to agree on the interface between them BEFORE either starts.

Format:
```typescript
// Interfaces that must be agreed on before parallel work begins
interface UserService {
  getUser(id: string): Promise<User>
  createUser(data: CreateUserInput): Promise<User>
}

interface NotificationService {
  send(userId: string, message: NotificationMessage): Promise<void>
}
```

**File-level change map**:
List every file that will be created, modified, or deleted:

```
CHANGE MAP
─────────────────────────────────────────────
CREATE  src/services/payment-service.ts
CREATE  src/services/payment-service.test.ts
MODIFY  src/api/routes/billing.ts
MODIFY  src/types/index.ts
CREATE  migrations/20240315_add_payment_table.sql
DELETE  src/legacy/old-payment-handler.ts
─────────────────────────────────────────────
```

**Dependency graph**:
Identify which changes depend on which other changes. This determines execution order.

#### 2.2 Validate the Design

Present the design to the user:

> "Here's the implementation design before I break it into tasks. Does this match
> what you're expecting? Any changes before I continue?"

Wait for confirmation. Do not proceed to task decomposition without approval.

---

### Phase 3: Task Decomposition

Break the approved design into Dispatch-ready tasks.

#### 3.1 Task Sizing Rules

Each task must be:
- **Self-contained**: Can be executed by a single Dispatch worker with no follow-up questions
- **Bounded**: Touches a specific set of files (listed in the task)
- **Testable**: Has a clear definition of done that can be verified
- **Safe to parallelize**: Does not conflict with other parallel tasks at the file level

Size targets:
- **Minimum**: 15 minutes of focused work
- **Maximum**: 4 hours of focused work (if larger, split it)
- **Sweet spot**: 30–90 minutes

Flags that a task is too large:
- "Refactor the entire X layer"
- "Implement all the Y features"
- Touches > 15 files
- Has more than 3 acceptance criteria

#### 3.2 Execution Groups

Organize tasks into groups that respect the dependency graph:

```
GROUP A — Foundation (must complete before B or C)
  Task A1: [name]
  Task A2: [name]

GROUP B — Core Features (can run in parallel after A)
  Task B1: [name]
  Task B2: [name]
  Task B3: [name]

GROUP C — Integration and Polish (can run in parallel after B)
  Task C1: [name]
  Task C2: [name]

GROUP FINAL — Review, Testing, and Merge Prep
  Task F1: End-to-end testing
  Task F2: Documentation
  Task F3: Changelog and migration guide
```

Rules:
- All GROUP A tasks must complete before GROUP B starts
- GROUP B tasks may run in parallel (no shared file writes)
- GROUP C tasks may run in parallel (no shared file writes)
- GROUP FINAL runs after all C tasks complete
- Never put tasks in the same group if they write to the same file

#### 3.3 Task Template

Each task must follow this exact format:

```markdown
## Task [GROUP][NUMBER]: [Short Name]

**Objective:** [One sentence — what this task accomplishes]

**Context:**
[2-4 sentences giving the Dispatch worker enough background to understand
why this task exists and how it fits the larger project. Include relevant
design decisions from Phase 2.]

**Files to create:**
- `path/to/file.ts` — [what it should contain]

**Files to modify:**
- `path/to/existing.ts` — [what changes to make and why]

**Files to leave untouched:**
- `path/to/other.ts` — [this file is being worked on in Task B2]

**Acceptance criteria:**
- [ ] [Specific, verifiable condition]
- [ ] [Specific, verifiable condition]
- [ ] All new code has unit tests
- [ ] TypeScript compiles with no errors (or language equivalent)
- [ ] Existing tests still pass

**Token budget:** ~[N]k tokens
**Suggested model:** [claude-opus-4-6 / claude-sonnet-4-6 / claude-haiku-4-5]

**Dependencies:** [Task A1 must complete first / none]

**Do not:**
- [Specific anti-pattern or out-of-scope thing to avoid]
- [Another]
```

#### 3.4 Interface Contract Tasks

For every interface shared between parallel tasks, create a dedicated Group A task:

```markdown
## Task A0: Define Shared Interfaces and Types

**Objective:** Establish all TypeScript interfaces, types, and constants that
parallel Group B tasks depend on, so workers don't make incompatible assumptions.

**Files to create:**
- `src/types/payment.ts` — PaymentIntent, PaymentMethod, PaymentStatus types
- `src/types/notification.ts` — NotificationMessage, NotificationChannel types

**Files to modify:**
- `src/types/index.ts` — export new types

**Acceptance criteria:**
- [ ] All interfaces from the Phase 2 design are defined
- [ ] Types are exported correctly
- [ ] No implementation code — types only
- [ ] TypeScript compiles with no errors

**Dependencies:** none
```

---

### Phase 4: Plan Assembly and Commit

Assemble the final plan file and save it.

#### 4.1 Plan File Format

The plan file is a standalone markdown document that a human can hand directly
to Dispatch. It must be fully self-contained — no references to "the conversation"
or "what we discussed".

```markdown
# Dispatch Plan: [Project Name]

**Created:** [date]
**Repository:** [repo URL or path]
**Estimated total tokens:** ~[N]k across all tasks
**Execution model:** [parallel groups / sequential]

---

## Summary

[3-5 sentence overview of what this plan accomplishes, why, and what the
outcome will be. Written for a human reviewer who hasn't seen the interrogation.]

---

## Code Report

[Paste the full Code Report from Phase 1.5]

---

## Architecture Summary

[Paste the design from Phase 2.1 — data model, API changes, interface contracts,
change map, and dependency graph]

---

## Execution Plan

[All task groups and tasks in order, using the Task Template format from 3.3]

---

## Validation Checklist

After all tasks complete, a human should verify:
- [ ] All acceptance criteria in every task are checked off
- [ ] Full test suite passes
- [ ] No new TypeScript/lint errors
- [ ] [App-specific checks: migrations ran, env vars documented, etc.]
- [ ] CHANGELOG updated
- [ ] PR description written

---

## Notes for the Reviewer

[Any design tradeoffs, known risks, or decisions the architect made that
the reviewer should be aware of]
```

#### 4.2 Save the Plan File

Save the plan to the repository:

```bash
# Save plan to repo
mkdir -p .dispatch-plans
PLAN_FILE=".dispatch-plans/$(date +%Y-%m-%d)-[project-slug].md"
# Write plan to $PLAN_FILE
```

Or if the user prefers, save to their preferred location.

#### 4.3 Summary to User

Present a final summary:

```
ARCHITECT PLAN COMPLETE
════════════════════════════════════════════════════════
Project:        [name]
Plan file:      [path]

Execution groups:
  Group A:  [N] tasks (foundation — run sequentially)
  Group B:  [N] tasks (can run in parallel)
  Group C:  [N] tasks (can run in parallel)
  Final:    [N] tasks (review + merge prep)

Total tasks:      [N]
Est. total tokens: ~[N]k
Suggested workers: [N] parallel Dispatch workers

Interface contracts defined: [N]
Files to be created:         [N]
Files to be modified:        [N]
Files to be deleted:         [N]

Next step: Review the plan file, then hand Group A tasks to Dispatch.
════════════════════════════════════════════════════════
```

---

## Rules

1. **Never skip the code report.** Designing without reading the codebase produces
   plans that conflict with reality. Always read first.

2. **Every task must be self-contained.** A Dispatch worker has no memory of the
   conversation. Every task must include all context it needs to execute.

3. **Front-load interface contracts.** Any interface shared between parallel tasks
   must be defined in Group A before parallel work begins. Conflicts discovered
   after parallel execution waste tokens and cause merges.

4. **Be specific about file paths.** "Add a service" is not a task. "Create
   `src/services/payment-service.ts`" is a task.

5. **Estimate tokens conservatively.** Over-estimate by 30%. Under-estimated
   tasks stall when workers hit context limits.

6. **Never include secrets in plan files.** Plan files may be committed to repos.
   Never include API keys, passwords, or credentials — even as examples.

7. **When in doubt, make a smaller task.** A task that's too small wastes one
   worker turn. A task that's too large blocks the whole group.

8. **Honor the user's model overrides.** If the user specifies a model for certain
   task types (e.g., "use Haiku for boilerplate"), respect that in the task template.
