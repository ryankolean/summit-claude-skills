# Findings — Good vs. Bad Examples

The single biggest quality lever for this skill is finding specificity. Vague findings get ignored. Specific findings get fixed.

## Phase 1 — Calibration check

**Good:**

> "Here's what I'm seeing: this is a microservices migration plan for your payment processing system, moving from a monolith to three bounded services (orders, payments, notifications) communicating over an event bus. The design optimizes for independent deployability over raw performance. Did I get that right?"

**Bad:**

> "This looks like a system design. Let me review it."

(Never skip the calibration. If you misread the system, every subsequent phase compounds the error.)

## Phase 3 — Technical Deep Dive findings

**Good (specific, actionable):**

> FINDING 3: [Severity: HIGH]
> Dimension: Completeness
> Location: Section 5.2 — Event Bus Design
> Issue: The event schema includes a `timestamp` field but does not specify timezone or format. Consumers will parse this inconsistently — some as UTC, some as local time, some as epoch milliseconds.
> Impact: Silent data corruption in any time-based logic downstream (billing cycles, SLA calculations, audit logs).
> Evidence: "Events include a timestamp field" (Section 5.2, paragraph 3)

**Bad (vague, unhelpful):**

> "The error handling could use more detail."

(NEVER do this. Say exactly what's missing and draft the content in Phase 5.)

## Phase 5 — Autoheal content

**Good (concrete, preserves author style):**

> AUTOHEAL 4: Timestamp specification
> Source: Phase 3, Finding 3
> Action: REVISED EXISTING
> Content: "Events include a `timestamp` field formatted as ISO 8601 with explicit UTC offset (e.g., `2026-04-15T14:30:00Z`). All producers MUST emit UTC. Consumers MUST NOT assume local timezone. The event bus rejects messages with non-conforming timestamps (HTTP 422, error code `INVALID_TIMESTAMP_FORMAT`)."

**Bad (generic, doesn't match the design):**

> "Add appropriate error handling for all API endpoints."

(NEVER do this. Write the actual error handling spec for the actual endpoints.)
