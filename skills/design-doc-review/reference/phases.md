# Design Doc Review — Phase Details

## Contents
- Phase 1: Ingest and Comprehend
- Phase 2: Structural Audit
- Phase 3: Technical Deep Dive
- Phase 4: Continuity and Consistency Check
- Phase 5: Gap Analysis and Autoheal
- Phase 6: Adversarial Final Review
- Phase 7: Hardened Output

---

## Phase 1: Ingest and Comprehend

**What happens:** Read the entire document. Build a mental model of what the system is, what problem it solves, how the pieces fit together, and what the author's intent is.

**Output to user:**

```
PHASE 1: INGEST AND COMPREHEND
================================
Document: [title or filename]
Type: [RFC / Spec / ADR / Proposal / Informal Design / Other]
Maturity: [Napkin / Draft / Review-Ready / Near-Final]

System Summary:
[2-4 sentences describing what this system does, who it serves, and the
core architectural approach, in your own words.]

Key Components Identified:
- [Component 1]: [one-line description]
- [Component 2]: [one-line description]

Design Intent (as I understand it):
[1-2 sentences on what the author is optimizing for — performance? simplicity?
extensibility? correctness?]
```

**Why this matters:** If the reviewer misunderstands the system, every subsequent phase produces noise. Ask the user to confirm: "Did I get this right, or am I misreading something?" Wait for confirmation before proceeding.

---

## Phase 2: Structural Audit

**What happens:** Check the document's structure against the canonical 16-point checklist. This is not about whether the design is *good* — it's about whether the design is *complete*.

The 16 sections to evaluate: [canonical-checklist.md](canonical-checklist.md).

A section that exists but is hand-wavy ("errors will be handled appropriately") counts as WEAK, not PRESENT.

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

## Phase 3: Technical Deep Dive

**What happens:** Evaluate the *quality* of what IS present. Read each section with the eye of a principal engineer who has to sign off before the team starts building. Challenge every design decision.

**Six review dimensions:**

- **Correctness** — Does the logic hold? Race conditions, ordering assumptions, invariant violations?
- **Completeness** — All code paths covered? Unhappy path? Edge cases? Concurrent access?
- **Consistency** — Do the pieces fit together? API contract matches data model? Stated goals match the design?
- **Feasibility** — Buildable with the stated stack and constraints? Hidden complexity cliffs? Timeline math?
- **Operational Readiness** — Can on-call support this? Failure modes observable? Rollback path? Production debuggable?
- **Security Posture** — Beyond the security section: injection points, privilege escalation, data exposure, OWASP-style vulns embedded in the design itself?

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

Summary:
- Critical: X findings
- High: X findings
- Medium: X findings
- Low: X findings

The critical and high findings must be resolved before this design is
implementation-ready.
```

Order findings by severity, then by document order. Be specific. See [../examples/findings.md](../examples/findings.md) for good vs. bad finding examples.

---

## Phase 4: Continuity and Consistency Check

**What happens:** Cross-reference every section against every other. Catch the class of bugs that come from designs written across multiple sessions, by multiple authors, or after scope changes that updated some sections but not others.

**What to cross-check:**

- API contracts vs. data model (types match? all fields accounted for?)
- Error handling strategy vs. individual component descriptions
- Goals/non-goals vs. detailed design (does it achieve the goals? accidentally cover non-goals?)
- Security section vs. API design (all endpoints covered? auth on every mutation?)
- Performance targets vs. architecture (can it actually hit those numbers?)
- Migration plan vs. data model changes (all schema diffs covered?)
- Testing strategy vs. identified risks (highest risks covered by tests?)
- Component dependencies vs. failure modes (what happens when dependency X goes down?)
- Terminology consistency (same concept named the same everywhere?)
- Sequence/ordering assumptions across components

**Output to user:**

```
PHASE 4: CONTINUITY AND CONSISTENCY CHECK
============================================
Cross-referencing all sections for internal contradictions.

CONTRADICTION 1:
Sections: [Section A] vs [Section B]
Issue: [specific description of the inconsistency]
Resolution needed: [which section should be source of truth, or both need updating]

CONTRADICTION 2: ...

TERMINOLOGY INCONSISTENCIES:
- "[Term A]" in Section X vs "[Term B]" in Section Y — same concept, different names

Continuity Score: [CLEAN / MINOR ISSUES / SIGNIFICANT CONTRADICTIONS / STRUCTURALLY INCOHERENT]
```

If the document is clean, say so. Don't invent contradictions.

---

## Phase 5: Gap Analysis and Autoheal

**What happens:** Take every gap from Phases 2-4 and *draft the missing content*. Don't say "add an error handling section" — write it.

**Autoheal priority order:**

1. Critical findings from Phase 3 (fix the design, not just the doc)
2. Missing sections from Phase 2 (draft new sections)
3. Contradictions from Phase 4 (resolve with a consistent answer)
4. High findings from Phase 3
5. Weak sections from Phase 2 (strengthen with specifics)
6. Medium/Low findings (address inline)

**Autoheal rules:**

- **Mark every addition** with explicit AUTOHEALED markers so the user can distinguish original from added content:
  ```
  <!-- AUTOHEALED: [reason] -->
  [new content]
  <!-- /AUTOHEALED -->
  ```

- **Preserve author intent.** Extend the author's design philosophy, don't impose a different one. If they chose REST over GraphQL, autoheal the error handling in REST idioms.

- **Be concrete, not generic.** "Implement rate limiting" is not autohealed content. "Rate limit /api/v1/submit to 100 req/min/user via sliding window in Redis with key `ratelimit:{user_id}:{endpoint}`, return HTTP 429 + Retry-After" is autohealed content.

- **Flag uncertainty.** If autohealing requires a design decision the author should make, flag it explicitly:
  ```
  <!-- AUTOHEAL: DECISION REQUIRED -->
  Two viable approaches exist here:
  Option A: [description] — better for [tradeoff]
  Option B: [description] — better for [tradeoff]
  Recommendation: Option [X] because [reasoning]
  <!-- /AUTOHEAL: DECISION REQUIRED -->
  ```

- **Don't autoheal what you can't justify.** If a gap requires domain knowledge you don't have (compliance specifics, proprietary internals), flag as NEEDS AUTHOR INPUT rather than guessing.

**Output to user:**

```
PHASE 5: GAP ANALYSIS AND AUTOHEAL
=====================================
Addressing X gaps across Phases 2-4.

AUTOHEAL 1: [Gap description]
Source: Phase [N], Finding/Gap [reference]
Action: [DRAFTED NEW SECTION / REVISED EXISTING / RESOLVED CONTRADICTION / FLAGGED FOR AUTHOR]
Content: [The actual drafted content, or a summary if long]

AUTOHEAL 2: ...

Autoheal Summary:
- New sections drafted: X
- Existing sections strengthened: X
- Contradictions resolved: X
- Decisions flagged for author: X
- Gaps requiring author domain knowledge: X
```

---

## Phase 6: Adversarial Final Review

**What happens:** Take the now-healed document and attack it as if you're a hostile reviewer trying to block approval. The "would I bet my production uptime on this?" check.

**The Five Kill Questions:**

1. **"What's the blast radius?"** — If the worst-case failure happens, what's the impact? Is it contained? Can you recover? How fast?
2. **"What happens at 10x scale?"** — Does the design degrade gracefully or collapse? Where's the first bottleneck? Capacity cliff?
3. **"How does an attacker exploit this?"** — Most creative abuse path? Social engineering? API abuse? Exfiltration? Privilege escalation?
4. **"What can't you monitor?"** — Blind spots in observability? Silent failures? Corruption that won't trigger alerts until too late?
5. **"What did you assume that isn't written down?"** — Implicit assumptions about infra, team, third-party SLAs, user behavior, data volumes, network. If it's not in the doc, it's a risk.

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

ADDITIONAL ADVERSARIAL FINDINGS:
[Issues discovered during the adversarial pass not caught earlier]

Final Adversarial Verdict:
[IMPLEMENTATION-READY / NEEDS REVISION / NEEDS SIGNIFICANT REWORK]

Confidence Level:
- HIGH: 90%+ of implementation decisions resolved in the document
- MEDIUM: 70-89% resolved, some decisions made during implementation
- LOW: Below 70%, significant design work remains
```

---

## Phase 7: Hardened Output

**What happens:** Assemble the final deliverable.

**Three deliverables:**

1. **Review Scorecard** — single-page summary:

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

Top 3 Improvements Made:
  1. [Brief description of the most impactful autoheal]
  2. [Brief description]
  3. [Brief description]
```

2. **Hardened Document** — the full design with all autohealed content integrated inline, AUTOHEAL markers preserved. Output as a markdown file.

3. **Changelog** — diff-style list of every change, organized by phase:

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

**Output format:** Scorecard inline in conversation; Hardened Document saved as markdown file; Changelog appended as appendix. If the input is Word/PDF, output hardened version as markdown with a note about format conversion.
