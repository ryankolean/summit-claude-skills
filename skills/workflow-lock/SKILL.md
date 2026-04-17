---
name: workflow-lock
description: >
  Captures a successful one-off Claude interaction and convert it into a repeatable,
  templatized workflow with variables and trigger conditions. Activates when the
  user says "lock this workflow", "save this as a template", "I want to reuse this",
  or after a successful task where the user indicates they'll need to do it again.
  Turns one good result into infinite consistent results.
---

# Workflow Lock

The user just did something that worked well and wants to do it again consistently.
Capture the successful pattern and convert it into a reusable template with
variables, trigger conditions, and quality checks.

## When to Activate

**Manual triggers:**
- "Lock this workflow"
- "Save this as a template"
- "I want to reuse this"
- "Turn this into a repeatable process"
- "Template this"

**Auto-detect triggers:**
- User says "I'll need to do this again next week/month/quarter"
- User asks Claude to do the same task with different inputs
- User says "can we do exactly this but for [different thing]?"
- User expresses satisfaction with a result and hints at reuse

## Phase 1: Identify What Worked

Review the successful interaction and extract:

1. **The trigger:** What initiated the task? (A question, a data input, a
   recurring event)
2. **The inputs:** What information did the user provide? What changes each time?
3. **The process:** What steps did Claude follow to produce the output?
4. **The output:** What was the format, structure, length, and quality of the
   result?
5. **The implicit rules:** What constraints or preferences were applied that
   the user didn't explicitly state but that shaped the good result?

Ask the user one question at a time to confirm each:

"I want to capture this so you can reuse it. Let me make sure I've got the
pattern right. The trigger for this task is [X] — is that right?"

## Phase 2: Templatize

Convert the successful interaction into a reusable template with:

### Variables
Replace every instance-specific detail with a named variable in {brackets}.

Example:
- Original: "Write a blog post about React performance optimization"
- Template: "Write a blog post about {topic}"

Identify ALL variables — common ones include:
- {topic}, {audience}, {company_name}, {date_range}, {data_source}
- {tone}, {length}, {format}, {recipient}

### Trigger Condition
Define when this workflow should be used:
- Time-based: "Every Monday morning" or "End of each quarter"
- Event-based: "When a new client signs up" or "After each sprint"
- Request-based: "When someone asks for X"

### Quality Gate
Define what makes the output acceptable:
- Minimum requirements the output must meet
- Common failure modes to check for
- A quick self-check Claude should run before delivering

## Phase 3: Output the Locked Workflow

Present the locked workflow in this format:

```
# Workflow: [Name]

## When to Use
[Trigger condition — when should this workflow run?]

## Variables
Fill these in before running:
- {variable_1}: [Description of what goes here]
- {variable_2}: [Description of what goes here]

## Prompt Template
[The complete, copy-pasteable prompt with {variables} in place]

## Expected Output
[Description of what the output should look like, including format,
length, sections, and tone]

## Quality Checklist
Before accepting the output, verify:
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]

## Example
**Variables filled:** {variable_1} = "X", {variable_2} = "Y"
**Result:** [Brief description or excerpt of what this produces]
```

## Phase 4: Offer Next Steps

After presenting the locked workflow, ask:

1. "Want me to run this right now with different inputs to test it?"
2. "Should I turn this into a SKILL.md you can install permanently?"
3. "Want me to build a version that works with a spreadsheet of inputs
   for batch processing?"

## Rules

1. Capture implicit preferences, not just explicit instructions. If the user
   liked a casual tone but never asked for it, include "Use a conversational,
   casual tone" in the template.

2. Every variable must have a description. "{data}" is useless. "{data: the
   raw CSV export from Salesforce containing Q3 pipeline metrics}" is useful.

3. Include at least one example of the template filled in. People understand
   templates better when they see a concrete instance.

4. The locked workflow should be usable by someone other than the original
   user. Write it as if you're handing it to a colleague who wasn't in the
   original conversation.

5. Don't over-templatize. If something is always the same (e.g., the output
   format), hardcode it. Only variablize what actually changes.

## Chaining

- **prompt-architect → workflow-lock:** Build the prompt, then lock it into
  a repeatable workflow
- **automate-audit → workflow-lock:** For recurring tasks identified in the
  audit, lock workflows for each one
- **Any successful interaction → workflow-lock:** This skill can be chained
  after ANY task that the user wants to repeat
