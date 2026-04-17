# Taxonomy

The mindspace classifies every idea along two axes plus emergent tags.

## Axis 1: Project

Use the slug (left column) in frontmatter and folder paths.

| Slug | Full name | Scope |
|---|---|---|
| `summit` | Summit Software Solutions LLC | Consultancy work, GTM, content, tooling |
| `dtst` | DTST (Dental Talent Sourcing Tracker) | Specialty Dental Brands product |
| `carrot-hire` | Carrot Hire | Pre-ATS coordination tool for Carrot Fertility |
| `stockx` | StockX | W-2 platform engineer role |
| `rare-find` | Rare Find LLC | Krysta's recruiting consultancy (sales channel for Summit) |
| `healthspan` | Healthspan app | Open-source longevity health platform |
| `personal` | Personal | Health, home, finance, travel, relationships, anything not work |

**New project rule.** If an idea doesn't fit any existing project, propose a new slug. Slug rules: lowercase, hyphenated, max 3 words. On user approval, add a row to this table in the same commit that writes the first idea card.

## Axis 2: Idea-type

| Type | Meaning | Typical action |
|---|---|---|
| `build` | Something to make (feature, tool, content piece, asset) | Spike, prototype, ship |
| `research` | Something to investigate before deciding | Read, compare, synthesize |
| `buy` | Product or service to acquire | Evaluate, purchase |
| `read` | Article, book, paper, thread to consume | Read by date |
| `watch` | Video, talk, course | Watch by date |
| `try` | Experiment to run on self/process/system | Test, measure, decide |
| `explore` | Open-ended curiosity, no defined output | Sit with it, return later |

**New type rule.** Same as project — propose, get approval, append a row.

## Tags (emergent)

Tags are free-form but tracked in `_meta/patterns.json` with frequency counters. Conventions:

- lowercase, hyphenated
- prefer nouns and noun phrases
- 2-5 tags per card (3 is the sweet spot)
- prefer reusing existing tags over inventing new ones

When a tag's frequency crosses **10**, it becomes a candidate for promotion to a first-class field (e.g. a sub-type or a new axis). The self-learn protocol surfaces these candidates.

## Priority

| Level | Meaning | Calendar behavior |
|---|---|---|
| `high` | Time-sensitive or high-leverage; act within 7 days | Auto-creates calendar event |
| `medium` | Worth doing in the next 30 days | Suggests calendar event, asks first |
| `low` | Backburner, no urgency | No calendar event unless asked |

Default to `medium` when uncertain. If the source is purely informational (a `read` or `watch` with no deadline), `low` is usually right.
