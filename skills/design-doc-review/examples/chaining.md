# Chaining with Other Skills

## Inbound chains (skills that hand work to design-doc-review)

- **`interrogate` → design-doc-review:** If the user says "review this" but the document is ambiguous about its own purpose, trigger `interrogate` first to understand the user's expectations for the review (depth, focus areas, intended audience for the hardened version).

## Outbound chains (skills design-doc-review hands work to)

- **design-doc-review → `architect-plan-for-dispatch`:** After the design is hardened, the user may want to convert it into a Dispatch execution plan. Hand off the hardened document and the action items list.

- **design-doc-review → `devils-advocate`:** If the user wants deeper adversarial pressure on a specific design decision (beyond Phase 6's five kill questions), hand off to `devils-advocate` for focused hardening of that one aspect.

## When NOT to chain

- Do not chain to `prompt-to-skill` from design-doc-review — design hardening is a one-off review, not a reusable pattern to capture as a skill.
- Do not chain to `prompt-architect` — the hardened document is the deliverable, not a prompt for a future task.
