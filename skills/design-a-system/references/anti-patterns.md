# Anti-Patterns

Load when reviewing your own draft or when the user asks "what's wrong with this design?"

## Over-design

A system with 12 parts, 20 interface fields, and four failure tables for a weekend project is waste. Match depth to stakes. Three similar parts beat a premature abstraction.

## Premature technology binding

Calling a part `LambdaFunction` instead of `LeadIntake` locks the design to an implementation choice before the shape is proven. Names belong to responsibilities, not runtimes.

## Happy-path-only

Skipping Phase 4 produces designs that look clean in a doc and shatter in production. Every part needs at least one named failure mode.

## Designing around a single user story

A system designed for one user's one use case ships brittle. Force the dialog to name at least one adjacent use case the system should accommodate — or explicitly reject.

## Confusing design with planning

This skill produces a design. The build plan — file paths, commits, task ordering — is `architect-plan-for-dispatch`. Stay on the design side of the line.

## Phantom parts

A part that nobody triggers and nothing consumes. Often appears as "we'll need this someday." Delete it. Re-add when the day comes.

## Abstraction first

Inventing a `BaseProcessor` before two concrete processors exist. Wait for the third occurrence; the first two will mislead the abstraction.

## Hidden state

A part marked "stateless" that secretly relies on a cache, env var, or external file. Either declare the state in the contract or remove the dependency.
