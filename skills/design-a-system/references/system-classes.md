# System Classes — Vocabulary and Artifacts

Load this when the user has named the system class and you need class-specific guidance for parts, interfaces, and flow.

## UI

**Examples.** App screen, form flow, dashboard, component tree, modal sequence.

**Parts vocabulary.** Components (presentational, container), hooks, state slices, route segments, providers.

**Interfaces.** Props in, events out, context consumed, side effects (network, local storage).

**Flow.** State transitions and data binding. Diagram as state chart or component tree with prop arrows.

**Failure modes.** Loading state, empty state, error state, partial data, stale cache, race condition between user input and async update.

**Likely consumers.** End user, analytics, deep links from other screens.

## Code architecture

**Examples.** Service, module layout, library, API surface, package boundary.

**Parts vocabulary.** Modules, packages, services, classes, pure functions, schemas.

**Interfaces.** Function signatures, HTTP routes, queue topics, schema contracts, env vars.

**Flow.** Call graph, module imports, request/response paths. Prefer dependency direction arrows.

**Failure modes.** Timeout, retry, partial failure, schema mismatch, version skew, dependency outage, idempotency violation.

**Likely consumers.** Other services, CLI, SDK clients, tests.

## Business process

**Examples.** Intake workflow, approval flow, review cycle, onboarding sequence.

**Parts vocabulary.** Roles, steps, decisions, artifacts, channels, escalations.

**Interfaces.** Inputs each role receives, outputs each role produces, decision criteria, escalation triggers.

**Flow.** Role handoffs over time. Swim-lane diagram. Capture both happy path and exception branches.

**Failure modes.** Role unavailable, stalled approval, ambiguous criteria, lost artifact, missed SLA, conflicting approvals.

**Likely consumers.** Downstream systems, audit, customer/stakeholder.

## Automation pipeline

**Examples.** Scraper + enrich + notify, cron chain, webhook flow, ETL job.

**Parts vocabulary.** Stages, triggers, transforms, sinks, queues, schedulers.

**Interfaces.** Trigger source, input schema, output schema, side effects, dead-letter behavior.

**Flow.** Stage diagram with retries, fan-out/fan-in, error paths to DLQ or alert.

**Failure modes.** Source unavailable, rate limit, malformed payload, idempotency, partial batch failure, downstream backpressure.

**Likely consumers.** Notification channel, downstream pipeline, dashboard, ticket system.
