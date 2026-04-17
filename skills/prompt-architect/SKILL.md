---
name: prompt-architect
description: >
  Translates a plain-English task description into a production-quality Claude prompt
  with structure, examples, and output formatting. Activates when the user says
  "write me a prompt for this", "turn this into a prompt", "prompt-architect", or
  when they describe what they want Claude to do but can't get the right output.
  Bridges the gap between knowing what you want and knowing how to ask for it.
---

# Prompt Architect

The user knows what they want Claude to do but can't write the prompt to get
consistent, high-quality results. Turn their plain-English description into a
structured, reusable Claude prompt.

## When to Activate

**Manual triggers:**
- "Write me a prompt for this"
- "Turn this into a prompt"
- "Prompt-architect"
- "Build me a Claude prompt"
- "I can't get Claude to do this right"

**Auto-detect triggers:**
- User describes a task they want to repeat with Claude but results are inconsistent
- User shares a prompt that isn't working and asks for help fixing it
- User says "how do I get Claude to..." or "Claude keeps getting this wrong"

## Phase 1: Understand the Task

Ask one question at a time until you know:

1. **What the prompt should do:** "Describe the task in plain English — what
   goes in, and what should come out?"
2. **What good looks like:** "Can you show me an example of good output? Or
   describe what it looks like when it's done right?"
3. **What bad looks like:** "What does Claude keep getting wrong, or what do
   you NOT want in the output?"
4. **How it will be used:** "Is this a one-time prompt or something you'll
   reuse repeatedly with different inputs?"
5. **Variables:** "What changes each time you use this? (e.g., different data,
   different audience, different topic)"

## Phase 2: Build the Prompt

Construct the prompt using these structural elements. Not every prompt needs
every element — use what the task requires.

### Prompt Blueprint

```
[ROLE ASSIGNMENT]
Establish who Claude is in this context. Be specific.
Example: "Act as a senior technical writer with 10 years of experience
writing API documentation for developer audiences."

[CONTEXT]
Background information Claude needs to do the job well.
Include: domain, audience, constraints, tone.

[TASK]
Clear, specific instruction. One primary action.
Use imperative verbs: "Write...", "Analyze...", "Create...", "Extract..."

[INPUT SPECIFICATION]
Define what the user will provide each time.
Use placeholder variables: {company_name}, {raw_data}, {topic}

[OUTPUT SPECIFICATION]
Define the exact format, structure, and length of the output.
Include: format (markdown, JSON, prose), sections, word count, tone.

[EXAMPLES] (if the task benefits from them)
One good example showing the expected input → output transformation.
One bad example showing what to avoid (optional but powerful).

[CONSTRAINTS]
Hard rules the prompt must follow.
"Do NOT include...", "Always start with...", "Keep under X words..."

[QUALITY CHECKS]
Self-verification steps.
"Before responding, verify that: [checklist]"
```

### Prompt Quality Checklist

Before delivering the prompt, verify it passes ALL of:

- [ ] **Single responsibility:** The prompt asks for one clear thing
- [ ] **Specificity:** No ambiguous words ("good", "nice", "appropriate")
- [ ] **Measurable output:** You could tell if the output is correct or not
- [ ] **Variables marked:** Anything that changes per use is in {brackets}
- [ ] **Anti-examples included:** At least one "do NOT" constraint
- [ ] **Format specified:** Output structure is explicit, not implied
- [ ] **Tested mentally:** You can imagine running this prompt and getting
  a consistent, useful result

## Phase 3: Deliver

Present the finished prompt in a code block the user can copy-paste directly.
Then explain:

1. **How to use it:** Where to paste, what to replace
2. **Variables to fill:** List each {variable} and what goes there
3. **When to use it:** The trigger condition or recurring schedule
4. **How to iterate:** What to tweak if results aren't perfect

If the prompt is reusable, offer: "Want me to also turn this into a SKILL.md
so Claude activates it automatically?"

## Rules

1. Write the prompt as if the user will hand it to someone else to use.
   It should work without the user explaining anything verbally.

2. Prefer specific over clever. A boring, clear prompt that works every time
   beats an elegant prompt that works 70% of the time.

3. Include at least one constraint. Unconstrained prompts produce generic output.

4. Match the user's technical level. If they're non-technical, don't use jargon
   in the prompt. If they're an engineer, be precise.

5. Always produce a copy-pasteable prompt. Never just describe what the prompt
   should contain — write the actual prompt.

6. Test the prompt mentally before delivering. Ask yourself: "If I pasted this
   into a fresh Claude session with no context, would it produce the right
   output?" If not, revise.

## Chaining

- **automate-audit → prompt-architect:** For each quick-win automation, build
  the prompt that makes it happen
- **decompose → prompt-architect:** For each automatable step, build the prompt
- **prompt-architect → workflow-lock:** Once the prompt works well, lock it into
  a repeatable workflow template
