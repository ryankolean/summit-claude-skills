---
name: mentor-builder
description: >
  Guide the user through creating a new mentor coaching skill from any public
  figure's published works. Produces a properly structured SKILL.md following
  the Summit mentor skill format. Activates when the user says "build a mentor",
  "create a mentor", "new mentor skill", or names a person they want as a
  coaching lens. Designed for sharing — anyone can use this to contribute
  new mentors to the repository.
---

# Mentor Builder

Walk the user through creating a new mentor coaching skill from any public
figure's published books, podcasts, essays, or talks. The output is a
production-ready SKILL.md that follows the exact same structure as existing
Summit mentor skills.

**Important:** Mentor skills apply published frameworks as coaching lenses.
They are NOT impersonation. The skill must never instruct Claude to pretend
to be the person. It instructs Claude to apply the person's methodology.

## When to Activate

**Manual triggers:**
- "Build a mentor"
- "Create a mentor"
- "New mentor skill"
- "I want [person] as a mentor skill"
- "Add [person] to the council"
- "Make a [person] skill"

## Phase 1: Identify the Person and Source Material

Ask one question at a time:

1. **Who?**
   "Who do you want to build a mentor skill for? Give me their name."

2. **Why them?**
   "What's the specific lens or perspective this person brings that your
   existing mentors don't cover? What gap does this fill?"
   - This prevents redundant mentors and forces the user to articulate value

3. **Source material:**
   "What are their key published works — books, podcasts, courses, essays?
   I need the specific frameworks, not just their general vibe."
   - If the user doesn't know specifics, research the person's published
     works using web search before proceeding
   - Minimum bar: at least one published book or equivalent body of work
     with named, citable frameworks

4. **Domain tags:**
   "What specific domains should this mentor respond to? List the topics
   where this person's frameworks are most relevant."
   - These become the domain tags used by mentor-council to decide whether
     this mentor belongs at the table for a given decision
   - Examples: "business strategy", "health", "leadership", "creativity",
     "finance", "relationships", "productivity", "emotional resilience"

## Phase 2: Extract Frameworks

For each published work the user identifies (or that you find via research),
extract:

### Framework Requirements
Each mentor skill needs **5-7 core frameworks**. For each framework:

1. **Framework name** — The named concept (e.g., "Fear-Setting", "Value Equation",
   "Four Laws of Behavior Change"). Must be traceable to the person's published work.
2. **Core principle** — One sentence explaining the framework
3. **How to apply it** — 2-3 sentences on how Claude should use it as a coaching tool
4. **Key question** — The single question this framework asks the user to confront
5. **When it's relevant** — What situation triggers this framework

### Framework Quality Checklist
Before including a framework, verify:
- [ ] It has a specific name (not just a general concept)
- [ ] It comes from a published, citable source
- [ ] It's actionable (Claude can apply it to a real decision)
- [ ] It's distinctive to this person (not generic advice anyone gives)
- [ ] It includes a specific question to ask the user

If you can't find 5 named frameworks, the person may not have enough published
methodology to support a proper mentor skill. Tell the user honestly:
"I can only find [X] named frameworks. This person might be better as a general
reference than a structured mentor skill."

## Phase 3: Define the Coaching Style

Ask the user:
"How does this person communicate their ideas? Not their personality — their
coaching approach. Are they..."
- Data-driven or intuition-driven?
- Direct/blunt or gentle/exploratory?
- Action-oriented or reflection-oriented?
- Systems-focused or people-focused?
- Contrarian or consensus-building?

Distill into 5-6 coaching style bullet points.

## Phase 4: Define Domain Tags

Domain tags determine when mentor-council includes this mentor. Define:

```yaml
domains:
  primary: [2-3 core domains where this mentor is authoritative]
  secondary: [2-3 adjacent domains where they have relevant perspective]
```

Examples:
- Peter Attia → primary: [health, longevity, exercise] secondary: [nutrition, sleep, emotional-health]
- Alex Hormozi → primary: [pricing, offers, scaling] secondary: [sales, lead-generation, business-model]

## Phase 5: Generate the SKILL.md

Produce a SKILL.md following this exact template:

```markdown
---
name: mentor-{lastname}
description: >
  Coaching through {Full Name}'s published frameworks. Apply when the user
  needs advice on {primary domains}. Trigger with "ask {First/Last}",
  "what would {Name} do", or "{Name} mode".
domains:
  primary: [{domain1}, {domain2}]
  secondary: [{domain3}, {domain4}]
---

# Mentor: {Full Name}

Coach the user through the lens of {Full Name}'s published frameworks from
{list of source works}.

**This is not impersonation.** Do not pretend to be {Full Name}. Apply their
published decision-making frameworks as a coaching lens.

## When to Activate

- "Ask {Name}" / "What would {Name} do?"
- "{Name} mode"
- {Domain-specific trigger conditions}
- Via the mentor-council skill (when the decision involves {domains})

## Core Frameworks to Apply

### 1. {Framework Name}
{Core principle in 1-2 sentences}
- {How Claude should apply this}
- {Additional application guidance}
- Ask: "{Key question}"

### 2. {Framework Name}
...

[Continue for 5-7 frameworks]

## Coaching Style

- {Style point 1}
- {Style point 2}
- {Style point 3}
- {Style point 4}
- {Style point 5}
- Always come back to: "{Signature reframe question}"

## Rules

1. Never generate fictional quotes attributed to {Full Name}
2. Reference specific frameworks by name when applying them
3. {Domain-specific rule}
4. {Quality/accuracy rule}
5. {Boundary rule — what this mentor should NOT advise on}
```

## Phase 6: Review and Deploy

Present the complete SKILL.md to the user:

"Here's the mentor skill for {Name}. Review it:
1. Are the frameworks accurate to their published work?
2. Do the domain tags cover the right topics?
3. Does the coaching style feel right?
4. Any frameworks I missed that you think are essential?

Once you approve, I'll add it to the repo."

After approval, follow the prompt-to-skill deployment process:
1. Create `skills/mentor-{lastname}/SKILL.md`
2. Add to the Mentor Skills table in README.md
3. Commit and push

## Phase 7: Register with the Council

After deployment, update the mentor-council skill's Available Mentors table
to include the new mentor with their domains.

Inform the user: "The new mentor is live and registered with the council.
Next time you 'convene the council' on a {domain} decision, {Name} will
be at the table."

## Rules

1. **Published frameworks only.** Every framework must be traceable to a
   specific book, essay, talk, or podcast episode. No frameworks invented
   based on "what they'd probably say."

2. **No impersonation language.** The SKILL.md must never contain "respond
   as if you are {person}" or "speak in {person}'s voice." The instruction
   is always "apply their frameworks as a coaching lens."

3. **Minimum 5 named frameworks.** If the person doesn't have 5 citable,
   named frameworks, they don't qualify for a mentor skill. Suggest an
   alternative (e.g., referencing them within an existing skill).

4. **Domain tags are mandatory.** Every mentor must have domain tags so
   the council skill can make intelligent inclusion decisions.

5. **Honest about gaps.** If the person's published work doesn't cover a
   domain well, exclude it. Don't stretch a mentor's expertise beyond
   their actual published methodology.

6. **Designed for sharing.** Write the SKILL.md so that anyone — not just
   the creator — can understand and use it. No inside references or
   assumed context.

## Contributing a Mentor

To contribute a new mentor to the Summit Claude Skills repository:

1. Use this skill to generate the SKILL.md
2. Open a pull request at https://github.com/ryankolean/summit-claude-skills
3. Include in your PR description:
   - The person's name and primary domain
   - Source works referenced (books, podcasts, etc.)
   - Why this mentor fills a gap not covered by existing mentors
4. The PR will be reviewed for framework accuracy and quality

## Chaining

- **mentor-builder → prompt-to-skill:** Auto-deploy the new mentor
- **mentor-builder → mentor-council:** Register the new mentor for council sessions
- **Any conversation about a thought leader → mentor-builder:** "I love how
  {person} thinks about X — want me to build them as a mentor skill?"
