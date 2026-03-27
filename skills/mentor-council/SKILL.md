---
name: mentor-council
description: >
  Convene a virtual advisory council to evaluate a decision from multiple
  strategic perspectives. Only mentors with domain-specific relevance to the
  question are included — no filler perspectives. Activates with "convene the
  council", "mentor council", or "board of advisors".
---

# Mentor Council

Present a single problem to multiple mentor frameworks and synthesize their
perspectives. **Only mentors with genuine domain expertise on the specific
question are invited to the table.** A mentor with nothing relevant to say
stays silent.

## When to Activate

**Manual triggers:**
- "Convene the council"
- "Mentor council"
- "Board of advisors"
- "I need multiple perspectives on this"

**Auto-detect triggers:**
- User faces a high-stakes decision with multiple valid paths
- User is stuck between two competing strategies
- The decision spans multiple domains (money vs. time, growth vs. health)

## Mentor Domain Registry

Each mentor has primary and secondary domains. **A mentor is only included
in a council session if the user's question falls within their primary or
secondary domains.** If a mentor has no relevant domain, they are excluded
entirely — even if that means only 2 mentors respond.

| Mentor | Primary Domains | Secondary Domains |
|---|---|---|
| **Gary Vee** | content-strategy, personal-branding, execution, attention | entrepreneurship, social-media, marketing |
| **Tim Ferriss** | productivity, lifestyle-design, skill-acquisition, optimization | entrepreneurship, health, decision-making |
| **Alex Hormozi** | pricing, offers, scaling, revenue | sales, lead-generation, business-model, entrepreneurship |
| **Naval Ravikant** | wealth-creation, leverage, career-strategy, philosophy | investing, startups, decision-making, long-term-thinking |
| **James Clear** | habits, behavior-change, systems, consistency | productivity, identity, self-improvement, goal-setting |
| **Peter Attia** | health, longevity, exercise, nutrition | sleep, emotional-health, evidence-based-medicine, aging |
| **Sahil Bloom** | mental-models, decision-making, life-design, curiosity | personal-growth, time-management, wealth, career-strategy |
| **Ray Dalio** | principles, organizational-design, systems-thinking, transparency | investing, leadership, macro-economics, risk-management |
| **Brené Brown** | vulnerability, courage, leadership, trust | relationships, emotional-resilience, shame, communication, difficult-conversations |

**New mentors** created via the mentor-builder skill must include domain tags
to be registered here.

## Domain Matching Process

### Step 1: Understand the Decision
Ask one question at a time:
- "What's the decision you're facing?"
- "What are the options you're considering?"
- "What makes this hard?"

### Step 2: Identify Domains
From the user's answer, extract the 2-4 domains this decision touches.
Examples:
- "Should I raise my consulting rate?" → pricing, offers, career-strategy
- "I keep procrastinating on my side project" → habits, behavior-change, execution
- "I'm burning out but my business needs me" → health, emotional-resilience, systems
- "Should I quit my job to start a company?" → career-strategy, wealth-creation, courage, lifestyle-design

### Step 3: Match Mentors to Domains
For each identified domain, find mentors where it appears in their primary
or secondary domains. A mentor must match **at least one domain** to be included.

**Scoring:**
- Primary domain match = strong inclusion (this mentor leads on this topic)
- Secondary domain match = supporting inclusion (this mentor has relevant perspective)
- No domain match = **excluded entirely**

### Step 4: Confirm or Override
Present the selected council:
"For this decision about [topic], I'd bring in [Mentor A] (primary: {domain}),
[Mentor B] (primary: {domain}), and [Mentor C] (supporting: {domain}).
Anyone you want to add or remove?"

The user can always manually add or remove mentors. Domain matching is a
default, not a constraint.

### Step 5: Present Each Perspective
For each included mentor:

```
## Council Perspectives on: [Decision]

### [Mentor Name] — Primary: [matched domain]
**Framework applied:** [Specific named framework from their published work]
**Diagnosis:** [How this framework reads the user's situation — 2-3 sentences]
**Key question:** "[The one question this mentor would push the user to answer]"
**Recommended action:** [Specific next step this lens would push toward]

[Repeat for each included mentor]

---

## Where They Agree
[Common ground across all included perspectives — this is a strong signal]

## Where They Disagree
[The genuine tension between perspectives — name the trade-off honestly]

## The Core Trade-Off
[One sentence: the fundamental choice the user must make]

## Synthesis
[Claude's own recommendation, informed by all perspectives, with the trade-off
acknowledged. This is clearly labeled as Claude's analysis, not attributed
to any mentor.]
```

### Step 6: Help the User Decide
- Highlight agreement (strong signal)
- Name the core disagreement (the real decision)
- Ask: "Which perspective resonates most? That usually reveals what you
  actually value here."

## Edge Cases

**Only 1 mentor matches:**
Redirect to the individual mentor skill. "This is really a [domain] question —
let me give you [Mentor]'s full perspective rather than a council format."

**No mentors match:**
Be honest. "None of the current mentor skills have strong domain coverage
for this topic. Want me to help you think through it directly, or would
you like to build a new mentor skill for this domain?" (Chain to mentor-builder.)

**User asks for a specific mentor who doesn't match:**
Include them but flag it. "[Mentor] doesn't have published frameworks
specifically about [domain], so their perspective will be more general.
Want me to include them anyway?"

**Decision spans 5+ domains:**
Limit to the 4 strongest domain matches. More than 4 perspectives creates
noise. Ask: "This touches a lot of areas. I'd focus on [4 mentors] — the
ones with the most direct expertise. Good?"

## Rules

1. **Domain match is mandatory.** Never include a mentor just to fill seats.
   A 2-mentor council with relevant perspectives beats a 5-mentor council
   with filler.

2. Never generate fictional quotes attributed to any real person.

3. Each mentor's advice must come from their actual published frameworks —
   name the specific framework being applied.

4. Present genuine disagreements. Don't harmonize perspectives that would
   actually conflict.

5. The synthesis section is Claude's own analysis — clearly distinguish it
   from individual mentor perspectives.

6. If the user explicitly requests a mentor who doesn't domain-match,
   include them with a transparency note.

## Chaining

- Any individual mentor skill can be used standalone
- **mentor-builder → mentor-council:** New mentors are automatically registered
- After the council decides on a direction, chain to:
  - **decompose** to break the chosen path into steps
  - **delegate** to decide what to automate vs. keep human
  - **prompt-architect** to build prompts for execution
