---
name: design-doc-review
description: >
  Expert architect-level review system that takes a software design document and
  systematically refines, reworks, and hardens it into a foolproof implementation
  blueprint with no blind spots. Runs a multi-phase pipeline: ingest, structural
  audit, technical deep dive, continuity check, gap analysis with autoheal,
  adversarial final review, and hardened output. Activates when the user says
  "review this design doc", "harden this design", "audit this spec", "review my
  architecture", "design doc review", or when the user provides a software design
  document and asks for feedback, critique, improvements, or validation. Also
  activate when the user uploads a technical spec, RFC, architecture doc, or
  system design and wants it improved, stress-tested, or made implementation-ready.
  Use this skill even when the user simply says "review this" and the input is
  clearly a software design document.
---

# Design Doc Review

Takes a software design document at any maturity level and systematically hardens
it into an implementation-ready blueprint. The philosophy: design everything up
front. Every decision deferred to implementation is a bug, scope creep vector,
or miscommunication waiting to happen.

## When to activate

**Manual triggers:** "review this design doc", "harden this design", "audit this
spec", "review my architecture", "design doc review", "make this
implementation-ready", "stress test this spec", "is this spec complete?", "what's
missing from this design?"

**Auto-detect:** User provides a software design document and asks for feedback,
critique, or improvements; user uploads a technical spec, RFC, or architecture
doc and asks "is this ready to build?"

**Do NOT activate when:**
- User wants a design written from scratch (use `interrogate` + `architect-plan-for-dispatch`)
- User wants a code review, not a design review
- The document is not a software design (business plan, marketing doc)
- User says "just give me quick feedback" — give conversational feedback instead

## Input

Any form of software design document: formal RFC, informal spec, ADR, technical
proposal, system design with diagrams, partial designs. The skill calibrates
review depth to the document's maturity (see [reference/calibration-and-rules.md](reference/calibration-and-rules.md)).

## The seven-phase pipeline

Each phase produces visible output. Never skip a phase. Run them in order. Full
detail for each phase: [reference/phases.md](reference/phases.md).

| Phase | Purpose | Output |
|---|---|---|
| 1. Ingest and Comprehend | Build mental model, calibration checkpoint | System summary, components, design intent — wait for user confirmation |
| 2. Structural Audit | Check completeness against 16-point checklist | Per-section status (STRONG / WEAK / MISSING), structural score |
| 3. Technical Deep Dive | Evaluate quality across 6 dimensions | Findings ordered by severity (CRITICAL / HIGH / MEDIUM / LOW) |
| 4. Continuity and Consistency | Cross-reference all sections for contradictions | Contradictions list, terminology inconsistencies, continuity score |
| 5. Gap Analysis and Autoheal | Draft missing content, resolve contradictions | Autohealed sections marked inline, decisions flagged for author |
| 6. Adversarial Final Review | Five kill-question stress test | Per-question SURVIVES / PARTIALLY / FAILS, final verdict |
| 7. Hardened Output | Assemble final deliverable | Scorecard + hardened document + changelog |

The 16-point structural checklist used in Phase 2 is its own reference: [reference/canonical-checklist.md](reference/canonical-checklist.md).

## Workflow checklist

Copy this into your response and check off as you progress:

```
Design doc review pipeline:
- [ ] Phase 1: Ingest and Comprehend (calibration confirmed by user)
- [ ] Phase 2: Structural Audit
- [ ] Phase 3: Technical Deep Dive
- [ ] Phase 4: Continuity and Consistency
- [ ] Phase 5: Gap Analysis and Autoheal
- [ ] Phase 6: Adversarial Final Review
- [ ] Phase 7: Hardened Output (scorecard + document + changelog)
```

## Process transparency

Every phase MUST include a brief plain-English description of what's happening
and why before showing results. Write as if you're a senior architect walking a
colleague through your review. Don't just dump tables and scores — explain what
you're looking for, why it matters, and what you found.

Example lead-in (Phase 3):

> "Now I'm going through the actual design quality. Phase 2 told us what's
> missing from the document — this phase tells us what's wrong with what IS
> there. I'm reading each component with the question: if I had to implement
> this tomorrow, would I have enough information to build it correctly?"

## Calibrating review depth

Not every document needs the same scrutiny. Match depth to maturity:

| Document maturity | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 |
|---|---|---|---|---|---|
| Napkin sketch | Heavy | Light | Skip | Heavy (draft missing) | Quick sanity |
| Draft | Full | Calibrated | Full | Big gaps only | Full |
| Review-ready | Full | Exhaustive | Full | Full | Genuinely adversarial |
| Near-final | Light | Heavy | Heavy (devil in details) | Targeted | Primary value |

Full guidance and the 8 review rules: [reference/calibration-and-rules.md](reference/calibration-and-rules.md).

## Examples

- Good vs. bad findings (specific vs. vague): [examples/findings.md](examples/findings.md)
- How to chain with other skills: [examples/chaining.md](examples/chaining.md)
