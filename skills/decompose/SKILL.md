---
name: decompose
description: >
  Take any complex, messy, or overwhelming process and break it into discrete,
  ordered, automatable steps with dependencies mapped. Activates when the user
  says "break this down", "decompose this", "I don't know where to start", or
  describes a large process they need to untangle. Turns chaos into a task list.
---

# Decompose

Turn a big messy process into a clear sequence of steps that can each be
executed, automated, or delegated independently.

## When to Activate

**Manual triggers:**
- "Break this down"
- "Decompose this"
- "I don't know where to start"
- "This is overwhelming — help me plan"
- "Map this process out"

**Auto-detect triggers:**
- User describes a multi-step process with unclear ordering
- User mentions being overwhelmed or stuck on a large task
- User says "I need to do X" where X involves 5+ implicit sub-tasks
- User is trying to explain a process but keeps jumping between steps

## Phase 1: Understand the Whole

Before decomposing, understand the complete picture. Ask one question at a time:

1. "What's the end result when this process is done successfully?"
2. "Walk me through how it works today — even if it's messy. I need the real
   version, not the idealized one."
3. "Who's involved? Is it just you, or are there handoffs to other people or
   systems?"
4. "Where does it usually break down or get stuck?"

Stop asking when you can describe the full process back to the user accurately.

## Phase 2: Decompose

Break the process into steps using these rules:

### Step Granularity Rules
- Each step should be completable by one person (or one tool) in one sitting
- Each step should have a clear input and a clear output
- If a step requires a decision, split it: one step to gather info, one step
  to decide, one step to execute on the decision
- If a step takes longer than 30 minutes, it can probably be broken down further
- If a step can't be broken down further, mark it as atomic

### Dependency Mapping
For each step, identify:
- **Depends on:** Which steps must be completed first?
- **Blocks:** Which steps can't start until this one is done?
- **Parallel:** Which steps can happen simultaneously?

### Automation Tagging
Tag each step with one of:
- `[AUTOMATE]` — Can be fully automated with existing tools
- `[AI-ASSIST]` — Needs human judgment but AI can do 80% of the work
- `[HUMAN]` — Requires human judgment, creativity, or relationship
- `[TOOL]` — Already handled by existing software, just needs configuration

## Phase 3: Output

Present the decomposition in this format:

```
# Process Decomposition: [Process Name]

## Overview
[One paragraph: what this process achieves and who it's for]

## Steps

### Step 1: [Name] [AUTOMATE]
- **Input:** What you need before starting
- **Action:** What happens in this step
- **Output:** What this step produces
- **Depends on:** Nothing (starting step)
- **Time estimate:** X minutes
- **Notes:** [Any context or gotchas]

### Step 2: [Name] [AI-ASSIST]
- **Input:** Output from Step 1
- **Action:** ...
- **Output:** ...
- **Depends on:** Step 1
- **Time estimate:** X minutes

[Continue for all steps]

## Dependency Map
Step 1 → Step 2 → Step 3
                 ↘ Step 4 (parallel with Step 3)
Step 3 + Step 4 → Step 5

## Quick Wins
Steps that can be automated immediately:
- Step X: [How to automate]
- Step Y: [How to automate]

## Bottlenecks
Steps most likely to cause delays:
- Step X: [Why and how to mitigate]
```

## Rules

1. Always decompose from the user's current reality, not an idealized version.
   Work with how things actually happen, then optimize.

2. Number every step. People need to reference them ("let's talk about step 4").

3. Keep step names short and action-oriented. "Pull Q3 data from Salesforce"
   not "The quarterly data retrieval process for third-quarter metrics."

4. After presenting the decomposition, ask: "Does this match how it actually
   works? Any steps I'm missing or got in the wrong order?"

5. Offer to go deeper on any step. "Want me to decompose Step 4 further?"

## Chaining

- **automate-audit → decompose:** When an automation opportunity is high-effort,
  decompose it to find the automatable sub-steps
- **decompose → prompt-architect:** Once steps are identified, build Claude prompts
  for the automatable ones
- **decompose → delegate:** For steps tagged [AI-ASSIST], use delegate to clarify
  the human-vs-AI split
