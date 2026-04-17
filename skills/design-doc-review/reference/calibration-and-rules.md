# Calibration and Rules

## Contents
- Review depth calibration by document maturity
- The eight review rules
- Closing options

## Review depth calibration

Not every document needs the same scrutiny:

**Napkin-stage docs:** Focus on Phase 2 (structural gaps) and Phase 5 (drafting missing sections). Light touch on Phase 3 — the design isn't detailed enough to deep-dive. Skip Phase 4 (nothing to cross-reference). Phase 6 is a quick sanity check, not full adversarial.

**Draft-stage docs:** Full pipeline, but calibrate Phase 3 findings to "things that would be costly to fix later" not "every possible nitpick." Phase 5 autoheals focus on the biggest gaps.

**Review-ready docs:** Full pipeline at maximum depth. Phase 3 should be exhaustive. Phase 6 should be genuinely adversarial.

**Near-final docs:** Lighter Phase 2 (structure should be settled). Heavy Phase 3 and Phase 4 (the devil is in the details and contradictions). Phase 6 is the primary value — the design has been reviewed before, so fresh adversarial eyes are what's needed.

## The eight review rules

1. **Never skip a phase.** Even if a phase finds nothing, report that. A clean phase is valuable information — it means that class of problem isn't present.

2. **Be specific, not vague.** "The security section could be stronger" is not a finding. "The API accepts user-supplied SQL fragments in the `filter` query parameter (Section 6.3) with no parameterization, creating a SQL injection vector" is a finding.

3. **Preserve the author's voice.** Autohealed content should read like the original author wrote it. Match formality, naming conventions, documentation style.

4. **Distinguish opinion from defect.** If you'd do it differently but the author's approach works, say so: "I'd prefer X, but the author's choice of Y is valid because Z." Only flag as a finding if it's objectively wrong or has a concrete risk.

5. **Autohealed content is a draft, not gospel.** Always tell the user: these are starting points for the missing sections. The author knows their domain better than the reviewer. Autohealed content should be reviewed, not blindly accepted.

6. **Don't inflate severity.** CRITICAL only if it would cause data loss, security breach, system-wide outage, or make the design unimplementable. HIGH means production issues that aren't catastrophic. MEDIUM means suboptimal but works. LOW means style or minor improvements.

7. **The user decides when it's done.** After Phase 7, the user may want another pass, may want to address flagged decisions and re-review, or may be satisfied. Offer to re-run specific phases on the revised document if they make changes.

8. **Time-box your depth.** If the document is very large (30+ pages), call out that you're doing a breadth-first pass and offer to do a deep dive on specific sections the user is most concerned about.

## Closing options

After Phase 7, offer the user three paths:

- **Ship it** — accept the hardened doc as-is and move to implementation
- **Iterate** — address the flagged decisions, re-submit for a focused re-review on the changed sections only
- **Hand off** — chain to `architect-plan-for-dispatch` to convert the hardened design into a Dispatch execution plan
