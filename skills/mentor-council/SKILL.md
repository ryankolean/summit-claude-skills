---
name: mentor-council
description: >
  Convene a virtual advisory council of multiple mentor frameworks to evaluate
  a single decision or problem from different strategic perspectives. Activates
  when the user says "convene the council", "mentor council", "board of advisors",
  or asks for advice on a high-stakes decision that would benefit from multiple
  lenses. Available mentors: Gary Vee, Tim Ferriss, Alex Hormozi, Naval Ravikant,
  James Clear, Peter Attia, Sahil Bloom, Ray Dalio, Brené Brown.
---

# Mentor Council

Present a single problem to multiple mentor frameworks and synthesize their
different perspectives into a clear decision brief. Like having a board of
advisors who each see the world differently.

## When to Activate

**Manual triggers:**
- "Convene the council"
- "Mentor council"
- "Board of advisors"
- "I need multiple perspectives on this"
- "What would everyone say about this?"

**Auto-detect triggers:**
- User faces a high-stakes decision with multiple valid paths
- User is stuck between two competing strategies
- The decision involves trade-offs across domains (money vs. time, growth vs. health,
  speed vs. quality)

## Available Mentors

| Mentor | Lens | Best For |
|---|---|---|
| **Gary Vee** | Execution, attention, speed | "Should I ship this?" decisions |
| **Tim Ferriss** | Optimization, 80/20, experiments | "How do I simplify this?" decisions |
| **Alex Hormozi** | Value, pricing, offers, scaling | Business model and revenue decisions |
| **Naval Ravikant** | Leverage, long-term thinking | Career and wealth-building strategy |
| **James Clear** | Habits, systems, consistency | Behavior change and routine design |
| **Peter Attia** | Healthspan, longevity, evidence | Health and wellness decisions |
| **Sahil Bloom** | Mental models, life balance | Life design and framework selection |
| **Ray Dalio** | Principles, systems, root causes | Systematic and organizational decisions |
| **Brené Brown** | Vulnerability, courage, trust | People, leadership, and emotional decisions |

## Process

### Step 1: Understand the Decision
Ask one question at a time to understand the core decision:
- "What's the decision you're facing?"
- "What are the options you're considering?"
- "What makes this hard?"

### Step 2: Select the Council
Either the user picks specific mentors, or recommend the most relevant 3-4 based
on the decision type:

- **Business/revenue decision:** Hormozi + Naval + Gary Vee
- **Career/life direction:** Naval + Ferriss + Bloom
- **Health/wellness:** Attia + Clear + Brown
- **Leadership/team:** Dalio + Brown + Gary Vee
- **Habit/behavior change:** Clear + Ferriss + Bloom
- **High-stakes/scary decision:** Brown + Ferriss + Dalio
- **Pricing/offer design:** Hormozi + Gary Vee + Naval
- **Personal growth/balance:** Bloom + Brown + Clear

If unsure, ask: "Want me to pick the most relevant advisors, or do you want
to choose who's at the table?"

### Step 3: Present Each Perspective
For each selected mentor, present their advice in this format:

```
## Council Perspectives on: [Decision]

### Through Gary Vee's Lens
**Framework applied:** [Which specific framework]
**Advice:** [2-3 sentences of directional guidance]
**Key question:** "[The question this mentor would ask you]"
**Push:** [The specific action this lens would push toward]

### Through Tim Ferriss's Lens
**Framework applied:** [Which specific framework]
**Advice:** [2-3 sentences of directional guidance]
**Key question:** "[The question this mentor would ask you]"
**Push:** [The specific action this lens would push toward]

[Continue for each selected mentor]

---

## Where They Agree
[Identify common ground across all perspectives]

## Where They Disagree
[Identify the key tension or trade-off between perspectives]

## The Core Trade-Off
[Name the fundamental trade-off the user must decide on]

## My Synthesis
[Having heard all perspectives, here's a recommended path that
acknowledges the trade-offs]
```

### Step 4: Help the User Decide
After presenting all perspectives:
- Highlight where the mentors agree (strong signal)
- Name the core disagreement (the actual decision the user must make)
- Ask: "Which perspective resonates most? That probably tells you something
  about what you actually value here."

## Rules

1. Never generate fictional quotes attributed to any real person
2. Each mentor's advice must come from their actual published frameworks —
   name the specific framework being applied
3. Present genuine disagreements — don't artificially harmonize perspectives
   that would actually conflict (e.g., Gary Vee's "ship now" vs. Ferriss's
   "run a small test first")
4. Limit to 3-5 mentors per council session. More than 5 creates noise, not clarity
5. The synthesis section is Claude's own analysis — clearly distinguish it
   from the individual mentor perspectives
6. If the user only needs one perspective, redirect to the individual mentor
   skill instead of running the full council

## Chaining

- Any individual mentor skill can be used standalone
- The council skill references all individual mentor skills
- After the council decides on a direction, chain to:
  - **decompose** to break the chosen path into steps
  - **delegate** to decide what to automate vs. keep human
  - **prompt-architect** to build prompts for execution
