---
name: socratic-check
description: >
  Pre-decision Socratic checklist — 7 prompts that force the user (and Claude)
  to challenge a position before committing. Anti-vending-machine habit:
  bring the thinking, let the prompts attack the premises. Activates when the
  user says "socratic check", "pre-decision", "before I commit", "stress my
  reasoning", or presents a decision and asks to pressure-test their own logic
  (not the idea itself — use devils-advocate for idea attacks).
---

# Socratic Check

A structured 7-prompt pre-decision checklist. Ryan brings a position; each
prompt challenges one layer of the reasoning. The output is not a verdict — it
is a sharper version of Ryan's own thinking with the weak joints exposed.

## When to Activate

**Manual triggers:**
- "Socratic check"
- "Run the 7 prompts"
- "Pre-decision check"
- "Before I commit"
- "Stress my reasoning"
- "Am I thinking about this right?"

**Auto-detect:**
- User states a decision they are about to make (not an idea to explore) and
  asks whether they are reasoning about it correctly.
- User says "I'm about to X" and signals hesitation.

**Do NOT activate when:**
- User wants the idea itself attacked → use `devils-advocate`.
- User wants requirements discovery → use `interrogate`.
- User wants to learn a concept → use `mentor-feynman`.

## The Anti-Pattern This Fixes

Vending-machine usage: user asks, Claude answers, user ships. Zero learning,
outsourced judgment, unchecked assumptions. Socratic prompting reverses the
polarity — the user states a position, Claude attacks premises, the user
rebuilds the position stronger or walks away from it.

## The 7 Prompts

Run one at a time. Wait for the user's answer before moving to the next.
Capture the user's answers verbatim — do not paraphrase. The point is to hear
the user's own reasoning, not Claude's summary of it.

### 1. Challenge assumptions

> "What are you assuming is true here that you have not verified? For each
> assumption, what is the cheapest way to check it before committing?"

Why: most failed decisions trace to an unexamined assumption treated as fact.

### 2. Test evidence

> "What is the strongest piece of evidence supporting this decision, and
> what is the strongest piece against it? If the 'against' evidence is weak
> or absent, why is that — have you actually looked?"

Why: confirmation bias. Most users can cite pro-evidence and go silent on con.

### 3. Premortem failure analysis

> "Fast-forward 6 months. This decision has failed badly. Write the post-mortem:
> what went wrong, what we missed, what signal we ignored. Be specific."

Why: anticipating failure modes is easier in the future tense than the present.

### 4. Counter-argument strength

> "Steelman the opposing position. Not a strawman — the strongest version of
> the argument for doing the opposite. Does your position still hold against
> that version?"

Why: if you can't argue against yourself, you don't understand your own position.

### 5. Bias detection

> "What bias might be driving this choice — sunk cost, novelty, recency,
> social proof, motivated reasoning? If you stripped the bias out, would you
> still make the same call?"

Why: biases are invisible until named. Forcing the name surfaces the pull.

### 6. Framing challenge

> "How is this decision framed? Who framed it that way? What frame would a
> competitor, a skeptic, or someone five years from now use? Does the choice
> change under a different frame?"

Why: the frame often decides the answer before the analysis begins.

### 7. Consequence evaluation

> "What are the second and third-order consequences — not just the direct
> outcome but what it enables, forecloses, or signals? What becomes harder
> after this? What becomes impossible?"

Why: first-order consequences are obvious. Second-order is where the real
cost or leverage lives.

## Output Format

After all 7 answers are captured, produce:

1. **Position (restated)** — one sentence, Ryan's own words.
2. **Strongest joint** — the part of the reasoning that held up under every prompt.
3. **Weakest joint** — the prompt where the reasoning wobbled most, and what
   needs to be shored up before committing.
4. **Open verification** — the cheapest check from prompt 1 that is still
   pending, if any.
5. **Recommendation** — commit / shore up then commit / kill / park.

Keep the output to under 150 words. The work is in the 7 prompts; the summary
is just the scoreboard.

## Modes

- **Fast** (default for Ryan, personal mode) — present all 7 prompts at once
  as a numbered list, let the user answer inline. Skip per-prompt explainers.
- **Guided** (candidate / customer mode) — one prompt at a time, with the "why"
  line shown. Wait for answer. Move on.

## Cross-skill integration

- If prompt 3 (premortem) surfaces a real failure mode, offer to escalate to
  `devils-advocate` for a full adversarial pass on that mode.
- If prompt 1 (assumptions) surfaces an unverified assumption that requires
  external research, offer to run a web search or pull internal docs.
- If the user tries to run this on a vague idea rather than a specific
  decision, redirect to `interrogate` first to pin down what is actually
  being decided.

## Source

@dailyprompter Instagram post 2026-03-21 — the framing (7 prompts that
challenge thinking) was public; the actual 7 prompts were gated behind an
engagement wall. Reconstructed from the principle plus related literature:
Edward Y. Chang's Socratic Method paper (arxiv 2303.08769), the
intellectual-sparring-partner template, and the "10 Prompts That Force AI to
Challenge Your Worst Ideas" toolkit. Card:
`~/mindspace/library/summit/try/2026-04-17-1146-socratic-prompting-7-prompts.md`.
