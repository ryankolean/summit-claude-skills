# Research protocol

D-lite three-phase research cycle invoked per card by the brain-dump skill's `research` mode. Each invocation dispatches one subagent per card; the subagent runs the three phases below in parallel via concurrent tool calls.

## Per-card budget

| Resource | Limit | Notes |
|---|---|---|
| Tokens | 15,000 soft / 30,000 hard | Soft = 20% overflow allowed; hard = orchestrator truncates |
| Tool calls | ~10 across all phases | Distributed roughly 30/40/30 across A/B/C |
| Wall clock | 1-2 min with parallel calls | 5 cards in parallel = ~8 min for 18-card backfill |

## Phase A — Source expansion

**Tools**: `WebFetch`
**Budget**: 5,000 tokens / 3 calls
**Inputs**: `card.source_url` (frontmatter), any URLs in card body

**Steps**:
1. Collect every URL from `source_url` and from the body (regex `https?://[^\s)]+`)
2. Skip rule: if the body already contains the post body verbatim (e.g., a fully-transcribed Instagram caption), emit the "already captured at depth" line and exit phase
3. WebFetch each URL with the prompt: "Extract: full body text, author + bio, publish date, key claims not summarized in '<insert card summary here>'."
4. Distill into 2-3 bullets that ADD information beyond what's in the card

**Failure handling**:
- 4xx/5xx: emit `- Source unreachable ({status}): {url}` as a bullet
- Auth-walled (Instagram, etc.): emit `- Source requires authentication — content not retrievable` and proceed
- Rate-limited: emit `- Source rate-limited — retry later` and proceed

## Phase B — Related discovery

**Tools**: `WebSearch`, `WebFetch`
**Budget**: 6,000 tokens / 5 calls
**Inputs**: `card.title`, top 3 `card.tags`

**Steps**:
1. Build a query string by combining the title with the top 3 tags. Drop stop words. Keep under 12 words.
2. Run one `WebSearch` with that query
3. Pick the top 2-3 results that are NOT the same as `source_url`
4. WebFetch each chosen result with the prompt: "One-sentence summary of the most relevant content for someone working on '<card.title>'."
5. Format each as `- [Title](url) — relevance hook`

**Failure handling**:
- Zero results: emit `- No related content found for query: '{query}'` and exit
- All results are duplicates of source_url: same exit message
- WebFetch failures: skip that result, fall back to using the search snippet

## Phase C — Internal context

**Tools**: `Grep`, `Glob`
**Budget**: 4,000 tokens / 3 calls
**Inputs**: top 3 `card.tags`, `card.suggested_action` (for path mentions), `card.project`

**Steps**:
1. Define scan paths:
   - `/Users/ryankolean/mindspace/library/` (always)
   - `/Users/ryankolean/summit-claude-skills/` (always)
   - Any explicit path mentioned in `card.suggested_action` (e.g., `/Users/ryankolean/freedom-at-45`)
   - Any well-known project directory: `/Users/ryankolean/dtst`, `/Users/ryankolean/fair-pass`, `/Users/ryankolean/summitsoftwaresolutionsllc` if `card.project` matches
2. Grep for each tag (top 3) across those paths. Combine results.
3. Glob for files matching the project name (e.g. `**/*freedom-at-45*`).
4. Pick the 2-3 most relevant matches based on:
   - Same project as the card
   - File contains multiple matching tags
   - Recency (newer files preferred)
5. Format as `- \`relative/path:line\` — 1-line connection`

**Failure handling**:
- Nothing matches: emit `- No internal references located across mindspace, summit-claude-skills, or referenced repos.` and exit

## Synthesis

Subagent assembles outputs into the format from `templates/research-block.md`. Returns ONLY the block, nothing else (no preamble, no commentary). Orchestrator handles file IO and commit.

## Refresh / staleness

Before dispatching a research subagent for a card, the orchestrator checks the card body for an existing `<!-- research: ISO_TIMESTAMP -->` marker:

| Condition | Action |
|---|---|
| No marker present | Run research, append block |
| Marker present, timestamp ≥ 4 days ago | Run research, replace block atomically |
| Marker present, timestamp < 4 days ago | Skip silently |
| Invocation is `research refresh <id>` | Override staleness, always run |

Block replacement: regex-locate `<!-- research:` through `<!-- /research -->` (DOTALL match), replace with the new block.

## Worked example — Freedom at 45 mini-app card

Input card frontmatter (excerpt):
```yaml
title: Build Freedom at 45 mini-app on summit website
project: summit
idea_type: build
tags: [mini-app, personal-finance, freedom-at-45, asset-management, summit-website]
priority: high
suggested_action: "Locate the existing Freedom at 45 codebase, link it here, then scope the mini-app version for the summit website."
```

Expected research output:

```markdown
<!-- research: 2026-04-18T15:30:00-04:00 -->
## Research

### Source expansion
- Source content already captured at depth — no expansion.

### Related discovery
- [Open Source Personal Finance Tools 2026](https://opensource.com/article/...) — covers GnuCash, Firefly III, Maybe Finance for self-hosted asset tracking
- [Building Embedded Mini-Apps in Next.js](https://nextjs.org/blog/...) — patterns for embedding interactive React tools inside a marketing site
- [Maybe Finance — open-source net-worth tracker](https://github.com/maybe-finance/maybe) — closest existing reference for the data model

### Internal context
- `/Users/ryankolean/freedom-at-45/README.md` — locate the actual codebase here (verify path)
- `/Users/ryankolean/summitsoftwaresolutionsllc/src/pages/index.tsx` — summit site entry point where the mini-app would mount
- `/Users/ryankolean/mindspace/library/summit/build/2026-04-17-1131-employee-educational-modules.md` — sibling mini-app card; share scaffolding decisions
<!-- /research -->
```

## Hard rules

- Subagent must return ONLY the research block. Any commentary breaks orchestrator parsing.
- Never modify card content outside the research block markers.
- Never skip a phase entirely without emitting its "none found" message — always preserve all three section headings.
- Never run research on a card whose existing block is < 4 days old, except via explicit `refresh` invocation.
