---
name: delegate
description: >
  Decision framework that evaluates any task against criteria (repetitiveness,
  judgment required, error tolerance, data sensitivity) and recommends whether
  to automate fully, AI-assist, or keep human. Activates when the user asks
  "should I automate this?", "delegate this?", "AI or human?", or when they're
  unsure whether a task belongs in an automation pipeline.
---

# Delegate

Help the user decide: should this task be fully automated, AI-assisted, or
kept human? Not everything should be automated. This skill provides a
structured decision framework.

## When to Activate

**Manual triggers:**
- "Should I automate this?"
- "AI or human?"
- "Can Claude do this, or should I?"
- "Delegate this"
- "Is this worth automating?"

**Auto-detect triggers:**
- User hesitates about whether to automate something
- User describes a task with mixed automation potential (partly automatable,
  partly needs judgment)
- User asks "can Claude handle this?" about a task with ambiguous complexity

## The Evaluation Framework

For each task, evaluate across five dimensions. Score each 1-5.

### 1. Repetitiveness (1-5)
How often does this task recur with a similar pattern?
- 5 = Daily or more, nearly identical each time
- 4 = Weekly, same structure with minor variations
- 3 = Monthly, moderate variations
- 2 = Quarterly or irregular, significant variations
- 1 = One-off or rarely recurring

### 2. Judgment Required (1-5, inverted — high score = low judgment)
How much human judgment, creativity, or nuance is needed?
- 5 = Zero judgment — purely mechanical (data formatting, file conversion)
- 4 = Minimal judgment — clear rules cover 90%+ of cases
- 3 = Moderate judgment — some edge cases need human review
- 2 = Significant judgment — context-dependent decisions
- 1 = Deep judgment — requires empathy, politics, creativity, or taste

### 3. Error Tolerance (1-5)
What happens if the automation gets it wrong?
- 5 = Errors are trivially fixable, no consequences
- 4 = Errors cause minor inconvenience, easily caught
- 3 = Errors are noticeable, require some cleanup
- 2 = Errors cause real problems — wrong data sent, incorrect decisions
- 1 = Errors are catastrophic — legal, financial, safety, or reputational damage

### 4. Data Sensitivity (1-5, inverted — high score = low sensitivity)
How sensitive is the data involved?
- 5 = Public or non-sensitive data
- 4 = Internal but non-confidential
- 3 = Business-confidential
- 2 = Personally identifiable information (PII) or financial data
- 1 = Regulated data (HIPAA, SOX, classified) or credentials

### 5. Current Time Cost (1-5)
How much time does this task consume?
- 5 = Multiple hours per occurrence
- 4 = 1-2 hours per occurrence
- 3 = 30-60 minutes per occurrence
- 2 = 15-30 minutes per occurrence
- 1 = Under 15 minutes per occurrence

## The Decision Matrix

Calculate the **Delegation Score** = average of all five dimensions.

| Score Range | Recommendation | What It Means |
|---|---|---|
| 4.0-5.0 | **AUTOMATE FULLY** | Build it and forget it. No human in the loop. |
| 3.0-3.9 | **AI-ASSIST** | Claude does the heavy lifting, human reviews before finalizing. |
| 2.0-2.9 | **HUMAN + AI TOOLS** | Human drives, Claude is a tool (research, drafting, analysis). |
| 1.0-1.9 | **KEEP HUMAN** | This task needs human judgment, empathy, or accountability. Don't automate. |

## Output Format

Present the evaluation as:

```
# Delegation Assessment: [Task Name]

## Scores
| Dimension | Score | Reasoning |
|---|---|---|
| Repetitiveness | X/5 | [One sentence why] |
| Judgment Required | X/5 | [One sentence why] |
| Error Tolerance | X/5 | [One sentence why] |
| Data Sensitivity | X/5 | [One sentence why] |
| Current Time Cost | X/5 | [One sentence why] |

## Delegation Score: X.X/5

## Recommendation: [AUTOMATE FULLY / AI-ASSIST / HUMAN + AI TOOLS / KEEP HUMAN]

### Why
[2-3 sentences explaining the recommendation, highlighting the dimension(s)
that most influenced the decision]

### If Automating
[Specific recommendation for how to automate, what tools to use]

### If Keeping Human
[What the human should focus on, and where AI can still help at the margins]

### Risk to Watch
[The single biggest risk of following this recommendation, and how to mitigate it]
```

## Rules

1. Never recommend full automation for tasks scoring below 2 on Error Tolerance
   or Data Sensitivity. Some tasks are too risky regardless of other scores.

2. Be honest when automation isn't the answer. Saying "keep this human" is a
   valid, valuable recommendation. Don't force automation where it doesn't fit.

3. When recommending AI-ASSIST, be specific about the split. "Claude drafts,
   you review" is better than "use AI to help."

4. Consider the user's technical level. A non-technical user can't maintain a
   custom Python script. Recommend tools they can actually use.

5. If the scores are borderline (e.g., 2.8-3.2), present both options and let
   the user decide. Acknowledge the ambiguity.

## Chaining

- **automate-audit → delegate:** When the audit surfaces a task, use delegate
  to decide if it should actually be automated
- **delegate → decompose:** If the recommendation is AI-ASSIST, decompose the
  task to find which sub-steps are automatable
- **delegate → prompt-architect:** If the recommendation is AUTOMATE, build the
  prompt to do it
