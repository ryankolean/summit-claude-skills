---
name: prompt-to-skill
description: >
  Convert a working Claude prompt into a permanent, installable SKILL.md file with
  proper frontmatter, activation triggers, execution rules, and examples. Then
  automatically add it to the Summit Custom Skills table in the repo README and
  push to GitHub. Chains naturally after prompt-architect. Activates when the user
  says "make this a skill", "prompt to skill", "install this permanently", or when
  a prompt-architect output is confirmed working and the user wants to keep it.
---

# Prompt to Skill

Take a working prompt — either freshly built by prompt-architect or one the user
already has — and package it into a permanent, installable SKILL.md. Then register
it in the Summit Claude Skills repository automatically.

## When to Activate

**Manual triggers:**
- "Make this a skill"
- "Prompt to skill"
- "Install this permanently"
- "Turn this prompt into a skill"
- "Skill this"
- "Add this to my skills repo"

**Chain trigger (after prompt-architect):**
- User confirms a prompt-architect output is working and says anything like
  "this is great, I want to keep it" or "I'll reuse this"
- Offer proactively: "This prompt is working well — want me to turn it into
  a permanent skill so Claude activates it automatically?"

## Phase 1: Extract the Skill DNA

From the working prompt, extract these components. If any are missing, ask
one question at a time to fill the gaps.

### Required Components

1. **Skill name** (kebab-case, 1-64 characters)
   - Derive from the prompt's purpose. "weekly-status-report", "api-doc-writer",
     "invoice-generator"
   - Ask: "What should we call this skill? I'm thinking `{suggested-name}` —
     does that work?"

2. **Description** (1-2 sentences for frontmatter)
   - Must clearly state WHAT it does and WHEN to use it
   - Written for Claude's skill scanner — it reads this to decide relevance

3. **Activation triggers**
   - Manual phrases the user would say to invoke it
   - Auto-detect conditions where it should fire without being asked
   - Ask: "What would you naturally say when you need this? And should Claude
     ever activate it automatically without being asked?"

4. **The core prompt logic**
   - The actual instructions Claude follows when the skill is active
   - Restructured from a flat prompt into the SKILL.md format with sections

5. **Input specification**
   - What the user provides each time (variables from prompt-architect)
   - What format the input comes in

6. **Output specification**
   - Exact format, structure, and quality bar for the output
   - Include an example if available from the working session

7. **Rules and constraints**
   - Hard limits, anti-patterns, quality checks
   - Anything that makes this skill produce consistently good results

## Phase 2: Build the SKILL.md

Generate a complete SKILL.md following this structure:

```markdown
---
name: {skill-name}
description: >
  {One to two sentences: what the skill does and when to use it. Written for
  Claude's skill scanner to determine relevance.}
---

# {Skill Title}

{One paragraph explaining the skill's purpose and value.}

## When to Activate

**Manual triggers:**
- "{trigger phrase 1}"
- "{trigger phrase 2}"
- "{trigger phrase 3}"

**Auto-detect triggers:**
- {Condition 1}
- {Condition 2}

## Input

{What the user provides. Format, variables, examples.}

## Process

{Step-by-step instructions Claude follows. This is the core prompt logic
restructured into clear phases or steps.}

## Output

{Exact specification of what the skill produces. Format, structure, sections,
length, tone. Include a concrete example.}

## Rules

{Numbered list of hard constraints and quality checks.}

## Examples

**Good example:**
{Show a realistic input and the expected output}

**Bad example (what to avoid):**
{Show a common failure mode}

## Chaining

{How this skill connects to other Summit skills, if applicable.}
```

### SKILL.md Quality Checklist

Before finalizing, verify:

- [ ] **Frontmatter is scannable:** Description clearly states what + when in
  under 200 characters
- [ ] **Triggers are natural:** Phrases a human would actually say, not jargon
- [ ] **Process is complete:** A fresh Claude session with no context could
  follow these instructions and produce the right output
- [ ] **Output spec is measurable:** You could objectively tell if the output
  passes or fails
- [ ] **At least one concrete example:** Shows input → output transformation
- [ ] **Rules prevent common failures:** Each rule exists because of a real
  failure mode, not as filler

## Phase 3: Confirm with the User

Present the complete SKILL.md and ask:

"Here's the skill. Review it and let me know:
1. Does the description capture what this does?
2. Are the trigger phrases natural for you?
3. Anything to add or change in the rules?

Once you approve, I'll add it to the Summit Claude Skills repo and push it live."

## Phase 4: Deploy to Repository

After user confirmation, execute these steps automatically:

### 4a. Create the skill directory and file
```
skills/{skill-name}/SKILL.md
```

### 4b. Update the Summit Custom Skills table in README.md
Add a new row to the skills table with:
- Skill name (linked to the SKILL.md file)
- One-sentence description
- Trigger phrases

### 4c. Commit and push
```
git add skills/{skill-name}/SKILL.md README.md
git commit -m "feat: add {skill-name} skill — {one-line description}"
git push origin main
```

### 4d. Confirm to the user
"Done — `{skill-name}` is now live at:
https://github.com/ryankolean/summit-claude-skills/blob/main/skills/{skill-name}/SKILL.md

The README has been updated and it's ready to use."

## Rules

1. Never deploy without explicit user confirmation. Always show the full
   SKILL.md and get approval before touching the repo.

2. The SKILL.md must be self-contained. A fresh Claude instance with no
   conversation history should be able to follow it perfectly.

3. Frontmatter descriptions must be concise. Claude's skill scanner reads
   these to decide relevance — verbose descriptions reduce matching accuracy.

4. Suggest trigger phrases, don't dictate. The user knows what they'll
   naturally say. Offer 2-3 suggestions and ask if they fit.

5. If the source prompt has variables from prompt-architect, preserve them
   in the skill's Input section with clear descriptions.

6. Always include chaining information. Every skill connects to at least
   one other Summit skill — identify the natural chain.

7. After deployment, offer to update Claude's memory: "Want me to also add
   this to my memory so I recognize the trigger phrases automatically?"

## Chaining

- **prompt-architect → prompt-to-skill:** The primary chain. Build the prompt,
  test it, then install it as a permanent skill.
- **workflow-lock → prompt-to-skill:** A locked workflow that's used frequently
  enough to warrant becoming a full skill.
- **Any working prompt → prompt-to-skill:** This skill accepts input from any
  source, not just other Summit skills.
