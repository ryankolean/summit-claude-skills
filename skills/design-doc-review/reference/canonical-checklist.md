# Canonical Design Doc Checklist — 16 Sections

Used in Phase 2 (Structural Audit) of [phases.md](phases.md).

Evaluate presence AND quality of each section. A section that exists but is hand-wavy ("errors will be handled appropriately") counts as WEAK, not PRESENT.

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

## Status definitions

- **STRONG** — Section is present, complete, and specific. An implementer can act on it without follow-up questions.
- **WEAK** — Section is present but hand-wavy, generic, or missing critical specifics. Will require interpretation or follow-up.
- **MISSING** — No section addresses this concern. Will be flagged for autoheal in Phase 5.

## Critical gap rule

If sections 1, 4, 5, 6, 7, or 8 are MISSING, the document is not implementation-ready regardless of how strong the other sections are. These are the load-bearing sections.
