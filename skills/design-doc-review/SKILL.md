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

Take a software design document — at any stage of maturity — and systematically
harden it into an implementation-ready blueprint that a development team can
execute with zero ambiguity and zero blind spots. Think of this as a principal
engineer's design review, compressed into a structured pipeline.

The philosophy: **design everything up front.** Every decision deferred to
implementation is a bug waiting to happen, a scope creep vector, or a
miscommunication between engineer and spec. This skill forces those decisions
to the surface before a single line of code is written.

## When to Activate

**Manual triggers:**
- "Review this design doc"
- "Harden this design"
- "Audit this spec"
- "Review my architecture"
- "Design doc review"
- "Make this implementation-ready"
- "Stress test this spec"
- "Is this spec complete?"
- "What's missing from this design?"

**Auto-detect triggers:**
- User provides a software design document and asks for feedback or improvements
- User uploads a technical spec, RFC, or architecture doc and asks for critique
- User shares a system design and asks "is this ready to build?"

**Do NOT activate when:**
- The user wants a design written from scratch (use interrogate + architect-plan-for-dispatch instead)
- The user wants a code review, not a design review
- The document is not a software design (e.g., a business plan, marketing doc)
- The user says "just give me quick feedback" — give conversational feedback instead

## Input

Accepts any form of software design document:
- Formal RFC or design doc (structured sections, diagrams, interface definitions)
- Informal spec (prose description of what to build and how)
- Architecture decision record (ADR)
- Technical proposal or feasibility study
- System design with diagrams (describe diagrams textually if images aren't parseable)
- Partial designs — the skill identifies what's missing and fills gaps

No specific format required. The skill adapts its review depth to the document's
maturity level. A napkin sketch gets a different treatment than a 40-page RFC.

## The Review Pipeline

The pipeline has seven phases. Each phase produces visible output so the user
can follow along and understand what's happening. Never skip a phase — each
one catches a different class of problem. Run them in order.

---

### Phase 1: Ingest and Comprehend

**What happens:** Read the entire document. Build a mental model of what the
system is, what problem it solves, how the pieces fit together, and what the
author's intent is.

**Output to user:**

```
PHASE 1: INGEST AND COMPREHEND
================================
Document: [title or filename]
Type: [RFC / Spec / ADR / Proposal / Informal Design / Other]
Maturity: [Napkin / Draft / Review-Ready / Near-Final]

System Summary:
[2-4 sentences describing what this system does, who it serves, and the
core architectural approach, in your own words. This proves you understood
it — if you got it wrong, the user catches it here before you review
against a misunderstanding.]

Key Components Identified:
- [Component 1]: [one-line description]
- [Component 2]: [one-line description]
- ...

Design Intent (as I understand it):
[1-2 sentences on what the author is optimizing for — performance? simplicity?
extensibility? correctness? This frames the review criteria.]
```

**Why this matters:** If the reviewer misunderstands the system, every
subsequent phase produces noise. This is a calibration checkpoint. Ask the
user to confirm: "Did I get this right, or am I misreading something?"
Wait for confirmation before proceeding.

---

### Phase 2: Structural Audit

**What happens:** Check the document's structure against a canonical design
doc checklist. This is not about whether the design is *good* — it's about
whether the design is *complete*. A brilliant architecture with no error
handling section is still a gap.

**Canonical Checklist:**

Evaluate presence AND quality of each section. A section that exists but
is hand-wavy ("errors will be handled appropriately") counts as WEAK, not
PRESENT.

| # | Section | What It Should Cover |
|---|---------|---------------------|
| 1 | Problem Statement | What problem this solves, why it matters, who's affected |
| 2 | Goals and Non-Goals | Explicit boundaries — what this does AND does not do |
| 3 | Background / Context | Prior art, existing system state, why now |
| 4 | High-Level Architecture | System components, their relationships, data flow |
| 5 | Detailed Design | Per-component behavior, algorithms, data structures |
| 6 | API / Interface Contracts | Endpoints, function signatures, message formats, schemas |
| 7 | Data Model | Storage schema, relationships, migrations, lifecycle |
| 8 | Error Handling Strategy | Failure modes, retry logic, degradation, circuit breakers |
| 9 | Security Considerations | Auth, authz, input validation, secrets, attack surfaces |
| 10 | Scalability and Performance | Load expectations, bottlenecks, capacity plan |
| 11 | Observability | Logging, metrics, alerting, tracing, dashboards |
| 12 | Testing Strategy | Unit, integration, e2e, load, chaos — what and how |
| 13 | Migration / Rollout Plan | Phased rollout, feature flags, rollback procedure |
| 14 | Dependencies and Risks | External dependencies, technical risks, mitigation |
| 15 | Open Questions | Unresolved decisions the author is aware of |
| 16 | Alternatives Considered | What was rejected and why |

**Output to user:**

```
PHASE 2: STRUCTURAL AUDIT
============================
Checking document completeness against 16-point canonical checklist.

 #  | Section                    | Status  | Notes
----|----------------------------|---------|----------------------------------
  1 | Problem Statement          | STRONG  | Clear, well-motivated
  2 | Goals and Non-Goals        | MISSING | No section found
  3 | Background / Context       | WEAK    | Mentions prior system but no detail
  ...
 16 | Alternatives Considered    | MISSING | —

Structural Score: X/16 sections present (Y strong, Z weak)

Critical Gaps:
- [List the MISSING and WEAK sections that most impact implementation clarity]
```

This phase is purely diagnostic. No fixes yet — that happens in Phase 5.

---

### Phase 3: Technical Deep Dive

**What happens:** Now evaluate the *quality* of what IS present. Read each
section with the eye of a principal engineer who has to sign off on this
before the team starts building. Challenge every design decision.

**Review Dimensions:**

For each significant design element, evaluate against these lenses:

**Correctness:** Does the logic hold? Are there race conditions, ordering
assumptions, or invariant violations? Would this actually work as described?

**Completeness:** Are all code paths covered? What about the unhappy path?
Edge cases? Boundary conditions? Empty states? Concurrent access?

**Consistency:** Do the pieces fit together? Does the API contract match the
data model? Does the error handling strategy align with the retry logic?
Do the stated goals match the actual design?

**Feasibility:** Can this be built with the stated tech stack and constraints?
Are there hidden complexity cliffs? Does the timeline/scope math work?

**Operational Readiness:** If this ships tomorrow, can the on-call team
support it? Are failure modes observable? Can you rollback? Debug in production?

**Security Posture:** Beyond the security section — are there injection points,
privilege escalation paths, data exposure risks, or OWASP-style vulnerabilities
embedded in the design itself?

**Output to user:**

```
PHASE 3: TECHNICAL DEEP DIVE
===============================
Reviewing design quality across 6 dimensions.

FINDING 1: [Severity: CRITICAL / HIGH / MEDIUM / LOW]
Dimension: [which review dimension]
Location: [which section/component of the design]
Issue: [clear description of the problem]
Impact: [what goes wrong if this isn't addressed]
Evidence: [quote or reference the specific part of the doc]

FINDING 2: ...
[Continue for all findings]

Summary:
- Critical: X findings
- High: X findings
- Medium: X findings
- Low: X findings

The critical and high findings must be resolved before this design is
implementation-ready.
```

Order findings by severity, then by the order they appear in the document.
Be specific — "the error handling is insufficient" is not a finding. "The
retry logic in Section 4.2 retries on all 5xx errors including 501 Not
Implemented, which will never succeed and wastes retry budget" is a finding.

---

### Phase 4: Continuity and Consistency Check

**What happens:** Cross-reference every section against every other section.
Design documents rot from internal contradictions — Section 3 says "eventual
consistency" but Section 6 assumes strong consistency. Section 4 defines a
field as optional but Section 7's validation rejects requests without it.

This phase catches the class of bugs that come from a design written over
multiple sessions, by multiple authors, or after scope changes that updated
some sections but not others.

**What to cross-check:**

- API contracts vs. data model (do types match? are all fields accounted for?)
- Error handling strategy vs. individual component descriptions (consistent?)
- Goals/non-goals vs. detailed design (does the design actually achieve the goals? does it accidentally cover non-goals?)
- Security section vs. API design (are all endpoints covered? auth on every mutation?)
- Performance targets vs. architecture (can the architecture actually hit those numbers?)
- Migration plan vs. data model changes (does the migration cover all schema diffs?)
- Testing strategy vs. identified risks (are the highest risks covered by tests?)
- Component dependencies vs. failure modes (what happens when dependency X goes down?)
- Terminology consistency (is the same concept called the same thing everywhere?)
- Sequence/ordering assumptions across components

**Output to user:**

```
PHASE 4: CONTINUITY AND CONSISTENCY CHECK
============================================
Cross-referencing all sections for internal contradictions.

CONTRADICTION 1:
Sections: [Section A] vs [Section B]
Issue: [specific description of the inconsistency]
Resolution needed: [which section should be the source of truth, or both need updating]

CONTRADICTION 2: ...

TERMINOLOGY INCONSISTENCIES:
- "[Term A]" in Section X vs "[Term B]" in Section Y — same concept, different names
- ...

Continuity Score: [CLEAN / MINOR ISSUES / SIGNIFICANT CONTRADICTIONS / STRUCTURALLY INCOHERENT]
```

If the document is clean, say so. Don't invent contradictions.

---

### Phase 5: Gap Analysis and Autoheal

**What happens:** This is where the skill earns its keep. Take every gap
identified in Phases 2-4 and *draft the missing content*. Don't just say
"add an error handling section" — write the error handling section.

**Autoheal priority order:**
1. Critical findings from Phase 3 (fix the design, not just the doc)
2. Missing sections from Phase 2 (draft new sections)
3. Contradictions from Phase 4 (resolve with a consistent answer)
4. High findings from Phase 3
5. Weak sections from Phase 2 (strengthen with specifics)
6. Medium/Low findings (address in-line)

**Autoheal rules:**

- **Mark every addition.** Wrap all new content with clear markers so the user
  can distinguish original content from autohealed content:
  ```
  <!-- AUTOHEALED: [reason] -->
  [new content]
  <!-- /AUTOHEALED -->
  ```

- **Preserve author intent.** When filling gaps, extend the author's design
  philosophy — don't impose a different one. If the author chose REST over
  GraphQL, autoheal the error handling in REST idioms, not GraphQL error
  extensions.

- **Be concrete, not generic.** "Implement rate limiting" is not autohealed
  content. "Rate limit the /api/v1/submit endpoint to 100 requests per minute
  per authenticated user, using a sliding window counter in Redis with key
  pattern `ratelimit:{user_id}:{endpoint}`, returning HTTP 429 with a
  Retry-After header" is autohealed content.

- **Flag uncertainty.** If autohealing requires making a design decision the
  author should make, flag it explicitly:
  ```
  <!-- AUTOHEAL: DECISION REQUIRED -->
  Two viable approaches exist here:
  Option A: [description] — better for [tradeoff]
  Option B: [description] — better for [tradeoff]
  Recommendation: Option [X] because [reasoning]
  <!-- /AUTOHEAL: DECISION REQUIRED -->
  ```

- **Don't autoheal what you can't justify.** If a gap requires domain
  knowledge you don't have (e.g., specific compliance requirements, proprietary
  system internals), flag it as NEEDS AUTHOR INPUT rather than guessing.

**Output to user:**

```
PHASE 5: GAP ANALYSIS AND AUTOHEAL
=====================================
Addressing X gaps across Phases 2-4.

AUTOHEAL 1: [Gap description]
Source: Phase [N], Finding/Gap [reference]
Action: [DRAFTED NEW SECTION / REVISED EXISTING / RESOLVED CONTRADICTION / FLAGGED FOR AUTHOR]
Content: [The actual drafted content, or a summary if the content is long]

AUTOHEAL 2: ...

Autoheal Summary:
- New sections drafted: X
- Existing sections strengthened: X
- Contradictions resolved: X
- Decisions flagged for author: X
- Gaps requiring author domain knowledge: X
```

---

### Phase 6: Adversarial Final Review

**What happens:** Take the now-healed document and attack it as if you're a
hostile reviewer trying to block the design from being approved. This is the
"would I bet my production uptime on this?" check.

**The Five Kill Questions:**

Every design must survive these. If it can't answer all five clearly, it's
not ready.

1. **"What's the blast radius?"** — If the worst-case failure happens, what's
   the impact? Is it contained? Can you recover? How fast?

2. **"What happens at 10x scale?"** — Does the design degrade gracefully or
   collapse? Where's the first bottleneck? Is there a capacity cliff?

3. **"How does an attacker exploit this?"** — What's the most creative abuse
   path? Social engineering? API abuse? Data exfiltration? Privilege escalation?

4. **"What can't you monitor?"** — Are there blind spots in observability?
   Silent failures? Corruption that won't trigger alerts until it's too late?

5. **"What did you assume that isn't written down?"** — Implicit assumptions
   about infrastructure, team capabilities, third-party SLAs, user behavior,
   data volumes, network conditions. If it's not in the doc, it's a risk.

**Output to user:**

```
PHASE 6: ADVERSARIAL FINAL REVIEW
====================================
Stress-testing the hardened document against five kill questions.

KILL QUESTION 1: "What's the blast radius?"
Assessment: [SURVIVES / PARTIALLY SURVIVES / FAILS]
Analysis: [Specific assessment with evidence from the document]
Remaining risk: [What's still exposed, if anything]

KILL QUESTION 2: ...
[Repeat for all five]

ADDITIONAL ADVERSARIAL FINDINGS:
[Any issues discovered during the adversarial pass that weren't caught
in earlier phases. These tend to be systemic or cross-cutting concerns.]

Final Adversarial Verdict:
[IMPLEMENTATION-READY / NEEDS REVISION / NEEDS SIGNIFICANT REWORK]

Confidence Level: [How confident are you that a team could build this
from the document alone, with no follow-up questions?]
- HIGH: 90%+ of implementation decisions are resolved in the document
- MEDIUM: 70-89% resolved, some decisions will need to be made during implementation
- LOW: Below 70%, significant design work remains
```

---

### Phase 7: Hardened Output

**What happens:** Assemble the final deliverable. Produce the complete
hardened document with all autohealed content integrated, plus a review
summary the user can scan before reading the full doc.

**Deliverables:**

1. **Review Scorecard** — A single-page summary of the entire review:

```
DESIGN DOC REVIEW: FINAL SCORECARD
=====================================
Document: [title]
Reviewed: [timestamp]
Original Maturity: [from Phase 1]
Final Maturity: [after hardening]

Phase Results:
  Phase 1 (Comprehend):    [CONFIRMED]
  Phase 2 (Structure):     [X/16 sections — Y strong, Z weak, W missing]
  Phase 3 (Deep Dive):     [X critical, Y high, Z medium, W low findings]
  Phase 4 (Continuity):    [CLEAN / MINOR / SIGNIFICANT / INCOHERENT]
  Phase 5 (Autoheal):      [X gaps addressed, Y flagged for author]
  Phase 6 (Adversarial):   [IMPLEMENTATION-READY / NEEDS REVISION / NEEDS REWORK]

Confidence Level: [HIGH / MEDIUM / LOW]

Author Action Items:
  1. [Decision required: brief description] — see Phase 5, Autoheal #N
  2. [Domain knowledge needed: brief description] — see Phase 5, Autoheal #N
  3. ...

Top 3 Improvements Made:
  1. [Brief description of the most impactful autoheal]
  2. [Brief description]
  3. [Brief description]
```

2. **Hardened Document** — The full design document with all autohealed
   content integrated inline, preserving the autoheal markers so the
   author can identify and review all additions. Output as a markdown file.

3. **Changelog** — A diff-style list of every change made, organized by
   phase:

```
CHANGELOG
==========
Phase 2 additions:
  + Added "Goals and Non-Goals" section
  + Added "Alternatives Considered" section

Phase 3 fixes:
  ~ Revised retry logic to exclude non-retryable status codes
  ~ Added circuit breaker specification to database connection pool

Phase 4 resolutions:
  ~ Aligned terminology: "user" → "authenticated principal" throughout
  ~ Resolved consistency model contradiction between Sections 3 and 6

Phase 5 drafts:
  + Drafted error handling strategy (Section 8)
  + Drafted observability section with metric definitions (Section 11)
  ! DECISION REQUIRED: Rate limiting approach (Section 6, API Contracts)
  ! NEEDS AUTHOR INPUT: Compliance requirements for PII handling (Section 9)
```

## Output Format

The final deliverables should be produced as files:
- **Scorecard:** Presented inline in conversation for immediate readability
- **Hardened Document:** Saved as a markdown file (or matching the input format)
- **Changelog:** Appended to the end of the hardened document as an appendix

If the input document is a Word doc, PDF, or other format, output the hardened
version as markdown with a note that the user can convert it back to the
original format.

## Process Transparency

Every phase MUST include a brief plain-English description of what's happening
and why before showing results. The user is following along — don't just dump
tables and scores. Explain what you're looking for, why it matters, and what
you found. Write as if you're a senior architect walking a colleague through
your review.

Example lead-in (Phase 3):
> "Now I'm going through the actual design quality. Phase 2 told us what's
> missing from the document — this phase tells us what's wrong with what IS
> there. I'm reading each component with the question: if I had to implement
> this tomorrow, would I have enough information to build it correctly?"

## Calibrating Review Depth

Not every document needs the same level of scrutiny. Calibrate based on:

- **Napkin-stage docs:** Focus on Phase 2 (structural gaps) and Phase 5
  (drafting missing sections). Light touch on Phase 3 — the design isn't
  detailed enough to deep-dive. Skip Phase 4 (nothing to cross-reference).
  Phase 6 is a quick sanity check, not a full adversarial review.

- **Draft-stage docs:** Full pipeline, but calibrate Phase 3 findings to
  "things that would be costly to fix later" not "every possible nitpick."
  Phase 5 autoheals focus on the biggest gaps.

- **Review-ready docs:** Full pipeline at maximum depth. Phase 3 should be
  exhaustive. Phase 6 should be genuinely adversarial.

- **Near-final docs:** Lighter Phase 2 (structure should be settled). Heavy
  Phase 3 and Phase 4 (the devil is in the details and contradictions). Phase 6
  is the primary value — the design has been reviewed before, so fresh
  adversarial eyes are what's needed.

## Rules

1. **Never skip a phase.** Even if a phase finds nothing, report that it found
   nothing. A clean phase is valuable information — it means that class of
   problem isn't present.

2. **Be specific, not vague.** "The security section could be stronger" is not
   a finding. "The API accepts user-supplied SQL fragments in the `filter`
   query parameter (Section 6.3) with no parameterization, creating a SQL
   injection vector" is a finding.

3. **Preserve the author's voice.** Autohealed content should read like the
   original author wrote it. Match their level of formality, their naming
   conventions, their documentation style.

4. **Distinguish opinion from defect.** If you'd do it differently but the
   author's approach works, say so: "I'd prefer X, but the author's choice
   of Y is valid because Z." Only flag it as a finding if it's objectively
   wrong or has a concrete risk.

5. **Autohealed content is a draft, not gospel.** Always tell the user:
   these are starting points for the sections that were missing. The author
   knows their domain better than the reviewer. Autohealed content should be
   reviewed, not blindly accepted.

6. **Don't inflate severity.** A finding is CRITICAL only if it would cause
   data loss, security breach, system-wide outage, or make the design
   unimplementable. HIGH means production issues that aren't catastrophic.
   MEDIUM means suboptimal design that works but has cost. LOW means style,
   best-practice suggestions, or minor improvements.

7. **The user decides when it's done.** After Phase 7, the user may want
   another pass, may want to address the flagged decisions and re-review,
   or may be satisfied. Offer to re-run specific phases on the revised
   document if they make changes.

8. **Time-box your depth.** If the document is very large (30+ pages), call
   out that you're doing a breadth-first pass and offer to do a deep dive on
   specific sections the user is most concerned about.

## Chaining

- **interrogate → design-doc-review:** If the user says "review this" but
  the document is ambiguous about its own purpose, trigger interrogate first
  to understand the user's expectations for the review.
- **design-doc-review → architect-plan-for-dispatch:** After the design is
  hardened, the user may want to convert it into a Dispatch execution plan.
- **design-doc-review → devils-advocate:** If the user wants deeper adversarial
  pressure on a specific design decision, hand off to devils-advocate for
  focused hardening of that one aspect.

## Examples

**Good Phase 1 calibration check:**

> "Here's what I'm seeing: this is a microservices migration plan for your
> payment processing system, moving from a monolith to three bounded services
> (orders, payments, notifications) communicating over an event bus. The design
> optimizes for independent deployability over raw performance. Did I get that
> right?"

**Good Phase 3 finding (specific, actionable):**

> FINDING 3: [Severity: HIGH]
> Dimension: Completeness
> Location: Section 5.2 — Event Bus Design
> Issue: The event schema includes a `timestamp` field but does not specify
> timezone or format. Consumers will parse this inconsistently — some as UTC,
> some as local time, some as epoch milliseconds.
> Impact: Silent data corruption in any time-based logic downstream (billing
> cycles, SLA calculations, audit logs).
> Evidence: "Events include a timestamp field" (Section 5.2, paragraph 3)

**Good autoheal (concrete, preserves author style):**

> AUTOHEAL 4: Timestamp specification
> Source: Phase 3, Finding 3
> Action: REVISED EXISTING
> Content: "Events include a `timestamp` field formatted as ISO 8601 with
> explicit UTC offset (e.g., `2026-04-15T14:30:00Z`). All producers MUST
> emit UTC. Consumers MUST NOT assume local timezone. The event bus rejects
> messages with non-conforming timestamps (HTTP 422, error code
> `INVALID_TIMESTAMP_FORMAT`)."

**Bad finding (vague, unhelpful):**

> "The error handling could use more detail."
> (NEVER do this. Say exactly what's missing and draft the content.)

**Bad autoheal (generic, doesn't match the design):**

> "Add appropriate error handling for all API endpoints."
> (NEVER do this. Write the actual error handling spec for the actual endpoints.)
