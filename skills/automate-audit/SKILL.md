---
name: automate-audit
description: >
  Interview the user about their daily and weekly routines, then produce a ranked
  list of automation opportunities with effort-vs-impact scoring. Activates when the
  user asks "what should I automate?", "audit my workflow", "find my time wasters",
  or when they describe repetitive frustrations. Serves both technical and
  non-technical users.
---

# Automate Audit

Discover what the user is wasting time on that they don't realize could be automated.
Interview them about their routines, then deliver a ranked automation opportunity report.

## When to Activate

**Manual triggers:**
- "What should I automate?"
- "Audit my workflow"
- "Find my time wasters"
- "Where am I wasting time?"
- "Help me find things to automate"

**Auto-detect triggers:**
- User describes doing the same thing repeatedly ("every week I have to...",
  "I always end up manually...")
- User complains about a tedious process
- User mentions copy-pasting between tools, manual data entry, or repetitive formatting

## Interview Phase

Ask one question at a time. Work through these areas in order, skipping what
isn't relevant based on context.

### 1. Daily Rhythm
Start broad: "Walk me through a typical workday from start to finish — what are
the first few things you do when you sit down, and what eats the most time?"

### 2. Weekly Recurring Tasks
"What do you do every week that feels like groundhog day? Reports, updates,
check-ins, data pulls, scheduling?"

### 3. Tool Friction
"What tools or apps do you use daily? Where do you find yourself switching
between tools or copying information from one place to another?"

### 4. The Dread Question
"What task do you actively dread or procrastinate on — not because it's hard,
but because it's tedious?"

### 5. Communication Overhead
"How much time do you spend writing similar messages — status updates,
follow-ups, onboarding emails, responses to common questions?"

### 6. Data and Reporting
"Do you regularly pull data, format it, or create reports? How manual is that
process?"

Adapt your questions based on who you're talking to:
- **Technical users:** Ask about CI/CD, deployments, code review, monitoring, testing
- **Non-technical users:** Ask about spreadsheets, email, scheduling, document creation, invoicing

## Analysis Phase

After interviewing, score each identified task on two dimensions:

**Impact (1-5):** How much time/frustration would automation save?
- 5 = Hours per week recovered
- 4 = Significant weekly time savings (1-2 hours)
- 3 = Moderate savings (30-60 min/week)
- 2 = Minor convenience
- 1 = Nice-to-have

**Effort (1-5):** How hard is it to automate?
- 1 = Can be done with a single Claude prompt or simple tool
- 2 = Needs a structured prompt or basic script
- 3 = Requires a workflow with multiple steps or tool integration
- 4 = Needs custom development or complex integration
- 5 = Requires significant engineering investment

## Output: The Automation Opportunity Report

Present findings as a structured report:

```
# Automation Opportunity Report

## Quick Wins (High Impact, Low Effort)
These should be automated this week.

1. **[Task Name]** — Impact: X/5 | Effort: X/5
   - What you're doing now: [current manual process]
   - How to automate it: [specific recommendation]
   - Tool/approach: [Claude prompt, Zapier, script, MCP server, etc.]
   - Estimated time saved: [per week]

## High-Value Projects (High Impact, Higher Effort)
Worth investing in over the next month.

2. **[Task Name]** — Impact: X/5 | Effort: X/5
   ...

## Low-Priority (Lower Impact)
Automate these after the above are done.

3. **[Task Name]** — Impact: X/5 | Effort: X/5
   ...

## Summary
- Total tasks identified: X
- Quick wins: X (start here)
- Estimated weekly time savings if all quick wins are automated: X hours
```

## Rules

1. Be specific in recommendations. Don't say "automate this" — say exactly how.
   Name the tool, write the prompt, describe the integration.

2. For each quick win, offer to build the automation right now. "Want me to write
   the Claude prompt for this one?"

3. Tailor technical depth to the user. If they're non-technical, recommend no-code
   tools (Zapier, Make, Claude prompts). If they're an engineer, suggest scripts,
   MCP servers, or Claude Code skills.

4. Don't oversell. If something genuinely requires human judgment and shouldn't
   be automated, say so and explain why.

5. The report should be actionable the same day — at least the quick wins. Don't
   produce a report that requires weeks of planning to act on.

## Chaining

This skill pairs naturally with other Summit skills:
- **decompose:** For high-effort automation opportunities, use decompose to break
  them into manageable steps
- **prompt-architect:** For quick wins, use prompt-architect to build the Claude
  prompt that automates the task
- **delegate:** If the user isn't sure whether to automate or keep doing manually,
  use delegate to evaluate
